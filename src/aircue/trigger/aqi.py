"""India Central Pollution Control Board (CPCB) National AQI sub-index calculations.

Strictly typed, side-effect-free functions implementing linear interpolation across
official CPCB breakpoint bands for PM2.5 and PM10.
"""
from __future__ import annotations

from typing import NamedTuple


class BreakpointBand(NamedTuple):
    c_low: float
    c_high: float
    i_low: float
    i_high: float


# Official CPCB Breakpoints for PM2.5 (in µg/m³)
# Good (0-50): 0-30
# Satisfactory (51-100): 31-60
# Moderate (101-200): 61-90
# Poor (201-300): 91-120
# Very Poor (301-400): 121-250
# Severe (401-500): 250+ (capped at 500 for index)
PM25_BREAKPOINTS: list[BreakpointBand] = [
    BreakpointBand(0.0, 30.0, 0.0, 50.0),
    BreakpointBand(30.0, 60.0, 51.0, 100.0),
    BreakpointBand(60.0, 90.0, 101.0, 200.0),
    BreakpointBand(90.0, 120.0, 201.0, 300.0),
    BreakpointBand(120.0, 250.0, 301.0, 400.0),
    BreakpointBand(250.0, 500.0, 401.0, 500.0),
]

# Official CPCB Breakpoints for PM10 (in µg/m³)
# Good (0-50): 0-50
# Satisfactory (51-100): 51-100
# Moderate (101-200): 101-250
# Poor (201-300): 251-350
# Very Poor (301-400): 351-430
# Severe (401-500): 430+ (capped at 500 for index)
PM10_BREAKPOINTS: list[BreakpointBand] = [
    BreakpointBand(0.0, 50.0, 0.0, 50.0),
    BreakpointBand(50.0, 100.0, 51.0, 100.0),
    BreakpointBand(100.0, 250.0, 101.0, 200.0),
    BreakpointBand(250.0, 350.0, 201.0, 300.0),
    BreakpointBand(350.0, 430.0, 301.0, 400.0),
    BreakpointBand(430.0, 600.0, 401.0, 500.0),
]


def interpolate_sub_index(conc: float, breakpoints: list[BreakpointBand]) -> float | None:
    """Linearly interpolate sub-index for a concentration value across breakpoint bands.

    Returns None if concentration is negative or non-finite.
    """
    if conc < 0.0:
        return None

    # Handle value exceeding highest band: clamp to 500
    if conc >= breakpoints[-1].c_high:
        return 500.0

    for band in breakpoints:
        if band.c_low <= conc <= band.c_high:
            if band.c_high == band.c_low:
                return band.i_low
            ratio = (conc - band.c_low) / (band.c_high - band.c_low)
            return band.i_low + ratio * (band.i_high - band.i_low)

    # In case concentration lands slightly beyond highest low bound
    if conc > breakpoints[-1].c_low:
        ratio = (conc - breakpoints[-1].c_low) / (breakpoints[-1].c_high - breakpoints[-1].c_low)
        return min(500.0, breakpoints[-1].i_low + ratio * (breakpoints[-1].i_high - breakpoints[-1].i_low))

    return None


def calculate_pm25_sub_index(pm25: float | None) -> float | None:
    """Calculate CPCB PM2.5 sub-index."""
    if pm25 is None or pm25 < 0.0:
        return None
    return interpolate_sub_index(pm25, PM25_BREAKPOINTS)


def calculate_pm10_sub_index(pm10: float | None) -> float | None:
    """Calculate CPCB PM10 sub-index."""
    if pm10 is None or pm10 < 0.0:
        return None
    return interpolate_sub_index(pm10, PM10_BREAKPOINTS)


def calculate_cpcb_aqi(pm25: float | None, pm10: float | None) -> float | None:
    """Calculate CPCB National AQI from PM2.5 and PM10 sub-indices.

    Under CPCB guidelines, at least one critical pollutant must be valid,
    and AQI is defined as the maximum of sub-indices.
    """
    si_pm25 = calculate_pm25_sub_index(pm25)
    si_pm10 = calculate_pm10_sub_index(pm10)

    if si_pm25 is None and si_pm10 is None:
        return None
    if si_pm25 is None:
        return si_pm10
    if si_pm10 is None:
        return si_pm25
    return max(si_pm25, si_pm10)


def aqi_to_category_cpcb(aqi: float | None) -> str:
    """Map a CPCB AQI value to standard category name."""
    if aqi is None or aqi < 0:
        return "Unknown"
    if aqi <= 50.0:
        return "Good"
    if aqi <= 100.0:
        return "Satisfactory"
    if aqi <= 200.0:
        return "Moderate"
    if aqi <= 300.0:
        return "Poor"
    if aqi <= 400.0:
        return "Very Poor"
    return "Severe"
