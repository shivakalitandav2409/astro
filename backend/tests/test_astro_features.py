import pytest
from datetime import date
from backend.astro_engine.ephemeris import (
    calculate_kp_sub_lords,
    assign_jaimini_karakas,
    compute_weekly_personal_forecast,
    full_kundli_bundle,
    compute_chart,
)

def test_kp_sub_lords_calculation():
    # Test Ashwini 0 deg (Aries 0 deg): RL=Mars, NL=Ketu, SL=Ketu, SSL=Ketu
    rl, nl, sl, ssl = calculate_kp_sub_lords(0.0)
    assert rl == "Mars"
    assert nl == "Ketu"
    assert sl == "Ketu"
    assert ssl == "Ketu"

    # Test Rohini around Taurus 15 deg (45 deg lon): RL=Venus, NL=Moon
    rl, nl, sl, ssl = calculate_kp_sub_lords(45.0)
    assert rl == "Venus"
    assert nl == "Moon"
    assert sl in ["Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu"]
    assert ssl in ["Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu"]

def test_jaimini_karakas_assignment():
    planets = [
        {"planet": "Sun", "lon": 128.5},      # Leo 8.5 deg
        {"planet": "Moon", "lon": 44.2},      # Taurus 14.2 deg
        {"planet": "Mars", "lon": 89.1},      # Gemini 29.1 deg -> Highest degree -> AK
        {"planet": "Mercury", "lon": 140.0},   # Leo 20.0 deg
        {"planet": "Jupiter", "lon": 215.3},   # Scorpio 5.3 deg
        {"planet": "Venus", "lon": 182.1},     # Libra 2.1 deg
        {"planet": "Saturn", "lon": 325.8},    # Aquarius 25.8 deg
        {"planet": "Rahu", "lon": 310.0},      # Excluded from 7 karakas
        {"planet": "Ketu", "lon": 130.0},      # Excluded from 7 karakas
    ]
    assigned = assign_jaimini_karakas(planets)
    p_dict = {p["planet"]: p for p in assigned}

    # Mars has highest degree in sign (29.1) -> AK
    assert p_dict["Mars"]["karaka_code"] == "AK"
    assert "Atmakaraka" in p_dict["Mars"]["karaka_en"]
    assert "आत्मकारक" in p_dict["Mars"]["karaka_hi"]

    # Venus has lowest degree in sign (2.1) -> DK
    assert p_dict["Venus"]["karaka_code"] == "DK"
    assert "Darakaraka" in p_dict["Venus"]["karaka_en"]

    # Rahu & Ketu should not have karaka_code
    assert "karaka_code" not in p_dict["Rahu"]
    assert "karaka_code" not in p_dict["Ketu"]

def test_weekly_personal_forecast():
    chart = compute_chart(
        dob="1995-08-15",
        birth_time="09:30",
        latitude=28.6139,
        longitude=77.2090,
    )
    start_d = "2026-11-28"
    forecast = compute_weekly_personal_forecast(chart, start_date=start_d)

    assert forecast["start_date"] == "2026-11-28"
    assert len(forecast["days"]) == 7
    for d in forecast["days"]:
        assert "date" in d
        assert "weekday" in d
        assert "transit_rashi_en" in d
        assert "house_from_moon" in d
        assert d["severity"] in ["mild", "moderate", "severe"]
        assert "theme_hi" in d
        assert "remedy_hi" in d
        assert "lucky_color_hi" in d
        assert "lucky_number" in d

def test_full_kundli_bundle_kp_and_weekly():
    member = {
        "name": "Integration Test Native",
        "dob": "1995-08-15",
        "birth_time": "09:30",
        "gender": "Male",
        "latitude": 28.6139,
        "longitude": 77.2090,
    }
    bundle = full_kundli_bundle(member)

    # Check weekly forecast presence
    assert "weekly_forecast" in bundle
    assert len(bundle["weekly_forecast"]["days"]) == 7

    # Check KP attributes on planets
    planets = bundle["chart"]["planets"]
    for p in planets:
        assert "rl" in p
        assert "nl" in p
        assert "sl" in p
        assert "ssl" in p
        assert "rl_hi" in p
        assert "nl_hi" in p
        assert "sl_hi" in p
        assert "ssl_hi" in p

    # Check KP attributes on ascendant
    asc = bundle["chart"]["ascendant"]
    assert "rl" in asc
    assert "nl" in asc
    assert "sl" in asc
    assert "ssl" in asc
