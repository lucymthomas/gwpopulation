"""
Implemented spin models
"""
import numpy as xp

from ..utils import beta_dist, truncnorm, truncskewnorm, unnormalized_2d_gaussian, unnormalized_2d_skew_gaussian
from .interped import InterpolatedNoBaseModelIdentical


def iid_spin(dataset, xi_spin, sigma_spin, amax, alpha_chi, beta_chi):
    r"""
    Independently and identically distributed spins.
    The magnitudes are assumed to follow a Beta distribution and the
    orientations are assumed to follow an isotropic + truncated half
    Gaussian mixture model.

    Parameters
    ----------
    dataset: dict
        Dictionary of numpy arrays containing 'a_1' and 'a_2'.
    xi_spin: float
        Fraction of black holes in preferentially aligned component.
    sigma_spin: float
        Width of preferentially aligned component.
    alpha_chi, beta_chi: float
        Parameters of Beta distribution for both black holes.
    amax: float
        Maximum black hole spin.
    """
    prior = iid_spin_orientation_gaussian_isotropic(
        dataset, xi_spin, sigma_spin
    ) * iid_spin_magnitude_beta(dataset, amax, alpha_chi, beta_chi)
    return prior


def iid_spin_magnitude_beta(dataset, amax=1, alpha_chi=1, beta_chi=1):
    """Independent and identically distributed beta distributions for both spin magnitudes.

    https://arxiv.org/abs/1805.06442 Eq. (10)
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html

    Parameters
    ----------
    dataset: dict
        Dictionary of numpy arrays containing 'a_1' and 'a_2'.
    alpha_chi, beta_chi: float
        Parameters of Beta distribution for both black holes.
    amax: float
        Maximum black hole spin.
    """
    return independent_spin_magnitude_beta(
        dataset, alpha_chi, alpha_chi, beta_chi, beta_chi, amax, amax
    )


def independent_spin_magnitude_beta(
    dataset, alpha_chi_1, alpha_chi_2, beta_chi_1, beta_chi_2, amax_1, amax_2
):
    """Independent beta distributions for both spin magnitudes.

    https://arxiv.org/abs/1805.06442 Eq. (10)
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html

    Parameters
    ----------
    dataset: dict
        Dictionary of numpy arrays containing 'a_1' and 'a_2'.
    alpha_chi_1, beta_chi_1: float
        Parameters of Beta distribution for more massive black hole.
    alpha_chi_2, beta_chi_2: float
        Parameters of Beta distribution for less massive black hole.
    amax_1, amax_2: float
        Maximum spin of the more/less massive black hole.
    """
    prior = beta_dist(
        dataset["a_1"], alpha_chi_1, beta_chi_1, scale=amax_1
    ) * beta_dist(dataset["a_2"], alpha_chi_2, beta_chi_2, scale=amax_2)
    return prior


def iid_spin_orientation_gaussian_isotropic(dataset, xi_spin, sigma_spin):
    r"""A mixture model of spin orientations with isotropic and normally
    distributed components. The distribution of primary and secondary spin
    orientations are expected to be identical and independent.

    https://arxiv.org/abs/1704.08370 Eq. (4)

    .. math::
        p(z_1, z_2 | \xi, \sigma) =
        \frac{(1 - \xi)^2}{4}
        + \xi \prod_{i\in\{1, 2\}} \mathcal{N}(z_i; \mu=1, \sigma=\sigma, z_\min=-1, z_\max=1)

    Where :math:`\mathcal{N}` is the truncated normal distribution.

    Parameters
    ----------
    dataset: dict
        Dictionary of numpy arrays for 'cos_tilt_1' and 'cos_tilt_2'.
    xi_spin: float
        Fraction of black holes in preferentially aligned component (:math:`\xi`).
    sigma_spin: float
        Width of preferentially aligned component.
    """
    return independent_spin_orientation_gaussian_isotropic(
        dataset, xi_spin, sigma_spin, sigma_spin
    )


