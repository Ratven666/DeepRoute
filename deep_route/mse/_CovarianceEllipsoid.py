import numpy as np


class CovarianceEllipsoid:
    """
    Klass dlya opisaniya ellipsoyda pogreshnosti po kovariacionnoj matrice.

    Pozvolyaet:
    - Vychislit' poluosi ellipsoyda (sobstvennye znacheniya)
    - Poluchit' pogreshnost' vdol' proizvol'nogo napravleniya
    - Rasschitat' radius ellipsoyda po azimutu i naklonu
    - Poluchit' harakteristiki ellipsoyda

    Koordinatnaya sistema:
    - North (N): gorizontal'noe napravlenie sever
    - East (E): gorizontal'noe napravlenie vostok
    - Vertical (V): vertikal'noe napravlenie (polozhitel'noe = vniz)

    Parameters
    ----------
    nn : float
        Dispersiya v napravlenii North (sigma_N^2), m^2
    ee : float
        Dispersiya v napravlenii East (sigma_E^2), m^2
    vv : float
        Dispersiya v napravlenii Vertical (sigma_V^2), m^2
    ne : float, default=0.0
        Kova rianciya mezhdu North i East
    nv : float, default=0.0
        Kovariantsiya mezhdu North i Vertical
    ev : float, default=0.0
        Kovariantsiya mezhdu East i Vertical

    Attributes
    ----------
    cov_matrix : np.ndarray, shape (3, 3)
        Kovariacionna ya matrica 3x3
    sigma_n, sigma_e, sigma_v : float
        Standartnye otkloneniya vdol' osey (v m)
    eigenvalues : np.ndarray, shape (3,)
        Sobstvennye znacheniya (dispersii vdol' glavnykh osey)
    eigenvectors : np.ndarray, shape (3, 3)
        Sobstvennye vektory (napravleniya glavnykh osey)
    semi_axes : np.ndarray, shape (3,)
        Poluosi ellipsoyda (sigma vdol' glavnykh osey)

    Examples
    --------
    # >>> ellipsoid = CovarianceEllipsoid(nn=1.5, ee=1.5, vv=0.7, ne=0.1)
    # >>> sigma_along_direction = ellipsoid.get_sigma_by_azimuth_inclination(45, 0)
    # >>> properties = ellipsoid.get_ellipsoid_properties()
    """

    def __init__(self, nn, ee, vv, ne=0.0, nv=0.0, ev=0.0):
        """
        Inicializacija ellipsoyda pogreshnosti

        Parameters
        ----------
        nn : float
            Dispersiya v napravlenii North
        ee : float
            Dispersiya v napravlenii East
        vv : float
            Dispersiya v napravlenii Vertical
        """
        self.cov_matrix = np.array([
            [nn, ne, nv],
            [ne, ee, ev],
            [nv, ev, vv]
        ])

        self.sigma_n = np.sqrt(max(nn, 0))
        self.sigma_e = np.sqrt(max(ee, 0))
        self.sigma_v = np.sqrt(max(vv, 0))

        self._calculate_eigenvalues()

    def _calculate_eigenvalues(self):
        """
        Vychislenie sobstvennykh znacheniy i vektorov kovariacionnoj matricy.

        Sobstvennye znacheniya predstavlyayut kvadraty poluosey ellipsoyda,
        sobstvennye vektory opredelyayut napravleniya etikh osey.
        """
        eigenvalues, eigenvectors = np.linalg.eigh(self.cov_matrix)

        idx = np.argsort(eigenvalues)[::-1]
        self.eigenvalues = eigenvalues[idx]
        self.eigenvectors = eigenvectors[:, idx]

        self.semi_axes = np.sqrt(np.maximum(self.eigenvalues, 0))

    def get_sigma_along_direction(self, direction_vector):
        """
        Rasschyot standartnogo otkloneniya vdol' proizvol'nogo napravleniya.

        Ispol'zuet formulu: sigma(u) = sqrt(u^T * Cov * u),
        gde u - normirovannyy napravlyayushchiy vektor

        Parameters
        ----------
        direction_vector : array-like, shape (3,)
            Napravlenie v vide vektora [n, e, v]

        Returns
        -------
        float
            Standartnoe otkloneniye vdol' dannogo napravleniya (v m)
        """
        u = np.array(direction_vector).flatten()
        norm = np.linalg.norm(u)

        if norm < 1e-10:
            return 0.0

        u = u / norm

        sigma_sq = u @ self.cov_matrix @ u
        return np.sqrt(max(sigma_sq, 0))

    def get_sigma_by_azimuth_inclination(self, azimuth_deg, inclination_deg):
        """
        Rasschyot pogreshnosti pozicii vdol' napravleniya,
        zadannogo azimutom i uglom naklona.

        Parameters
        ----------
        azimuth_deg : float
            Azimut v gradusakh (0-360)
            0 = North, 90 = East, 180 = South, 270 = West
        inclination_deg : float
            Ugol naklona v gradusakh (-90 do 90)
            0 = gorizontal'no
            90 = vertikal'no vniz
            -90 = vertikal'no vverkh

        Returns
        -------
        float
            Pogreshnost' pozicii vdol' dannogo napravleniya (v m)
        """
        az_rad = np.radians(azimuth_deg)
        inc_rad = np.radians(inclination_deg)

        nx = np.cos(inc_rad) * np.cos(az_rad)
        ex = np.cos(inc_rad) * np.sin(az_rad)
        vx = np.sin(inc_rad)

        direction = np.array([nx, ex, vx])
        return self.get_sigma_along_direction(direction)

    def get_radius_3sigma(self):
        """
        Poluchit' razmery ellipsoyda na urovne 3-sigma.

        Na urovne 3-sigma (trehsigma) veroyatnost' popadeniya tochki ~99.7%
        dlya normal'nogo raspredeleniya.

        Returns
        -------
        tuple
            (r1_3sigma, r2_3sigma, r3_3sigma) - razmery poluosey x 3
        """
        return tuple(3 * self.semi_axes)

    def get_ellipsoid_properties(self):
        """
        Poluchit' polnye svojstva ellipsoyda.

        Returns
        -------
        dict
            Slovar' so sleduyushchimi klyuchami:
            - 'sigma_n', 'sigma_e', 'sigma_v': standartnye otkloneniya
            - 'semi_axis_1', 'semi_axis_2', 'semi_axis_3': poluosi ellipsoyda
            - 'variance_1', 'variance_2', 'variance_3': dispersii
            - 'direction_1', 'direction_2', 'direction_3': napravleniya
        """
        return {
            'sigma_n': self.sigma_n,
            'sigma_e': self.sigma_e,
            'sigma_v': self.sigma_v,
            'semi_axis_1': self.semi_axes[0],
            'semi_axis_2': self.semi_axes[1],
            'semi_axis_3': self.semi_axes[2],
            'variance_1': self.eigenvalues[0],
            'variance_2': self.eigenvalues[1],
            'variance_3': self.eigenvalues[2],
            'direction_1': self.eigenvectors[:, 0],
            'direction_2': self.eigenvectors[:, 1],
            'direction_3': self.eigenvectors[:, 2],
        }

    @classmethod
    def from_row(cls, row_dict):
        """
        Sozdanie ellipsoyda iz slovarya s klyuchami
        'NN', 'EE', 'VV', 'NE', 'NV', 'EV'

        Parameters
        ----------
        row_dict : dict
            Slovar' s kovariancionnymy komponentami

        Returns
        -------
        CovarianceEllipsoid
            Novyy ob'ekt ellipsoyda
        """
        return cls(
            nn=row_dict.get('NN', 0),
            ee=row_dict.get('EE', 0),
            vv=row_dict.get('VV', 0),
            ne=row_dict.get('NE', 0),
            nv=row_dict.get('NV', 0),
            ev=row_dict.get('EV', 0)
        )


