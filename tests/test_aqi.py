"""Unit tests for India CPCB AQI calculations, breakpoints, and edge cases."""
from aircue.trigger.aqi import (
    aqi_to_category_cpcb,
    calculate_cpcb_aqi,
    calculate_pm10_sub_index,
    calculate_pm25_sub_index,
)


def test_pm25_breakpoints():
    # Good band: 0-30 -> 0-50
    assert calculate_pm25_sub_index(0.0) == 0.0
    assert calculate_pm25_sub_index(15.0) == 25.0
    assert calculate_pm25_sub_index(30.0) == 50.0

    # Satisfactory band: 30-60 -> 51-100
    assert calculate_pm25_sub_index(60.0) == 100.0

    # Moderate band: 60-90 -> 101-200
    assert calculate_pm25_sub_index(90.0) == 200.0

    # Poor band: 90-120 -> 201-300
    assert calculate_pm25_sub_index(120.0) == 300.0

    # Very Poor: 120-250 -> 301-400
    assert calculate_pm25_sub_index(250.0) == 400.0

    # Severe: 250-500 -> 401-500
    assert calculate_pm25_sub_index(500.0) == 500.0
    assert calculate_pm25_sub_index(600.0) == 500.0  # Capped at 500


def test_pm10_breakpoints():
    # Good band: 0-50 -> 0-50
    assert calculate_pm10_sub_index(0.0) == 0.0
    assert calculate_pm10_sub_index(50.0) == 50.0

    # Satisfactory: 50-100 -> 51-100
    assert calculate_pm10_sub_index(100.0) == 100.0

    # Moderate: 100-250 -> 101-200
    assert calculate_pm10_sub_index(250.0) == 200.0

    # Poor: 250-350 -> 201-300
    assert calculate_pm10_sub_index(350.0) == 300.0

    # Very Poor: 350-430 -> 301-400
    assert calculate_pm10_sub_index(430.0) == 400.0

    # Severe: >430 -> 401-500
    assert calculate_pm10_sub_index(600.0) == 500.0


def test_cpcb_aqi_composite():
    # PM2.5 = 60 (AQI 100), PM10 = 250 (AQI 200) -> composite should be max = 200
    aqi = calculate_cpcb_aqi(pm25=60.0, pm10=250.0)
    assert aqi == 200.0

    # Missing one pollutant
    assert calculate_cpcb_aqi(pm25=30.0, pm10=None) == 50.0
    assert calculate_cpcb_aqi(pm25=None, pm10=50.0) == 50.0
    assert calculate_cpcb_aqi(pm25=None, pm10=None) is None

    # Invalid / negative
    assert calculate_cpcb_aqi(pm25=-10.0, pm10=None) is None


def test_aqi_categories():
    assert aqi_to_category_cpcb(25.0) == "Good"
    assert aqi_to_category_cpcb(75.0) == "Satisfactory"
    assert aqi_to_category_cpcb(150.0) == "Moderate"
    assert aqi_to_category_cpcb(250.0) == "Poor"
    assert aqi_to_category_cpcb(350.0) == "Very Poor"
    assert aqi_to_category_cpcb(450.0) == "Severe"
    assert aqi_to_category_cpcb(None) == "Unknown"