def independent_spin_orientation_gaussian_isotropic(dataset, xi_spin, sigma_1, sigma_2):
    r"""A mixture model of spin orientations with isotropic and normally
    distributed components.

    https://arxiv.org/abs/1704.08370 Eq. (4)

    .. math::
        p(z_1, z_2 | \xi, \sigma_1, \sigma_2) =
        \frac{(1 - \xi)^2}{4}
        + \xi \prod_{i\in\{1, 2\}} \mathcal{N}(z_i; \mu=1, \sigma=\sigma_i, z_\min=-1, z_\max=1)

    Where :math:`\mathcal{N}` is the truncated normal distribution.

    Parameters
    ----------
    dataset: dict
        Dictionary of numpy arrays for 'cos_tilt_1' and 'cos_tilt_2'.
    xi_spin: float
        Fraction of black holes in preferentially aligned component (:math:`\xi`).
    sigma_1: float
        Width of preferentially aligned component for the more
        massive black hole (:math:`\sigma_1`).
    sigma_2: float
        Width of preferentially aligned component for the less
        massive black hole (:math:`\sigma_2`).
    """
    prior = (1 - xi_spin) / 4 + xi_spin * truncnorm(
        dataset["cos_tilt_1"], 1, sigma_1, 1, -1
    ) * truncnorm(dataset["cos_tilt_2"], 1, sigma_2, 1, -1)
    return prior


def gaussian_chi_eff(dataset, mu_chi_eff, sigma_chi_eff):
    r"""
    A Gaussian in chi effective distribution

    See https://arxiv.org/abs/2001.06051, https://arxiv.org/abs/2010.14533

    .. math::
        p(\chi_{\text{eff}}) = \mathcal{N}(\chi_{\text{eff}}; \mu=\mu_\chi, \sigma=\sigma_\chi, x_\min=-1, m_\max=1)

    Where :math:`\mathcal{N}` is a truncated Gaussian.

    Parameters
    ----------
    dataset: dict
        Input data, must contain `chi_eff` (:math:`\chi_{\text{eff}}`)
    mu_chi_eff: float
        Mean of the distribution (:math:`\mu_\chi`)
    sigma_chi_eff: float
        Standard deviation of the distribution (:math:`\sigma_\chi`)

    Returns
    -------
    array-like: The probability
    """
    return truncnorm(
        dataset["chi_eff"], mu=mu_chi_eff, sigma=sigma_chi_eff, low=-1, high=1
    )


def gaussian_chi_p(dataset, mu_chi_p, sigma_chi_p):
    r"""
    A Gaussian distribution in precessing effective spin (chi p)

    See https://arxiv.org/abs/2001.06051, https://arxiv.org/abs/2010.14533

    .. math::
        p(\chi_p) = \mathcal{N}(\chi_p}; \mu=\mu_\chi, \sigma=\sigma_\chi, x_\min=0, m_\max=1)

    Where :math:`\mathcal{N}` is a truncated Gaussian.

    Parameters
    ----------
    dataset: dict
        Input data, must contain `chi_eff` (:math:`\chi_p`)
    mu_chi_p: float
        Mean of the distribution (:math:`\mu_\chi`)
    sigma_chi_p: float
        Standard deviation of the distribution (:math:`\sigma_\chi`)

    Returns
    -------
    array-like: The probability
    """
    return truncnorm(dataset["chi_p"], mu=mu_chi_p, sigma=sigma_chi_p, low=0, high=1)


