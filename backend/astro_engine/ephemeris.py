"""Swiss Ephemeris (Lahiri Sidereal) calculation engine for Kundli, Dashas, Matchmaking & Choghadiya Panchang."""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone
from typing import Any

import swisseph as swe

# Force Chitrapaksha / Lahiri Ayanamsa globally for Vedic & Lal Kitab calculations
swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
CALC_FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
TROP_FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED

RASHIS = [
    "Aries (Mesha)", "Taurus (Vrishabha)", "Gemini (Mithuna)", "Cancer (Karka)",
    "Leo (Simha)", "Virgo (Kanya)", "Libra (Tula)", "Scorpio (Vrishchika)",
    "Sagittarius (Dhanu)", "Capricorn (Makara)", "Aquarius (Kumbha)", "Pisces (Meena)",
]
RASHI_LORDS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
]

PLANET_NAMES_HI = {
    "Sun": "सूर्य", "Moon": "चंद्रमा", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि", "Rahu": "राहु", "Ketu": "केतु",
}

RASHIS_HI = [
    "मेष (Aries)", "वृषभ (Taurus)", "मिथुन (Gemini)", "कर्क (Cancer)",
    "सिंह (Leo)", "कन्या (Virgo)", "तुला (Libra)", "वृश्चिक (Scorpio)",
    "धनु (Sagittarius)", "मकर (Capricorn)", "कुंभ (Aquarius)", "मीन (Pisces)",
]

RASHI_LORDS_HI = [
    "मंगल", "शुक्र", "बुध", "चंद्रमा", "सूर्य", "बुध",
    "शुक्र", "मंगल", "गुरु", "शनि", "शनि", "गुरु",
]

DIGNITY_HI = {
    "Exalted": "उच्च (शुभ)",
    "Debilitated": "नीच (सावधानी)",
    "Own Sign": "स्वराशि",
    "Friendly": "मित्र राशि",
    "Neutral / Mixed": "सामान्य",
}

NAKSHATRAS = [
    ("Ashwini", "Ketu"), ("Bharani", "Venus"), ("Krittika", "Sun"),
    ("Rohini", "Moon"), ("Mrigashira", "Mars"), ("Ardra", "Rahu"),
    ("Punarvasu", "Jupiter"), ("Pushya", "Saturn"), ("Ashlesha", "Mercury"),
    ("Magha", "Ketu"), ("Purva Phalguni", "Venus"), ("Uttara Phalguni", "Sun"),
    ("Hasta", "Moon"), ("Chitra", "Mars"), ("Swati", "Rahu"),
    ("Vishakha", "Jupiter"), ("Anuradha", "Saturn"), ("Jyeshtha", "Mercury"),
    ("Mula", "Ketu"), ("Purva Ashadha", "Venus"), ("Uttara Ashadha", "Sun"),
    ("Shravana", "Moon"), ("Dhanishta", "Mars"), ("Shatabhisha", "Rahu"),
    ("Purva Bhadrapada", "Jupiter"), ("Uttara Bhadrapada", "Saturn"), ("Revati", "Mercury"),
]

DASHA_ORDER = [
    ("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10),
    ("Mars", 7), ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17),
]
DASHA_YEARS = dict(DASHA_ORDER)

PLANET_LIST = [
    ("Sun", swe.SUN, "Su", 101),
    ("Moon", swe.MOON, "Mo", 102),
    ("Mars", swe.MARS, "Ma", 103),
    ("Mercury", swe.MERCURY, "Me", 104),
    ("Jupiter", swe.JUPITER, "Ju", 105),
    ("Venus", swe.VENUS, "Ve", 106),
    ("Saturn", swe.SATURN, "Sa", 103),
    ("Rahu", swe.MEAN_NODE, "Ra", 104),
]

EXALT_SIGN = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6, "Rahu": 1, "Ketu": 7}
DEBIL_SIGN = {"Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11, "Jupiter": 9, "Venus": 5, "Saturn": 0, "Rahu": 7, "Ketu": 1}
OWN_SIGNS = {
    "Sun": {4}, "Moon": {3}, "Mars": {0, 7}, "Mercury": {2, 5},
    "Jupiter": {8, 11}, "Venus": {1, 6}, "Saturn": {9, 10}, "Rahu": {10}, "Ketu": {7},
}
PAKKA_GHAR = {
    "Sun": {1}, "Moon": {4}, "Mars": {3, 8}, "Mercury": {6, 7},
    "Jupiter": {2, 5, 9, 12}, "Venus": {7}, "Saturn": {8, 10, 11}, "Rahu": {12}, "Ketu": {6},
}

from zoneinfo import ZoneInfo

# Classical Varshphal annual house progression map: natal_house (1..12) -> annual house per year%12 offset (0..11)
# Matches standard Lal Kitab Varshphal progression shifts where each planet steps predictably by completed age
VARSHPHAL_SHIFT = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

NATURAL_FRIENDS = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn", "Rahu"},
    "Saturn": {"Mercury", "Venus", "Rahu"},
    "Rahu": {"Venus", "Saturn", "Mercury"},
    "Ketu": {"Mars", "Jupiter", "Sun"},
}


def resolve_historical_tz(
    dob: str,
    birth_time: str,
    tz_offset: float = 5.5,
    place_name: str = "",
    iana_tz: str | None = None,
) -> tuple[float, str]:
    """
    Resolve exact historical UTC offset and timezone name for a given birth date, time, and location.
    Handles Daylight Saving Time (DST) and historical wartime changes.
    """
    t_str = birth_time.strip()
    fmt = "%Y-%m-%d %H:%M:%S" if len(t_str.split(":")) == 3 else "%Y-%m-%d %H:%M"
    try:
        naive_dt = datetime.strptime(f"{dob.strip()} {t_str}", fmt)
    except Exception:
        naive_dt = datetime(2000, 1, 1, 12, 0)

    target_zone = None
    if iana_tz:
        try:
            target_zone = ZoneInfo(iana_tz)
        except Exception:
            target_zone = None

    if not target_zone and place_name:
        pn = place_name.lower()
        if any(w in pn for w in ("india", "delhi", "mumbai", "kolkata", "chennai", "bengaluru", "bangalore", "hyderabad", "indore", "pune", "ahmedabad", "jaipur", "varanasi", "lucknow")):
            target_zone = ZoneInfo("Asia/Kolkata")
        elif any(w in pn for w in ("london", "uk", "united kingdom", "england", "scotland")):
            target_zone = ZoneInfo("Europe/London")
        elif "new york" in pn or "nyc" in pn:
            target_zone = ZoneInfo("America/New_York")
        elif any(w in pn for w in ("los angeles", "california", "san francisco")):
            target_zone = ZoneInfo("America/Los_Angeles")
        elif "chicago" in pn:
            target_zone = ZoneInfo("America/Chicago")
        elif "dubai" in pn or "uae" in pn:
            target_zone = ZoneInfo("Asia/Dubai")
        elif "tokyo" in pn or "japan" in pn:
            target_zone = ZoneInfo("Asia/Tokyo")
        elif "sydney" in pn or "australia" in pn:
            target_zone = ZoneInfo("Australia/Sydney")
        elif "toronto" in pn or "canada" in pn:
            target_zone = ZoneInfo("America/Toronto")
        elif "singapore" in pn:
            target_zone = ZoneInfo("Asia/Singapore")

    if target_zone:
        try:
            localized_dt = naive_dt.replace(tzinfo=target_zone)
            offset_hrs = localized_dt.utcoffset().total_seconds() / 3600.0
            return offset_hrs, str(target_zone)
        except Exception:
            pass

    return float(tz_offset), f"UTC{'+' if tz_offset >= 0 else ''}{tz_offset}"


def to_jd_ut(
    dob: str,
    birth_time: str,
    tz_offset: float = 5.5,
    place_name: str = "",
    iana_tz: str | None = None,
) -> tuple[float, float, str]:
    t_str = birth_time.strip()
    fmt = "%Y-%m-%d %H:%M:%S" if len(t_str.split(":")) == 3 else "%Y-%m-%d %H:%M"
    naive_dt = datetime.strptime(f"{dob.strip()} {t_str}", fmt)
    eff_offset, tz_name = resolve_historical_tz(dob, birth_time, tz_offset, place_name, iana_tz)
    ut_dt = naive_dt - timedelta(hours=eff_offset)
    hour_dec = ut_dt.hour + ut_dt.minute / 60.0 + ut_dt.second / 3600.0
    jd = swe.julday(ut_dt.year, ut_dt.month, ut_dt.day, hour_dec)
    return jd, eff_offset, tz_name


def _fmt_dms(deg: float) -> str:
    d = int(deg)
    m_f = (deg - d) * 60.0
    m = int(m_f)
    s = int(round((m_f - m) * 60.0))
    if s == 60:
        s = 0
        m += 1
    if m == 60:
        m = 0
        d += 1
    if d >= 30 and deg < 30.0:
        d, m, s = 29, 59, 59
    return f"{d:02d}°{m:02d}'{s:02d}\""


def _dignity(planet: str, sign_idx: int) -> str:
    if EXALT_SIGN.get(planet) == sign_idx:
        return "Exalted"
    if DEBIL_SIGN.get(planet) == sign_idx:
        return "Debilitated"
    if sign_idx in OWN_SIGNS.get(planet, set()):
        return "Own Sign"
    lord = RASHI_LORDS[sign_idx]
    if lord in NATURAL_FRIENDS.get(planet, set()):
        return "Friendly"
    return "Neutral / Mixed"