if __name__ == "__main__":
    ellipsoid = CovarianceEllipsoid(
        nn=1.5, ee=1.5, vv=0.7,
        ne=0.1, nv=0.0, ev=0.0
    )

    props = ellipsoid.get_ellipsoid_properties()
    print("Svojstva ellipsoyda:")
    print(f"  sigma_N: {props['sigma_n']:.4f} m")
    print(f"  sigma_E: {props['sigma_e']:.4f} m")
    print(f"  sigma_V: {props['sigma_v']:.4f} m")

    print(f"  A: {props['semi_axis_1']:.4f} m")
    print(f"  B: {props['semi_axis_2']:.4f} m")
    print(f"  C: {props['semi_axis_3']:.4f} m")

    print(f"  dirA: {props['direction_1']} m")
    print(f"  dirB: {props['direction_2']} m")
    print(f"  dirC: {props['direction_3']} m")

    sigma = ellipsoid.get_sigma_by_azimuth_inclination(45, 0)
    print(f"\nPogreshnost' vdol' azimuta 45: {sigma:.4f} m")

    r1, r2, r3 = ellipsoid.get_radius_3sigma()
    print(f"\nRazmery ellipsoyda (3sigma):")
    print(f"  Os' 1: {r1:.4f} m")
    print(f"  Os' 2: {r2:.4f} m")
    print(f"  Os' 3: {r3:.4f} m")