def gaussian_chi_p_chi_eff(dataset, mu_chi_eff, sigma_chi_eff, mu_chi_p, sigma_chi_p, rho):
    r"""
    A covariant Gaussian in effective aligned and precessing spins.

    See https://arxiv.org/abs/2001.06051, https://arxiv.org/abs/2010.14533

    The covariance matrix is given by:

    .. math::
        \Sigma = \begin{bmatrix}
            \sigma^2_{\text{eff}} & \rho \sigma_{\text{eff}} \sigma_{p} \\
            \rho \sigma_{\text{eff}} \sigma_{p} & \sigma^2_{p}
        \end{bmatrix}

    Parameters
    ----------
    dataset: dict
        Dictionary of numpy arrays for 'chi_eff' and 'chi_p'.
    mu_chi_eff: float
        Mean of the chi effective distribution (:math:`\mu_{\text{eff}}`)
    mu_chi_p: float
        Mean of the chi p distribution (:math:`\mu_{p}`)
    sigma_chi_eff: float
        Standard deviation of the chi effective distribution (:math:`\sigma_{\text{eff}}`)
    sigma_chi_p: float
        Standard deviation of the chi p distribution (:math:`\sigma_{p}`)
    rho: float
        Covariance between the two parameters (:math:`\rho`)
    Returns
    -------
    array-like: The probability
    """

    def _normalization(mu_chi_eff, sigma_chi_eff, mu_chi_p, sigma_chi_p, rho):
        chi_eff_linspace = xp.linspace(-1, 1, 500)
        chi_p_linspace = xp.linspace(0, 1, 250)
        chi_eff_grid, chi_p_grid = xp.meshgrid(chi_eff_linspace, chi_p_linspace)

        prob_grid = unnormalized_2d_gaussian(
            chi_eff_grid,
            chi_p_grid,
            mu_chi_eff,
            mu_chi_p,
            sigma_chi_eff,
            sigma_chi_p,
            rho,
        )
        normalization = xp.trapz(y=xp.trapz(y=prob_grid, axis=-1, x=chi_eff_linspace), axis=-1, x=chi_p_linspace)
        return normalization
    
    if rho == 0:
        prob = gaussian_chi_eff(
            dataset=dataset,
            mu_chi_eff=mu_chi_eff,
            sigma_chi_eff=sigma_chi_eff,
        )
        prob *= gaussian_chi_p(
            dataset=dataset, mu_chi_p=mu_chi_p, sigma_chi_p=sigma_chi_p
        )
    else:
        prob = unnormalized_2d_gaussian(
            dataset["chi_eff"],
            dataset["chi_p"],
            mu_chi_eff,
            mu_chi_p,
            sigma_chi_eff,
            sigma_chi_p,
            rho,
        )
        normalization = _normalization(
            mu_chi_eff=mu_chi_eff,
            sigma_chi_eff=sigma_chi_eff,
            mu_chi_p=mu_chi_p,
            sigma_chi_p=sigma_chi_p,
            rho=rho,
        )
        prob /= normalization
        prob *= xp.abs(dataset["chi_eff"]) <= 1
        prob *= (dataset["chi_p"] <= 1) * (dataset["chi_p"] >= 0)
        
    return prob


def skew_gaussian_chi_eff(dataset, mu_chi_eff, sigma_chi_eff, skew_chi_eff):
    r"""
    A Gaussian in chi effective distribution with skewness

    See https://arxiv.org/abs/2001.06051, https://arxiv.org/abs/2010.14533

    .. math::
        p(\chi_{\text{eff}}) = \mathcal{N}(\chi_{\text{eff}}; \mu=\mu_\chi, \sigma=\sigma_\chi, x_\min=-1, m_\max=1)

    Where :math:`\mathcal{N}` is a truncated Gaussian.

    Parameters
    ----------
    dataset: dict
        Input data, must contain `chi_eff` (:math:`\chi_{\text{eff}}`)
    mu_chi_eff: float
        Mean of the distribution (:math:`\mu_\chi`)
    sigma_chi_eff: float
        Standard deviation of the distribution (:math:`\sigma_\chi`)

    Returns
    -------
    array-like: The probability
    """
    return truncskewnorm(
        dataset["chi_eff"], mu=mu_chi_eff, sigma=sigma_chi_eff, alpha=skew_chi_eff, low=-1, high=1
    )


def skew_gaussian_chi_p(dataset, mu_chi_p, sigma_chi_p, skew_chi_p):
    r"""
    A Gaussian distribution in precessing effective spin (chi p) with skewness

    See https://arxiv.org/abs/2001.06051, https://arxiv.org/abs/2010.14533

    .. math::
        p(\chi_p) = \mathcal{N}(\chi_p}; \mu=\mu_\chi, \sigma=\sigma_\chi, x_\min=0, m_\max=1)

    Where :math:`\mathcal{N}` is a truncated Gaussian.

    Parameters
    ----------
    dataset: dict
        Input data, must contain `chi_eff` (:math:`\chi_p`)
    mu_chi_p: float
        Mean of the distribution (:math:`\mu_\chi`)
    sigma_chi_p: float
        Standard deviation of the distribution (:math:`\sigma_\chi`)

    Returns
    -------
    array-like: The probability
    """
    return truncskewnorm(dataset["chi_p"], mu=mu_chi_p, sigma=sigma_chi_p, alpha=skew_chi_p, low=0, high=1)

