"""Empirical optical PM sensor relative humidity correction module.

Low-cost particulate sensors (PMS5003, SPS30) measure particles using light scattering.
At elevated relative humidity (typically >65%), hygroscopic aerosol growth increases
particle diameter, causing the sensor to overestimate dry particle mass concentration.
"""
from __future__ import annotations


def correct_pm_for_humidity(
    pm_raw: float | None,
    humidity_rh: float | None,
    factor: float = 0.25,
    rh_threshold: float = 65.0,
) -> float | None:
    """Apply empirical Kohler/hygroscopic aerosol correction to optical PM readings.

    Formula (Chakrabarti et al. / US EPA low-cost sensor correction form):
        If RH > rh_threshold:
            PM_corr = PM_raw / (1 + factor * (RH / (100 - RH)))
        Else:
            PM_corr = PM_raw
    """
    if pm_raw is None or pm_raw < 0.0:
        return None
    if humidity_rh is None or humidity_rh < 0.0 or humidity_rh > 100.0:
        return pm_raw

    if humidity_rh <= rh_threshold:
        return pm_raw

    # Avoid divide-by-zero if RH reaches 100%
    clamped_rh = min(99.0, humidity_rh)
    growth_factor = 1.0 + factor * (clamped_rh / (100.0 - clamped_rh))
    return max(0.0, pm_raw / growth_factor)
