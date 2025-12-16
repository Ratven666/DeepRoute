import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class WellPath:
    def __init__(self, data_frame, cov_data=None):
        self.df = data_frame.copy()
        self._detect_column_names()
        self.df['Inc_rad'] = np.radians(self.df[self.inc_col])
        self.df['Az_rad'] = np.radians(self.df[self.az_col])
        self.df['X'] = 0.0
        self.df['Y'] = 0.0
        self.df['Z'] = 0.0
        self._calculate_coordinates()
        self.cov_data = cov_data
        if cov_data is not None:
            self._calculate_ellipsoids()

    def _detect_column_names(self):
        cols = self.df.columns
        if 'Inc (В°)' in cols:
            self.inc_col = 'Inc (В°)'
        elif 'Inc' in cols:
            self.inc_col = 'Inc'
        else:
            raise ValueError("Not found Inc")

        if 'Az (В°)' in cols:
            self.az_col = 'Az (В°)'
        elif 'Az' in cols:
            self.az_col = 'Az'
        else:
            raise ValueError("Not found Az")

    @classmethod
    def init_by_csv_file(cls, filepath, sep=';', cov_filepath=None):
        df = pd.read_csv(filepath, sep=sep, encoding='utf-8-sig')
        df.columns = df.columns.str.strip()
        df = df.replace(',', '.', regex=True)
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        cov_data = None
        if cov_filepath is not None:
            cov_data = pd.read_csv(cov_filepath, sep=sep, encoding='utf-8-sig')
            cov_data.columns = cov_data.columns.str.strip()
            cov_data = cov_data.replace(',', '.', regex=True)
            for col in cov_data.columns:
                cov_data[col] = pd.to_numeric(cov_data[col], errors='coerce')

        return cls(df, cov_data)

    def _calculate_coordinates(self):
        x, y, z = 0.0, 0.0, 0.0
        for i in range(len(self.df)):
            self.df.loc[i, 'X'] = x
            self.df.loc[i, 'Y'] = y
            self.df.loc[i, 'Z'] = z

            if i < len(self.df) - 1:
                inc_avg = (self.df.loc[i, 'Inc_rad'] + self.df.loc[i + 1, 'Inc_rad']) / 2
                az_avg = (self.df.loc[i, 'Az_rad'] + self.df.loc[i + 1, 'Az_rad']) / 2
                md_interval = self.df.loc[i + 1, 'MD'] - self.df.loc[i, 'MD']

                dz = md_interval * np.cos(inc_avg)
                dr = md_interval * np.sin(inc_avg)
                dx = dr * np.sin(az_avg)
                dy = dr * np.cos(az_avg)

                x += dx
                y += dy
                z += dz

    def _calculate_ellipsoids(self):
        self.df['sigma_n'] = 0.0
        self.df['sigma_e'] = 0.0
        self.df['sigma_v'] = 0.0
        self.df['semi_axis_1'] = 0.0
        self.df['semi_axis_2'] = 0.0
        self.df['semi_axis_3'] = 0.0
        self.df['azimuth_axis1'] = 0.0
        self.df['inclination_axis1'] = 0.0
        self.df['azimuth_axis2'] = 0.0
        self.df['inclination_axis2'] = 0.0
        self.df['azimuth_axis3'] = 0.0
        self.df['inclination_axis3'] = 0.0

        for i, row in self.df.iterrows():
            md = row['MD']
            cov_row = self.cov_data[self.cov_data['Md'] == md]

            if cov_row.empty:
                idx_before = (self.cov_data['Md'] <= md).sum() - 1

                if idx_before < 0:
                    continue

                if idx_before >= len(self.cov_data) - 1:
                    cov_row = self.cov_data.iloc[-1:]
                else:
                    row_before = self.cov_data.iloc[idx_before]
                    row_after = self.cov_data.iloc[idx_before + 1]

                    alpha = (md - row_before['Md']) / (row_after['Md'] - row_before['Md'])

                    nn = row_before['NN'] + alpha * (row_after['NN'] - row_before['NN'])
                    ee = row_before['EE'] + alpha * (row_after['EE'] - row_before['EE'])
                    vv = row_before['VV'] + alpha * (row_after['VV'] - row_before['VV'])
                    ne = row_before['NE'] + alpha * (row_after['NE'] - row_before['NE'])
                    nv = row_before['NV'] + alpha * (row_after['NV'] - row_before['NV'])
                    ev = row_before['EV'] + alpha * (row_after['EV'] - row_before['EV'])

                    cov_dict = {'NN': nn, 'EE': ee, 'VV': vv, 'NE': ne, 'NV': nv, 'EV': ev}
            else:
                cov_dict = cov_row.iloc[0].to_dict()

            sigma_n = np.sqrt(max(cov_dict['NN'], 0))
            sigma_e = np.sqrt(max(cov_dict['EE'], 0))
            sigma_v = np.sqrt(max(cov_dict['VV'], 0))

            self.df.loc[i, 'sigma_n'] = sigma_n
            self.df.loc[i, 'sigma_e'] = sigma_e
            self.df.loc[i, 'sigma_v'] = sigma_v

            cov_matrix = np.array([
                [cov_dict['NN'], cov_dict['NE'], cov_dict['NV']],
                [cov_dict['NE'], cov_dict['EE'], cov_dict['EV']],
                [cov_dict['NV'], cov_dict['EV'], cov_dict['VV']]
            ])

            eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

            idx = np.argsort(eigenvalues)[::-1]
            eigenvalues = eigenvalues[idx]
            eigenvectors = eigenvectors[:, idx]

            semi_axes = np.sqrt(np.maximum(eigenvalues, 0))

            self.df.loc[i, 'semi_axis_1'] = semi_axes[0]
            self.df.loc[i, 'semi_axis_2'] = semi_axes[1]
            self.df.loc[i, 'semi_axis_3'] = semi_axes[2]

            for axis_idx in range(3):
                dir_vec = eigenvectors[:, axis_idx]
                n, e, v = dir_vec[0], dir_vec[1], dir_vec[2]

                azimuth = np.degrees(np.arctan2(e, n))
                if azimuth < 0:
                    azimuth += 360

                inclination = np.degrees(np.arcsin(-v))

                if axis_idx == 0:
                    self.df.loc[i, 'azimuth_axis1'] = azimuth
                    self.df.loc[i, 'inclination_axis1'] = inclination
                elif axis_idx == 1:
                    self.df.loc[i, 'azimuth_axis2'] = azimuth
                    self.df.loc[i, 'inclination_axis2'] = inclination
                elif axis_idx == 2:
                    self.df.loc[i, 'azimuth_axis3'] = azimuth
                    self.df.loc[i, 'inclination_axis3'] = inclination

    @staticmethod
    def _create_ellipsoid_points(center, semi_axes, rotation_angles, n_points=20):
        u = np.linspace(0, 2 * np.pi, n_points)
        v = np.linspace(0, np.pi, n_points)

        x_sphere = np.outer(np.cos(u), np.sin(v))
        y_sphere = np.outer(np.sin(u), np.sin(v))
        z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))

        a, b, c = semi_axes
        x_ellipsoid = a * x_sphere
        y_ellipsoid = b * y_sphere
        z_ellipsoid = c * z_sphere

        az_rad = np.radians(rotation_angles['azimuth'])
        inc_rad = np.radians(rotation_angles['inclination'])

        x_rot = (x_ellipsoid * np.cos(az_rad) - y_ellipsoid * np.sin(az_rad))
        y_rot = (x_ellipsoid * np.sin(az_rad) + y_ellipsoid * np.cos(az_rad))
        z_rot = z_ellipsoid

        x = x_rot + center[0]
        y = y_rot + center[1]
        z = z_rot + center[2]
        return x, y, z

    def plot_3d_with_ellipsoids_better(self, indices=None, n_points=25, scale_factor=1.0):
        if self.cov_data is None:
            print("Нет данных по ковариационным матрицам!")
            return None, None

        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')

        ax.plot(self.df['X'], self.df['Y'], -self.df['Z'],
                'b-', linewidth=3, label='РўСЂР°РµРєС‚РѕСЂРёСЏ', zorder=10)

        scatter = ax.scatter(self.df['X'], self.df['Y'], -self.df['Z'],
                             c=self.df[self.inc_col], cmap='viridis',
                             s=15, alpha=0.4, zorder=5)

        cbar = plt.colorbar(scatter, ax=ax, pad=0.1, shrink=0.8)
        cbar.set_label('РЈРіРѕР» (deg)', rotation=270, labelpad=15)

        if indices is None:
            n_ellipsoids = min(8, len(self.df) // 10)
            indices = np.linspace(10, len(self.df) - 1, n_ellipsoids, dtype=int)

        colors = plt.cm.plasma(np.linspace(0, 1, len(indices)))

        for idx_num, idx in enumerate(indices):
            if idx >= len(self.df):
                continue

            row = self.df.iloc[idx]

            if pd.isna(row['semi_axis_1']) or row['semi_axis_1'] < 0.1:
                continue

            center = np.array([row['X'], row['Y'], -row['Z']])
            semi_axes = np.array([
                row['semi_axis_1'],
                row['semi_axis_2'],
                row['semi_axis_3']
            ]) * scale_factor

            rotation_angles = {
                'azimuth': row['azimuth_axis1'],
                'inclination': row['inclination_axis1']
            }

            X_ell, Y_ell, Z_ell = self._create_ellipsoid_points(
                center, semi_axes, rotation_angles, n_points=n_points)

            surf = ax.plot_surface(X_ell, Y_ell, Z_ell,
                                   color=colors[idx_num],
                                   alpha=0.4,
                                   edgecolor='darkgray',
                                   linewidth=0.3,
                                   rstride=2, cstride=2)

            ax.scatter([row['X']], [row['Y']], [-row['Z']],
                       color=colors[idx_num], s=100, marker='o',
                       edgecolors='black', linewidth=2, zorder=20,
                       label=f"MD={row['MD']:.0f}m (a1={row['semi_axis_1']:.1f}m)")

        ax.set_xlabel('X (m)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Y (m)', fontsize=12, fontweight='bold')
        ax.set_zlabel('Z - Depth (m)', fontsize=12, fontweight='bold')
        ax.set_title('3D Well Trajectory with Uncertainty Ellipsoids',
                     fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=9, ncol=1, framealpha=0.95)
        plt.tight_layout()
        return fig, ax

    def get_coordinates(self):
        return self.df[['MD', self.inc_col, self.az_col, 'TVD', 'X', 'Y', 'Z']]

    def get_ellipsoid_info(self):
        if self.cov_data is None:
            return None
        columns = [
            'MD',
            'sigma_n', 'sigma_e', 'sigma_v',
            'semi_axis_1', 'semi_axis_2', 'semi_axis_3',
            'azimuth_axis1', 'inclination_axis1',
            'azimuth_axis2', 'inclination_axis2',
            'azimuth_axis3', 'inclination_axis3'
        ]
        return self.df[columns]


if __name__ == "__main__":
    from tabulate import tabulate

    well = WellPath.init_by_csv_file(
        filepath='src/WELLPATH.csv',
        cov_filepath='src/Covariance.csv'
    )

    # Выдод графика
    fig, ax = well.plot_3d_with_ellipsoids_better(scale_factor=10.0)
    plt.show()

    # Вывод датафрейма с праметрами эллипсойдов погрешности
    print("\n" + "=" * 120)
    print("Параметры эллипсойдов погрешности")
    print("=" * 120)
    print(tabulate(well.get_ellipsoid_info(), headers='keys', tablefmt='pretty'))

    print("\n" + "=" * 120)
    print("Координаты точек")
    print("=" * 120)
    print(tabulate(well.get_coordinates(), headers='keys', tablefmt='pretty'))
