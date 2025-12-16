import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class WellPath:
    """
    РљР»Р°СЃСЃ РґР»СЏ СЂР°Р±РѕС‚С‹ СЃ С‚СЂР°РµРєС‚РѕСЂРёСЏРјРё СЃРєРІР°Р¶РёРЅ Рё СЌР»Р»РёРїСЃРѕРёРґР°РјРё РѕС€РёР±РѕРє.

    РџРѕРґРґРµСЂР¶РёРІР°РµС‚ РґРІРµ СЃРёСЃС‚РµРјС‹ РєРѕРІР°СЂРёР°С†РёРѕРЅРЅС‹С… РґР°РЅРЅС‹С…:
    1. Р›РѕРєР°Р»СЊРЅР°СЏ СЃРёСЃС‚РµРјР° (N-E-V): North, East, Vertical
    2. РђР·РёРјСѓС‚Р°Р»СЊРЅР°СЏ СЃРёСЃС‚РµРјР° (H-L-A): Horizontal, Lateral, Angular
    """

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
        """Р Р°СЃСЃС‡РёС‚С‹РІР°РµС‚ РґРµРєР°СЂС‚РѕРІС‹ РєРѕРѕСЂРґРёРЅР°С‚С‹ РјРµС‚РѕРґРѕРј СѓСЃСЂРµРґРЅС‘РЅРЅС‹С… СѓРіР»РѕРІ"""
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
        """Р Р°СЃСЃС‡РёС‚С‹РІР°РµС‚ СЌР»Р»РёРїСЃРѕРёРґС‹ РѕС€РёР±РѕРє Рё СЃРѕС…СЂР°РЅСЏРµС‚ РѕСЂРёРµРЅС‚РёСЂРѕРІР°РЅРёРµ РІСЃРµС… РїРѕР»СѓРѕСЃРµР№"""
        # РРЅРёС†РёР°Р»РёР·РёСЂСѓРµРј СЃС‚РѕР»Р±С†С‹ РґР»СЏ РєРѕРјРїРѕРЅРµРЅС‚ РєРѕРІР°СЂРёР°С†РёРё
        self.df['sigma_n'] = 0.0
        self.df['sigma_e'] = 0.0
        self.df['sigma_v'] = 0.0

        # Р”РѕРїРѕР»РЅРёС‚РµР»СЊРЅС‹Рµ РєРѕРјРїРѕРЅРµРЅС‚С‹ (РµСЃР»Рё РµСЃС‚СЊ РІ РґР°РЅРЅС‹С…)
        self.df['sigma_h'] = 0.0
        self.df['sigma_l'] = 0.0
        self.df['sigma_a'] = 0.0

        # РРЅРёС†РёР°Р»РёР·РёСЂСѓРµРј СЃС‚РѕР»Р±С†С‹ РґР»СЏ РїРѕР»СѓРѕСЃРµР№
        self.df['semi_axis_1'] = 0.0
        self.df['semi_axis_2'] = 0.0
        self.df['semi_axis_3'] = 0.0

        # РћСЂРёРµРЅС‚РёСЂРѕРІР°РЅРёРµ РїРѕР»СѓРѕСЃРµР№
        self.df['azimuth_axis1'] = 0.0
        self.df['inclination_axis1'] = 0.0
        self.df['azimuth_axis2'] = 0.0
        self.df['inclination_axis2'] = 0.0
        self.df['azimuth_axis3'] = 0.0
        self.df['inclination_axis3'] = 0.0

        # Р¤Р»Р°Рі РІР°Р»РёРґРЅРѕСЃС‚Рё РґР°РЅРЅС‹С…
        self.df['ellipsoid_valid'] = False

        for i, row in self.df.iterrows():
            md = row['MD']

            # РџРѕРёСЃРє Рё РёРЅС‚РµСЂРїРѕР»СЏС†РёСЏ РєРѕРІР°СЂРёР°С†РёРѕРЅРЅС‹С… РґР°РЅРЅС‹С…
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

            # Р Р°СЃСЃС‡РёС‚С‹РІР°РµРј СЃС‚Р°РЅРґР°СЂС‚РЅС‹Рµ РѕС‚РєР»РѕРЅРµРЅРёСЏ
            sigma_n = np.sqrt(max(cov_dict['NN'], 0))
            sigma_e = np.sqrt(max(cov_dict['EE'], 0))
            sigma_v = np.sqrt(max(cov_dict['VV'], 0))

            self.df.loc[i, 'sigma_n'] = sigma_n
            self.df.loc[i, 'sigma_e'] = sigma_e
            self.df.loc[i, 'sigma_v'] = sigma_v

            # РџРѕРїС‹С‚РєР° РїРѕР»СѓС‡РёС‚СЊ РєРѕРјРїРѕРЅРµРЅС‚С‹ H, L, A РµСЃР»Рё РѕРЅРё РµСЃС‚СЊ
            if 'HH' in cov_dict:
                self.df.loc[i, 'sigma_h'] = np.sqrt(max(cov_dict.get('HH', 0), 0))
                self.df.loc[i, 'sigma_l'] = np.sqrt(max(cov_dict.get('LL', 0), 0))
                self.df.loc[i, 'sigma_a'] = np.sqrt(max(cov_dict.get('AA', 0), 0))

            # РЎС‚СЂРѕРёРј РєРѕРІР°СЂРёР°С†РёРѕРЅРЅСѓСЋ РјР°С‚СЂРёС†Сѓ 3x3
            cov_matrix = np.array([
                [cov_dict['NN'], cov_dict['NE'], cov_dict['NV']],
                [cov_dict['NE'], cov_dict['EE'], cov_dict['EV']],
                [cov_dict['NV'], cov_dict['EV'], cov_dict['VV']]
            ])

            # Р’С‹С‡РёСЃР»СЏРµРј СЃРѕР±СЃС‚РІРµРЅРЅС‹Рµ Р·РЅР°С‡РµРЅРёСЏ Рё СЃРѕР±СЃС‚РІРµРЅРЅС‹Рµ РІРµРєС‚РѕСЂС‹
            eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

            # РЎРѕСЂС‚РёСЂСѓРµРј РІ СѓР±С‹РІР°СЋС‰РµРј РїРѕСЂСЏРґРєРµ
            idx = np.argsort(eigenvalues)[::-1]
            eigenvalues = eigenvalues[idx]
            eigenvectors = eigenvectors[:, idx]

            # Р Р°СЃСЃС‡РёС‚С‹РІР°РµРј РїРѕР»СѓРѕСЃРё
            semi_axes = np.sqrt(np.maximum(eigenvalues, 0))

            self.df.loc[i, 'semi_axis_1'] = semi_axes[0]
            self.df.loc[i, 'semi_axis_2'] = semi_axes[1]
            self.df.loc[i, 'semi_axis_3'] = semi_axes[2]

            # Р Р°СЃСЃС‡РёС‚С‹РІР°РµРј РѕСЂРёРµРЅС‚РёСЂРѕРІР°РЅРёРµ РґР»СЏ РљРђР–Р”РћР™ РїРѕР»СѓРѕСЃРё
            for axis_idx in range(3):
                dir_vec = eigenvectors[:, axis_idx]
                n, e, v = dir_vec[0], dir_vec[1], dir_vec[2]

                # РђР·РёРјСѓС‚
                azimuth = np.degrees(np.arctan2(e, n))
                if azimuth < 0:
                    azimuth += 360

                # РРЅРєР»РёРЅР°С†РёСЏ
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

            self.df.loc[i, 'ellipsoid_valid'] = True

    def get_ellipsoid_info(self):
        """Р’РѕР·РІСЂР°С‰Р°РµС‚ РёРЅС„РѕСЂРјР°С†РёСЋ РѕР± СЌР»Р»РёРїСЃРѕРёРґР°С… РѕС€РёР±РѕРє"""
        if self.cov_data is None:
            return None

        columns = [
            'MD',
            'sigma_n', 'sigma_e', 'sigma_v',
            'sigma_h', 'sigma_l', 'sigma_a',
            'semi_axis_1', 'semi_axis_2', 'semi_axis_3',
            'azimuth_axis1', 'inclination_axis1',
            'azimuth_axis2', 'inclination_axis2',
            'azimuth_axis3', 'inclination_axis3',
            'ellipsoid_valid'
        ]

        return self.df[columns]

    def validate_ellipsoid_calculations(self):
        """
        РўРµСЃС‚РёСЂСѓРµС‚ РїСЂР°РІРёР»СЊРЅРѕСЃС‚СЊ СЂР°СЃС‡РµС‚РѕРІ СЌР»Р»РёРїСЃРѕРёРґРѕРІ РѕС€РёР±РѕРє.
        Р’РѕР·РІСЂР°С‰Р°РµС‚ РЅР°Р±РѕСЂ РїСЂРѕРІРµСЂРѕРє Рё СЃС‚Р°С‚РёСЃС‚РёРєСѓ.
        """
        if self.cov_data is None:
            return {"error": "РќРµС‚ РґР°РЅРЅС‹С… РєРѕРІР°СЂРёР°С†РёРё"}

        ellipsoid_data = self.get_ellipsoid_info()
        valid_data = ellipsoid_data[ellipsoid_data['ellipsoid_valid']]

        results = {
            'total_points': len(ellipsoid_data),
            'valid_points': len(valid_data),
            'checks': {}
        }

        if len(valid_data) == 0:
            results['error'] = "РќРµС‚ РІР°Р»РёРґРЅС‹С… СЌР»Р»РёРїСЃРѕРёРґРѕРІ"
            return results

        # РџСЂРѕРІРµСЂРєР° 1: РЈРїРѕСЂСЏРґРѕС‡РµРЅРёРµ РїРѕР»СѓРѕСЃРµР№
        axis_order_check = (valid_data['semi_axis_1'] >= valid_data['semi_axis_2']).all() and \
                           (valid_data['semi_axis_2'] >= valid_data['semi_axis_3']).all()
        results['checks']['semi_axes_ordered'] = {
            'status': 'вњ“ PASS' if axis_order_check else 'вњ— FAIL',
            'description': 'РџРѕР»СѓРѕСЃРё СѓРїРѕСЂСЏРґРѕС‡РµРЅС‹: axis1 >= axis2 >= axis3'
        }

        # РџСЂРѕРІРµСЂРєР° 2: РђР·РёРјСѓС‚С‹ РІ РїСЂР°РІРёР»СЊРЅРѕРј РґРёР°РїР°Р·РѕРЅРµ
        az_check = ((valid_data['azimuth_axis1'] >= 0) & (valid_data['azimuth_axis1'] < 360)).all()
        results['checks']['azimuth_range'] = {
            'status': 'вњ“ PASS' if az_check else 'вњ— FAIL',
            'description': 'РђР·РёРјСѓС‚С‹ РІ РґРёР°РїР°Р·РѕРЅРµ [0-360)',
            'min': valid_data['azimuth_axis1'].min(),
            'max': valid_data['azimuth_axis1'].max()
        }

        # РџСЂРѕРІРµСЂРєР° 3: РРЅРєР»РёРЅР°С†РёРё РІ РїСЂР°РІРёР»СЊРЅРѕРј РґРёР°РїР°Р·РѕРЅРµ
        inc_check = ((valid_data['inclination_axis1'] >= -90) & (valid_data['inclination_axis1'] <= 90)).all()
        results['checks']['inclination_range'] = {
            'status': 'вњ“ PASS' if inc_check else 'вњ— FAIL',
            'description': 'РРЅРєР»РёРЅР°С†РёРё РІ РґРёР°РїР°Р·РѕРЅРµ [-90, 90]',
            'min': valid_data['inclination_axis1'].min(),
            'max': valid_data['inclination_axis1'].max()
        }

        # РџСЂРѕРІРµСЂРєР° 4: РћС‚РЅРѕС€РµРЅРёРµ РїРѕР»СѓРѕСЃРµР№
        axis_ratio = (valid_data['semi_axis_1'] / (valid_data['semi_axis_3'] + 1e-6)).max()
        ratio_check = axis_ratio < 100  # Р Р°Р·СѓРјРЅРѕРµ РѕРіСЂР°РЅРёС‡РµРЅРёРµ
        results['checks']['axis_ratio'] = {
            'status': 'вњ“ PASS' if ratio_check else 'вљ  WARNING',
            'description': 'РћС‚РЅРѕС€РµРЅРёРµ max/min РїРѕР»СѓРѕСЃРµР№',
            'max_ratio': axis_ratio,
            'recommendation': 'Р”РѕР»Р¶РЅРѕ Р±С‹С‚СЊ < 100 РґР»СЏ С„РёР·РёС‡РµСЃРєРё СЂРµР°Р»СЊРЅС‹С… СЌР»Р»РёРїСЃРѕРёРґРѕРІ'
        }

        # РџСЂРѕРІРµСЂРєР° 5: РњРѕРЅРѕС‚РѕРЅРЅС‹Р№ СЂРѕСЃС‚ РѕС€РёР±РѕРє СЃ РіР»СѓР±РёРЅРѕР№
        growth_check = (valid_data['semi_axis_1'].iloc[-1] > valid_data['semi_axis_1'].iloc[0])
        results['checks']['monotonic_growth'] = {
            'status': 'вњ“ PASS' if growth_check else 'вњ— FAIL',
            'description': 'РћС€РёР±РєР° СЂР°СЃС‚РµС‚ СЃ РіР»СѓР±РёРЅРѕР№',
            'first_axis1': valid_data['semi_axis_1'].iloc[0],
            'last_axis1': valid_data['semi_axis_1'].iloc[-1]
        }

        # РџСЂРѕРІРµСЂРєР° 6: РЎС‚Р°С‚РёСЃС‚РёРєР° РїРѕ РєРѕРјРїРѕРЅРµРЅС‚Р°Рј
        results['checks']['component_statistics'] = {
            'description': 'РЎС‚Р°С‚РёСЃС‚РёРєР° РєРѕРјРїРѕРЅРµРЅС‚ РѕС€РёР±РѕРє',
            'sigma_n': {
                'mean': valid_data['sigma_n'].mean(),
                'max': valid_data['sigma_n'].max(),
                'std': valid_data['sigma_n'].std()
            },
            'sigma_e': {
                'mean': valid_data['sigma_e'].mean(),
                'max': valid_data['sigma_e'].max(),
                'std': valid_data['sigma_e'].std()
            },
            'sigma_v': {
                'mean': valid_data['sigma_v'].mean(),
                'max': valid_data['sigma_v'].max(),
                'std': valid_data['sigma_v'].std()
            }
        }

        # РџСЂРѕРІРµСЂРєР° 7: РќР°Р»РёС‡РёРµ РґР°РЅРЅС‹С… H-L-A (РµСЃР»Рё РµСЃС‚СЊ)
        has_hla = valid_data['sigma_h'].max() > 0
        results['checks']['has_hla_components'] = {
            'status': 'вњ“ YES' if has_hla else 'вњ— NO',
            'description': 'РќР°Р»РёС‡РёРµ РєРѕРјРїРѕРЅРµРЅС‚ H-L-A'
        }

        if has_hla:
            # РџСЂРѕРІРµСЂРєР° СЃРѕРѕС‚РІРµС‚СЃС‚РІРёСЏ N-E-V Рё H-L-A
            # HH РґРѕР»Р¶РЅРѕ Р±С‹С‚СЊ в‰€ СЃСЂРµРґРЅРµРјСѓ РёР· NN Рё EE РґР»СЏ РІРµСЂС‚РёРєР°Р»СЊРЅРѕР№ СЃРєРІР°Р¶РёРЅС‹
            results['checks']['nev_hla_correspondence'] = {
                'description': 'РЎРѕРѕС‚РІРµС‚СЃС‚РІРёРµ СЃРёСЃС‚РµРј РєРѕРѕСЂРґРёРЅР°С‚ N-E-V Рё H-L-A',
                'avg_ne': (valid_data['sigma_n'] + valid_data['sigma_e']).mean() / 2,
                'avg_h': valid_data['sigma_h'].mean(),
                'correlation': 'РќР° РЅР°С‡Р°Р»СЊРЅС‹С… РіР»СѓР±РёРЅР°С… HH в‰€ (NN+EE)/2'
            }

        # РџСЂРѕРІРµСЂРєР° 8: Р¤РёР·РёС‡РµСЃРєР°СЏ СЂРµР°Р»СЊРЅРѕСЃС‚СЊ (РѕС€РёР±РєРё > 0)
        positive_check = (valid_data['semi_axis_1'] > 0).all() and \
                         (valid_data['semi_axis_2'] > 0).all() and \
                         (valid_data['semi_axis_3'] > 0).all()
        results['checks']['positive_values'] = {
            'status': 'вњ“ PASS' if positive_check else 'вњ— FAIL',
            'description': 'Р’СЃРµ РїРѕР»СѓРѕСЃРё > 0'
        }

        return results

    def print_validation_report(self):
        """Р’С‹РІРѕРґРёС‚ РїРѕРґСЂРѕР±РЅС‹Р№ РѕС‚С‡РµС‚ Рѕ РІР°Р»РёРґРЅРѕСЃС‚Рё СЂР°СЃС‡РµС‚РѕРІ"""
        results = self.validate_ellipsoid_calculations()

        print("\n" + "=" * 100)
        print("РћРўР§Р•Рў Рћ Р’РђР›РР”РђР¦РР Р РђРЎР§Р•РўРћР’ Р­Р›Р›РРџРЎРћРР”РћР’ РћРЁРР‘РћРљ")
        print("=" * 100)

        if 'error' in results:
            print(f"вњ— РћРЁРР‘РљРђ: {results['error']}")
            return

        print(f"\nРћР±СЂР°Р±РѕС‚Р°РЅРѕ С‚РѕС‡РµРє: {results['total_points']}")
        print(f"Р’Р°Р»РёРґРЅС‹С… С‚РѕС‡РµРє: {results['valid_points']}")
        print(f"РџСЂРѕС†РµРЅС‚ РІР°Р»РёРґРЅС‹С…: {100 * results['valid_points'] / results['total_points']:.1f}%")

        print("\n" + "-" * 100)
        print("Р Р•Р—РЈР›Р¬РўРђРўР« РџР РћР’Р•Р РћРљ:")
        print("-" * 100)

        for check_name, check_result in results['checks'].items():
            if isinstance(check_result, dict):
                status = check_result.get('status', '')
                description = check_result.get('description', '')

                print(f"\nвњ“ {check_name}")
                print(f"   РЎС‚Р°С‚СѓСЃ: {status}")
                print(f"   {description}")

                # Р’С‹РІРѕРґРёРј РґРѕРїРѕР»РЅРёС‚РµР»СЊРЅСѓСЋ РёРЅС„РѕСЂРјР°С†РёСЋ
                for key, value in check_result.items():
                    if key not in ['status', 'description']:
                        if isinstance(value, dict):
                            print(f"   {key}:")
                            for k, v in value.items():
                                if isinstance(v, float):
                                    print(f"      {k}: {v:.6f}")
                                else:
                                    print(f"      {k}: {v}")
                        else:
                            if isinstance(value, float):
                                print(f"   {key}: {value:.6f}")
                            else:
                                print(f"   {key}: {value}")

        print("\n" + "=" * 100)
        print("РљРћРќР•Р¦ РћРўР§Р•РўРђ")
        print("=" * 100)

    def get_stats(self):
        """Р’РѕР·РІСЂР°С‰Р°РµС‚ СЃС‚Р°С‚РёСЃС‚РёРєСѓ РїРѕ СЃРєРІР°Р¶РёРЅРµ"""
        last_x = self.df['X'].iloc[-1]
        last_y = self.df['Y'].iloc[-1]
        last_z = self.df['Z'].iloc[-1]
        horizontal_dist = np.sqrt(last_x ** 2 + last_y ** 2)

        return {
            'MD': self.df['MD'].iloc[-1],
            'TVD': self.df['TVD'].iloc[-1],
            'Max_Inc': self.df[self.inc_col].max(),
            'Mean_Az': self.df[self.az_col].mean(),
            'Horizontal_Dist': horizontal_dist,
        }

    def get_coordinates(self):
        """Р’РѕР·РІСЂР°С‰Р°РµС‚ РґРµРєР°СЂС‚РѕРІС‹ РєРѕРѕСЂРґРёРЅР°С‚С‹ СЃРєРІР°Р¶РёРЅС‹"""
        return self.df[['MD', self.inc_col, self.az_col, 'TVD', 'X', 'Y', 'Z']]


if __name__ == "__main__":
    from tabulate import tabulate

    # Р—Р°РіСЂСѓР·РєР° Рё С‚РµСЃС‚РёСЂРѕРІР°РЅРёРµ
    well = WellPath.init_by_csv_file(
        filepath='src/WELLPATH.csv',
        cov_filepath='src/Covariance_full.csv'
    )

    # Р’С‹РїРѕР»РЅСЏРµРј РїРѕР»РЅСѓСЋ РІР°Р»РёРґР°С†РёСЋ
    well.print_validation_report()

    # Р’С‹РІРѕРґРёРј РїСЂРёРјРµСЂС‹ РґР°РЅРЅС‹С…
    ellipsoid_info = well.get_ellipsoid_info()
    valid_data = ellipsoid_info[ellipsoid_info['ellipsoid_valid']].head(10)

    print("\n" + "=" * 100)
    print("РџР•Р Р’Р«Р• 10 РўРћР§Р•Рљ РЎ Р’РђР›РР”РќР«РњР Р­Р›Р›РРџРЎРћРР”РђРњР")
    print("=" * 100)
    print(tabulate(valid_data, headers='keys', tablefmt='grid', floatfmt='.4f'))