def gaussian_chi_p_chi_eff_skew(dataset, mu_chi_eff, sigma_chi_eff, mu_chi_p, sigma_chi_p, skew_chi_eff, skew_chi_p, rho):
    r"""
    A covariant Gaussian in effective aligned and precessing spins, including skew.

    See https://arxiv.org/abs/2001.06051, https://arxiv.org/abs/2010.14533

    The covariance matrix is given by:

    .. math::
        \Sigma = \begin{bmatrix}
            \sigma^2_{\text{eff}} & \rho \sigma_{\text{eff}} \sigma_{p} \\
            \rho \sigma_{\text{eff}} \sigma_{p} & \sigma^2_{p}
        \end{bmatrix}

    Parameters
    ----------
    dataset: dict
        Dictionary of numpy arrays for 'chi_eff' and 'chi_p'.
    mu_chi_eff: float
        Mean of the chi effective distribution (:math:`\mu_{\text{eff}}`)
    mu_chi_p: float
        Mean of the chi p distribution (:math:`\mu_{p}`)
    sigma_chi_eff: float
        Standard deviation of the chi effective distribution (:math:`\sigma_{\text{eff}}`)
    sigma_chi_p: float
        Standard deviation of the chi p distribution (:math:`\sigma_{p}`)
    skew_chi_eff: float
        Skewness of the chi effective  distribution (:math:`\alpha_{\text{eff}}`)
    skew_chi_p: float
        Skewness of the chi p distribution (:math:`\alpha_{p}`)
    rho: float
        Covariance between the two parameters (:math:`\rho`)
    Returns
    -------
    array-like: The probability
    """

    def _normalization(mu_chi_eff, sigma_chi_eff, mu_chi_p, sigma_chi_p, skew_chi_eff, skew_chi_p, rho):
        chi_eff_linspace = xp.linspace(-1, 1, 500)
        chi_p_linspace = xp.linspace(0, 1, 250)
        chi_eff_grid, chi_p_grid = xp.meshgrid(chi_eff_linspace, chi_p_linspace)

        prob_grid = unnormalized_2d_skew_gaussian(
            chi_eff_grid,
            chi_p_grid,
            mu_chi_eff,
            mu_chi_p,
            sigma_chi_eff,
            sigma_chi_p,
            skew_chi_eff,
            skew_chi_p,
            rho,
        )
        normalization = xp.trapz(y=xp.trapz(y=prob_grid, axis=-1, x=chi_eff_linspace), axis=-1, x=chi_p_linspace)
        return normalization
    
    if rho == 0:
        prob = skew_gaussian_chi_eff(
            dataset=dataset,
            mu_chi_eff=mu_chi_eff,
            sigma_chi_eff=sigma_chi_eff,
            skew_chi_eff=skew_chi_eff,
        )
        prob *= skew_gaussian_chi_p(
            dataset=dataset, mu_chi_p=mu_chi_p, sigma_chi_p=sigma_chi_p,
            skew_chi_p=skew_chi_p,
        )
    else:
        prob = unnormalized_2d_skew_gaussian(
            dataset["chi_eff"],
            dataset["chi_p"],
            mu_chi_eff,
            mu_chi_p,
            sigma_chi_eff,
            sigma_chi_p,
            skew_chi_eff,
            skew_chi_p,
            rho,
        )
        normalization = _normalization(
            mu_chi_eff=mu_chi_eff,
            sigma_chi_eff=sigma_chi_eff,
            mu_chi_p=mu_chi_p,
            sigma_chi_p=sigma_chi_p,
            skew_chi_eff=skew_chi_eff,
            skew_chi_p=skew_chi_p,
            rho=rho,
        )
        prob /= normalization
        prob *= xp.abs(dataset["chi_eff"]) <= 1
        prob *= (dataset["chi_p"] <= 1) * (dataset["chi_p"] >= 0)
        
    return prob


class SplineSpinMagnitudeIdentical(InterpolatedNoBaseModelIdentical):
    def __init__(self, minimum=0, maximum=1, nodes=5, kind="cubic"):

        super(SplineSpinMagnitudeIdentical, self).__init__(
            parameters=["a_1", "a_2"],
            minimum=minimum,
            maximum=maximum,
            nodes=nodes,
            kind=kind,
        )


class SplineSpinTiltIdentical(InterpolatedNoBaseModelIdentical):
    def __init__(self, minimum=-1, maximum=1, nodes=5, kind="cubic"):

        super(SplineSpinTiltIdentical, self).__init__(
            parameters=["cos_tilt_1", "cos_tilt_2"],
            minimum=minimum,
            maximum=maximum,
            nodes=nodes,
            kind=kind,
        )