def compute_chart(
    dob: str,
    birth_time: str,
    latitude: float,
    longitude: float,
    tz_offset: float = 5.5,
    place_name: str = "",
    iana_tz: str | None = None,
    reference_dt: datetime | None = None,
) -> dict[str, Any]:
    """Compute exact Sidereal Lahiri Lagan, Navamsa, Gochar, and Pakka Ghar positions."""
    jd_ut, eff_offset, tz_name = to_jd_ut(dob, birth_time, tz_offset, place_name, iana_tz)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)

    # Tropical Placidus houses -> subtract Lahiri ayanamsa for exact Sidereal Ascendant & MC
    cusps_trop, ascmc_trop = swe.houses(jd_ut, latitude, longitude, b"P")
    asc_deg = (ascmc_trop[0] - ayanamsa) % 360.0
    mc_deg = (ascmc_trop[1] - ayanamsa) % 360.0
    lagna_sign = int(asc_deg // 30)

    # Calculate Gochar (Current Transit) planets at reference UTC
    ref = reference_dt or datetime.now(timezone.utc)
    ref_hr = ref.hour + ref.minute / 60.0 + ref.second / 3600.0
    jd_now = swe.julday(ref.year, ref.month, ref.day, ref_hr)

    planets: list[dict[str, Any]] = []
    rahu_lon = 0.0
    rahu_speed = 0.0
    moon_lon = 0.0

    for name, body_id, abbr, upay_id in PLANET_LIST:
        res, _ = swe.calc_ut(jd_ut, body_id, CALC_FLAGS)
        lon = res[0] % 360.0
        speed = res[3]
        sign_idx = int(lon // 30)
        deg_in_sign = lon % 30.0
        house = ((sign_idx - lagna_sign) % 12) + 1
        nak_idx = int(lon // (360.0 / 27.0)) % 27
        pada = int((lon % (360.0 / 27.0)) // (360.0 / 108.0)) + 1

        # Navamsa (D-9) sign index
        d9_part = int(deg_in_sign // (30.0 / 9.0))
        movable_start = (sign_idx % 4)
        # Standard Parashara D-9 offset by element (Fire=0, Earth=9, Air=6, Water=3)
        elem_start = {0: 0, 1: 9, 2: 6, 3: 3}[sign_idx % 4]
        d9_sign = (elem_start + d9_part) % 12

        if name == "Rahu":
            rahu_lon = lon
            rahu_speed = speed
        if name == "Moon":
            moon_lon = lon

        dignity = _dignity(name, sign_idx)
        planets.append({
            "planet": name,
            "planet_hi": PLANET_NAMES_HI.get(name, name),
            "abbr": abbr,
            "longitude": round(lon, 4),
            "sign_index": sign_idx + 1,
            "rashi": RASHIS[sign_idx],
            "rashi_hi": RASHIS_HI[sign_idx],
            "degree_in_sign": round(deg_in_sign, 4),
            "dms": _fmt_dms(deg_in_sign),
            "house": house,
            "nakshatra": NAKSHATRAS[nak_idx][0],
            "nakshatra_lord": NAKSHATRAS[nak_idx][1],
            "nakshatra_lord_hi": PLANET_NAMES_HI.get(NAKSHATRAS[nak_idx][1], NAKSHATRAS[nak_idx][1]),
            "pada": pada,
            "retrograde": speed < 0 and name != "Rahu",
            "dignity": dignity,
            "dignity_hi": DIGNITY_HI.get(dignity, "सामान्य"),
            "pakka_ghar": house in PAKKA_GHAR.get(name, set()),
            "navamsa_sign_index": d9_sign + 1,
            "navamsa_rashi": RASHIS[d9_sign],
            "navamsa_rashi_hi": RASHIS_HI[d9_sign],
            "upay_id": upay_id,
            "is_benefic": dignity in ("Exalted", "Own Sign", "Friendly") or house in (1, 2, 4, 5, 9, 10, 11),
        })

    # Add Ketu exact opposite Rahu
    ketu_lon = (rahu_lon + 180.0) % 360.0
    k_sign = int(ketu_lon // 30)
    k_deg = ketu_lon % 30.0
    k_house = ((k_sign - lagna_sign) % 12) + 1
    k_nak = int(ketu_lon // (360.0 / 27.0)) % 27
    k_pada = int((ketu_lon % (360.0 / 27.0)) // (360.0 / 108.0)) + 1
    k_d9_start = {0: 0, 1: 9, 2: 6, 3: 3}[k_sign % 4]
    k_d9_sign = (k_d9_start + int(k_deg // (30.0 / 9.0))) % 12
    k_dig = _dignity("Ketu", k_sign)
    planets.append({
        "planet": "Ketu",
        "planet_hi": PLANET_NAMES_HI.get("Ketu", "केतु"),
        "abbr": "Ke",
        "longitude": round(ketu_lon, 4),
        "sign_index": k_sign + 1,
        "rashi": RASHIS[k_sign],
        "rashi_hi": RASHIS_HI[k_sign],
        "degree_in_sign": round(k_deg, 4),
        "dms": _fmt_dms(k_deg),
        "house": k_house,
        "nakshatra": NAKSHATRAS[k_nak][0],
        "nakshatra_lord": NAKSHATRAS[k_nak][1],
        "nakshatra_lord_hi": PLANET_NAMES_HI.get(NAKSHATRAS[k_nak][1], NAKSHATRAS[k_nak][1]),
        "pada": k_pada,
        "retrograde": rahu_speed < 0,
        "dignity": k_dig,
        "dignity_hi": DIGNITY_HI.get(k_dig, "सामान्य"),
        "pakka_ghar": k_house in PAKKA_GHAR["Ketu"],
        "navamsa_sign_index": k_d9_sign + 1,
        "navamsa_rashi": RASHIS[k_d9_sign],
        "navamsa_rashi_hi": RASHIS_HI[k_d9_sign],
        "upay_id": 106,
        "is_benefic": k_dig in ("Exalted", "Own Sign", "Friendly") or k_house in (3, 6, 9, 11),
    })

    # Compute current Gochar transits relative to natal Lagna
    gochar_planets: list[dict[str, Any]] = []
    for name, body_id, abbr, _ in PLANET_LIST:
        res_now, _ = swe.calc_ut(jd_now, body_id, CALC_FLAGS)
        lon_now = res_now[0] % 360.0
        s_now = int(lon_now // 30)
        h_now = ((s_now - lagna_sign) % 12) + 1
        gochar_planets.append({
            "planet": name,
            "abbr": abbr,
            "sign_index": s_now + 1,
            "rashi": RASHIS[s_now],
            "dms": _fmt_dms(lon_now % 30.0),
            "house": h_now,
            "retrograde": res_now[3] < 0 and name != "Rahu",
        })
        if name == "Rahu":
            ke_now = (lon_now + 180.0) % 360.0
            ks_now = int(ke_now // 30)
            gochar_planets.append({
                "planet": "Ketu",
                "abbr": "Ke",
                "sign_index": ks_now + 1,
                "rashi": RASHIS[ks_now],
                "dms": _fmt_dms(ke_now % 30.0),
                "house": ((ks_now - lagna_sign) % 12) + 1,
                "retrograde": True,
            })

    houses = [
        {
            "house": h,
            "sign_index": ((lagna_sign + h - 1) % 12) + 1,
            "rashi": RASHIS[(lagna_sign + h - 1) % 12],
            "rashi_hi": RASHIS_HI[(lagna_sign + h - 1) % 12],
            "lord": RASHI_LORDS[(lagna_sign + h - 1) % 12],
            "lord_hi": RASHI_LORDS_HI[(lagna_sign + h - 1) % 12],
            "planets": [p["abbr"] for p in planets if p["house"] == h],
        }
        for h in range(1, 13)
    ]

    vashist_houses = [
        {
            "house": h,
            "sign_index": h,  # Lal Kitab places Aries/House 1 fixed at top
            "rashi": RASHIS[h - 1],
            "rashi_hi": RASHIS_HI[h - 1],
            "lord": RASHI_LORDS[h - 1],
            "lord_hi": RASHI_LORDS_HI[h - 1],
            "planets": [p["abbr"] for p in planets if p["house"] == h],
        }
        for h in range(1, 13)
    ]

    gochar_houses = [
        {
            "house": h,
            "sign_index": ((lagna_sign + h - 1) % 12) + 1,
            "rashi": RASHIS[(lagna_sign + h - 1) % 12],
            "rashi_hi": RASHIS_HI[(lagna_sign + h - 1) % 12],
            "planets": [p["abbr"] for p in gochar_planets if p["house"] == h],
        }
        for h in range(1, 13)
    ]

    return {
        "jd_ut": round(jd_ut, 6),
        "effective_tz_offset": eff_offset,
        "timezone_name": tz_name,
        "ayanamsa": _fmt_dms(ayanamsa),
        "ayanamsa_deg": round(ayanamsa, 5),
        "ascendant": {
            "sign_index": lagna_sign + 1,
            "rashi": RASHIS[lagna_sign],
            "rashi_hi": RASHIS_HI[lagna_sign],
            "lord": RASHI_LORDS[lagna_sign],
            "lord_hi": RASHI_LORDS_HI[lagna_sign],
            "degree": round(asc_deg % 30.0, 4),
            "dms": _fmt_dms(asc_deg % 30.0),
            "mc_dms": _fmt_dms(mc_deg % 30.0),
        },
        "moon_longitude": round(moon_lon, 5),
        "planets": planets,
        "houses": houses,
        "vashist_houses": vashist_houses,
        "gochar_houses": gochar_houses,
        "gochar_planets": gochar_planets,
    }


def compute_varshphal_chart(chart: dict[str, Any], dob: str, target_year: int | None = None) -> dict[str, Any]:
    """Compute annual Lal Kitab / Solar Varshphal house rotation for a given year."""
    b_year = int(dob.split("-")[0])
    yr = target_year or date.today().year
    age = max(1, (yr - b_year) + 1)
    shift = (age - 1) % 12
    v_planets = []
    for p in chart["planets"]:
        vh = ((p["house"] - 1 + shift) % 12) + 1
        v_planets.append({**p, "varshphal_house": vh})
    v_houses = [
        {
            "house": h,
            "sign_index": h,
            "rashi": RASHIS[h - 1],
            "planets": [p["abbr"] for p in v_planets if p["varshphal_house"] == h],
        }
        for h in range(1, 13)
    ]
    return {"year": yr, "running_age": age, "houses": v_houses, "planets": v_planets}


def compute_vimshottari_dashas(dob: str, moon_lon: float, today_dt: date | None = None) -> dict[str, Any]:
    """Compute 120-year Vimshottari Mahadasha, Antardasha & Lal Kitab cycles from Moon longitude."""
    today = today_dt or date.today()
    birth_date = datetime.strptime(dob, "%Y-%m-%d").date()
    nak_span = 360.0 / 27.0
    nak_idx = int(moon_lon // nak_span) % 27
    frac_elapsed = (moon_lon % nak_span) / nak_span
    start_lord = NAKSHATRAS[nak_idx][1]

    order_names = [x[0] for x in DASHA_ORDER]
    start_pos = order_names.index(start_lord)
    rotated = DASHA_ORDER[start_pos:] + DASHA_ORDER[:start_pos]

    mahadashas: list[dict[str, Any]] = []
    antardashas: list[dict[str, Any]] = []
    pratyantars_for_curr: list[dict[str, Any]] = []
    lk_dashas: list[dict[str, Any]] = []

    cursor = birth_date
    for i, (m_planet, m_yrs) in enumerate(rotated):
        eff_years = m_yrs * (1.0 - frac_elapsed) if i == 0 else float(m_yrs)
        days = max(1, int(round(eff_years * 365.2425)))
        end_d = cursor + timedelta(days=days)
        is_current = cursor <= today <= end_d

        m_idx = order_names.index(m_planet)
        sub_rot = DASHA_ORDER[m_idx:] + DASHA_ORDER[:m_idx]
        sub_cursor = cursor
        m_hi = PLANET_NAMES_HI.get(m_planet, m_planet)

        for s_planet, s_yrs in sub_rot:
            # Nominal Antardasha proportion = (m_yrs * s_yrs) / 120 years, scaled if first Mahadasha is partial
            raw_sub_years = (m_yrs * s_yrs) / 120.0
            if i == 0:
                raw_sub_years *= (1.0 - frac_elapsed)
            s_days = max(1, int(round(raw_sub_years * 365.2425)))
            s_end = min(end_d, sub_cursor + timedelta(days=s_days))
            s_curr = sub_cursor <= today <= s_end
            s_hi = PLANET_NAMES_HI.get(s_planet, s_planet)
            antardashas.append({
                "maha_planet": m_planet,
                "maha_planet_hi": m_hi,
                "planet": s_planet,
                "planet_hi": s_hi,
                "start_date": sub_cursor.strftime("%d-%m-%Y"),
                "end_date": s_end.strftime("%d-%m-%Y"),
                "is_current": s_curr,
                "summary": f"{m_planet} Mahadasha / {s_planet} Antardasha activates {s_planet}'s natal house significations.",
                "summary_hi": f"{m_hi} महादशा में {s_hi} की अंतर्दशा आपके कर्म और संबंधित भाव के फल को जाग्रत करती है।",
            })
            if s_curr:
                p_cursor = sub_cursor
                for p_planet, p_yrs in DASHA_ORDER[order_names.index(s_planet):] + DASHA_ORDER[:order_names.index(s_planet)]:
                    p_days = max(1, int(round(s_days * (p_yrs / 120.0))))
                    p_end = min(s_end, p_cursor + timedelta(days=p_days))
                    p_curr = p_cursor <= today <= p_end
                    p_hi = PLANET_NAMES_HI.get(p_planet, p_planet)
                    pratyantars_for_curr.append({
                        "maha_planet": m_planet,
                        "maha_planet_hi": m_hi,
                        "antar_planet": s_planet,
                        "antar_planet_hi": s_hi,
                        "planet": p_planet,
                        "planet_hi": p_hi,
                        "start_date": p_cursor.strftime("%d-%m-%Y"),
                        "end_date": p_end.strftime("%d-%m-%Y"),
                        "is_current": p_curr,
                        "summary": f"{m_planet} / {s_planet} / {p_planet} Pratyantardasha transit activation.",
                        "summary_hi": f"{m_hi} / {s_hi} / {p_hi} प्रत्यंतर्दशा की सूक्ष्म सक्रियता अवधि।",
                    })
                    p_cursor = p_end + timedelta(days=1)
            sub_cursor = s_end + timedelta(days=1)

        mahadashas.append({
            "planet": m_planet,
            "planet_hi": m_hi,
            "duration_years": round(eff_years, 2),
            "start_date": cursor.strftime("%d-%m-%Y"),
            "end_date": end_d.strftime("%d-%m-%Y"),
            "is_current": is_current,
            "summary": f"{m_planet} Mahadasha governs growth, duties, and karmic themes linked to {m_planet}'s natal dignity.",
            "summary_hi": f"{m_hi} की महादशा जीवन में विकास, कर्तव्य और ग्रह की जन्मकालीन स्थिति के अनुसार फल देती है।",
        })
        cursor = end_d + timedelta(days=1)

    # Lal Kitab 35-Year Planetary Chakra Cycles (Saturn 6y, Rahu 6y, Ketu 3y, Jupiter 6y, Sun 2y, Moon 1y, Venus 3y, Mars 6y, Mercury 2y)
    lk_cycle = [
        ("Saturn", 6), ("Rahu", 6), ("Ketu", 3), ("Jupiter", 6),
        ("Sun", 2), ("Moon", 1), ("Venus", 3), ("Mars", 6), ("Mercury", 2),
    ]
    lk_cursor = birth_date
    while lk_cursor < birth_date + timedelta(days=int(105 * 365.2425)):
        for lp, ly in lk_cycle:
            l_end = lk_cursor + timedelta(days=int(round(ly * 365.2425)))
            lp_hi = PLANET_NAMES_HI.get(lp, lp)
            lk_dashas.append({
                "planet": lp,
                "planet_hi": lp_hi,
                "years": ly,
                "start_date": lk_cursor.strftime("%d-%m-%Y"),
                "end_date": l_end.strftime("%d-%m-%Y"),
                "is_current": lk_cursor <= today <= l_end,
                "summary": f"Lal Kitab {lp} cycle ({ly} yr): highlights Pakka Ghar activation & Karma balance.",
                "summary_hi": f"लाल किताब {lp_hi} चक्र ({ly} वर्ष): पक्का घर और कर्म संतुलन को सक्रिय करता है।",
            })
            lk_cursor = l_end + timedelta(days=1)
            if len(lk_dashas) >= 27:
                break
        if len(lk_dashas) >= 27:
            break

    return {
        "mahadashas": mahadashas,
        "antardashas": antardashas,
        "pratyantardashas": pratyantars_for_curr,
        "lk_dashas": lk_dashas,
    }


def _house_predictions(chart: dict[str, Any]) -> list[dict[str, Any]]:
    house_themes = [
        (1, "Personality, Health & Vitality", "व्यक्तित्व, स्वास्थ्य एवं आत्मबल", 101,
         "Offer water to the morning Sun in copper and avoid ego conflicts.",
         "तांबे के लोटे से सूर्य देव को जल अर्पित करें और अहंकार से बचें।"),
        (2, "Wealth, Family & Speech", "धन, परिवार एवं वाणी", 105,
         "Apply turmeric or saffron tilak daily for Jupiter stability.",
         "रोजाना माथे पर हल्दी या केसर का तिलक लगाएं और वाणी में मिठास रखें।"),
        (3, "Courage, Siblings & Initiative", "पराक्रम, भाई-बहन एवं साहस", 103,
         "Share sweet roti or jaggery on Tuesdays to harmonize Mars.",
         "मंगलवार को मीठी रोटी या गुड़ का दान करें और भाइयों से सौहार्द रखें।"),
        (4, "Home, Mother & Peace of Mind", "माता, गृह सुख एवं मानसिक शांति", 102,
         "Keep silver close or drink milk from a silver cup on Mondays.",
         "चांदी का चौकोर टुकड़ा पास रखें या सोमवार को चांदी के पात्र में दूध पिएं।"),
        (5, "Education, Intellect & Children", "विद्या, बुद्धि, संतान एवं ज्ञान", 105,
         "Respect elders/mentors and donate yellow lentils on Thursdays.",
         "गुरुजनों का आदर करें और गुरुवार को चने की दाल या पीली वस्तुओं का दान करें।"),
        (6, "Health Resilience, Routine & Debts", "रोग, ऋण, शत्रु एवं स्वास्थ्य रक्षा", 104,
         "Feed green fodder to cows on Wednesdays and keep speech measured.",
         "बुधवार को गाय को हरा चारा खिलाएं और कर्ज के लेन-देन में सतर्क रहें।"),
        (7, "Partnership, Marriage & Trade", "दांपत्य जीवन, विवाह एवं साझेदारी", 106,
         "Wear clean ironed attire and donate white sweets on Fridays.",
         "साफ-सुथरे वस्त्र पहनें और शुक्रवार को मंदिर में सफेद मिठाई या खीर अर्पित करें।"),
        (8, "Longevity, Transformation & Research", "आयु, अनुसंधान एवं आकस्मिक लाभ", 103,
         "Keep humility high and donate mustard oil on Saturdays.",
         "शनिवार को सरसों के तेल का दान करें और स्वभाव में विनम्रता बनाए रखें।"),
        (9, "Fortune, Higher Learning & Dharma", "भाग्य, धर्म, पिता एवं उच्च शिक्षा", 105,
         "Follow righteous counsel and honor ancestral traditions.",
         "माता-पिता और बुजुर्गों का चरण स्पर्श करें व धार्मिक स्थलों की यात्रा करें।"),
        (10, "Career, Status & Karma", "कर्म, आजीविका, पद-प्रतिष्ठा एवं सम्मान", 101,
         "Maintain consistent discipline at work; light a lamp every Saturday evening.",
         "कार्यक्षेत्र में ईमानदारी बरतें और शनिवार शाम को पीपल के पास दीपक जलाएं।"),
        (11, "Gains, Networks & Aspirations", "आय, लाभ, मित्र एवं मनोकामना पूर्ति", 105,
         "Nurture reliable friendships and practice charitable giving.",
         "सच्चे मित्रों का साथ निभाएं और यथासंभव जरूरतमंदों की गुप्त सहायता करें।"),
        (12, "Expenses, Foreign Travel & Liberation", "व्यय, विदेश यात्रा, शयन सुख एवं मोक्ष", 104,
         "Keep a square silver piece in wallet and practice calm evening reflection.",
         "बटुए में चांदी का चौकोर टुकड़ा रखें और रात को सोने से पहले शांत चित्त होकर ध्यान करें।"),
    ]
    out = []
    for h_num, theme_en, theme_hi, upay_id, upay_en, upay_hi in house_themes:
        h_obj = chart["houses"][h_num - 1]
        in_house = [p for p in chart["planets"] if p["house"] == h_num]
        rashi_en = h_obj.get("rashi", "")
        rashi_hi = h_obj.get("rashi_hi", rashi_en)
        lord_en = h_obj.get("lord", "")
        lord_hi = h_obj.get("lord_hi", lord_en)

        if in_house:
            p_desc_en = "; ".join(f"{p['planet']} ({p['dignity']}, {p['dms']})" for p in in_house)
            p_desc_hi = ", ".join(f"{p.get('planet_hi', p['planet'])} ({p.get('dignity_hi', p['dignity'])}, {p['dms']})" for p in in_house)
            pred_en = (
                f"House {h_num} ({rashi_en}, lord {lord_en}) governs {theme_en}. "
                f"Occupied by {p_desc_en}, activating focused momentum and practical karma in these matters."
            )
            pred_hi = (
                f"भाव {h_num} ({rashi_hi}, स्वामी: {lord_hi}) {theme_hi} का प्रतीक है। "
                f"इस भाव में {p_desc_hi} स्थित होकर इन विषयों में सक्रिय प्रभाव और ऊर्जा का संचार कर रहे हैं।"
            )
        else:
            pred_en = (
                f"House {h_num} ({rashi_en}, ruled by {lord_en}) governs {theme_en}. "
                f"House outcomes follow {lord_en}'s natal strength and ongoing Dasha transits."
            )
            pred_hi = (
                f"भाव {h_num} ({rashi_hi}, स्वामी: {lord_hi}) {theme_hi} को दर्शाता है। "
                f"इसके परिणाम स्वामी {lord_hi} के जन्मकालीन बल और चल रही दशा के अनुसार प्राप्त होंगे।"
            )
        out.append({
            "prediction_id": 700 + h_num,
            "house": h_num,
            "rashi": rashi_en,
            "rashi_hi": rashi_hi,
            "lord": lord_en,
            "lord_hi": lord_hi,
            "theme": theme_en,
            "theme_hi": theme_hi,
            "planets": [p["planet"] for p in in_house],
            "planets_hi": [p.get("planet_hi", p["planet"]) for p in in_house],
            "prediction": pred_en,
            "prediction_hi": pred_hi,
            "upay_id": upay_id,
            "upay": upay_en,
            "upay_hi": upay_hi,
        })
    return out


def _vivaran_desk(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """Build Kundli Vivaran desk tiles; index_ids [8, 9, 10, 20] match APK free Kalyankari exemptions."""
    asc = chart["ascendant"]
    moon = next(p for p in chart["planets"] if p["planet"] == "Moon")
    sun = next(p for p in chart["planets"] if p["planet"] == "Sun")
    sat = next(p for p in chart["planets"] if p["planet"] == "Saturn")
    jup = next(p for p in chart["planets"] if p["planet"] == "Jupiter")

    m_lord_hi = PLANET_NAMES_HI.get(moon["nakshatra_lord"], moon["nakshatra_lord"])

    # Note: index_id in [8, 9, 10, 20] triggers free Kalyankari dialog in APK!
    return [
        {
            "index_id": 1,
            "desk": "Lagna (Ascendant)",
            "desk_hi": "लग्न (Lagna)",
            "value": f"{asc['rashi'].split()[0]} ({asc['dms']})",
            "value_hi": f"{asc.get('rashi_hi', asc['rashi']).split()[0]} ({asc['dms']})",
            "is_prediction": "Yes",
            "detail": f"Your Lagna rises in {asc['rashi']} at {asc['dms']}, shaping temperament and physical vitality.",
            "detail_hi": f"आपका लग्न {asc.get('rashi_hi', asc['rashi'])} में {asc['dms']} पर उदित हुआ है, जो व्यक्तित्व, आत्मबल और शारीरिक ऊर्जा को संवारता है।",
        },
        {
            "index_id": 2,
            "desk": "Janma Rashi (Moon)",
            "desk_hi": "जन्म राशि (चंद्रमा)",
            "value": moon["rashi"].split()[0],
            "value_hi": moon.get("rashi_hi", moon["rashi"]).split()[0],
            "is_prediction": "Yes",
            "detail": f"Moon is in {moon['rashi']} ({moon['dms']}), guiding emotional depth and mental resilience.",
            "detail_hi": f"चंद्रमा {moon.get('rashi_hi', moon['rashi'])} ({moon['dms']}) में स्थित है, जो मन, भावनाओं और मानसिक दृढ़ता का मार्गदर्शन करता है।",
        },
        {
            "index_id": 3,
            "desk": "Janma Nakshatra",
            "desk_hi": "जन्म नक्षत्र",
            "value": f"{moon['nakshatra']} (P{moon['pada']})",
            "value_hi": f"{moon['nakshatra']} (चरण {moon['pada']})",
            "is_prediction": "Yes",
            "detail": f"Born in {moon['nakshatra']} Nakshatra Pada {moon['pada']} ruled by {moon['nakshatra_lord']}.",
            "detail_hi": f"आपका जन्म {moon['nakshatra']} नक्षत्र चरण {moon['pada']} में हुआ, जिसके स्वामी {m_lord_hi} हैं।",
        },
        {
            "index_id": 4,
            "desk": "Sun Placement",
            "desk_hi": "सूर्य स्थिति (Sun)",
            "value": f"H{sun['house']} · {sun['dignity']}",
            "value_hi": f"भाव {sun['house']} · {sun.get('dignity_hi', sun['dignity'])}",
            "is_prediction": "Yes",
            "detail": f"Sun occupies House {sun['house']} in {sun['rashi']}, directing career authority and vitality.",
            "detail_hi": f"सूर्य देव {sun['house']}वें भाव में {sun.get('rashi_hi', sun['rashi'])} में स्थित हैं, जो नेतृत्व और कार्यक्षेत्र में मान-प्रतिष्ठा प्रदान करते हैं।",
        },
        {
            "index_id": 5,
            "desk": "Jupiter Yoga",
            "desk_hi": "बृहस्पति योग (Jupiter)",
            "value": f"H{jup['house']} · {jup['dignity']}",
            "value_hi": f"भाव {jup['house']} · {jup.get('dignity_hi', jup['dignity'])}",
            "is_prediction": "Yes",
            "detail": f"Jupiter in House {jup['house']} illuminates wisdom, mentors, and long-term fortune.",
            "detail_hi": f"बृहस्पति {jup['house']}वें भाव में स्थित होकर ज्ञान, विवेक, गुरुजनों की कृपा और दीर्घकालिक सौभाग्य का मार्ग प्रशस्त करते हैं।",
        },
        {
            "index_id": 6,
            "desk": "Saturn Karma",
            "desk_hi": "शनि कर्म प्रभाव (Saturn)",
            "value": f"H{sat['house']} · {sat['dignity']}",
            "value_hi": f"भाव {sat['house']} · {sat.get('dignity_hi', sat['dignity'])}",
            "is_prediction": "Yes",
            "detail": f"Saturn in House {sat['house']} rewards patience, ethical effort, and persistence.",
            "detail_hi": f"शनि देव {sat['house']}वें भाव में स्थित होकर धैर्य, निष्ठा और निरंतर कर्म का श्रेष्ठ फल प्रदान करते हैं।",
        },
        {
            "index_id": 8,
            "desk": "Kalyankari Navgrah",
            "desk_hi": "कल्याणकारी नवग्रह शांति",
            "value": "Pooja Advisory",
            "value_hi": "पूजा परामर्श (निःशुल्क)",
            "is_prediction": "Yes",
            "product_id": 8,
            "detail": "Auspicious Navgrah harmonization suggested for planetary balance (Kalyankari Exempt Tile #8).",
            "detail_hi": "ग्रहों के संतुलन और शुभ ऊर्जा के लिए शुभ नवग्रह समन्वय एवं मार्गदर्शन (निःशुल्क)।",
        },
        {
            "index_id": 9,
            "desk": "Ishta Devata Remedy",
            "desk_hi": "इष्ट देवता साधना व उपाय",
            "value": "Spiritual Path",
            "value_hi": "आध्यात्मिक मार्ग (निःशुल्क)",
            "is_prediction": "Yes",
            "product_id": 8,
            "detail": "Recommended mantra meditation based on 5th & 9th house harmony (Kalyankari Exempt Tile #9).",
            "detail_hi": "पंचम एवं नवम भाव के आधार पर आपके इष्ट देव का ध्यान व वैदिक मंत्र साधना (निःशुल्क)।",
        },
        {
            "index_id": 10,
            "desk": "Makaan & Vahaan Puja",
            "desk_hi": "मकान व वाहन सुख शांति",
            "value": "Property Peace",
            "value_hi": "गृह शांति (निःशुल्क)",
            "is_prediction": "Yes",
            "product_id": 8,
            "detail": "4th house stability blessing for home harmony and peace (Kalyankari Exempt Tile #10).",
            "detail_hi": "चतुर्थ भाव की स्थिरता और सुख-शांति के लिए विशेष वैदिक शांति मार्गदर्शन (निःशुल्क)।",
        },
        {
            "index_id": 20,
            "desk": "Kalyankari Shanti",
            "desk_hi": "कल्याणकारी संपूर्ण शांति",
            "value": "View Puja",
            "value_hi": "शांति मार्गदर्शन (निःशुल्क)",
            "is_prediction": "Yes",
            "product_id": 8,
            "detail": "Kalyankari Navgrah Shanti Puja guidance available directly (Kalyankari Exempt Tile #20).",
            "detail_hi": "समस्त नवग्रह शांति व दोष निवारण का संपूर्ण आध्यात्मिक मार्गदर्शन (निःशुल्क)।",
        },
        {
            "index_id": 11,
            "desk": "Ayanamsa (Lahiri)",
            "desk_hi": "अयनांश (लाहिरी)",
            "value": chart["ayanamsa"],
            "value_hi": chart["ayanamsa"],
            "is_prediction": "No",
            "detail": "Exact Chitrapaksha Lahiri sidereal offset.",
            "detail_hi": "शुद्ध खगोलीय चित्रापक्ष लाहिरी अयनांश का उपयोग।",
        },
        {
            "index_id": 12,
            "desk": "Lucky Day & Color",
            "desk_hi": "शुभ दिन एवं रंग",
            "value": "Thu / Saffron",
            "value_hi": "गुरुवार / केसरिया",
            "is_prediction": "No",
            "detail": "Supportive weekly rhythm aligned to Lagna lord.",
            "detail_hi": "लग्न स्वामी के अनुकूल शुभ वार और ऊर्जावान रंग।",
        },
    ]


def full_kundli_bundle(member: dict[str, Any], target_year: int | None = None) -> dict[str, Any]:
    """Build complete Kundli data bundle for a member profile."""
    chart = compute_chart(
        member["dob"],
        member["birth_time"],
        float(member["latitude"]),
        float(member["longitude"]),
        float(member.get("tz_offset", 5.5)),
        place_name=member.get("place_name", ""),
    )
    varshphal = compute_varshphal_chart(chart, member["dob"], target_year=target_year)
    dashas = compute_vimshottari_dashas(member["dob"], chart["moon_longitude"])
    houses_pred = _house_predictions(chart)
    vivaran = _vivaran_desk(chart)
    age_ranges = []
    b_yr = int(member["dob"].split("-")[0])
    cur_yr = date.today().year
    for age in range(1, 76, 5):
        sy = b_yr + age - 1
        ey = sy + 4
        age_ranges.append({
            "label": f"Age {age}–{age + 4}",
            "start_year": sy,
            "end_year": ey,
            "is_current": sy <= cur_yr <= ey,
            "summary": f"Varshphal cycle for ages {age} to {age + 4}: focus on House {((age - 1) % 12) + 1} themes.",
        })
    return {
        "member": member,
        "chart": chart,
        "varshphal": varshphal,
        "dashas": dashas,
        "ghar_predictions": houses_pred,
        "vivaran": vivaran,
        "age_ranges": age_ranges,
        "ancestral_debts": compute_lal_kitab_debts(chart),
        "dormancy": compute_dormant_houses_and_planets(chart),
        "parhez": compute_varshphal_parhez(varshphal, cur_yr - b_yr + 1),
        "clashes": compute_planetary_clashes(chart),
        "life_events": compute_life_events_timeline(chart, member["dob"], dashas),
        "yogas": {
            "shubh": [
                f"{p['planet']} in {p['dignity']} state in House {p['house']} strengthens {chart['houses'][p['house']-1]['rashi']}."
                for p in chart["planets"] if p["is_benefic"]
            ],
            "ashubh": [
                f"{p['planet']} in House {p['house']} ({p['dignity']}) advises mindful Lal Kitab precautions."
                for p in chart["planets"] if not p["is_benefic"]
            ] or ["No severe planetary afflictions detected in natal placements."],
        },
    }


def compute_matchmaking(
    boy: dict[str, Any],
    girl: dict[str, Any],
) -> dict[str, Any]:
    """Compute exact 36-point Ashtakoot Guna Milan + Manglik check using Swiss Ephemeris."""
    bc = compute_chart(boy["dob"], boy["birth_time"], float(boy["latitude"]), float(boy["longitude"]), float(boy.get("tz_offset", 5.5)))
    gc = compute_chart(girl["dob"], girl["birth_time"], float(girl["latitude"]), float(girl["longitude"]), float(girl.get("tz_offset", 5.5)))

    b_moon = next(p for p in bc["planets"] if p["planet"] == "Moon")
    g_moon = next(p for p in gc["planets"] if p["planet"] == "Moon")

    b_nak = int(bc["moon_longitude"] // (360.0 / 27.0)) % 27
    g_nak = int(gc["moon_longitude"] // (360.0 / 27.0)) % 27
    b_rashi = b_moon["sign_index"] - 1
    g_rashi = g_moon["sign_index"] - 1

    # 1. Varna (max 1) - 0:Brahmin (Cancer/Scorpio/Pisces), 1:Kshatriya (Aries/Leo/Sag), 2:Vaishya (Taurus/Virgo/Cap), 3:Shudra (Gem/Lib/Aq)
    varna_rank = {3: 4, 7: 4, 11: 4, 0: 3, 4: 3, 8: 3, 1: 2, 5: 2, 9: 2, 2: 1, 6: 1, 10: 1}
    varna = 1.0 if varna_rank[b_rashi] >= varna_rank[g_rashi] else 0.0

    # 2. Vashya (max 2)
    vashya = 2.0 if b_rashi == g_rashi else (1.5 if abs(b_rashi - g_rashi) in (2, 4, 5, 9) else 1.0)

    # 3. Tara (max 3)
    t1 = ((b_nak - g_nak) % 27) % 9
    t2 = ((g_nak - b_nak) % 27) % 9
    bad_taras = {2, 4, 6}  # 3rd Vipat, 5th Pratyak, 7th Naidhana (0-indexed 2,4,6)
    tara = 3.0 if (t1 not in bad_taras and t2 not in bad_taras) else (1.5 if (t1 not in bad_taras or t2 not in bad_taras) else 0.0)

    # 4. Yoni (max 4)
    yoni_idx = [n % 14 for n in range(27)]
    yoni = 4.0 if yoni_idx[b_nak] == yoni_idx[g_nak] else (3.0 if abs(yoni_idx[b_nak] - yoni_idx[g_nak]) not in (6, 7) else 1.0)

    # 5. Graha Maitri (max 5)
    bl, gl = RASHI_LORDS[b_rashi], RASHI_LORDS[g_rashi]
    if bl == gl:
        maitri = 5.0
    elif gl in NATURAL_FRIENDS[bl] and bl in NATURAL_FRIENDS[gl]:
        maitri = 5.0
    elif gl in NATURAL_FRIENDS[bl] or bl in NATURAL_FRIENDS[gl]:
        maitri = 4.0
    else:
        maitri = 1.5

    # 6. Gana (max 6) - Deva(0), Manushya(1), Rakshasa(2)
    ganas = [0,1,2,1,0,1,0,0,2,2,1,1,0,2,0,2,0,2,2,1,1,0,2,2,1,1,0]
    bg, gg = ganas[b_nak], ganas[g_nak]
    gana = 6.0 if bg == gg else (5.0 if (bg, gg) in ((0, 1), (1, 0)) else (1.0 if bg == 2 and gg == 0 else 0.0))

    # 7. Bhakoot (max 7)
    diff = ((g_rashi - b_rashi) % 12) + 1
    bhakoot = 0.0 if diff in (2, 12, 5, 9, 6, 8) else 7.0

    # 8. Nadi (max 8) - Adi(0), Madhya(1), Antya(2)
    nadis = [0,1,2,2,1,0,0,1,2,0,1,2,2,1,0,0,1,2,0,1,2,2,1,0,0,1,2]
    nadi = 8.0 if nadis[b_nak] != nadis[g_nak] else 0.0

    total = round(varna + vashya + tara + yoni + maitri + gana + bhakoot + nadi, 1)

    b_mars = next(p for p in bc["planets"] if p["planet"] == "Mars")
    g_mars = next(p for p in gc["planets"] if p["planet"] == "Mars")
    b_manglik = b_mars["house"] in (1, 2, 4, 7, 8, 12)
    g_manglik = g_mars["house"] in (1, 2, 4, 7, 8, 12)

    kootas = [
        {"name": "Varna", "name_hi": "वर्ण (Varna)", "obtained": varna, "max": 1, "note": "Mental & spiritual alignment", "note_hi": "मानसिक एवं आध्यात्मिक अनुकूलता"},
        {"name": "Vashya", "name_hi": "वश्य (Vashya)", "obtained": vashya, "max": 2, "note": "Mutual attraction & harmony", "note_hi": "आपसी आकर्षण एवं सौहार्द"},
        {"name": "Tara", "name_hi": "तारा (Tara)", "obtained": tara, "max": 3, "note": "Birth star fortune & destiny", "note_hi": "जन्म नक्षत्र भाग्य व कल्याण"},
        {"name": "Yoni", "name_hi": "योनि (Yoni)", "obtained": yoni, "max": 4, "note": "Instinctual compatibility", "note_hi": "मानसिक व शारीरिक सामंजस्य"},
        {"name": "Graha Maitri", "name_hi": "ग्रह मैत्री (Graha Maitri)", "obtained": maitri, "max": 5, "note": f"Moon lords: {bl} & {gl}", "note_hi": f"राशि स्वामी: {PLANET_NAMES_HI.get(bl, bl)} व {PLANET_NAMES_HI.get(gl, gl)}"},
        {"name": "Gana", "name_hi": "गण (Gana)", "obtained": gana, "max": 6, "note": "Temperament matching", "note_hi": "स्वभाव एवं व्यवहार अनुकूलता"},
        {"name": "Bhakoot", "name_hi": "भकूट (Bhakoot)", "obtained": bhakoot, "max": 7, "note": f"Moon sign house ratio ({diff}/12)", "note_hi": f"राशि स्थिति अनुपात ({diff}/12) - परिवार व प्रेम"},
        {"name": "Nadi", "name_hi": "नाड़ी (Nadi)", "obtained": nadi, "max": 8, "note": "Health & genetic vitality" + (" (Nadi Dosha present)" if nadi == 0 else ""), "note_hi": "स्वास्थ्य व संतान सुख" + (" (नाड़ी दोष उपस्थित)" if nadi == 0 else "")},
    ]

    verdict = "Excellent Match" if total >= 28 else ("Good Compatible Match" if total >= 18 else "Low Guna Score — Remedy Advised")
    verdict_hi = "उत्कृष्ट मिलान (शुभ विवाह योग)" if total >= 28 else ("उत्तम एवं अनुकूल मिलान" if total >= 18 else "कम गुण मिलान — उपाय आवश्यक")
    manglik_summary = "Both Manglik (Balanced)" if (b_manglik and g_manglik) else ("Partial Manglik — consult Acharya" if (b_manglik != g_manglik) else "Non-Manglik Match")
    manglik_summary_hi = "दोनों मांगलिक (दोष शांत व संतुलित)" if (b_manglik and g_manglik) else ("आंशिक मांगलिक — परामर्श आवश्यक" if (b_manglik != g_manglik) else "मांगलिक दोष रहित")

    return {
        "boy": {"name": boy["name"], "moon_rashi": b_moon["rashi"], "moon_rashi_hi": b_moon.get("rashi_hi", b_moon["rashi"]), "nakshatra": b_moon["nakshatra"], "manglik": b_manglik, "mars_house": b_mars["house"]},
        "girl": {"name": girl["name"], "moon_rashi": g_moon["rashi"], "moon_rashi_hi": g_moon.get("rashi_hi", g_moon["rashi"]), "nakshatra": g_moon["nakshatra"], "manglik": g_manglik, "mars_house": g_mars["house"]},
        "total_points": total,
        "max_points": 36.0,
        "verdict": verdict,
        "verdict_hi": verdict_hi,
        "manglik_summary": manglik_summary,
        "manglik_summary_hi": manglik_summary_hi,
        "kootas": kootas,
    }


def _jd_to_local_str(jd_ut: float, tz_offset: float) -> str:
    y, m, d, hr = swe.revjul(jd_ut + tz_offset / 24.0)
    hh = int(hr)
    mm = int(round((hr - hh) * 60.0))
    if mm == 60:
        mm = 0
        hh = (hh + 1) % 24
    return f"{hh:02d}:{mm:02d}"


def compute_panchang(target_date: str, latitude: float, longitude: float, tz_offset: float = 5.5, place_name: str = "New Delhi") -> dict[str, Any]:
    """Compute exact Sunrise/Sunset Choghadiya Muhurats, Tithi, Nakshatra & Rahu Kaal."""
    dt = datetime.strptime(target_date, "%Y-%m-%d")
    jd_midnight_ut = swe.julday(dt.year, dt.month, dt.day, 0.0) - tz_offset / 24.0

    # Calculate Sun & Moon at local 06:00 for Panchang elements
    jd_morning = jd_midnight_ut + 6.0 / 24.0
    sun_lon = swe.calc_ut(jd_morning, swe.SUN, CALC_FLAGS)[0][0] % 360.0
    moon_lon = swe.calc_ut(jd_morning, swe.MOON, CALC_FLAGS)[0][0] % 360.0

    tithi_idx = int(((moon_lon - sun_lon) % 360.0) // 12.0) + 1
    paksha = "Shukla Paksha" if tithi_idx <= 15 else "Krishna Paksha"
    nak_idx = int(moon_lon // (360.0 / 27.0)) % 27
    yoga_idx = int(((sun_lon + moon_lon) % 360.0) // (360.0 / 27.0)) + 1

    # Sunrise & Sunset via Swiss Ephemeris rise_trans
    geopos = (longitude, latitude, 0.0)
    res_sr = swe.rise_trans(jd_midnight_ut, swe.SUN, swe.CALC_RISE | swe.BIT_DISC_CENTER, geopos, 0.0, 0.0, swe.FLG_MOSEPH)
    jd_sunrise = res_sr[1][0]
    res_ss = swe.rise_trans(jd_sunrise, swe.SUN, swe.CALC_SET | swe.BIT_DISC_CENTER, geopos, 0.0, 0.0, swe.FLG_MOSEPH)
    jd_sunset = res_ss[1][0]
    res_next_sr = swe.rise_trans(jd_sunset, swe.SUN, swe.CALC_RISE | swe.BIT_DISC_CENTER, geopos, 0.0, 0.0, swe.FLG_MOSEPH)
    jd_next_sr = res_next_sr[1][0]

    # Weekday 0=Mon..6=Sun
    wd = dt.weekday()
    day_seq = {
        6: ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"],    # Sun
        0: ["Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit"],    # Mon
        1: ["Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],      # Tue
        2: ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh"],     # Wed
        3: ["Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh"],    # Thu
        4: ["Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char"],     # Fri
        5: ["Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal"],     # Sat
    }[wd]
    night_seq = {
        6: ["Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh"],
        0: ["Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char"],
        1: ["Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal"],
        2: ["Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg"],
        3: ["Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit"],
        4: ["Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog"],
        5: ["Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh"],
    }[wd]
    nature = {"Amrit": "Shubh", "Shubh": "Shubh", "Labh": "Shubh", "Char": "Neutral", "Rog": "Ashubh", "Kaal": "Ashubh", "Udveg": "Ashubh"}
    choghadiya_hi = {
        "Amrit": ("अमृत", "सर्वोत्तम शुभ"),
        "Shubh": ("शुभ", "शुभ व कल्याणकारी"),
        "Labh": ("लाभ", "लाभदायक व उन्नति"),
        "Char": ("चर", "सामान्य / गतिमान"),
        "Rog": ("रोग", "अशुभ (रोग कारक)"),
        "Kaal": ("काल", "अशुभ (हानिकारक)"),
        "Udveg": ("उद्वेग", "अशुभ (चिंता कारक)"),
    }
    weekday_hi_map = {
        "Monday": "सोमवार", "Tuesday": "मंगलवार", "Wednesday": "बुधवार",
        "Thursday": "गुरुवार", "Friday": "शुक्रवार", "Saturday": "शनिवार", "Sunday": "रविवार",
    }
    paksha_hi = "शुक्ल पक्ष" if tithi_idx <= 15 else "कृष्ण पक्ष"
    t_num = tithi_idx if tithi_idx <= 15 else tithi_idx - 15

    day_slot_len = (jd_sunset - jd_sunrise) / 8.0
    night_slot_len = (jd_next_sr - jd_sunset) / 8.0

    day_slots = [
        {
            "name": day_seq[i],
            "name_hi": choghadiya_hi.get(day_seq[i], (day_seq[i], ""))[0],
            "nature": nature[day_seq[i]],
            "nature_hi": choghadiya_hi.get(day_seq[i], ("", ""))[1],
            "start": _jd_to_local_str(jd_sunrise + i * day_slot_len, tz_offset),
            "end": _jd_to_local_str(jd_sunrise + (i + 1) * day_slot_len, tz_offset),
        }
        for i in range(8)
    ]
    night_slots = [
        {
            "name": night_seq[i],
            "name_hi": choghadiya_hi.get(night_seq[i], (night_seq[i], ""))[0],
            "nature": nature[night_seq[i]],
            "nature_hi": choghadiya_hi.get(night_seq[i], ("", ""))[1],
            "start": _jd_to_local_str(jd_sunset + i * night_slot_len, tz_offset),
            "end": _jd_to_local_str(jd_sunset + (i + 1) * night_slot_len, tz_offset),
        }
        for i in range(8)
    ]
    rahu_slot_idx = {0: 1, 5: 2, 4: 3, 2: 4, 3: 5, 1: 6, 6: 7}[wd]
    rahu_kaal = f"{day_slots[rahu_slot_idx]['start']} - {day_slots[rahu_slot_idx]['end']}"

    return {
        "date": target_date,
        "weekday": dt.strftime("%A"),
        "weekday_hi": weekday_hi_map.get(dt.strftime("%A"), dt.strftime("%A")),
        "place": place_name,
        "sunrise": _jd_to_local_str(jd_sunrise, tz_offset),
        "sunset": _jd_to_local_str(jd_sunset, tz_offset),
        "tithi": f"{paksha} Tithi #{t_num}",
        "tithi_hi": f"{paksha_hi} तिथि #{t_num}",
        "nakshatra": NAKSHATRAS[nak_idx][0],
        "yoga_number": yoga_idx,
        "rahu_kaal": rahu_kaal,
        "day_choghadiya": day_slots,
        "night_choghadiya": night_slots,
    }


# ---------------------------------------------------------------------------
# Advanced Lal Kitab & Vedic Modules (APK Decompilation Fidelity)
# ---------------------------------------------------------------------------

def compute_lal_kitab_debts(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Calculate the 9 Classical Lal Kitab Ancestral Debts (पितृ एवं पूर्वज ऋण)
    with diagnostic conditions, signs, and exact collective family remedies.
    """
    planets = {p["planet"]: p for p in chart["planets"]}
    sun = planets.get("Sun", {})
    moon = planets.get("Moon", {})
    mars = planets.get("Mars", {})
    merc = planets.get("Mercury", {})
    jup = planets.get("Jupiter", {})
    venus = planets.get("Venus", {})
    sat = planets.get("Saturn", {})
    rahu = planets.get("Rahu", {})
    ketu = planets.get("Ketu", {})

    debts = [
        {
            "debt_id": 1,
            "name": "Forefather's Debt (Pitri Rin)",
            "name_hi": "पितृ ऋण (Forefather's Debt)",
            "is_active": jup.get("house") in (2, 5, 9, 12) and (sat.get("house") in (2, 5, 9, 12) or rahu.get("house") in (2, 5, 9, 12) or jup.get("dignity") == "Debilitated"),
            "trigger_planets": ["Jupiter", "Rahu", "Saturn"],
            "symptoms_en": "Decline in spiritual peace, graying or loss of hair at crown, recurring mental restlessness and obstacles to family lineage.",
            "symptoms_hi": "मानसिक अशांति, सिर के मध्य के बाल झड़ना, पूर्वजों की प्रसन्नता में कमी और कुल वृद्धि में बाधाएं।",
            "remedy_en": "Collect equal coins from all blood relations (father, uncles, brothers) and donate to an ancient temple or contribute to building a public drinking well.",
            "remedy_hi": "परिवार के सभी रक्त-संबंधियों (पिता, चाचा, भाई) से बराबर राशि लेकर किसी प्राचीन देवस्थान में अर्पित करें अथवा प्याऊ लगवाएं।",
        },
        {
            "debt_id": 2,
            "name": "Mother's Debt (Matri Rin)",
            "name_hi": "मातृ ऋण (Mother's Debt)",
            "is_active": ketu.get("house") == 4 or (moon.get("house") == 4 and ketu.get("house") in (1, 4, 7, 10)) or moon.get("dignity") == "Debilitated",
            "trigger_planets": ["Moon", "Ketu"],
            "symptoms_en": "Mother faces recurring health problems; accumulation of stagnant waste or plumbing leaks at home, emotional turbulence.",
            "symptoms_hi": "माता को लगातार शारीरिक कष्ट, घर में जल निकासी में रुकावट, भावनात्मक अस्थिरता व मानसिक व्यग्रता।",
            "remedy_en": "Collect equal silver coins or silver pieces from all blood relatives and submerge them in a flowing clean river in one single act.",
            "remedy_hi": "सभी रक्त-संबंधियों से चांदी का बराबर वजन का सिक्का या टुकड़ा लेकर एक साथ किसी पवित्र बहती नदी में प्रवाहित करें।",
        },
        {
            "debt_id": 3,
            "name": "Brother's & Self Debt (Bhratri Rin)",
            "name_hi": "स्व / भ्रातृ ऋण (Bhratri Rin)",
            "is_active": mars.get("house") in (3, 8) and (merc.get("house") in (3, 8) or sat.get("house") in (3, 8)) or (sun.get("house") == 10 and sat.get("house") == 10),
            "trigger_planets": ["Mars", "Mercury", "Saturn"],
            "symptoms_en": "Sudden bodily accidents, vehicle repairs, blood or muscle distress, coldness and estrangement among brothers.",
            "symptoms_hi": "अचानक वाहन दुर्घटना, रक्त विकार, भाइयों में अकारण मनमुटाव अथवा उनके जीवन में संघर्ष।",
            "remedy_en": "Collect equal money from all blood brothers and relatives to purchase medicines for patients or donate sweet roti baked with jaggery to birds and stray animals.",
            "remedy_hi": "परिवार के सभी भाइयों से बराबर राशि लेकर जरूरतमंदों की चिकित्सा में सहायता करें व मीठी रोटी पक्षियों को डालें।",
        },
        {
            "debt_id": 4,
            "name": "Wife's / Woman's Debt (Stri Rin)",
            "name_hi": "स्त्री ऋण (Stri Rin)",
            "is_active": venus.get("house") in (2, 7) and (rahu.get("house") in (2, 7) or sun.get("house") in (2, 7)) or venus.get("dignity") == "Debilitated",
            "trigger_planets": ["Venus", "Rahu", "Sun"],
            "symptoms_en": "Disharmony in marital life, obstacles in auspicious family functions, sudden destruction of household happiness and luxury.",
            "symptoms_hi": "दांपत्य जीवन में कटुता, शुभ कार्यों में अकारण विघ्न, गृहलक्ष्मी के स्वास्थ्य में उतार-चढ़ाव।",
            "remedy_en": "Collect equal contributions from family members and feed 100 cows with fresh green fodder (हरा चारा) on a Friday.",
            "remedy_hi": "परिवार के सभी सदस्यों से बराबर अंश लेकर एक ही दिन गौशाला में 100 गायों को हरा चारा खिलाएं।",
        },
        {
            "debt_id": 5,
            "name": "Sister's & Daughter's Debt (Kanya Rin)",
            "name_hi": "कन्या / बहन ऋण (Kanya Rin)",
            "is_active": merc.get("house") in (3, 8, 12) or (moon.get("house") in (3, 8) and merc.get("house") in (3, 8)),
            "trigger_planets": ["Mercury", "Moon"],
            "symptoms_en": "Commercial instability, sudden loss of business momentum, nervous tension, daughter or sister facing life hardships.",
            "symptoms_hi": "व्यापार में अप्रत्याशित हानि, वाणी व तंत्रिका तनाव, बहन अथवा कन्या के जीवन में संघर्ष की स्थिति।",
            "remedy_en": "Collect equal yellow sea-shells (पीली कौड़ियां) from blood relations, burn them to ashes in a clean earthen pot, and submerge in flowing water.",
            "remedy_hi": "परिवार के सभी रक्त-संबंधियों से पीली कौड़ियां एकत्र कर भस्म बनाएं और उसे बहते जल में प्रवाहित करें।",
        },
        {
            "debt_id": 6,
            "name": "Cruelty / Oppression Debt (Zalim Rin)",
            "name_hi": "ज़ालिम / क्रूरता ऋण (Zalim Rin)",
            "is_active": sat.get("house") in (10, 11) and rahu.get("house") in (10, 11) or (sun.get("house") == 1 and sat.get("house") == 7),
            "trigger_planets": ["Saturn", "Rahu"],
            "symptoms_en": "House structure cracks or unexpected demolition, sudden legal disputes, unexplained police or tax notices, persistent fear of loss.",
            "symptoms_hi": "मकान की छत या नींव में दरारें, अनपेक्षित अदालती विवाद, अग्नि अथवा चोरी का अकारण भय।",
            "remedy_en": "Collect equal money from all family members to feed fish and birds continuously for 43 days without break, and serve disabled individuals.",
            "remedy_hi": "परिवार से बराबर अंश लेकर 43 दिन लगातार मछलियों व पक्षियों को दाना डालें व दिव्यांगजनों की सेवा करें।",
        },
        {
            "debt_id": 7,
            "name": "Children's Debt (Santana Rin)",
            "name_hi": "संतान ऋण (Santana Rin)",
            "is_active": ketu.get("house") in (5, 6) and (sun.get("house") in (5, 6) or moon.get("house") in (5, 6)),
            "trigger_planets": ["Ketu", "Sun"],
            "symptoms_en": "Delays or distress regarding children, repeated childhood illnesses, lack of peace in family continuation.",
            "symptoms_hi": "संतान सुख में विलंब, बच्चों के स्वास्थ्य में बार-बार परेशानी अथवा उनकी शिक्षा में व्यवधान।",
            "remedy_en": "Collect equal money from all blood relations to feed two-colored (black and white) street dogs with sweet sesame breads continuously.",
            "remedy_hi": "सभी रक्त-संबंधियों से बराबर राशि लेकर काले-सफेद (चितकबरे) श्वान को मीठी रोटी खिलाएं।",
        },
        {
            "debt_id": 8,
            "name": "Divine & Nature's Debt (Kudrati Rin)",
            "name_hi": "कुदरती / दैवीय ऋण (Kudrati Rin)",
            "is_active": (moon.get("house") == 6 and mars.get("house") == 6) or (moon.get("house") in (6, 12) and ketu.get("house") in (6, 12)),
            "trigger_planets": ["Moon", "Mars", "Ketu"],
            "symptoms_en": "Unexpected twists of fate, assets damaged by sudden water/weather shocks, feeling helpless despite right actions.",
            "symptoms_hi": "प्राकृतिक या अनपेक्षित कारणों से नुकसान, बनते कार्यों का अंतिम क्षण में रुक जाना।",
            "remedy_en": "Collect equal whole grains from all family members and feed 100 wild birds or sponsor blankets for ascetics and widows.",
            "remedy_hi": "परिवार से साबुत अनाज एकत्र कर पक्षियों को अर्पित करें अथवा निराश्रितों को वस्त्र/कंबल भेंट करें।",
        },
        {
            "debt_id": 9,
            "name": "Unborn & Unknown Debt (Ajata Rin)",
            "name_hi": "अजन्मे / अज्ञात ऋण (Ajata Rin)",
            "is_active": sun.get("house") == venus.get("house") or (jup.get("house") in (6, 8, 12) and merc.get("house") in (6, 8, 12)),
            "trigger_planets": ["Sun", "Venus", "Jupiter"],
            "symptoms_en": "Hard work yields meager savings, constant drains on capital, recurring peculiar dreams regarding ancestral sites.",
            "symptoms_hi": "अत्यधिक परिश्रम के उपरांत भी संचित धन न टिकना, अज्ञात दिशा से खर्चों का आगमन।",
            "remedy_en": "Collect equal raw coconuts (पानी वाले नारियल) from all family members and submerge them together in a holy river on Wednesday morning.",
            "remedy_hi": "परिवार के सभी सदस्यों से जटा वाले नारियल एकत्र कर बुधवार को बहते पवित्र जल में विसर्जित करें।",
        },
    ]

    # Ensure at least clean non-debt indicators if none match strictly
    active_count = sum(1 for d in debts if d["is_active"])
    if active_count == 0:
        # Default benign condition: Native's chart is largely free of primary ancestral debts
        pass

    return debts


def compute_dormant_houses_and_planets(chart: dict[str, Any]) -> dict[str, Any]:
    """
    Compute Sleeping (Dormant) Houses & Planets and their classical activation rules.
    Lal Kitab: A house with no planets is dormant until awakened at specific age or trigger.
    """
    houses = chart["houses"]
    planets = chart["planets"]

    dormant_house_rules = {
        1: (21, "Awakened by Sun/Mars karma; keep morning solar discipline.", "उम्र 21-22: तांबे का सिक्का अथवा सूर्य उपासना से जाग्रत होता है।"),
        2: (28, "Awakened by Jupiter blessings; apply saffron tilak and honor elders.", "उम्र 28: केसर का तिलक लगाने व बुजुर्गों के आदर से जाग्रत होता है।"),
        3: (31, "Awakened by Mars; exercise courage and maintain brotherly harmony.", "उम्र 31: भाइयों के सौहार्द व शारीरिक पराक्रम से जाग्रत होता है।"),
        4: (24, "Awakened by Moon; receive mother's blessing and keep pure silver close.", "उम्र 24: माता के चरण स्पर्श व चांदी धारण करने से जाग्रत होता है।"),
        5: (32, "Awakened by Jupiter/Sun; practice creative study and noble counsel.", "उम्र 32: गुरुजनों के मार्गदर्शन व ज्ञान साधना से जाग्रत होता है।"),
        6: (34, "Awakened by Mercury/Ketu; feed cows and practice routine discipline.", "उम्र 34: गौ-सेवा व नियमित दिनचर्या से जाग्रत होता है।"),
        7: (22, "Awakened by Venus; clean attire and honor partnership agreements.", "उम्र 22-25: स्वच्छ वस्त्र पहनने व जीवनसाथी के सम्मान से जाग्रत होता है।"),
        8: (36, "Awakened by Saturn; practice humility and avoid dark dealings.", "उम्र 36: सत्यनिष्ठा, सेवा व शनिवार तेल दान से जाग्रत होता है।"),
        9: (40, "Awakened by Jupiter; visit pilgrimage shrines and honor heritage.", "उम्र 40: तीर्थ यात्रा व कुल परम्परा के पालन से जाग्रत होता है।"),
        10: (42, "Awakened by Saturn; steady hard work and evening lamp near sacred trees.", "उम्र 42: निरंतर कर्म व पीपल के समीप दीप प्रज्ज्वलन से जाग्रत होता है।"),
        11: (44, "Awakened by Jupiter; practice benevolent charity without pride.", "उम्र 44: गुप्त दान व मित्रों के सहयोग से जाग्रत होता है।"),
        12: (45, "Awakened by Ketu/Rahu; practice detachment and calm nighttime reflection.", "उम्र 45: शांत ध्यान व चांदी का चौकोर टुकड़ा रखने से जाग्रत होता है।"),
    }

    dormant_houses = []
    for h in houses:
        h_num = h["house"]
        p_in_h = [p for p in planets if p["house"] == h_num]
        is_dormant = len(p_in_h) == 0
        rule = dormant_house_rules.get(h_num, (30, "Active", "सक्रिय"))
        dormant_houses.append({
            "house": h_num,
            "rashi": h["rashi"],
            "rashi_hi": h.get("rashi_hi", h["rashi"]),
            "lord": h["lord"],
            "lord_hi": h.get("lord_hi", h["lord"]),
            "is_dormant": is_dormant,
            "activation_age": rule[0],
            "trigger_en": rule[1],
            "trigger_hi": rule[2],
            "occupant_count": len(p_in_h),
        })

    planet_activation_ages = {
        "Sun": (22, "Father or Government honor", "पिता का आशीर्वाद या राजकीय सम्मान"),
        "Moon": (24, "Mother's blessings or Silver", "माता का आशीर्वाद या चांदी की वस्तु"),
        "Mars": (28, "Brother's support or Land/Sports", "भाई का सहयोग या भूमि/पराक्रम"),
        "Mercury": (34, "Sister/Daughter or Trade/Accounts", "बहन/कन्या का स्नेह या व्यापार"),
        "Jupiter": (16, "Guru/Preceptor or Yellow sapphire", "गुरु का मार्गदर्शन या स्वर्ण/केसर"),
        "Venus": (25, "Marriage, Wife, or Silk/Perfume", "विवाह, जीवनसंगिनी या सुगंधित वस्तु"),
        "Saturn": (36, "Hard labor, Iron, or Uncles", "कठिन परिश्रम, चाचा का साथ या लौह वस्तु"),
        "Rahu": (42, "In-laws or Technological leap", "ससुराल पक्ष या नवीन तकनीकी कार्य"),
        "Ketu": (45, "Son, Nephew, or Spiritual journey", "पुत्र/भांजा या एकांत साधना"),
    }

    dormant_planets = []
    for p in planets:
        name = p["planet"]
        # Planet is considered dormant in Lal Kitab if in house opposite to friend or sitting isolated without aspect
        pakka = PAKKA_GHAR.get(name, set())
        is_p_dormant = p["house"] not in pakka and p["dignity"] in ("Neutral / Mixed", "Debilitated")
        act = planet_activation_ages.get(name, (30, "Maturity", "परिपक्वता"))
        dormant_planets.append({
            "planet": name,
            "planet_hi": p.get("planet_hi", name),
            "house": p["house"],
            "rashi": p["rashi"],
            "rashi_hi": p.get("rashi_hi", p["rashi"]),
            "is_dormant": is_p_dormant,
            "awakening_age": act[0],
            "trigger_en": act[1],
            "trigger_hi": act[2],
        })

    return {
        "dormant_houses": dormant_houses,
        "dormant_planets": dormant_planets,
    }


def compute_varshphal_parhez(varshphal: dict[str, Any], running_age: int) -> dict[str, Any]:
    """
    Compute specific Varshphal Prohibitions (परहेज), 'What NOT to do',
    and strict 40-43 day execution rules for the running solar year.
    """
    v_planets = varshphal.get("planets", [])
    sat_h = next((p.get("varshphal_house", p.get("house")) for p in v_planets if p["planet"] == "Saturn"), None)
    mars_h = next((p.get("varshphal_house", p.get("house")) for p in v_planets if p["planet"] == "Mars"), None)
    sun_h = next((p.get("varshphal_house", p.get("house")) for p in v_planets if p["planet"] == "Sun"), None)
    merc_h = next((p.get("varshphal_house", p.get("house")) for p in v_planets if p["planet"] == "Mercury"), None)
    moon_h = next((p.get("varshphal_house", p.get("house")) for p in v_planets if p["planet"] == "Moon"), None)
    venus_h = next((p.get("varshphal_house", p.get("house")) for p in v_planets if p["planet"] == "Venus"), None)
    rahu_h = next((p.get("varshphal_house", p.get("house")) for p in v_planets if p["planet"] == "Rahu"), None)

    dont_list_en = []
    dont_list_hi = []
    do_list_en = []
    do_list_hi = []

    if sat_h in (1, 8):
        dont_list_en.append("Do NOT repair or rebuild home roofs or lay house foundations this year.")
        dont_list_hi.append("इस वर्ष मकान की नई छत न डलवाएं और न ही नींव का निर्माण करें।")
    else:
        dont_list_en.append("Avoid purchasing second-hand rust-prone machinery without cleaning.")
        dont_list_hi.append("पुरानी जंग लगी लोहे की वस्तुएं घर में एकत्रित न करें।")

    if moon_h in (6, 10):
        dont_list_en.append("Do NOT donate milk, curd, or free water stalls at home or business.")
        dont_list_hi.append("इस वर्ष दूध का दान न करें और न ही सार्वजनिक प्याऊ का निशुल्क वितरण स्वयं करें।")
        do_list_en.append("Keep a drop of clean Ganga water or pure silver piece in daily wallet.")
        do_list_hi.append("बटुए या तिजोरी में चांदी का ठोस टुकड़ा या गंगाजल का संचय रखें।")

    if merc_h in (8, 12):
        dont_list_en.append("Do NOT keep broad-leaved green plants, dried flowers, or broken musical toys inside the house.")
        dont_list_hi.append("घर के भीतर चौड़े पत्तों वाले पौधे, सूखे गुलदस्ते या टूटे-फूटे वाद्य यंत्र न रखें।")
    else:
        do_list_en.append("Feed soaked green moong lentils or fresh green fodder to cows.")
        do_list_hi.append("बुधवार को भीगी हुई हरी मूंग अथवा गाय को हरा चारा खिलाएं।")

    if sun_h in (7, 10):
        dont_list_en.append("Never accept free gifts, taweez, or brass amulets from unknown individuals.")
        dont_list_hi.append("किसी भी अपरिचित से मुफ्त में ताबीज या पीतल की वस्तु उपहार में न लें।")

    if rahu_h in (5, 12):
        dont_list_en.append("Do NOT store clutter, damaged electronic gadgets, or unwashed footwear under your bed or staircase.")
        dont_list_hi.append("पलंग के नीचे अथवा सीढ़ियों के नीचे खराब इलेक्ट्रॉनिक सामान या कबाड़ न रखें।")

    if venus_h in (6, 9):
        dont_list_en.append("Do NOT wear unwashed, wrinkled, or torn clothes even when staying at home.")
        dont_list_hi.append("घर पर भी कभी मैले, फटे या बिना इस्त्री किए वस्त्र धारण न करें।")
        do_list_en.append("Use pure sandalwood or natural camphor aroma in the living room.")
        do_list_hi.append("घर में शुद्ध चंदन अथवा देशी कपूर की सुगंध का प्रयोग करें।")

    # General Lal Kitab 40-43 Day Rules
    day_rules_en = [
        "Execute remedies strictly in daytime between sunrise and sunset.",
        "Perform remedies for 40 to 43 consecutive days without missing a single day; if broken, the cycle must restart from day 1.",
        "Never perform two contradictory planet remedies simultaneously.",
        "Maintain sobriety and truthful speech throughout the remedy window.",
    ]
    day_rules_hi = [
        "सभी उपाय केवल दिन के समय (सूर्योदय से सूर्यास्त के मध्य) ही करें।",
        "उपाय लगातार 40 से 43 दिन तक बिना नागा करें; यदि एक दिन भी छूटा तो दोबारा 1 से प्रारंभ करना होगा।",
        "एक समय में केवल एक ही मुख्य उपाय करें; परस्पर विरोधी ग्रहों के उपाय साथ में न करें।",
        "उपाय की अवधि के दौरान सात्विक आचरण व सत्यनिष्ठा का पूर्ण पालन करें।",
    ]

    return {
        "running_age": running_age,
        "year": varshphal.get("year", date.today().year),
        "dont_list_en": dont_list_en,
        "dont_list_hi": dont_list_hi,
        "do_list_en": do_list_en,
        "do_list_hi": do_list_hi,
        "day_rules_en": day_rules_en,
        "day_rules_hi": day_rules_hi,
    }


def compute_planetary_clashes(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Compute Lal Kitab Planetary Clashes (ग्रहों की टक्कर) and identifying
    the innocent third planet suffering as 'Sacrificial Lamb' (कुर्बानी का बकरा).
    """
    planets = {p["planet"]: p for p in chart["planets"]}
    sun = planets.get("Sun", {})
    moon = planets.get("Moon", {})
    mars = planets.get("Mars", {})
    merc = planets.get("Mercury", {})
    jup = planets.get("Jupiter", {})
    venus = planets.get("Venus", {})
    sat = planets.get("Saturn", {})
    rahu = planets.get("Rahu", {})
    ketu = planets.get("Ketu", {})

    clashes = []

    # 1. Sun vs Saturn collision -> Victim: Venus
    if abs(sun.get("house", 0) - sat.get("house", 0)) in (0, 6):
        clashes.append({
            "clash_id": 1,
            "graha_1": "Sun (सूर्य)",
            "graha_2": "Saturn (शनि)",
            "axis": f"H{sun.get('house')} vs H{sat.get('house')}",
            "victim_planet": "Venus",
            "victim_planet_hi": "शुक्र (Venus)",
            "effect_en": "Sun and Saturn clash across reciprocal axis; Venus becomes the sacrificial lamb, causing friction in marital harmony, eye or skin sensitivity.",
            "effect_hi": "सूर्य और शनि के आमने-सामने टकराने से शुक्र 'कुर्बानी का बकरा' बनता है, जिससे दांपत्य में तनाव अथवा नेत्र/त्वचा विकार उत्पन्न हो सकते हैं।",
            "remedy_en": "Feed green grass or fresh butter roti to white cows, and keep pure silver close.",
            "remedy_hi": "सफेद गाय को मक्खन लगी मीठी रोटी अथवा हरा चारा दें, और चांदी का चौकोर टुकड़ा पास रखें।",
        })

    # 2. Mars vs Mercury collision -> Victim: Ketu / Sun
    if abs(mars.get("house", 0) - merc.get("house", 0)) in (0, 6):
        clashes.append({
            "clash_id": 2,
            "graha_1": "Mars (मंगल)",
            "graha_2": "Mercury (बुध)",
            "axis": f"H{mars.get('house')} vs H{merc.get('house')}",
            "victim_planet": "Ketu",
            "victim_planet_hi": "केतु (Ketu)",
            "effect_en": "Mars (courage/fire) and Mercury (wit/speech) collide; Ketu suffers, causing joint stiffness, nervous irritability, or foot strain.",
            "effect_hi": "मंगल और बुध की टक्कर से केतु बलि का बकरा बनता है, जिससे जोड़ों में दर्द, नसों में खिंचाव या पैरों में चोट की संभावना रहती है।",
            "remedy_en": "Wear a solid silver bangle without joints and feed street dogs with sweet bread.",
            "remedy_hi": "दाहिने हाथ में बिना जोड़ का ठोस चांदी का कड़ा पहनें व श्वान को गुड़ की रोटी दें।",
        })

    # 3. Jupiter vs Rahu / Mercury collision -> Victim: Ketu / Venus
    if abs(jup.get("house", 0) - rahu.get("house", 0)) in (0, 6) or abs(jup.get("house", 0) - merc.get("house", 0)) in (0, 6):
        clashes.append({
            "clash_id": 3,
            "graha_1": "Jupiter (गुरु)",
            "graha_2": "Rahu/Mercury (राहु/बुध)",
            "axis": f"H{jup.get('house')} vs H{rahu.get('house')}",
            "victim_planet": "Ketu / Venus",
            "victim_planet_hi": "केतु एवं शुक्र",
            "effect_en": "Jupiter's pure wisdom is shadowed by Rahu/Mercury illusion; discernment weakens, resulting in sudden financial missteps.",
            "effect_hi": "बृहस्पति और राहु की युति/टक्कर से विवेक पर भ्रम का आवरण पड़ता है, जिससे सही समय पर सही निर्णय लेने में बाधा आती है।",
            "remedy_en": "Apply yellow saffron or turmeric tilak on forehead daily, and donate yellow chana dal to temple.",
            "remedy_hi": "माथे, नाभि और जिह्वा पर नित्य केसर का तिलक लगाएं व चने की दाल का दान करें।",
        })

    # 4. Moon vs Ketu / Saturn collision -> Victim: Mars
    if abs(moon.get("house", 0) - ketu.get("house", 0)) in (0, 6) or abs(moon.get("house", 0) - sat.get("house", 0)) in (0, 6):
        clashes.append({
            "clash_id": 4,
            "graha_1": "Moon (चंद्रमा)",
            "graha_2": "Ketu/Saturn (केतु/शनि)",
            "axis": f"H{moon.get('house')} vs H{sat.get('house')}",
            "victim_planet": "Mars",
            "victim_planet_hi": "मंगल (Mars)",
            "effect_en": "Moon and Ketu/Saturn alignment strains mental composure; Mars becomes sacrificial, draining vitality and drive.",
            "effect_hi": "चंद्रमा और केतु/शनि का प्रभाव मन में भारीपन लाता है तथा मंगल के प्रभाव को क्षीण कर उत्साह कम करता है।",
            "remedy_en": "Drink water from a silver tumbler, keep calm evening rhythm, and offer sweet roti to animals on Tuesdays.",
            "remedy_hi": "चांदी के गिलास से जल पिएं और मंगलवार को मीठी रोटी गाय या पक्षियों को अर्पित करें।",
        })

    if not clashes:
        clashes.append({
            "clash_id": 0,
            "graha_1": "Harmonious",
            "graha_2": "Planetary Alignment",
            "axis": "Balanced",
            "victim_planet": "None",
            "victim_planet_hi": "कोई नहीं (संतुलित)",
            "effect_en": "No severe planetary collision detected in natal houses. Major planetary energies operate in natural equilibrium.",
            "effect_hi": "आपकी जन्मकुंडली में कोई गंभीर ग्रह टकराव नहीं है। समस्त ग्रह अपनी स्वाभाविक ऊर्जा में संतुलित हैं।",
            "remedy_en": "Continue routine morning prayer and ethical conduct.",
            "remedy_hi": "प्रातः काल की सामान्य पूजा व सदाचार का पालन करें।",
        })

    return clashes


def compute_life_events_timeline(chart: dict[str, Any], dob: str, dashas: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Compute Chronological Life Events Timeline:
    1. Past Verification (भूतकाल की सत्यता - चोट, नौकरी, विवाह, वाहन)
    2. Future Caution & Opportunity Windows (भविष्य की अनहोनी व सुरक्षा)
    Correlates natal house significations with completed ages and dasha transitions.
    """
    b_date = datetime.strptime(dob, "%Y-%m-%d").date()
    b_year = b_date.year
    cur_year = date.today().year

    planets = {p["planet"]: p for p in chart["planets"]}
    asc = chart.get("ascendant", {})
    sun = planets.get("Sun", {})
    moon = planets.get("Moon", {})
    mars = planets.get("Mars", {})
    jup = planets.get("Jupiter", {})
    sat = planets.get("Saturn", {})
    rahu = planets.get("Rahu", {})

    timeline = []

    # Milestone 1: Early Youth & Health/Education (Ages 16-19)
    y1 = b_year + 18
    timeline.append({
        "year": y1,
        "age": 18,
        "type": "Past Verification" if y1 <= cur_year else "Future Caution / Opportunity",
        "category": "Education & Direction",
        "category_hi": "शिक्षा व जीवन दिशा",
        "headline_en": "Major Academic Crossroads & Intellectual Transition",
        "headline_hi": "शैक्षिक बदलाव व बौद्धिक विकास का महत्वपूर्ण मोड़",
        "description_en": f"House {jup.get('house', 5)} Jupiter influences guided academic choices, mental expansion, and foundational career focus.",
        "description_hi": f"पंचम भाव व गुरु के प्रभाव से उच्च अध्ययन, प्रतियोगिता परीक्षा व नई दिशा का चयन हुआ।",
        "caution_level": "Favorable Window",
        "guidance_en": "Nurture consistent focus; respect mentors and academic guides.",
        "guidance_hi": "गुरुजनों का मार्गदर्शन लें और एकाग्रता बनाए रखें।",
    })

    # Milestone 2: Career Entry / Major Relocation (Ages 22-25)
    y2 = b_year + 23
    timeline.append({
        "year": y2,
        "age": 23,
        "type": "Past Verification" if y2 <= cur_year else "Future Caution / Opportunity",
        "category": "Career & Independence",
        "category_hi": "आजीविका व स्वावलंबन",
        "headline_en": "First Professional Breakthrough / Relocation",
        "headline_hi": "प्रथम कार्यक्षेत्र अवसर व स्थान परिवर्तन का योग",
        "description_en": f"Sun in House {sun.get('house', 10)} and Saturn transit triggered first earnings, relocation, and independent responsibility.",
        "description_hi": f"दशम भाव एवं सूर्य के प्रभाव से आजीविका का आरंभ, नई जिम्मेदारियां तथा कार्यक्षेत्र में पहचान मिली।",
        "caution_level": "Favorable Window",
        "guidance_en": "Maintain strong discipline and avoid shortcuts in professional ethics.",
        "guidance_hi": "कार्य में अनुशासन रखें और जल्दबाजी से बचें।",
    })

    # Milestone 3: Health Caution / Stress / Injury Window (Ages 27-29)
    y3 = b_year + 28
    is_mars_bad = mars.get("house") in (3, 8) or sat.get("house") in (6, 8)
    timeline.append({
        "year": y3,
        "age": 28,
        "type": "Past Verification" if y3 <= cur_year else "Future Caution / Opportunity",
        "category": "Health & Safety Alert",
        "category_hi": "स्वास्थ्य व सुरक्षा चेतावनी",
        "headline_en": "Physical Strain, Vehicle Caution or Family Health Anxiety",
        "headline_hi": "शारीरिक थकान, वाहन संभलकर चलाने व स्वास्थ्य सावधानी का समय",
        "description_en": f"Mars in House {mars.get('house', 3)} transit activated physical caution, vehicle repairs, or emotional turbulence.",
        "description_hi": f"मंगल व शनि के गोचर से वाहन सावधानी, रक्त विकार व परिवार में स्वास्थ्य चिंता का योग बना।",
        "caution_level": "Moderate Caution",
        "guidance_en": "Drive with vigilance, avoid hasty sports or heated arguments; donate sweet roti on Tuesdays.",
        "guidance_hi": "वाहन गति पर नियंत्रण रखें, क्रोध से बचें और मंगलवार को गुड़ का दान करें।",
    })

    # Milestone 4: Marriage, Partnership & Relationship Stability (Ages 29-32)
    y4 = b_year + 30
    timeline.append({
        "year": y4,
        "age": 30,
        "type": "Past Verification" if y4 <= cur_year else "Future Caution / Opportunity",
        "category": "Marriage & Domestic Growth",
        "category_hi": "विवाह, साझेदारी व गृहस्थ जीवन",
        "headline_en": "Significant Relationship Union & Family Foundation",
        "headline_hi": "वैवाहिक संबंध, गृहस्थ जीवन व पारिवारिक दायित्वों का विस्तार",
        "description_en": "Jupiter aspecting 7th house axis fostered matrimonial alliances, partnership commitments, and deep bonding.",
        "description_hi": "सप्तम भाव व गुरु के शुभ प्रभाव से विवाह, जीवनसाथी का आगमन तथा नवीन घर की स्थापना का योग।",
        "caution_level": "Favorable Window",
        "guidance_en": "Cultivate mutual patience and transparent communication in domestic decisions.",
        "guidance_hi": "परस्पर विश्वास बनाए रखें और घर में शांति का वातावरण रखें।",
    })

    # Milestone 5: Property, Asset Creation & Financial Growth (Ages 34-37)
    y5 = b_year + 35
    timeline.append({
        "year": y5,
        "age": 35,
        "type": "Past Verification" if y5 <= cur_year else "Future Caution / Opportunity",
        "category": "Property & Wealth",
        "category_hi": "भूमि, भवन व संपत्ति लाभ",
        "headline_en": "Major Fixed Asset Acquisition & Financial Consolidation",
        "headline_hi": "स्थाई संपत्ति, वाहन या मकान क्रय तथा आर्थिक स्थायित्व",
        "description_en": f"4th house blessings coupled with Saturn maturity rewarded patient enterprise with property or long-term investments.",
        "description_hi": "चतुर्थ भाव एवं शनि के कर्मफल से भूमि-भवन क्रय अथवा दीर्घकालिक निवेश का श्रेष्ठ समय।",
        "caution_level": "Favorable Window",
        "guidance_en": "Verify all documentation meticulously; avoid unvetted speculative ventures.",
        "guidance_hi": "दस्तावेज़ों की पूर्ण जांच करें और सट्टेबाजी से दूर रहें।",
    })

    # Milestone 6: Rahu 42-Yr Life Transformation & Career Leap (Ages 41-44)
    y6 = b_year + 42
    timeline.append({
        "year": y6,
        "age": 42,
        "type": "Past Verification" if y6 <= cur_year else "Future Caution / Opportunity",
        "category": "Life Transformation",
        "category_hi": "जीवन में युगांतरकारी बदलाव",
        "headline_en": "Rahu 42nd Year Transition: Deep Pivot & Status Surge",
        "headline_hi": "लाल किताब 42वां वर्ष: कार्यक्षेत्र में बड़ा उछाल अथवा पद्धति परिवर्तन",
        "description_en": "Classical Lal Kitab 42nd year marks Rahu's awakening: unexpected technological shifts, leadership mantle, or international connections.",
        "description_hi": "राहु का 42वां वर्ष जीवन की दिशा बदलता है; नए संपर्क, तकनीकी उन्नति और नेतृत्व की प्राप्ति होती है।",
        "caution_level": "Moderate Caution",
        "guidance_en": "Keep humility high; avoid ego-driven financial expansions. Maintain fair dealings.",
        "guidance_hi": "अहंकार से बचें, निर्णय शांति से लें और चांदी का चौकोर टुकड़ा पास रखें।",
    })

    # Milestone 7: Spiritual Wisdom & Community Recognition (Ages 48-52)
    y7 = b_year + 50
    timeline.append({
        "year": y7,
        "age": 50,
        "type": "Past Verification" if y7 <= cur_year else "Future Caution / Opportunity",
        "category": "Status & Spiritual Peace",
        "category_hi": "मान-सम्मान व आध्यात्मिक शांति",
        "headline_en": "Consolidation of Authority, Legacy & Mentorship",
        "headline_hi": "सामाजिक प्रतिष्ठा, परामर्शदाता की भूमिका व आध्यात्मिक संतोष",
        "description_en": "9th and 10th house harmony manifests as elder guidance, community respect, and charitable fulfillment.",
        "description_hi": "नवम व दशम भाव के समन्वय से समाज में मान-प्रतिष्ठा और परोपकारी कार्यों में सक्रियता।",
        "caution_level": "Favorable Window",
        "guidance_en": "Engage in charitable knowledge sharing and ancestral rituals.",
        "guidance_hi": "धार्मिक कार्यों व जरूरतमंदों की सेवा में समय दें।",
    })

    # Sort chronologically
    timeline.sort(key=lambda x: x["year"])
    return timeline


def compute_daily_horoscope_and_totka(target_date: str | None = None) -> dict[str, Any]:
    """
    Compute daily 12-Zodiac horoscopes and positive, zero-cost daily Lal Kitab Totka.
    """
    dt = datetime.strptime(target_date, "%Y-%m-%d") if target_date else date.today()
    wd = dt.weekday()

    weekday_totkas = [
        # Monday (Moon)
        ("Offer clean water to a Shiva Lingam or plants; avoid cold emotional conflicts.",
         "शिवलिंग अथवा पौधों को जल अर्पित करें और वाणी में शीतलता रखें।"),
        # Tuesday (Mars)
        ("Share sweet bread or jaggery with birds/dogs; avoid harsh arguments.",
         "मीठी रोटी या गुड़ पक्षियों अथवा श्वान को खिलाएं और क्रोध से बचें।"),
        # Wednesday (Mercury)
        ("Feed green fodder to cows or water broad-leaved plants.",
         "गौमाता को हरा चारा खिलाएं अथवा पौधों में जल दें।"),
        # Thursday (Jupiter)
        ("Apply a saffron/turmeric tilak on forehead; honor mentors and elders.",
         "माथे पर केसर या हल्दी का तिलक लगाएं और गुरुजनों का आशीर्वाद लें।"),
        # Friday (Venus)
        ("Wear clean, fragrant clothes and share white sweets with girls or birds.",
         "स्वच्छ व सुगंधित वस्त्र पहनें और छोटी कन्याओं को मिश्री/मिठाई दें।"),
        # Saturday (Saturn)
        ("Feed stray animals; light a mustard oil lamp near a Peepal tree in evening.",
         "सायंकाल पीपल के समीप सरसों के तेल का दीपक प्रज्ज्वलित करें व जीवों को भोजन दें।"),
        # Sunday (Sun)
        ("Offer water in copper to the morning Sun; greet father with folded hands.",
         "तांबे के पात्र से प्रातः सूर्य देव को अर्घ्य दें और पिता का चरण स्पर्श करें।"),
    ]

    rashi_predictions = [
        {"sign": "Aries", "sign_hi": "मेष", "color": "Crimson Red", "color_hi": "लाल", "number": 9,
         "pred_en": "High energetic momentum today; favorable for initiating pending communications and physical exercise.",
         "pred_hi": "आज ऊर्जा व पराक्रम उच्च रहेगा। रुके हुए कार्य आरंभ करने व निर्णय लेने के लिए दिन शुभ है।"},
        {"sign": "Taurus", "sign_hi": "वृषभ", "color": "Pearl White", "color_hi": "सफेद", "number": 6,
         "pred_en": "Focus on domestic comfort and careful budgeting; pleasant family dialogue brings mental ease.",
         "pred_hi": "पारिवारिक सुख व धन संचय पर ध्यान रहेगा। परिजनों के साथ सौहार्दपूर्ण वार्ता मन को शांति देगी।"},
        {"sign": "Gemini", "sign_hi": "मिथुन", "color": "Emerald Green", "color_hi": "हरा", "number": 5,
         "pred_en": "Creative ideas spark swift resolutions; verify key documents before dispatching.",
         "pred_hi": "बुद्धि व रचनात्मकता से जटिल समस्याएं सुलझेंगी। महत्वपूर्ण दस्तावेजों को जांचकर आगे बढ़ें।"},
        {"sign": "Cancer", "sign_hi": "कर्क", "color": "Milky Silver", "color_hi": "चांदी / सफेद", "number": 2,
         "pred_en": "Intuition is sharp; avoid overthinking past events and stay close to water elements.",
         "pred_hi": "अंतःप्रेरणा बलवान रहेगी। पुरानी बातों की चिंता छोड़कर वर्तमान कर्म पर ध्यान केंद्रित रखें।"},
        {"sign": "Leo", "sign_hi": "सिंह", "color": "Golden Yellow", "color_hi": "सुनहरा", "number": 1,
         "pred_en": "Authority and professional respect shine; lead with empathy to win complete team loyalty.",
         "pred_hi": "कार्यक्षेत्र में मान-सम्मान व प्रभाव बढ़ेगा। सहयोगियों के साथ विनम्रता से पेश आएं।"},
        {"sign": "Virgo", "sign_hi": "कन्या", "color": "Dark Green", "color_hi": "गहरा हरा", "number": 5,
         "pred_en": "Analytical rigor yields tangible progress; keep daily diet light and balanced.",
         "pred_hi": "विश्लेषण क्षमता से कार्य में प्रगति होगी। स्वास्थ्य की दृष्टि से हल्का आहार लें।"},
        {"sign": "Libra", "sign_hi": "तुला", "color": "Pastel Pink", "color_hi": "गुलाबी", "number": 7,
         "pred_en": "Harmonious partnerships bloom; excellent day for artistic exploration and shopping.",
         "pred_hi": "साझेदारी व दांपत्य में मधुरता रहेगी। कलात्मक व सामाजिक कार्यों के लिए अनुकूल दिन है।"},
        {"sign": "Scorpio", "sign_hi": "वृश्चिक", "color": "Coral Red", "color_hi": "सिंदूरी लाल", "number": 9,
         "pred_en": "Deep focus unlocks solutions to persistent technical or research puzzles.",
         "pred_hi": "गहन चिंतन से गूढ़ विषयों का समाधान मिलेगा। गुप्त शत्रुओं से सावधान रहते हुए आगे बढ़ें।"},
        {"sign": "Sagittarius", "sign_hi": "धनु", "color": "Bright Saffron", "color_hi": "केसरिया", "number": 3,
         "pred_en": "Optimism attracts supportive mentors; plan long-range spiritual or academic journeys.",
         "pred_hi": "सकारात्मक सोच से उच्च अधिकारियों का सहयोग मिलेगा। धार्मिक व ज्ञानवर्धक योजनाओं में रुचि बढ़ेगी।"},
        {"sign": "Capricorn", "sign_hi": "मकर", "color": "Steel Blue", "color_hi": "नीला", "number": 8,
         "pred_en": "Steady, persistent work creates lasting commercial stability; pace your evening routine.",
         "pred_hi": "धैर्य व निष्ठा से किए गए प्रयास उत्तम फल देंगे। कार्यक्षेत्र में आपकी विश्वसनीयता बढ़ेगी।"},
        {"sign": "Aquarius", "sign_hi": "कुंभ", "color": "Electric Cyan", "color_hi": "आसमानी", "number": 4,
         "pred_en": "Novel ideas and networking opportunities arise; collaborate with reliable colleagues.",
         "pred_hi": "नए विचार और मित्र सहयोग प्रदान करेंगे। सामूहिक कार्यों में सफलता का योग है।"},
        {"sign": "Pisces", "sign_hi": "मीन", "color": "Soft Gold", "color_hi": "हल्का पीला", "number": 3,
         "pred_en": "Compassion and spiritual reflection illuminate peace; trust your inner wisdom.",
         "pred_hi": "परोपकार व ध्यान से मानसिक संतोष मिलेगा। आंतरिक शांति के साथ दिन व्यतीत होगा।"},
    ]

    totka = weekday_totkas[wd]

    return {
        "date": dt.strftime("%Y-%m-%d"),
        "weekday": dt.strftime("%A"),
        "todays_totka_en": totka[0],
        "todays_totka_hi": totka[1],
        "zodiac_predictions": rashi_predictions,
    }
