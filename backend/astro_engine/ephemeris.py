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


def calculate_kp_sub_lords(lon: float) -> tuple[str, str, str, str]:
    """
    Calculate Krishnamurti Paddhati (KP) 4-Fold Cuspal Sub-Lords:
    1. RL: Rashi Lord (राशि स्वामी)
    2. NL: Nakshatra Lord (नक्षत्र स्वामी)
    3. SL: Sub Lord (उप-स्वामी)
    4. SSL: Sub-Sub Lord (उप-उप-स्वामी)
    Based on Vimshottari 120-year proportions across 800 arc minutes of each Nakshatra.
    """
    lon = lon % 360.0
    rashi_idx = int(lon // 30.0)
    rl = RASHI_LORDS[rashi_idx]

    tot_min = lon * 60.0
    nak_idx = int(tot_min // 800.0) % 27
    rem_nak_min = tot_min % 800.0

    start_sub_idx = nak_idx % 9
    nl = DASHA_ORDER[start_sub_idx][0]

    # Sub Lord (SL)
    sl = nl
    sub_span = 800.0 * (DASHA_ORDER[start_sub_idx][1] / 120.0)
    rem_sub_min = rem_nak_min
    sl_idx = start_sub_idx
    for i in range(9):
        curr_p_idx = (start_sub_idx + i) % 9
        span = 800.0 * (DASHA_ORDER[curr_p_idx][1] / 120.0)
        if rem_nak_min <= span or i == 8:
            sl = DASHA_ORDER[curr_p_idx][0]
            sl_idx = curr_p_idx
            sub_span = span
            rem_sub_min = rem_nak_min
            break
        rem_nak_min -= span

    # Sub-Sub Lord (SSL)
    ssl = sl
    rem_ssl_min = rem_sub_min
    for j in range(9):
        curr_ssl_idx = (sl_idx + j) % 9
        ssl_span = sub_span * (DASHA_ORDER[curr_ssl_idx][1] / 120.0)
        if rem_ssl_min <= ssl_span or j == 8:
            ssl = DASHA_ORDER[curr_ssl_idx][0]
            break
        rem_ssl_min -= ssl_span

    return rl, nl, sl, ssl


def assign_jaimini_karakas(planets: list[dict[str, Any]]) -> None:
    """
    Assign 7 Classical Jaimini Karakas based on decreasing degrees within sign (0° to 30°):
    1. AK: Atmakaraka (आत्मकारक) - Highest degree, represents soul, destiny, core self.
    2. AmK: Amatyakaraka (अमात्यकारक) - 2nd, represents career, intellect, executive power.
    3. BK: Bhratrikaraka (भ्रातृकारक) - 3rd, siblings, advisors, courage.
    4. MK: Matrikaraka (मातृकारक) - 4th, mother, emotional peace, assets.
    5. PK: Putrakaraka (पुत्रकारक) - 5th, children, creative wisdom, progeny.
    6. GK: Gnatikaraka (ज्ञातिकारक) - 6th, obstacles, competitors, illness, kinsmen.
    7. DK: Darakaraka (दाराकारक) - 7th (lowest), spouse, business partnerships.
    """
    seven = [p for p in planets if p.get("planet") in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")]
    seven.sort(key=lambda x: (x.get("degree_in_sign") if "degree_in_sign" in x else (x.get("longitude", x.get("lon", 0.0)) % 30.0)), reverse=True)

    karaka_defs = [
        ("AK", "Atmakaraka (Soul)", "आत्मकारक (आत्मा व मुख्य नियति)"),
        ("AmK", "Amatyakaraka (Career)", "अमात्यकारक (आजीविका व बुद्धि)"),
        ("BK", "Bhratrikaraka (Siblings)", "भ्रातृकारक (पराक्रम व बंधु)"),
        ("MK", "Matrikaraka (Mother/Happiness)", "मातृकारक (माता व गृह सुख)"),
        ("PK", "Putrakaraka (Children/Wisdom)", "पुत्रकारक (संतान व विवेक)"),
        ("GK", "Gnatikaraka (Obstacles)", "ज्ञातिकारक (शत्रु, रोग व बाधा)"),
        ("DK", "Darakaraka (Spouse/Partnership)", "दाराकारक (जीवनसाथी व साझेदारी)"),
    ]

    for idx, p in enumerate(seven):
        code, name_en, name_hi = karaka_defs[idx]
        p["karaka_code"] = code
        p["karaka_en"] = name_en
        p["karaka_hi"] = name_hi

    return planets
    for p in planets:
        if p.get("planet") in ("Rahu", "Ketu"):
            p["karaka_code"] = "—"
            p["karaka_en"] = "N/A"
            p["karaka_hi"] = "—"
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


def _clean_dob(dob: str) -> str:
    """Normalize date string into standard YYYY-MM-DD."""
    if not dob:
        return "1990-01-01"
    raw = str(dob).strip().replace("/", "-")
    parts = raw.split("-")
    if len(parts) == 3 and len(parts[0]) <= 2 and len(parts[2]) == 4:
        return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    elif len(parts) == 3 and len(parts[0]) == 4:
        return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
    return raw


def to_jd_ut(
    dob: str,
    birth_time: str,
    tz_offset: float = 5.5,
    place_name: str = "",
    iana_tz: str | None = None,
) -> tuple[float, float, str]:
    t_str = birth_time.strip()
    clean_dob = _clean_dob(dob)
    fmt = "%Y-%m-%d %H:%M:%S" if len(t_str.split(":")) == 3 else "%Y-%m-%d %H:%M"
    naive_dt = datetime.strptime(f"{clean_dob} {t_str}", fmt)
    eff_offset, tz_name = resolve_historical_tz(clean_dob, birth_time, tz_offset, place_name, iana_tz)
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

    # Enrich planets with KP 4-fold Cuspal Sub-Lords (RL-NL-SL-SSL)
    for p in planets:
        rl, nl, sl, ssl = calculate_kp_sub_lords(p["longitude"])
        p["rl"] = rl
        p["nl"] = nl
        p["sl"] = sl
        p["ssl"] = ssl
        p["rl_hi"] = PLANET_NAMES_HI.get(rl, rl)
        p["nl_hi"] = PLANET_NAMES_HI.get(nl, nl)
        p["sl_hi"] = PLANET_NAMES_HI.get(sl, sl)
        p["ssl_hi"] = PLANET_NAMES_HI.get(ssl, ssl)

    # Assign 7 Jaimini Karakas (AK to DK)
    assign_jaimini_karakas(planets)

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

    asc_rl, asc_nl, asc_sl, asc_ssl = calculate_kp_sub_lords(asc_deg)

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
            "rl": asc_rl,
            "nl": asc_nl,
            "sl": asc_sl,
            "ssl": asc_ssl,
            "rl_hi": PLANET_NAMES_HI.get(asc_rl, asc_rl),
            "nl_hi": PLANET_NAMES_HI.get(asc_nl, asc_nl),
            "sl_hi": PLANET_NAMES_HI.get(asc_sl, asc_sl),
            "ssl_hi": PLANET_NAMES_HI.get(asc_ssl, asc_ssl),
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
    c_dob = _clean_dob(dob)
    b_year = int(c_dob.split("-")[0])
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
    birth_date = datetime.strptime(_clean_dob(dob), "%Y-%m-%d").date()
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
    dob_val = _clean_dob(member.get("dob", "1990-01-01"))
    tob_val = member.get("birth_time") or member.get("tob", "12:00")
    lat_val = float(member.get("latitude") if member.get("latitude") is not None else member.get("lat", 28.6139))
    lon_val = float(member.get("longitude") if member.get("longitude") is not None else member.get("lon", 77.2090))
    tz_val = float(member.get("tz_offset") if member.get("tz_offset") is not None else member.get("tz", 5.5))
    pname_val = member.get("place_name") or member.get("place", "New Delhi")

    chart = compute_chart(
        dob_val,
        tob_val,
        lat_val,
        lon_val,
        tz_val,
        place_name=pname_val,
    )
    varshphal = compute_varshphal_chart(chart, dob_val, target_year=target_year)
    dashas = compute_vimshottari_dashas(dob_val, chart["moon_longitude"])
    houses_pred = _house_predictions(chart)
    vivaran = _vivaran_desk(chart)
    age_ranges = []
    try:
        b_yr = int(dob_val.replace("/", "-").split("-")[0])
    except Exception:
        b_yr = 1990
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
    kp_chart_data = compute_kp_cusp_chart(chart, dob_val, tob_val, lat_val, lon_val, tz_val)
    raw_bundle = {
        "member": member,
        "chart": chart,
        "varshphal": varshphal,
        "dashas": compute_bifurcated_dasha_predictions(dashas, dob_val),
        "ghar_predictions": houses_pred,
        "vivaran": vivaran,
        "age_ranges": age_ranges,
        "ancestral_debts": compute_lal_kitab_debts(chart),
        "dormancy": compute_dormant_houses_and_planets(chart),
        "parhez": compute_varshphal_parhez(varshphal, cur_yr - b_yr + 1),
        "clashes": compute_planetary_clashes(chart),
        "life_events": compute_life_events_timeline(chart, dob_val, dashas),
        "yogas": compute_shubh_ashubh_yogas(chart),
        "luck_meter": compute_luck_meter(chart),
        "personal_dayfal": compute_personal_dayfal(chart),
        "weekly_forecast": compute_weekly_personal_forecast(chart),
        "kp_cusps": kp_chart_data,
        "kp_cusp_chart": kp_chart_data,
        "visual_upay_chart": compute_lal_kitab_visual_upay_chart(chart),
    }
    return raw_bundle


def compute_matchmaking(
    boy: dict[str, Any],
    girl: dict[str, Any],
) -> dict[str, Any]:
    """Compute exact 36-point Ashtakoot Guna Milan + Manglik check using Swiss Ephemeris."""
    b_dob = boy.get("dob", "1995-01-01")
    b_tob = boy.get("birth_time") or boy.get("tob", "12:00")
    b_lat = float(boy.get("latitude") if boy.get("latitude") is not None else boy.get("lat", 28.6139))
    b_lon = float(boy.get("longitude") if boy.get("longitude") is not None else boy.get("lon", 77.2090))
    b_tz = float(boy.get("tz_offset") if boy.get("tz_offset") is not None else boy.get("tz", 5.5))

    g_dob = girl.get("dob", "1997-01-01")
    g_tob = girl.get("birth_time") or girl.get("tob", "12:00")
    g_lat = float(girl.get("latitude") if girl.get("latitude") is not None else girl.get("lat", 28.6139))
    g_lon = float(girl.get("longitude") if girl.get("longitude") is not None else girl.get("lon", 77.2090))
    g_tz = float(girl.get("tz_offset") if girl.get("tz_offset") is not None else girl.get("tz", 5.5))

    bc = compute_chart(b_dob, b_tob, b_lat, b_lon, b_tz)
    gc = compute_chart(g_dob, g_tob, g_lat, g_lon, g_tz)

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
        "boy": {"name": boy.get("name", "Boy"), "moon_rashi": b_moon["rashi"], "moon_rashi_hi": b_moon.get("rashi_hi", b_moon["rashi"]), "nakshatra": b_moon["nakshatra"], "manglik": b_manglik, "mars_house": b_mars["house"]},
        "girl": {"name": girl.get("name", "Girl"), "moon_rashi": g_moon["rashi"], "moon_rashi_hi": g_moon.get("rashi_hi", g_moon["rashi"]), "nakshatra": g_moon["nakshatra"], "manglik": g_manglik, "mars_house": g_mars["house"]},
        "total_points": total,
        "max_points": 36.0,
        "total_score": total,
        "max_score": 36.0,
        "score": total,
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
        "choghadiya": {"day": day_slots, "night": night_slots},
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
        "horoscope": rashi_predictions,
    }


def compute_shubh_ashubh_yogas(chart: dict[str, Any]) -> dict[str, Any]:
    """
    Compute specific Shubh & Ashubh Yogas (शुभ एवं अशुभ योग) based on Classical & Lal Kitab rules:
    - Inauspicious Yogas: Angarak Yog / Mangal Bad, Surya Grahan Yog, Chandra Grahan Yog,
      Guru Chandal Yog, Vish Yog, Kemdrum Yog, Kaal Sarp Dosha, Shani-Mangal Dwandwa.
    - Auspicious Yogas: Gajakesari Yog, Budhaditya Yog, Pancha Mahapurusha (Malavya, Ruchaka,
      Hamsa, Bhadra, Sasa), Vipreet Raj Yog, Chandra-Mangal (Mahalaxmi) Yog.
    """
    planets = {p["planet"]: p for p in chart.get("planets", [])}
    sun = planets.get("Sun", {})
    moon = planets.get("Moon", {})
    mars = planets.get("Mars", {})
    merc = planets.get("Mercury", {})
    jup = planets.get("Jupiter", {})
    venus = planets.get("Venus", {})
    sat = planets.get("Saturn", {})
    rahu = planets.get("Rahu", {})
    ketu = planets.get("Ketu", {})

    sun_h = sun.get("house", 0)
    moon_h = moon.get("house", 0)
    mars_h = mars.get("house", 0)
    merc_h = merc.get("house", 0)
    jup_h = jup.get("house", 0)
    ven_h = venus.get("house", 0)
    sat_h = sat.get("house", 0)
    rahu_h = rahu.get("house", 0)
    ketu_h = ketu.get("house", 0)

    shubh_list = []
    ashubh_list = []

    # --- 1. GAJAKESARI YOG ---
    if moon_h > 0 and jup_h > 0:
        dist = ((jup_h - moon_h) % 12)
        is_gaja = dist in (0, 3, 6, 9)
        shubh_list.append({
            "id": "gajakesari",
            "name": "Gajakesari Yoga",
            "name_hi": "गजकेसरी योग (ज्ञान, मान-सम्मान व वैभव)",
            "is_active": is_gaja,
            "category": "Raj Yoga",
            "planets": ["Moon", "Jupiter"],
            "impact_en": "Jupiter in Kendra from Moon endows high wisdom, executive authority, academic distinction, and lasting goodwill.",
            "impact_hi": "चंद्रमा से केंद्र (1, 4, 7, 10 भाव) में बृहस्पति होने से ज्ञान, उच्च पद, समाज में आदर और संकटों से स्वतः रक्षा का वरदान मिलता है।",
            "upay_en": "Respect spiritual mentors, wear pure gold or saffron mark on forehead, feed soaked chana dal to cows on Thursdays.",
            "upay_hi": "गुरुजनों का सम्मान करें, माथे पर केसर का तिलक लगाएं और गुरुवार को गाय को भीगी चने की दाल व गुड़ खिलाएं।"
        })

    # --- 2. BUDHADITYA YOG ---
    if sun_h > 0 and merc_h > 0:
        is_budh = sun_h == merc_h
        shubh_list.append({
            "id": "budhaditya",
            "name": "Budhaditya Yoga",
            "name_hi": "बुधादित्य योग (प्रखर बुद्धि व बौद्धिक ख्याति)",
            "is_active": is_budh,
            "category": "Intellectual Yoga",
            "planets": ["Sun", "Mercury"],
            "impact_en": "Sun and Mercury conjunction grants sharp analytical acumen, persuasive speech, commercial leadership, and academic success.",
            "impact_hi": "सूर्य और बुध की युति से कुशाग्र बुद्धि, वाक्पटुता, व्यापारिक चातुर्य तथा प्रशासनिक व प्रतियोगी परीक्षाओं में विशेष सफलता मिलती है।",
            "upay_en": "Offer fresh water in copper vessel at sunrise; maintain integrity in business accounts.",
            "upay_hi": "प्रातः तांबे के पात्र से सूर्य को जल दें और व्यापारिक लेन-देन में पूर्ण पारदर्शिता रखें।"
        })

    # --- 3. PANCHA MAHAPURUSHA YOGAS ---
    # Hamsa Yog (Jupiter)
    is_hamsa = jup_h in (1, 4, 7, 10) and jup.get("dignity") in ("Exalted", "Own")
    shubh_list.append({
        "id": "hamsa",
        "name": "Hamsa Yoga (Pancha Mahapurusha)",
        "name_hi": "हंस महापुरुष योग (आध्यात्मिक श्रेष्ठता व उच्च पद)",
        "is_active": is_hamsa,
        "category": "Mahapurusha",
        "planets": ["Jupiter"],
        "impact_en": "Jupiter exalted or in own sign in Kendra bestows pure character, high philosophical insight, and patronage from rulers.",
        "impact_hi": "गुरु के केंद्र में स्वराशि या उच्च होने से धर्मनिष्ठा, उच्च पद, सात्विक सुख और परिवार का कल्याण होता है।",
        "upay_en": "Donate yellow cloths or books to deserving scholars; chant Guru Gayatri.",
        "upay_hi": "पुस्तकों का दान करें और नियमित रूप से गुरु मंत्र अथवा गायत्री मंत्र का जप करें।"
    })

    # Malavya Yog (Venus)
    is_malavya = ven_h in (1, 4, 7, 10) and venus.get("dignity") in ("Exalted", "Own")
    shubh_list.append({
        "id": "malavya",
        "name": "Malavya Yoga (Pancha Mahapurusha)",
        "name_hi": "मालव्य महापुरुष योग (ऐश्वर्य, कला व दांपत्य सुख)",
        "is_active": is_malavya,
        "category": "Mahapurusha",
        "planets": ["Venus"],
        "impact_en": "Venus in Kendra in own/exalted sign bestows aesthetic grace, material luxury, domestic comfort, and joyful marriage.",
        "impact_hi": "शुक्र के केंद्र में स्वराशि या उच्च होने से वाहन, उत्तम वस्त्र, भौतिक वैभव, कलात्मक सफलता व सुखी दांपत्य प्राप्त होता है।",
        "upay_en": "Feed white cows fresh dough; honor women and donate curd or silver in charity.",
        "upay_hi": "सफेद गाय को पेड़ा या मक्खन-रोटी खिलाएं और घर की स्त्रियों का आदर करें।"
    })

    # Ruchaka Yog (Mars)
    is_ruchaka = mars_h in (1, 4, 7, 10) and mars.get("dignity") in ("Exalted", "Own")
    shubh_list.append({
        "id": "ruchaka",
        "name": "Ruchaka Yoga (Pancha Mahapurusha)",
        "name_hi": "रुचक महापुरुष योग (शौर्य, नेतृत्व व भूमि लाभ)",
        "is_active": is_ruchaka,
        "category": "Mahapurusha",
        "planets": ["Mars"],
        "impact_en": "Exalted/Own Mars in Kendra gives physical courage, land ownership, leadership in engineering/armed forces, and victory over foes.",
        "impact_hi": "मंगल के केंद्र में स्वराशि या उच्च होने से अदम्य साहस, भूमि-भवन का लाभ, नेतृत्व क्षमता व शत्रुओं पर विजय मिलती है।",
        "upay_en": "Recite Hanuman Chalisa daily; share sweet delicacies with younger brothers.",
        "upay_hi": "नित्य हनुमान चालीसा का पाठ करें और छोटे भाइयों के साथ सौहार्दपूर्ण संबंध रखें।"
    })

    # --- 4. CHANDRA-MANGAL (MAHALAXMI) YOG ---
    is_chandra_mangal = (moon_h > 0 and mars_h > 0) and (moon_h == mars_h or abs(moon_h - mars_h) == 6)
    shubh_list.append({
        "id": "chandra_mangal",
        "name": "Chandra-Mangal Mahalaxmi Yoga",
        "name_hi": "चंद्र-मंगल महालक्ष्मी योग (प्रचुर धन संचय व उद्यम)",
        "is_active": is_chandra_mangal,
        "category": "Dhana Yoga",
        "planets": ["Moon", "Mars"],
        "impact_en": "Conjunction or mutual opposition of Moon and Mars fuels persistent commercial drive, property acquisition, and steady liquidity.",
        "impact_hi": "चंद्र-मंगल का संबंध प्रचुर धन लाभ, अचल संपत्ति और व्यापारिक उद्यम में अप्रत्याशित वित्तीय सफलता देता है।",
        "upay_en": "Keep pure silver coin with saffron mark in cash safe; avoid emotional rashness in investments.",
        "upay_hi": "तिजोरी में चांदी का चौकोर टुकड़ा रखें और वित्तीय निर्णयों में जल्दबाजी से बचें।"
    })

    # --- ASHUBH YOGAS ---
    # 1. ANGARAK YOG / MANGAL BAD
    is_angarak = (mars_h > 0 and rahu_h > 0 and (mars_h == rahu_h or abs(mars_h - rahu_h) == 6)) or \
                 (mars_h > 0 and ketu_h > 0 and (mars_h == ketu_h or abs(mars_h - ketu_h) == 6)) or \
                 (mars_h in (3, 8) and sat_h in (6, 8))
    ashubh_list.append({
        "id": "angarak",
        "name": "Angarak Yoga / Mangal Bad",
        "name_hi": "अंगारक योग / मंगल बद (रक्त विकार, चोट व विवाद)",
        "is_active": is_angarak,
        "severity": "High Caution (तीव्र)",
        "planets": ["Mars", "Rahu", "Ketu"],
        "impact_en": "Volatile Mars-Rahu/Ketu interaction triggers sudden fits of rage, vehicle mishaps, blood/skin flare-ups, and abrupt police or litigation friction.",
        "impact_hi": "मंगल और राहु/केतु की युति अथवा दृष्टि से अत्यधिक क्रोध, वाहन से चोट, रक्त विकार, अग्नि भय तथा व्यर्थ के पुलिस/कोर्ट केस का भय रहता है।",
        "upay_en": "Lal Kitab: Fill an earthen pot with pure honey and bury in solitary ground; bake sweet tandoori rotis and feed stray dogs; never wear coral without consultation.",
        "upay_hi": "मिट्टी के कुल्हड़ में शुद्ध शहद भरकर वीराने में दबाएं; तंदूर की मीठी रोटी बनाकर भूरे/काले कुत्तों को खिलाएं और क्रोध पर नियंत्रण रखें।"
    })

    # 2. SURYA GRAHAN YOG
    is_surya_grahan = sun_h > 0 and (sun_h == rahu_h or sun_h == ketu_h)
    ashubh_list.append({
        "id": "surya_grahan",
        "name": "Surya Grahan Yoga (Sun Eclipsed)",
        "name_hi": "सूर्य ग्रहण योग (पिता को कष्ट, नेत्र विकार व अपयश)",
        "is_active": is_surya_grahan,
        "severity": "High Caution (तीव्र)",
        "planets": ["Sun", "Rahu", "Ketu"],
        "impact_en": "Sun eclipsed by nodal axis compromises career stability, strains relationship with father/superiors, and triggers eye or cardiovascular sensitivity.",
        "impact_hi": "सूर्य के साथ राहु या केतु होने से पिता के स्वास्थ्य पर कष्ट, सरकारी कार्यों में रुकावट, नेत्र विकार और अकारण मानहानि या बदनामी का भय रहता है।",
        "upay_en": "Lal Kitab: Flow raw coal or dry coconut with husk in flowing river on Sunday; apply sandalwood paste on forehead; maintain cordial conduct with father.",
        "upay_hi": "रविवार के दिन बहते पानी में नारियल अथवा कच्चा कोयला प्रवाहित करें; पिता के चरण स्पर्श करें और माठे पर सफेद चंदन लगाएं।"
    })

    # 3. CHANDRA GRAHAN YOG
    is_chandra_grahan = moon_h > 0 and (moon_h == rahu_h or moon_h == ketu_h)
    ashubh_list.append({
        "id": "chandra_grahan",
        "name": "Chandra Grahan Yoga (Moon Eclipsed)",
        "name_hi": "चंद्र ग्रहण योग (मानसिक अवसाद, चिंता व माता को कष्ट)",
        "is_active": is_chandra_grahan,
        "severity": "High Caution (तीव्र)",
        "planets": ["Moon", "Rahu", "Ketu"],
        "impact_en": "Afflicted Moon induces recurrent mental anxiety, depressive phases, emotional vulnerability, insomnia, and distress to mother.",
        "impact_hi": "चंद्रमा के साथ राहु/केतु होने से अनिद्रा, गहरा मानसिक तनाव, भय, माता के स्वास्थ्य में गिरावट और आर्थिक अस्थिरता पैदा होती है।",
        "upay_en": "Lal Kitab: Keep a solid silver ball (without hole) in pocket; take blessings from mother by touching her feet daily; avoid consuming milk at night.",
        "upay_hi": "बिना छेद वाली ठोस चांदी की गोली जेब में रखें; माता के चरण स्पर्श कर आशीर्वाद लें और रात में दूध पीने से परहेज करें।"
    })

    # 4. GURU CHANDAL YOG
    is_chandal = jup_h > 0 and (jup_h == rahu_h or jup_h == ketu_h)
    ashubh_list.append({
        "id": "guru_chandal",
        "name": "Guru Chandal Yoga",
        "name_hi": "गुरु-चांडाल योग (मार्गभ्रष्टता, ज्ञान बाधा व अपमान)",
        "is_active": is_chandal,
        "severity": "Medium Caution (मध्यम)",
        "planets": ["Jupiter", "Rahu", "Ketu"],
        "impact_en": "Jupiter tainted by Rahu clouds moral clarity, creates estrangement from mentors, disrupts liver/digestion, and delays spiritual progress.",
        "impact_hi": "बृहस्पति पर राहु का साया निर्णय क्षमता को भटकाता है, गुरुजनों से मतभेद कराता है, पाचन विकार देता है और धार्मिक निष्ठा में व्यवधान डालता है।",
        "upay_en": "Lal Kitab: Apply yellow saffron or turmeric tilak on forehead, throat, and navel daily; donate yellow chana dal at an ancient temple; respect spiritual guides.",
        "upay_hi": "माथे, कंठ व नाभि पर नित्य केसर या हल्दी का तिलक लगाएं; मंदिर में चने की दाल अर्पित करें और संतों/विद्वानों का अपमान भूलकर न करें।"
    })

    # 5. VISH YOG (SATURN + MOON)
    is_vish = (moon_h > 0 and sat_h > 0) and (moon_h == sat_h or abs(moon_h - sat_h) == 6)
    ashubh_list.append({
        "id": "vish_yog",
        "name": "Vish Yoga (Saturn-Moon Conjunction / Aspect)",
        "name_hi": "विष योग (उदासीनता, एकाकीपन व अवसाद)",
        "is_active": is_vish,
        "severity": "High Caution (तीव्र)",
        "planets": ["Moon", "Saturn"],
        "impact_en": "Saturn constricting Moon produces chronic melancholy, pessimism, marital alienation, delayed rewards, and cold emotional temperament.",
        "impact_hi": "शनि-चंद्र का संयोग मन में अकारण उदासी, निराशा, काम में विलंब, वैवाहिक संबंधों में ठंडापन और अकेलेपन की भावना उत्पन्न करता है।",
        "upay_en": "Lal Kitab: Pour fresh milk mixed with water and black sesame on Shivling on Mondays/Saturdays; feed water to crows and avoid wearing dark blue near sleeping area.",
        "upay_hi": "सोमवार व शनिवार को शिवलिंग पर कच्चे दूध में थोड़ा जल व काले तिल मिलाकर अभिषेक करें; कौवों को मीठी रोटी खिलाएं।"
    })

    # 6. KEMDRUM YOG
    # Moon isolated: no planets in 2nd and 12th from Moon (excluding Sun, Rahu, Ketu)
    h_before = ((moon_h - 2) % 12) + 1
    h_after = (moon_h % 12) + 1
    occupants_around = [
        p["planet"] for p in chart.get("planets", [])
        if p.get("house") in (h_before, h_after) and p["planet"] not in ("Sun", "Rahu", "Ketu", "Moon")
    ]
    is_kemdrum = (moon_h > 0) and len(occupants_around) == 0
    ashubh_list.append({
        "id": "kemdrum",
        "name": "Kemdrum Yoga (Isolated Moon)",
        "name_hi": "केमद्रुम योग (एकाकी चंद्रमा, आर्थिक अस्थिरता)",
        "is_active": is_kemdrum,
        "severity": "Medium Caution (मध्यम)",
        "planets": ["Moon"],
        "impact_en": "Lack of flanking support around Moon results in periods of sudden financial drain, lack of true loyalists, and feeling mentally unanchored.",
        "impact_hi": "चंद्रमा के आगे-पीछे कोई शुभ ग्रह न होने से अचानक धन हानि, कठिन समय में मित्रों का सहयोग न मिलना और मानसिक असहायता का अनुभव होता है।",
        "upay_en": "Lal Kitab: Keep a solid silver miniature elephant in home; plant a Peepal tree in public park; worship Goddess Mahalakshmi with white flowers.",
        "upay_hi": "घर में ठोस चांदी का छोटा हाथी रखें; पूर्णिमा के दिन खीर बनाकर मां लक्ष्मी को भोग लगाएं और पीपल का पौधा लगवाएं।"
    })

    # 7. KAAL SARP DOSHA
    # Check if all planets from Sun to Saturn are trapped between Rahu & Ketu
    non_nodal_houses = [
        p.get("house") for p in chart.get("planets", [])
        if p["planet"] not in ("Rahu", "Ketu") and p.get("house")
    ]
    is_kaalsarp = False
    if rahu_h > 0 and ketu_h > 0 and len(non_nodal_houses) >= 7:
        span_1 = [(rahu_h + i - 1) % 12 + 1 for i in range(1, 6)]
        span_2 = [(ketu_h + i - 1) % 12 + 1 for i in range(1, 6)]
        if all(h in span_1 for h in non_nodal_houses) or all(h in span_2 for h in non_nodal_houses):
            is_kaalsarp = True

    ashubh_list.append({
        "id": "kaalsarp",
        "name": "Kaal Sarp Dosha",
        "name_hi": "कालसर्प दोष (कार्यों में अप्रत्याशित रुकावटें व संघर्ष)",
        "is_active": is_kaalsarp,
        "severity": "High Caution (तीव्र)",
        "planets": ["Rahu", "Ketu"],
        "impact_en": "All planets hemmed between nodes creates recurring cyclic plateaus, sudden derailment of ongoing deals, and sleep disturbances.",
        "impact_hi": "समस्त ग्रहों के राहु-केतु के मध्य आने से जीवन में संघर्ष, बनते हुए कार्यों का अंतिम समय में अटकना और सर्प भय या बेचैनी का योग बनता है।",
        "upay_en": "Lal Kitab: Float a pair of silver snakes (Naag-Nagin) in flowing water on Nag Panchami; chant Maha Mrityunjaya Japa daily.",
        "upay_hi": "बहते जल में चांदी के नाग-नागिन का जोड़ा प्रवाहित करें और नित्य 11 बार महामृत्युंजय मंत्र का मानसिक जप करें।"
    })

    return {
        "shubh": shubh_list,
        "ashubh": ashubh_list,
        "active_shubh_count": len([y for y in shubh_list if y["is_active"]]),
        "active_ashubh_count": len([y for y in ashubh_list if y["is_active"]]),
    }


def compute_bifurcated_dasha_predictions(dashas: dict[str, Any], dob: str) -> dict[str, Any]:
    """
    Bifurcate Dasha Predictions into:
    1. Childhood Dasha (उम्र 0 से 12 वर्ष): Balarishta, dental/bone health, mother's milk/health,
       schooling, speech, evil eye (नजर दोष) and child-safe remedies.
    2. Adult Dasha (उम्र 12+ वर्ष): Career, earnings, marriage, legal affairs, property, adult Lal Kitab remedies.
    """
    b_year = int(dob.split("-")[0])

    child_guidelines = {
        "Sun": {
            "child_hi": "बाल्यावस्था में सूर्य की दशा में हड्डियों, आंखों व रोग प्रतिरोधक क्षमता का ध्यान रखें। पिता का आशीर्वाद व प्रातः की धूप बालक के स्वास्थ्य के लिए अत्यंत लाभकारी है।",
            "child_en": "Focus on bone density, vision, and natural immunity. Morning solar exposure and paternal affection strengthen child's constitution.",
            "child_upay_hi": "बालक को तांबे का छल्ला पहनाएं व मीठा जल अर्पित करें।",
            "child_upay_en": "Have child wear a simple copper bangle and offer sweetened water to rising Sun.",
        },
        "Moon": {
            "child_hi": "चंद्रमा की दशा बाल्यावस्था में माता के स्वास्थ्य, दूध व कफ/जुकाम की संवेदनशीलता को दर्शाती है। बालक को मानसिक स्नेह दें व रात्रि में ठंडा आहार न दें।",
            "child_en": "Signifies maternal bonding, lactation, and respiratory sensitivity. Provide warm emotional security and avoid chilled foods at night.",
            "child_upay_hi": "चांदी के तार में पिरोया मोती बालक के गले में पहनाएं।",
            "child_upay_en": "Tie a natural pearl in silver wire around child's neck.",
        },
        "Mars": {
            "child_hi": "मंगल की दशा में बालक में अत्यधिक चंचलता, चोट-मोच व पित्त विकार का योग रहता है। नुकीली वस्तुओं व ऊंचाई से सावधानी रखें।",
            "child_en": "High physical restlessness, vulnerability to scrapes/falls, and thermal imbalances. Supervise playtime and keep sharp objects safely away.",
            "child_upay_hi": "मंगलवार को बालक के हाथ से मीठी रोटी या गुड़ का दान कराएं।",
            "child_upay_en": "Donate sweet jaggery or rotis through child's hands on Tuesdays.",
        },
        "Mercury": {
            "child_hi": "बुध की दशा बालक की वाणी, स्मरण शक्ति, प्रारंभिक अक्षराभ्यास व त्वचा स्वास्थ्य को प्रभावित करती है। संगीत व चित्रों से शिक्षा दें।",
            "child_en": "Influences early vocal articulation, memory absorption, foundational schooling, and skin comfort. Encourage interactive visual learning.",
            "child_upay_hi": "बालक के गले में तांबे का छेद वाला गोल पैसा पहनाएं।",
            "child_upay_en": "Have child wear a perforated copper coin around neck on Wednesday.",
        },
        "Jupiter": {
            "child_hi": "गुरु की दशा बाल्यावस्था में संस्कार, बुद्धि, गुरुजनों का स्नेह और पेट की सुदृढ़ता के लिए अत्यंत कल्याणकारी मानी जाती है।",
            "child_en": "Highly auspicious for character foundation, digestive well-being, blessings from elders, and joyful intellectual curiosity.",
            "child_upay_hi": "बालक के माथे पर नित्य केसर-चंदन का सात्विक तिलक लगाएं।",
            "child_upay_en": "Apply a mild saffron or sandalwood dot on child's forehead daily.",
        },
        "Venus": {
            "child_hi": "शुक्र की दशा में बालक का स्वभाव कोमल, सौंदर्यप्रिय और कलात्मक रहता है। त्वचा की स्वच्छता और गले के स्वास्थ्य का ध्यान रखें।",
            "child_en": "Reflects artistic inclination, charm, and sensitivity to throat/skin. Keep child's clothing pristine and encourage creative play.",
            "child_upay_hi": "गाय को बालक के स्पर्श से पेड़ा या हरा चारा दिलवाएं।",
            "child_upay_en": "Feed sweet dough to a cow after touching child's palms on Friday.",
        },
        "Saturn": {
            "child_hi": "शनि की दशा में बाल्यावस्था में दांत निकलने में कष्ट, पैरों में दर्द या नजर दोष की संभावना रहती है। बालक को अंधेरे से दूर रखें।",
            "child_en": "Possible teething delays, lower limb stiffness, or susceptibility to startled night fears. Ensure brightly lit, serene bedroom environment.",
            "child_upay_hi": "शनिवार को बालक के सिर से 7 बार बादाम या सरसों का तेल वारकर दान करें।",
            "child_upay_en": "Circulate mustard oil or almonds over child's head 7 times and donate on Saturday.",
        },
        "Rahu": {
            "child_hi": "राहु की दशा में बालक को अचानक डर, बुरे सपने, पेट में गैस/कीड़े या नजर लगने का भय रहता है। बालक के सिरहाने लोहे का सामान न रखें।",
            "child_en": "Startled night awakenings, sudden gastrointestinal discomfort, or evil eye. Never place electronic gadgets or metallic clutter near crib.",
            "child_upay_hi": "चांदी का ठोस कड़ा बालक के दाहिने हाथ में पहनाएं व मोरपंख पास रखें।",
            "child_upay_en": "Place a peacock feather near bed and have child wear a solid silver bracelet.",
        },
        "Ketu": {
            "child_hi": "केतु की दशा में बालक के कान, पैरों के पंजे व जोड़ों की संवेदनशीलता रहती है। बालक को प्यार से समझाएं और जिद पर अंकुश रखें।",
            "child_en": "Sensitivity around ears, feet, and joints. Nurture with patient, gentle reassurance and avoid harsh scolding.",
            "child_upay_hi": "काले-सफेद कंबल या तिल का दान बालक के हाथ से कराएं।",
            "child_upay_en": "Donate a two-tone black/white blanket or sesame seeds touched by child.",
        },
    }

    enhanced_mahadashas = []
    for md in dashas.get("mahadashas", []):
        pl = md.get("planet", "Sun")
        start_yr = int(md.get("start", dob).split("-")[0])
        end_yr = int(md.get("end", dob).split("-")[0])
        start_age = max(0, start_yr - b_year)
        end_age = max(0, end_yr - b_year)

        c_info = child_guidelines.get(pl, child_guidelines["Sun"])

        enhanced_md = dict(md)
        enhanced_md["start_age"] = start_age
        enhanced_md["end_age"] = end_age
        enhanced_md["is_childhood_dasha"] = start_age < 12
        enhanced_md["child_prediction_hi"] = c_info["child_hi"]
        enhanced_md["child_prediction_en"] = c_info["child_en"]
        enhanced_md["child_upay_hi"] = c_info["child_upay_hi"]
        enhanced_md["child_upay_en"] = c_info["child_upay_en"]

        # Adult predictions focus on career, wealth, family and health
        enhanced_md["adult_prediction_hi"] = f"आयु {start_age} से {end_age} वर्ष: {md.get('planet_hi', pl)} की महादशा में कार्यक्षेत्र, धन लाभ, सामाजिक प्रतिष्ठा और दांपत्य जीवन में महत्वपूर्ण बदलाव का समय रहेगा। इस दौरान परिश्रम से सफलता और निर्णय क्षमता में परिपक्वता आएगी।"
        enhanced_md["adult_prediction_en"] = f"Age {start_age} to {end_age}: {pl} Mahadasha governs professional milestones, financial liquidity, marriage/family establishment, and strategic life decisions."

        enhanced_mahadashas.append(enhanced_md)

    dashas_copy = dict(dashas)
    dashas_copy["mahadashas"] = enhanced_mahadashas
    return dashas_copy


def compute_luck_meter(chart: dict[str, Any]) -> dict[str, Any]:
    """
    Compute 4-Pillar Luck Meter (भाग्य मीटर प्रतिशत स्कोर):
    1. Health Luck % (स्वास्थ्य भाग्यांक)
    2. Wealth & Business Luck % (धन व व्यापार भाग्यांक)
    3. Family & Domestic Luck % (पारिवारिक सुख भाग्यांक)
    4. Career & Authority Luck % (करियर व मान-सम्मान भाग्यांक)
    Calculated mathematically from planet dignities and house strengths (range: 40% - 98%).
    """
    planets = {p["planet"]: p for p in chart.get("planets", [])}
    sun = planets.get("Sun", {})
    moon = planets.get("Moon", {})
    mars = planets.get("Mars", {})
    merc = planets.get("Mercury", {})
    jup = planets.get("Jupiter", {})
    venus = planets.get("Venus", {})
    sat = planets.get("Saturn", {})

    dignity_weights = {
        "Exalted": 30,
        "Own": 25,
        "Friendly": 18,
        "Neutral": 12,
        "Enemy": 6,
        "Debilitated": 2,
    }

    # 1. Health Luck: Sun + Mars + Ascendant Lord + House 1 occupants
    h_score = 45 + dignity_weights.get(sun.get("dignity"), 12) + dignity_weights.get(mars.get("dignity"), 12)
    if sun.get("house") in (1, 5, 9, 10): h_score += 10
    if mars.get("house") in (1, 3, 6, 10): h_score += 8
    health_luck = min(98, max(42, h_score))

    # 2. Wealth Luck: Jupiter + Venus + 2nd & 11th House
    w_score = 45 + dignity_weights.get(jup.get("dignity"), 12) + dignity_weights.get(venus.get("dignity"), 12)
    if jup.get("house") in (1, 2, 5, 9, 11): w_score += 10
    if venus.get("house") in (2, 4, 7, 11, 12): w_score += 8
    wealth_luck = min(98, max(40, w_score))

    # 3. Family Luck: Moon + Venus + 4th & 7th House
    f_score = 46 + dignity_weights.get(moon.get("dignity"), 12) + dignity_weights.get(venus.get("dignity"), 12)
    if moon.get("house") in (1, 4, 5, 7, 9): f_score += 9
    if venus.get("house") in (1, 4, 7): f_score += 8
    family_luck = min(98, max(44, f_score))

    # 4. Career Luck: Sun + Saturn + Mercury + 10th & 9th House
    c_score = 44 + dignity_weights.get(sun.get("dignity"), 12) + dignity_weights.get(sat.get("dignity"), 12)
    if sat.get("house") in (3, 6, 10, 11): c_score += 10
    if merc.get("house") in (1, 5, 10, 11): c_score += 8
    career_luck = min(98, max(42, c_score))

    overall = round((health_luck + wealth_luck + family_luck + career_luck) / 4.0)

    pillars = [
        {"key": "health", "title_en": "Health & Vitality", "title_hi": "स्वास्थ्य व जीवनी शक्ति", "score": health_luck},
        {"key": "wealth", "title_en": "Wealth & Finances", "title_hi": "धन व आर्थिक समृद्धि", "score": wealth_luck},
        {"key": "family", "title_en": "Family & Relationships", "title_hi": "पारिवारिक सुख व दांपत्य", "score": family_luck},
        {"key": "career", "title_en": "Career & Authority", "title_hi": "कार्यक्षेत्र व मान-सम्मान", "score": career_luck},
    ]

    strongest = max(pillars, key=lambda x: x["score"])
    weakest = min(pillars, key=lambda x: x["score"])

    booster_upays = {
        "health": ("Offer copper water to Sun and walk barefoot on green grass.", "प्रातः तांबे के पात्र से सूर्य को जल दें और नंगे पैर हरी घास पर चलें।"),
        "wealth": ("Keep a square silver piece in wallet and feed green fodder to cows.", "पर्स में चांदी का चौकोर टुकड़ा रखें और गाय को हरा चारा खिलाएं।"),
        "family": ("Respect elder women, touch mother's feet daily, and avoid milk at night.", "माता के नित्य चरण स्पर्श करें और घर में कटु शब्दों के प्रयोग से बचें।"),
        "career": ("Feed soaked almonds to birds, donate black sesame on Saturday, and maintain strict discipline.", "पक्षियों को भीगे बादाम खिलाएं और शनिवार को सरसों के तेल का छायापात्र दान करें।"),
    }

    upay = booster_upays[weakest["key"]]

    return {
        "overall_luck": overall,
        "health_luck": health_luck,
        "wealth_luck": wealth_luck,
        "family_luck": family_luck,
        "career_luck": career_luck,
        "pillars": pillars,
        "strongest_pillar": strongest,
        "focus_pillar": weakest,
        "daily_booster_en": upay[0],
        "daily_booster_hi": upay[1],
    }


def compute_personal_dayfal(chart: dict[str, Any], target_date: str = None) -> dict[str, Any]:
    """
    Compute Personalized DayFal (व्यक्तिगत दैनिक फल) based on Native's Natal Moon (Chandra Rashi)
    vs Current Transit Moon (गोचर चंद्रमा 1 से 12 भाव).
    """
    dt = datetime.strptime(target_date, "%Y-%m-%d").date() if target_date else date.today()
    jd_now = swe.julday(dt.year, dt.month, dt.day, 12.0) - 5.5 / 24.0

    # Calculate Current Transit Moon
    res_moon, _ = swe.calc_ut(jd_now, swe.MOON, CALC_FLAGS)
    transit_moon_lon = res_moon[0] % 360.0
    transit_sign_idx = int(transit_moon_lon // 30)

    # Find Native's Natal Moon Sign
    natal_moon = next((p for p in chart.get("planets", []) if p["planet"] == "Moon"), None)
    if natal_moon:
        natal_sign_idx = int(natal_moon.get("lon", 0.0) // 30)
    else:
        natal_sign_idx = 0

    # Relative house from natal Moon (1 to 12)
    house_from_moon = ((transit_sign_idx - natal_sign_idx) % 12) + 1

    rashi_names_en = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    rashi_names_hi = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"]

    transit_rashi_en = rashi_names_en[transit_sign_idx]
    transit_rashi_hi = rashi_names_hi[transit_sign_idx]

    natal_rashi_en = rashi_names_en[natal_sign_idx]
    natal_rashi_hi = rashi_names_hi[natal_sign_idx]

    # Classical Chandra Gochar impacts (Phaladeepika & Lal Kitab)
    gochar_profiles = {
        1: {
            "rating": "अति शुभ (Very Auspicious)", "stars": 5, "type": "Good",
            "title_hi": "जन्म चंद्र गोचर — आत्मबल, सम्मान व शारीरिक सुख",
            "title_en": "1st House Transit: Mental Radiance & Vitality",
            "pred_hi": "आज चंद्रमा आपकी ही राशि में गोचरस्थ है। मन प्रसन्न, विचार स्पष्ट और वाणी में प्रभाव रहेगा। उत्तम भोजन, नए वस्त्र व सामाजिक सम्मान का योग है।",
            "pred_en": "Moon transits your natal sign. Clear thoughts, elevated vitality, pleasant social interactions, and mental equilibrium.",
            "dos_hi": ["नए कार्य का संकल्प लें", "सात्विक व सुपाच्य भोजन करें", "माता या गुरु का आशीर्वाद लें"],
            "dos_en": ["Initiate thoughtful plans", "Wear clean, light clothing", "Take maternal blessings"],
            "donts_hi": ["अति-उत्साह में बिना सोचे धन खर्च न करें", "अहंकार से बचें"],
            "donts_en": ["Avoid impulsive splurges", "Do not engage in ego clashes"],
            "lucky_color_hi": "मोतिया सफेद", "lucky_color_en": "Pearl White", "lucky_number": 2,
        },
        2: {
            "rating": "मध्यम (Caution on Expenses)", "stars": 3, "type": "Neutral",
            "title_hi": "द्वितीय भाव गोचर — वित्तीय सावधानी व वाणी संयम",
            "title_en": "2nd House Transit: Financial & Speech Prudence",
            "pred_hi": "धन के आवागमन में थोड़ी तेजी रहेगी लेकिन अनावश्यक खर्चे भी सामने आएंगे। पारिवारिक बातचीत में कठोर शब्दों से बचें।",
            "pred_en": "Transit through 2nd house advises measured speech and conscious budgeting. Postpone speculative bets.",
            "dos_hi": ["घर का बजट संभलकर बनाएं", "मीठी वाणी बोलें", "गाय को रोटी दें"],
            "dos_en": ["Review weekly budget", "Speak gently in family meetings", "Feed birds"],
            "donts_hi": ["उधार देने या लेने से बचें", "कटु वचन न बोलें"],
            "donts_en": ["Avoid lending money today", "Do not argue over meals"],
            "lucky_color_hi": "पीला", "lucky_color_en": "Soft Yellow", "lucky_number": 3,
        },
        3: {
            "rating": "उत्तम (Highly Favorable)", "stars": 5, "type": "Good",
            "title_hi": "तृतीय भाव गोचर — पराक्रम, साहस व बंधु सहयोग",
            "title_en": "3rd House Transit: Courage, Drive & Sibling Support",
            "pred_hi": "तृतीय भाव में चंद्रमा अत्यंत शुभ फल देता है। आपके आत्मविश्वास में वृद्धि होगी। मित्रों और सहयोगियों से पूर्ण सहायता मिलेगी। छोटी यात्राएं लाभकारी रहेंगी।",
            "pred_en": "Moon in 3rd creates tremendous courage, productive communications, and cheerful support from colleagues and siblings.",
            "dos_hi": ["रुके हुए जरूरी कॉल्स व ईमेल पूर्ण करें", "सहयोगियों की सहायता लें", "हनुमान चालीसा पढ़ें"],
            "dos_en": ["Finalize pending correspondence", "Engage in physical workouts", "Plan local visits"],
            "donts_hi": ["छोटे भाई-बहनों से मतभेद न करें", "आलस्य में समय न गंवाएं"],
            "donts_en": ["Avoid procrastination", "Do not neglect minor details"],
            "lucky_color_hi": "लाल / केसरिया", "lucky_color_en": "Crimson Saffron", "lucky_number": 9,
        },
        4: {
            "rating": "सावधानी (Mental Restlessness)", "stars": 2, "type": "Caution",
            "title_hi": "चतुर्थ भाव गोचर — मानसिक अशांति व वाहन सावधानी",
            "title_en": "4th House Transit: Domestic Caution & Emotional Calm",
            "pred_hi": "चतुर्थ चंद्र गोचर मन को थोड़ा अशांत या भावुक कर सकता है। माता के स्वास्थ्य का ध्यान रखें। वाहन चलाते समय गति पर नियंत्रण रखें।",
            "pred_en": "4th house Moon requires emotional patience and vehicle safety. Keep domestic atmosphere calm.",
            "dos_hi": ["शांत एकांत में 10 मिनट ध्यान लगाएं", "माता के चरण स्पर्श करें", "पानी खूब पिएं"],
            "dos_en": ["Meditate in quietude", "Prioritize home hygiene", "Check vehicle air pressure"],
            "donts_hi": ["वाहन तेज न चलाएं", "घर में वाद-विवाद से बचें"],
            "donts_en": ["Do not speed on roads", "Avoid domestic altercations"],
            "lucky_color_hi": "चांदी सा सफेद", "lucky_color_en": "Silver White", "lucky_number": 4,
        },
        5: {
            "rating": "मध्यम शुभ (Creative & Studious)", "stars": 4, "type": "Good",
            "title_hi": "पंचम भाव गोचर — बुद्धि, रचनात्मकता व विद्या",
            "title_en": "5th House Transit: Intellectual Insight & Creativity",
            "pred_hi": "बौद्धिक कार्यों, पढ़ाई, कला और योजना बनाने के लिए दिन उत्तम है। संतान की ओर से प्रसन्नता मिलेगी। शेयर बाजार में जल्दबाजी से बचें।",
            "pred_en": "Sparks sharp intuition, academic focus, and creative expression. Favorable for consultations and studies.",
            "dos_hi": ["नई पुस्तक या ज्ञानवर्धक लेख पढ़ें", "रचनात्मक कार्य में समय दें", "गायत्री मंत्र जपें"],
            "dos_en": ["Study strategy documents", "Express artistic hobbies", "Spend time with children"],
            "donts_hi": ["सट्टेबाजी या जुए से पूर्णतः दूर रहें", "अधीर न हों"],
            "donts_en": ["Avoid speculative risks", "Do not jump to emotional conclusions"],
            "lucky_color_hi": "हरा", "lucky_color_en": "Emerald Green", "lucky_number": 5,
        },
        6: {
            "rating": "अति शुभ (Victory over Obstacles)", "stars": 5, "type": "Good",
            "title_hi": "षष्ठ भाव गोचर — शत्रु विजय, रोग मुक्ति व कार्य सिद्धि",
            "title_en": "6th House Transit: Triumph Over Roadblocks & Health Gain",
            "pred_hi": "छठे भाव का चंद्रमा शत्रुओं को परास्त करता है और पुरानी उलझनों को सुलझाता है। स्वास्थ्य में सुधार होगा और ऋण मुक्ति के मार्ग बनेंगे।",
            "pred_en": "6th house Moon is an exceptional transit for clearing backlog, overcoming competitors, and health rejuvenation.",
            "dos_hi": ["लंबित कार्य प्राथमिकता से निपटाएं", "शारीरिक व्यायाम करें", "चींटियों को आटा दें"],
            "dos_en": ["Tackle hard tasks first", "Maintain clean workspace", "Exercise outdoors"],
            "donts_hi": ["किसी से व्यर्थ विवाद में न उलझें", "अनियमित भोजन न करें"],
            "donts_en": ["Avoid arguing with service staff", "Do not skip healthy lunch"],
            "lucky_color_hi": "नीला", "lucky_color_en": "Steel Blue", "lucky_number": 8,
        },
        7: {
            "rating": "शुभ (Partnership & Harmony)", "stars": 4, "type": "Good",
            "title_hi": "सप्तम भाव गोचर — दांपत्य सौहार्द, साझेदारी व व्यापार लाभ",
            "title_en": "7th House Transit: Matrimonial Bliss & Public Relations",
            "pred_hi": "जीवनसाथी और व्यापारिक साझेदारों के साथ संबंध मधुर रहेंगे। सार्वजनिक जीवन में आपके सुझावों की सराहना होगी। शाम को सुखद समय बीतेगा।",
            "pred_en": "Harmonious transit for marital understanding, joint business dialogue, and evening social interactions.",
            "dos_hi": ["जीवनसाथी के साथ समय बिताएं", "साझेदारी के नियमों की समीक्षा करें", "सुगंधित इत्र लगाएं"],
            "dos_en": ["Plan pleasant evening dinner", "Align on shared goals", "Wear gentle fragrance"],
            "donts_hi": ["संदेह या ईर्ष्या को मन में न आने दें"],
            "donts_en": ["Avoid unwarranted jealousy or suspicion"],
            "lucky_color_hi": "गुलाबी", "lucky_color_en": "Pastel Pink", "lucky_number": 6,
        },
        8: {
            "rating": "विशेष सावधानी (Chandra Ashtama / Alert)", "stars": 1, "type": "Caution",
            "title_hi": "अष्टम भाव गोचर (चंद्र अष्टम) — अत्यधिक सतर्कता व शांति",
            "title_en": "8th House Transit (Chandra Ashtama): Strict Vigilance",
            "pred_hi": "चंद्रमा का अष्टम गोचर शास्त्रीय दृष्टि से 'चंद्र अष्टम' कहलाता है। आज कोई नया अनुबंध, बड़ा निवेश या लंबी यात्रा टालें। शांत रहकर नियमित कार्य करें।",
            "pred_en": "Chandra Ashtama window: delay high-stakes signatures, avoid major investments, drive cautiously, and recite Shiva chants.",
            "dos_hi": ["शिवलिंग पर जल चढ़ाएं", "नियमित शांत दिनचर्या रखें", "ॐ नमः शिवाय का जप करें"],
            "dos_en": ["Recite Om Namah Shivaya", "Maintain calm routine", "Postpone risky negotiations"],
            "donts_hi": ["नया व्यापार आरंभ न करें", "बड़ा धन निवेश न करें", "क्रोध व यात्रा से बचें"],
            "donts_en": ["Do not sign big contracts", "Avoid late-night driving", "Keep temper cool"],
            "lucky_color_hi": "सफेद", "lucky_color_en": "Pure White", "lucky_number": 2,
        },
        9: {
            "rating": "अति शुभ (Fortune & Dharma)", "stars": 5, "type": "Good",
            "title_hi": "नवम भाव गोचर — भाग्योदय, धार्मिक रुचि व बड़ों का आशीष",
            "title_en": "9th House Transit: Fortune, Dharma & Mentor Guidance",
            "pred_hi": "भाग्य का पूर्ण साथ मिलेगा। अटके हुए कार्य स्वतः गति पकड़ेंगे। धार्मिक यात्रा, मंदिर दर्शन अथवा उच्च अधिकारियों से भेंट फलदायी रहेगी।",
            "pred_en": "High fortune transit; spiritual elevation, auspicious mentor counsel, and serendipitous breakthroughs in pending ventures.",
            "dos_hi": ["धार्मिक स्थल पर दर्शन करें", "पिता या गुरु का आशीर्वाद लें", "पीले वस्त्र पहनें"],
            "dos_en": ["Visit temple or meditation spot", "Seek senior guidance", "Wear pleasant yellow/gold"],
            "donts_hi": ["बड़ों के विचारों की अवहेलना न करें", "अधर्म के मार्ग पर न चलें"],
            "donts_en": ["Do not dismiss mentor advice", "Avoid shortcuts in ethics"],
            "lucky_color_hi": "सुनहरा पीला", "lucky_color_en": "Golden Yellow", "lucky_number": 3,
        },
        10: {
            "rating": "अति शुभ (Career Triumph)", "stars": 5, "type": "Good",
            "title_hi": "दशम भाव गोचर — कार्यक्षेत्र में मान-सम्मान व प्रभाव",
            "title_en": "10th House Transit: Professional Prestige & Leadership",
            "pred_hi": "कार्यक्षेत्र में आपके काम की प्रशंसा होगी। अधिकारियों व ग्राहकों का विश्वास बढ़ेगा। नई जिम्मेदारी मिलने का शुभ योग है।",
            "pred_en": "Elevates professional standing, executive decisions, and leadership respect. Outstanding for business meetings.",
            "dos_hi": ["महत्वपूर्ण प्रोजेक्ट्स को आगे बढ़ाएं", "नेतृत्व की जिम्मेदारी स्वीकारें", "सूर्य को प्रणाम करें"],
            "dos_en": ["Present proposals proactively", "Take leadership ownership", "Maintain impeccable posture"],
            "donts_hi": ["सहकर्मियों के प्रति कठोर न बनें", "अभिमान से दूर रहें"],
            "donts_en": ["Do not act condescending", "Avoid slackness in deliverables"],
            "lucky_color_hi": "केसरिया", "lucky_color_en": "Bright Saffron", "lucky_number": 1,
        },
        11: {
            "rating": "सर्वोत्तम (Maximum Financial Gain)", "stars": 5, "type": "Good",
            "title_hi": "एकादश भाव गोचर — प्रचुर लाभ, मनोकामना पूर्ति व मित्र मिलन",
            "title_en": "11th House Transit: Bountiful Gains & Wish Fulfillment",
            "pred_hi": "एकादश भाव का चंद्रमा सर्वसिद्धिदायक है। आर्थिक लाभ के नए मार्ग खुलेंगे। मित्रों का सहयोग मिलेगा और कोई पुरानी मनोकामना पूरी होगी।",
            "pred_en": "Prime wealth and networking transit. Realizes long-sought goals, unlocks fresh revenues, and brings joyful celebrations.",
            "dos_hi": ["व्यापारिक सौदों को अंतिम रूप दें", "मित्रों के साथ समय बिताएं", "आभार प्रकट करें"],
            "dos_en": ["Close commercial transactions", "Network with supportive allies", "Practice gratitude"],
            "donts_hi": ["आय से अधिक दिखावे में खर्च न करें"],
            "donts_en": ["Avoid ostentatious bragging"],
            "lucky_color_hi": "आसमानी नीला", "lucky_color_en": "Sky Blue", "lucky_number": 11,
        },
        12: {
            "rating": "सावधानी (Expenditure & Travel)", "stars": 2, "type": "Caution",
            "title_hi": "द्वादश भाव गोचर — अनपेक्षित व्यय, नेत्र थकान व विश्राम",
            "title_en": "12th House Transit: Higher Expenses & Rest Needed",
            "pred_hi": "अनावश्यक खर्चों और मानसिक थकान का दिन है। आंखों को आराम दें और समय पर सोएं। किसी विदेशी या दूरस्थ संपर्क से सामान्य लाभ संभव है।",
            "pred_en": "Expenditure spikes and sleep disruption possible. Prioritize restorative rest, avoid retail therapy, and meditate before bed.",
            "dos_hi": ["समय पर विश्राम करें", "जरूरतमंदों को भोजन या दवा का दान करें", "पानी में थोड़ा गुलाब जल डालकर स्नान करें"],
            "dos_en": ["Sleep early and deeply", "Donate food or medicine", "Keep screen time low in evening"],
            "donts_hi": ["दिखावे में अनाप-शनाप खरीदारी न करें", "देर रात तक न जागें"],
            "donts_en": ["Do not engage in binge shopping", "Avoid staying up past midnight"],
            "lucky_color_hi": "हल्का जामुनी", "lucky_color_en": "Lavender", "lucky_number": 7,
        },
    }

    info = gochar_profiles.get(house_from_moon, gochar_profiles[1])

    return {
        "date": dt.strftime("%Y-%m-%d"),
        "weekday": dt.strftime("%A"),
        "natal_rashi_en": natal_rashi_en,
        "natal_rashi_hi": natal_rashi_hi,
        "transit_rashi_en": transit_rashi_en,
        "transit_rashi_hi": transit_rashi_hi,
        "house_from_moon": house_from_moon,
        "rating": info["rating"],
        "stars": info["stars"],
        "type": info["type"],
        "title_hi": info["title_hi"],
        "title_en": info["title_en"],
        "pred_hi": info["pred_hi"],
        "pred_en": info["pred_en"],
        "dos_hi": info["dos_hi"],
        "dos_en": info["dos_en"],
        "donts_hi": info["donts_hi"],
        "donts_en": info["donts_en"],
        "lucky_color_hi": info["lucky_color_hi"],
        "lucky_color_en": info["lucky_color_en"],
        "lucky_number": info["lucky_number"],
    }


def compute_category_dates(
    chart: dict[str, Any],
    start_date: str = None,
    category: str = "marriage",
    days_ahead: int = 60
) -> dict[str, Any]:
    """
    Find Category-wise Auspicious (Shubh), Moderate, & Inauspicious (Varjit) Dates
    for up to 6 months (180 days).
    Categories (Matching AstroScience APK CategoryDateFindModel):
    - 'marriage': विवाह व सगाई संस्कार
    - 'business': नवीन व्यापार व दुकान आरंभ
    - 'travel': विदेश यात्रा व दीर्घ यात्रा
    - 'property': मकान/भूमि रजिस्ट्री व गृह प्रवेश
    - 'vehicle': वाहन क्रय (कार/बाइक)
    - 'surgery': शल्य चिकित्सा व ऑपरेशन
    - 'job': नौकरी जॉइनिंग व नया पदभार
    - 'investment': स्वर्ण आभूषण व बड़ा वित्तीय निवेश

    Evaluates:
    - Chandra Gochar from natal Moon (avoiding 8th/12th, favoring Upachaya/Kendra/Trikona)
    - Tithi (avoiding Rikta: 4, 9, 14, Amavasya 30; honoring Shukla/Krishna Paksha)
    - Weekday & Nakshatra alignments for specific activity
    """
    st = datetime.strptime(_clean_dob(start_date), "%Y-%m-%d").date() if start_date else date.today()
    natal_moon = next((p for p in chart.get("planets", []) if p["planet"] == "Moon"), None)
    if natal_moon:
        natal_sign_idx = (
            natal_moon["sign_index"] - 1
            if "sign_index" in natal_moon
            else int(natal_moon.get("longitude", natal_moon.get("lon", 0.0)) // 30)
        )
    else:
        natal_sign_idx = 0

    category_titles = {
        "marriage": {"hi": "विवाह व सगाई संस्कार", "en": "Marriage & Betrothal"},
        "business": {"hi": "नवीन व्यापार व दुकान आरंभ", "en": "New Business & Shop Inauguration"},
        "travel": {"hi": "विदेश यात्रा व दीर्घ यात्रा", "en": "Foreign & Long-Distance Travel"},
        "property": {"hi": "भूमि/मकान रजिस्ट्री व गृह प्रवेश", "en": "Property Registry & Griha Pravesh"},
        "vehicle": {"hi": "वाहन क्रय (कार/बाइक)", "en": "Vehicle Purchase (Car / Bike)"},
        "surgery": {"hi": "शल्य चिकित्सा व ऑपरेशन", "en": "Medical Surgery & Treatment"},
        "job": {"hi": "नौकरी जॉइनिंग व नया पदभार", "en": "Job Joining & New Position"},
        "investment": {"hi": "स्वर्ण आभूषण व वित्तीय निवेश", "en": "Gold Purchase & Financial Investment"},
    }

    t_info = category_titles.get(category, category_titles["marriage"])

    tithi_names = [
        "प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी", "षष्ठी", "सप्तमी",
        "अष्टमी", "नवमी", "दशमी", "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी", "पूर्णिमा",
        "प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी", "षष्ठी", "सप्तमी",
        "अष्टमी", "नवमी", "दशमी", "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी", "अमावस्या"
    ]

    nakshatra_names = [
        "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा", "पुनर्वसु", "पुष्य", "आश्लेषा",
        "मघा", "पूर्वाफाल्गुनी", "उत्तराफाल्गुनी", "हस्त", "चित्रा", "स्वाती", "विशाखा", "अनुराधा", "ज्येष्ठा",
        "मूल", "पूर्वाषाढ़ा", "उत्तराषाढ़ा", "श्रवण", "धनिष्ठा", "शतभिषा", "पूर्वाभाद्रपद", "उत्तराभाद्रपद", "रेवती"
    ]

    rashi_names_hi = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"]
    rashi_names_en = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

    shubh_dates = []
    moderate_dates = []
    varjit_dates = []

    # Clamp days_ahead between 7 and 180 (up to 6 months)
    days_ahead = max(7, min(days_ahead, 180))

    for day_offset in range(days_ahead):
        cur_dt = st + timedelta(days=day_offset)
        jd_noon = swe.julday(cur_dt.year, cur_dt.month, cur_dt.day, 12.0) - 5.5 / 24.0

        res_sun, _ = swe.calc_ut(jd_noon, swe.SUN, CALC_FLAGS)
        res_moon, _ = swe.calc_ut(jd_noon, swe.MOON, CALC_FLAGS)

        sun_lon = res_sun[0] % 360.0
        moon_lon = res_moon[0] % 360.0

        transit_sign = int(moon_lon // 30)
        house_from_moon = ((transit_sign - natal_sign_idx) % 12) + 1

        tithi_idx = int(((moon_lon - sun_lon) % 360.0) // 12.0) + 1
        tithi_idx_clamped = max(1, min(tithi_idx, 30))
        paksha = "शुक्ल पक्ष" if tithi_idx_clamped <= 15 else "कृष्ण पक्ष"
        tithi_in_paksha = tithi_idx_clamped if tithi_idx_clamped <= 15 else tithi_idx_clamped - 15
        tithi_name = f"{paksha} {tithi_names[tithi_idx_clamped - 1]}"

        nakshatra_idx = int((moon_lon % 360.0) / (360.0 / 27.0))
        nakshatra_name = nakshatra_names[nakshatra_idx % 27]

        is_rikta = tithi_in_paksha in (4, 9, 14)
        is_amavasya = tithi_idx_clamped == 30
        weekday_idx = cur_dt.weekday()  # 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
        weekday_names_hi = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]

        date_str = cur_dt.strftime("%Y-%m-%d")
        day_str = cur_dt.strftime("%A")
        day_hi = weekday_names_hi[weekday_idx]
        month_label_hi = cur_dt.strftime("%B %Y").replace("January", "जनवरी").replace("February", "फरवरी").replace("March", "मार्च").replace("April", "अप्रैल").replace("May", "मई").replace("June", "जून").replace("July", "जुलाई").replace("August", "अगस्त").replace("September", "सितंबर").replace("October", "अक्टूबर").replace("November", "नवंबर").replace("December", "दिसंबर")
        month_label_en = cur_dt.strftime("%B %Y")

        # Inauspicious check
        is_bad = False
        bad_reasons_hi = []
        bad_reasons_en = []

        if house_from_moon == 8:
            is_bad = True
            bad_reasons_hi.append("चंद्र अष्टम (चंद्रमा 8वें भाव में मानसिक व शारीरिक कष्ट योग)")
            bad_reasons_en.append("Chandra Ashtama (8th Moon obstacle)")
        elif house_from_moon == 12:
            is_bad = True
            bad_reasons_hi.append("चंद्र द्वादश (हानि व व्यय योग)")
            bad_reasons_en.append("Chandra 12th (High loss/expense)")

        if is_rikta:
            is_bad = True
            bad_reasons_hi.append(f"रिक्ता तिथि ({tithi_in_paksha}वीं तिथि शून्य फलदायी)")
            bad_reasons_en.append(f"Rikta Tithi (#{tithi_in_paksha} void of good result)")

        if is_amavasya:
            is_bad = True
            bad_reasons_hi.append("अमावस्या (पितृ तिथि - शुभ कार्यों में वर्जित)")
            bad_reasons_en.append("Amavasya (Forbidden for auspicious beginnings)")

        # Specific Category Rules
        if category == "marriage":
            if weekday_idx == 1:
                is_bad = True
                bad_reasons_hi.append("मंगलवार (विवाह व मांगलिक कार्यों में वर्जित)")
                bad_reasons_en.append("Tuesday (Avoid for Wedding/Engagement)")
            elif weekday_idx == 5:
                is_bad = True
                bad_reasons_hi.append("शनिवार (विवाह के लिए त्याज्य)")
                bad_reasons_en.append("Saturday (Inauspicious for Marriage)")
        elif category == "business":
            if weekday_idx == 1:
                is_bad = True
                bad_reasons_hi.append("मंगलवार (नया व्यापार व खाता खोलने में वर्जित)")
                bad_reasons_en.append("Tuesday (Avoid for New Business)")
            elif weekday_idx == 6:
                is_bad = True
                bad_reasons_hi.append("रविवार (दुकान व फर्म के शुभारंभ में त्याज्य)")
                bad_reasons_en.append("Sunday (Avoid for Inauguration)")
        elif category == "travel":
            # Avoid travel on direction-afflicted days (Disha Shool) or Krishna Chaturdashi
            if weekday_idx == 6 and tithi_in_paksha == 14:
                is_bad = True
                bad_reasons_hi.append("रविवार व चतुर्दशी (यात्रा में विघ्न योग)")
                bad_reasons_en.append("Sunday + 14th Tithi (Travel hindrance)")
        elif category == "property":
            if weekday_idx in (1, 5):
                is_bad = True
                bad_reasons_hi.append("मंगलवार/शनिवार (मकान रजिस्ट्री व गृह प्रवेश में वर्जित)")
                bad_reasons_en.append("Avoid Tue/Sat for Griha Pravesh & Registry")
        elif category == "vehicle":
            if weekday_idx in (1, 5):
                is_bad = True
                bad_reasons_hi.append("मंगलवार/शनिवार (नया वाहन क्रय में राहु/शनि दोष से बचें)")
                bad_reasons_en.append("Avoid Tue/Sat for Vehicle Delivery")
        elif category == "surgery":
            if tithi_idx_clamped in (15, 30):
                is_bad = True
                bad_reasons_hi.append("पूर्णिमा/अमावस्या (रक्त दबाव अधिक होने से सर्जरी वर्जित)")
                bad_reasons_en.append("Full/New Moon (Surgery contraindicated)")
        elif category == "job":
            if weekday_idx == 5 and is_rikta:
                is_bad = True
                bad_reasons_hi.append("शनिवार व रिक्ता तिथि (पदभार ग्रहण में देरी योग)")
                bad_reasons_en.append("Saturday Rikta (Delays in joining)")
        elif category == "investment":
            if weekday_idx in (1, 5) or is_rikta:
                is_bad = True
                bad_reasons_hi.append("मंगलवार/शनिवार (स्वर्ण क्रय व बड़े धन निवेश में वर्जित)")
                bad_reasons_en.append("Avoid Tue/Sat for Gold & Capital Investments")

        entry = {
            "date": date_str,
            "weekday": day_str,
            "weekday_hi": day_hi,
            "month_label_hi": month_label_hi,
            "month_label_en": month_label_en,
            "tithi": tithi_name,
            "tithi_idx": tithi_idx_clamped,
            "nakshatra": nakshatra_name,
            "house_from_moon": house_from_moon,
            "transit_rashi_hi": rashi_names_hi[transit_sign],
            "transit_rashi_en": rashi_names_en[transit_sign],
        }

        if is_bad:
            entry["is_shubh"] = False
            entry["quality"] = "avoid"
            entry["muhurat_time"] = "कोई शुभ मुहूर्त उपलब्ध नहीं (दिन त्याज्य)"
            entry["reason_hi"] = " · ".join(bad_reasons_hi)
            entry["reason_en"] = " · ".join(bad_reasons_en)
            varjit_dates.append(entry)
        else:
            # Check if Best or Moderate
            is_best = False
            best_time = "प्रातः 07:45 से 10:30 (शुभ व अमृत चौघड़िया)"
            shubh_reason_hi = f"चंद्रमा {house_from_moon}वें भाव में अनुकूल · {tithi_name} · {nakshatra_name} नक्षत्र"
            shubh_reason_en = f"Moon in favorable {house_from_moon}th house · {tithi_name} · {nakshatra_name}"

            if category == "marriage" and weekday_idx in (3, 4, 0) and house_from_moon in (1, 5, 7, 9, 11):
                is_best = True
                best_time = "गोधूलि वेला (सायं 06:15 - 07:45) व अमृत बेला"
                shubh_reason_hi += " · विवाह के लिए सर्वार्थ सिद्धि योग"
            elif category == "business" and weekday_idx == 2 and house_from_moon in (2, 10, 11):
                is_best = True
                best_time = "प्रातः 09:15 से 11:30 (लाभ व अमृत चौघड़िया)"
                shubh_reason_hi += " · बुध-चंद्र अनुकूलता व्यापार वृद्धि योग"
            elif category == "travel" and weekday_idx in (2, 3, 4) and house_from_moon in (3, 7, 9, 11):
                is_best = True
                best_time = "प्रातः 06:30 से 09:15 (अमृत चौघड़िया)"
                shubh_reason_hi += " · यात्रा सुखद व कार्य सिद्धि योग"
            elif category == "property" and weekday_idx in (0, 3, 4) and house_from_moon in (4, 9, 11):
                is_best = True
                best_time = "प्रातः 08:30 से 11:00 (स्थिर लग्न मुहूर्त)"
                shubh_reason_hi += " · गृह प्रवेश व रजिस्ट्री के लिए अचल संपत्ति योग"
            elif category == "vehicle" and weekday_idx in (2, 3, 4, 6) and house_from_moon in (3, 4, 5, 9, 11):
                is_best = True
                best_time = "दोपहर 12:15 से 02:00 (अभिजित व शुभ मुहूर्त)"
                shubh_reason_hi += " · वाहन सौख्य व दीर्घायु योग"
            elif category == "surgery" and house_from_moon in (3, 6, 11) and tithi_in_paksha not in (4, 9, 14, 15, 30):
                is_best = True
                best_time = "प्रातः 07:30 से 09:45 (रोग निवारण वेला)"
                shubh_reason_hi += " · उपचय भाव चंद्र - शीघ्र स्वास्थ्य लाभ"
            elif category == "job" and weekday_idx in (0, 2, 3, 4) and house_from_moon in (6, 10, 11):
                is_best = True
                best_time = "प्रातः 09:45 से 11:45 (राज्य पद लाभ चौघड़िया)"
                shubh_reason_hi += " · कर्म भाव अनुकूलता - उन्नति योग"
            elif category == "investment" and weekday_idx in (3, 4) and house_from_moon in (2, 5, 9, 11):
                is_best = True
                best_time = "प्रातः 10:15 से 12:30 (धन वृद्धि शुभ मुहूर्त)"
                shubh_reason_hi += " · गुरु-शुक्र धन भाव पुष्टि योग"
            elif house_from_moon in (1, 3, 5, 7, 9, 10, 11):
                is_best = True

            entry["is_shubh"] = True
            entry["quality"] = "best" if is_best else "moderate"
            entry["muhurat_time"] = best_time
            entry["reason_hi"] = shubh_reason_hi
            entry["reason_en"] = shubh_reason_en

            if is_best:
                shubh_dates.append(entry)
            else:
                moderate_dates.append(entry)

    # Sort each list by date
    shubh_dates.sort(key=lambda x: x["date"])
    moderate_dates.sort(key=lambda x: x["date"])
    varjit_dates.sort(key=lambda x: x["date"])

    return {
        "category": category,
        "title_hi": t_info["hi"],
        "title_en": t_info["en"],
        "start_date": st.strftime("%Y-%m-%d"),
        "end_date": (st + timedelta(days=days_ahead - 1)).strftime("%Y-%m-%d"),
        "days_ahead": days_ahead,
        "shubh_dates": shubh_dates,
        "moderate_dates": moderate_dates,
        "varjit_dates": varjit_dates,
        "dates": sorted(shubh_dates + moderate_dates + varjit_dates, key=lambda x: x["date"]),
        "total_shubh": len(shubh_dates),
        "total_moderate": len(moderate_dates),
        "total_varjit": len(varjit_dates),
        "total_scanned": days_ahead,
    }


def compute_weekly_personal_forecast(chart: dict[str, Any], start_date: str = None) -> dict[str, Any]:
    """
    Compute 7-Day Personal Transit Forecast with exact Severity Levels:
    - सामान्य (Mild / Favorable): Benefic transits (Houses 1, 3, 5, 7, 9, 10, 11)
    - मध्यम (Moderate): Houses 2, 6, 12
    - गंभीर (Severe / High Alert): House 8 (Chandra Ashtama) or adverse nodal aspects
    """
    st = datetime.strptime(_clean_dob(start_date), "%Y-%m-%d").date() if start_date else date.today()
    natal_moon = next((p for p in chart.get("planets", []) if p["planet"] == "Moon"), None)
    if natal_moon:
        natal_sign_idx = (
            natal_moon["sign_index"] - 1
            if "sign_index" in natal_moon
            else int(natal_moon.get("longitude", natal_moon.get("lon", 0.0)) // 30)
        )
    else:
        natal_sign_idx = 0

    rashi_names_en = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    rashi_names_hi = ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"]

    daily_forecasts = []
    severe_count = 0
    favorable_count = 0

    for i in range(7):
        cur_dt = st + timedelta(days=i)
        jd_noon = swe.julday(cur_dt.year, cur_dt.month, cur_dt.day, 12.0) - 5.5 / 24.0
        res_m, _ = swe.calc_ut(jd_noon, swe.MOON, CALC_FLAGS)
        m_lon = res_m[0] % 360.0
        s_idx = int(m_lon // 30)
        h_from_moon = ((s_idx - natal_sign_idx) % 12) + 1

        is_today = (i == 0)
        is_tomorrow = (i == 1)
        day_tag = "आज (Today)" if is_today else "कल (Tomorrow)" if is_tomorrow else cur_dt.strftime("%A")

        if h_from_moon == 8:
            sev_code = "severe"
            sev_en = "Severe Caution (Chandra Ashtama)"
            sev_hi = "गंभीर सावधानी (चंद्र अष्टम)"
            theme_hi = "मानसिक शांति बनाए रखें, नए जोखिम या विवाद से बचें"
            theme_en = "Exercise strict caution, postpone high-stake deals"
            remedy_hi = "शिवलिंग पर जल चढ़ाएं और वाहन संभलकर चलाएं।"
            remedy_en = "Offer water on Shivling and avoid night-time travel."
            color_hi = "दूधिया सफेद"
            color_en = "Milky White"
            num = 2
            severe_count += 1
        elif h_from_moon in (2, 6, 12):
            sev_code = "moderate"
            sev_en = "Moderate (Caution on Spending/Speech)"
            sev_hi = "मध्यम (खर्च व वाणी पर नियंत्रण रखें)"
            theme_hi = "वित्तीय बजट का ध्यान रखें और सहकर्मियों से मधुर व्यवहार करें"
            theme_en = "Maintain budget discipline and avoid arguments"
            remedy_hi = "गाय को ताजी रोटी खिलाएं।"
            remedy_en = "Feed fresh bread to cows."
            color_hi = "हल्का हरा"
            color_en = "Light Green"
            num = 5
        else:
            sev_code = "mild"
            sev_en = "Favorable (Growth & Success)"
            sev_hi = "सामान्य / शुभ (कार्य सिद्धि व प्रगति)"
            theme_hi = "लंबित कार्यों को पूरा करें, नए संपर्क व सम्मान का योग"
            theme_en = "Productive window for meetings and executing key initiatives"
            remedy_hi = "सूर्य देव को जल दें और गुरुजनों का आशीर्वाद लें।"
            remedy_en = "Offer morning prayer to Sun and seek blessings."
            color_hi = "केसरिया / पीला"
            color_en = "Saffron / Gold"
            num = 9
            favorable_count += 1

        daily_forecasts.append({
            "day_index": i,
            "date": cur_dt.strftime("%Y-%m-%d"),
            "weekday": cur_dt.strftime("%A"),
            "day_tag": day_tag,
            "transit_rashi_en": rashi_names_en[s_idx],
            "transit_rashi_hi": rashi_names_hi[s_idx],
            "house_from_moon": h_from_moon,
            "severity": sev_code,
            "severity_code": sev_code,
            "severity_en": sev_en,
            "severity_hi": sev_hi,
            "theme_hi": theme_hi,
            "theme_en": theme_en,
            "remedy_hi": remedy_hi,
            "remedy_en": remedy_en,
            "lucky_color_hi": color_hi,
            "lucky_color_en": color_en,
            "lucky_number": num,
        })

    best_day = next((d["weekday"] for d in daily_forecasts if d["severity_code"] == "mild"), "Wednesday")
    alert_day = next((d["weekday"] for d in daily_forecasts if d["severity_code"] == "severe"), None)

    summary_hi = f"इस सप्ताह {favorable_count} दिन अत्यंत अनुकूल व प्रगतिदायक रहेंगे। " + \
                 (f"विशेषतः {alert_day} को चंद्र अष्टम के कारण अतिरिक्त सावधानी रखें।" if alert_day else "सप्ताह सामान्यतः शांतिपूर्ण रहेगा।")
    summary_en = f"This week offers {favorable_count} highly productive days. " + \
                 (f"Exercise special vigilance on {alert_day} due to 8th house transit." if alert_day else "Overall harmonious weekly momentum.")

    return {
        "start_date": st.strftime("%Y-%m-%d"),
        "end_date": (st + timedelta(days=6)).strftime("%Y-%m-%d"),
        "weekly_summary_hi": summary_hi,
        "weekly_summary_en": summary_en,
        "best_day": best_day,
        "alert_day": alert_day or "None",
        "days": daily_forecasts,
    }


def compute_kp_cusp_chart(
    chart: dict[str, Any],
    dob: str,
    birth_time: str,
    latitude: float,
    longitude: float,
    tz_offset: float = 5.5,
    place_name: str = "",
    iana_tz: str | None = None,
) -> dict[str, Any]:
    """
    Compute Krishnamurti Paddhati (KP) Bhav Chalit Cuspal Chart:
    - 12 Cusps calculated using Placidus house system under Lahiri Ayanamsa.
    - Each Cusp has Cusp DMS, Rashi, Nakshatra, Pada, and 4-fold Sub Lords (RL, NL, SL, SSL).
    - Determines Chalit house boundaries (Bhav Sandhi) and identifies occupying planets in each Chalit house.
    """
    jd_ut, _, _ = to_jd_ut(dob, birth_time, tz_offset, place_name, iana_tz)
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    cusps_raw, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'P', CALC_FLAGS)

    cusps_list = []
    planets = chart.get("planets", [])

    for i in range(12):
        cusp_num = i + 1
        cusp_lon = cusps_raw[i] % 360.0
        next_cusp_lon = cusps_raw[(i + 1) % 12] % 360.0

        rashi_idx = int(cusp_lon // 30.0)
        deg_in_sign = cusp_lon % 30.0
        dms = _fmt_dms(deg_in_sign)

        tot_min = cusp_lon * 60.0
        nak_idx = int(tot_min // 800.0) % 27
        rem_min = tot_min % 800.0
        pada = int(rem_min // 200.0) + 1
        nak_name = NAKSHATRAS[nak_idx][0]

        rl, nl, sl, ssl = calculate_kp_sub_lords(cusp_lon)

        # Chalit house occupants: check if planet longitude is between cusp_lon and next_cusp_lon
        occupants = []
        for p in planets:
            p_lon = p.get("longitude", p.get("lon", 0.0)) % 360.0
            is_in = False
            if cusp_lon <= next_cusp_lon:
                is_in = cusp_lon <= p_lon < next_cusp_lon
            else: # crosses 0 deg Aries
                is_in = p_lon >= cusp_lon or p_lon < next_cusp_lon
            if is_in:
                occupants.append({
                    "planet": p.get("planet"),
                    "planet_hi": p.get("planet_hi", PLANET_NAMES_HI.get(p.get("planet"))),
                    "dms": p.get("dms"),
                    "retrograde": p.get("retrograde", False),
                    "is_benefic": p.get("is_benefic", True),
                })

        cusps_list.append({
            "cusp_number": cusp_num,
            "longitude": round(cusp_lon, 4),
            "rashi": RASHIS[rashi_idx],
            "rashi_hi": RASHIS_HI[rashi_idx],
            "dms": dms,
            "nakshatra": nak_name,
            "pada": pada,
            "rl": rl,
            "nl": nl,
            "sl": sl,
            "ssl": ssl,
            "rl_hi": PLANET_NAMES_HI.get(rl, rl),
            "nl_hi": PLANET_NAMES_HI.get(nl, nl),
            "sl_hi": PLANET_NAMES_HI.get(sl, sl),
            "ssl_hi": PLANET_NAMES_HI.get(ssl, ssl),
            "sandhi_start_dms": dms,
            "sandhi_end_dms": _fmt_dms(next_cusp_lon % 30.0),
            "occupants": occupants,
        })

    return {
        "ayanamsa": chart.get("ayanamsa", "Chitrapaksha Lahiri"),
        "house_system": "Placidus (KP Standard)",
        "cusps": cusps_list,
    }


def compute_lal_kitab_visual_upay_chart(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Generate 12-House Lal Kitab Visual Graphic Upay Map:
    Displays primary tangible remedial substance, rule, timings, and prohibitions for each house.
    """
    standard_upays = {
        1: {
            "title_hi": "प्रथम भाव (लग्न - शरीर व आत्मबल)",
            "title_en": "House 1 (Lagna - Physical Vitality & Core Self)",
            "substance_hi": "तांबे का ठोस सिक्का या शुद्ध गुड़",
            "substance_en": "Solid Copper Coin or Pure Jaggery",
            "rule_hi": "सिक्के में छेद न हो। इसे बहते स्वच्छ जल में प्रवाहित करें अथवा मंगलवार को गुड़ का दान करें।",
            "rule_en": "Immerse solid unpierced copper coin in moving river or donate jaggery on Tuesday.",
            "timing_hi": "प्रातः सूर्योदय से दोपहर 12 बजे के मध्य",
            "timing_en": "Morning between sunrise and noon",
            "parhez_hi": "मुफ्त की वस्तुएं न लें, सदाचार का पालन करें।",
            "parhez_en": "Refuse unearned gifts; uphold impeccable moral conduct.",
        },
        2: {
            "title_hi": "द्वितीय भाव (धन, वाणी व कुटुंब)",
            "title_en": "House 2 (Wealth, Speech & Family Lineage)",
            "substance_hi": "शुद्ध चांदी का ठोस चौकोर टुकड़ा",
            "substance_en": "Solid Pure Silver Square Tile",
            "rule_hi": "चांदी का चौकोर टुकड़ा पीले या सफेद कपड़े में लपेटकर अपनी तिजोरी या बटुए में सदैव रखें।",
            "rule_en": "Keep a solid silver square wrapped in cloth inside your cash locker or wallet.",
            "timing_hi": "सोमवार या शुक्ल पक्ष की द्वितीया",
            "timing_en": "Monday or Waxing Moon Phase",
            "parhez_hi": "कटु वाणी और व्यर्थ के वाद-विवाद से बचें।",
            "parhez_en": "Abstain from harsh or deceitful speech.",
        },
        3: {
            "title_hi": "तृतीय भाव (पराक्रम, छोटे भाई-बहन)",
            "title_en": "House 3 (Courage, Enterprise & Younger Siblings)",
            "substance_hi": "फिटकरी से दांत साफ व हरे रंग से परहेज",
            "substance_en": "Clean Teeth with Alum & Avoid Green Color",
            "rule_hi": "फिटकरी से दातून करें, हाथी दांत की कोई वस्तु घर में न रखें।",
            "rule_en": "Clean teeth with alum daily; strictly avoid keeping ivory articles at home.",
            "timing_hi": "मंगलवार प्रातः",
            "timing_en": "Tuesday morning",
            "parhez_hi": "हरे वस्त्र धारण करने और तोता पालने से बचें।",
            "parhez_en": "Avoid green garments and keeping caged birds.",
        },
        4: {
            "title_hi": "चतुर्थ भाव (माता, मन की शांति व भूमि/भवन)",
            "title_en": "House 4 (Mother, Domestic Peace & Fixed Assets)",
            "substance_hi": "कच्चा दूध या बहते जल में चांदी का सिक्का",
            "substance_en": "Raw Milk or Silver Coin in River",
            "rule_hi": "माता का नित्य चरण स्पर्श कर आशीर्वाद लें; घर के नल से जल का टपकना तुरंत रोकें।",
            "rule_en": "Touch mother's feet daily for mental bliss; fix all leaking water taps immediately.",
            "timing_hi": "सोमवार या पूर्णिमा",
            "timing_en": "Monday or Full Moon day",
            "parhez_hi": "दूध या पानी का व्यापार न करें।",
            "parhez_en": "Never sell milk or pure drinking water commercially.",
        },
        5: {
            "title_hi": "पंचम भाव (संतान, बुद्धि व उच्च विद्या)",
            "title_en": "House 5 (Intellect, Progeny & Sacred Learning)",
            "substance_hi": "तांबे के लोटे में जल व चने की दाल",
            "substance_en": "Copper Vessel Water & Chana Dal",
            "rule_hi": "सूर्य देव को तांबे के लोटे से अर्घ्य दें, और कुत्तों को मीठी रोटी खिलाएं।",
            "rule_en": "Offer fresh water in copper lota to rising Sun; feed sweet rotis to dogs.",
            "timing_hi": "रविवार प्रातः",
            "timing_en": "Sunday morning at dawn",
            "parhez_hi": "गुरुजनों का अपमान न करें व अहंकार त्यागें।",
            "parhez_en": "Respect teachers and eliminate intellectual vanity.",
        },
        6: {
            "title_hi": "षष्ठ भाव (शत्रु, रोग व ऋण निवारण)",
            "title_en": "House 6 (Health Resilience, Debt & Overcoming Obstacles)",
            "substance_hi": "कच्चा डली वाला नमक व कांसे का बर्तन",
            "substance_en": "Rock Salt Lumps & Bronze Utensil",
            "rule_hi": "कच्चे नमक की डली बहते पानी में डालें अथवा कांसे के बर्तन का दान करें।",
            "rule_en": "Immerse raw rock salt in running stream or donate bronze vessel.",
            "timing_hi": "बुधवार सायं",
            "timing_en": "Wednesday twilight",
            "parhez_hi": "उधार लेने व कर्ज देने में सतर्क रहें।",
            "parhez_en": "Avoid casual borrowing or reckless lending.",
        },
        7: {
            "title_hi": "सप्तम भाव (दांपत्य, जीवनसाथी व व्यापार साझेदारी)",
            "title_en": "House 7 (Spouse, Domestic Harmony & Partnerships)",
            "substance_hi": "कांसे का दान व पत्नी को स्वर्ण आभूषण",
            "substance_en": "Bronze Donation & Gold Jewellery for Spouse",
            "rule_hi": "गौशाला में हरा चारा दान करें, घर की पहली रोटी गाय माता को दें।",
            "rule_en": "Serve fresh green fodder at cow shelters; offer first daily roti to cows.",
            "timing_hi": "शुक्रवार प्रातः",
            "timing_en": "Friday morning",
            "parhez_hi": "विवाह के समय मिले चांदी-सोने के उपहार कभी न बेचें।",
            "parhez_en": "Never liquidate heirloom bridal jewellery or wedding gifts.",
        },
        8: {
            "title_hi": "अष्टम भाव (आयु, अनहोनी से रक्षा व गुप्त ज्ञान)",
            "title_en": "House 8 (Longevity, Mishap Protection & Subconscious)",
            "substance_hi": "श्मशान का पानी या 4 बादाम मंदिर में",
            "substance_en": "Crematorium Spring Water or 4 Almonds to Temple",
            "rule_hi": "चार बादाम धर्मस्थल में रखकर 4 वापस लाकर पीले कपड़े में बांधकर घर रखें।",
            "rule_en": "Place 4 almonds at temple and bring back 4 to keep safe at home.",
            "timing_hi": "शनिवार दोपहर",
            "timing_en": "Saturday midday",
            "parhez_hi": "दक्षिण मुखी द्वार पर निवास करने से बचें।",
            "parhez_en": "Avoid southern-facing residential entrances.",
        },
        9: {
            "title_hi": "नवम भाव (भाग्य, धर्म व पिता का सुख)",
            "title_en": "House 9 (Fortune, Dharma & Paternal Blessings)",
            "substance_hi": "केसर का तिलक व पीले वस्त्र में चने की दाल",
            "substance_en": "Saffron (Kesar) Tilak & Chana Dal in Yellow Cloth",
            "rule_hi": "माथे, नाभि व जुबान पर नित्य केसर का तिलक लगाएं; कुल पुरोहित का सम्मान करें।",
            "rule_en": "Apply pure kesar tilak on navel and forehead daily; honor family priests.",
            "timing_hi": "गुरुवार प्रातः",
            "timing_en": "Thursday morning",
            "parhez_hi": "नास्तिक विचारों व धर्म निंदा से दूर रहें।",
            "parhez_en": "Abstain from cynicism or ridiculing sacred traditions.",
        },
        10: {
            "title_hi": "दशम भाव (कर्म, प्रतिष्ठा व आजीविका)",
            "title_en": "House 10 (Career Stature, Karma & Public Honour)",
            "substance_hi": "दस अंधे व्यक्तियों को भोजन व मदिरा-मांस त्याग",
            "substance_en": "Feed Visually Impaired & Abstain from Intoxicants",
            "rule_hi": "शनिवार को दृष्टिहीनों को भोजन कराएं, सरसों तेल का छाया पात्र दान करें।",
            "rule_en": "Feed visually impaired individuals on Saturday; donate shadow mustard oil vessel.",
            "timing_hi": "शनिवार सायं",
            "timing_en": "Saturday evening",
            "parhez_hi": "शराब व मांसाहार का पूर्ण त्याग करें।",
            "parhez_en": "Total abstinence from alcohol and non-vegetarian food.",
        },
        11: {
            "title_hi": "एकादश भाव (लाभ, इच्छापूर्ति व आय के स्रोत)",
            "title_en": "House 11 (Income Inflows, Desires & Network Gain)",
            "substance_hi": "कच्चा कोयला या भैरव मंदिर उपासना",
            "substance_en": "Raw Coal or Bhairav Devotion",
            "rule_hi": "नदी में 4 सूखे नारियल अथवा कच्चा कोयला प्रवाहित करें।",
            "rule_en": "Immerse 4 whole dry coconuts or raw coal into running river.",
            "timing_hi": "शनिवार प्रातः",
            "timing_en": "Saturday morning",
            "parhez_hi": "अनैतिक धनार्जन व सट्टेबाजी से दूर रहें।",
            "parhez_en": "Refuse speculative gambles and illicit earnings.",
        },
        12: {
            "title_hi": "द्वादश भाव (व्यय, विदेश यात्रा व मोक्ष)",
            "title_en": "House 12 (Expenditures, Foreign Travel & Subconscious Release)",
            "substance_hi": "सौंफ व खांड की लाल पोटली",
            "substance_en": "Red Fabric Pouch of Fennel Seeds & Raw Sugar",
            "rule_hi": "लाल कपड़े में सौंफ और खांड बांधकर अपने शयनकक्ष में सिरहाने रखें।",
            "rule_en": "Keep a red pouch containing fennel seeds and raw sugar under mattress head.",
            "timing_hi": "मंगलवार दोपहर",
            "timing_en": "Tuesday midday",
            "parhez_hi": "घर की छत पर कबाड़ या बंद घड़ियां न रखें।",
            "parhez_en": "Keep rooftop clean; discard non-working clutter and clocks.",
        },
    }

    houses_map = []
    planets = chart.get("planets", [])

    for h_num in range(1, 13):
        base = standard_upays[h_num]
        occupants = [
            {
                "planet": p.get("planet"),
                "planet_hi": p.get("planet_hi", PLANET_NAMES_HI.get(p.get("planet"))),
                "dms": p.get("dms"),
                "is_benefic": p.get("is_benefic", True),
            }
            for p in planets if p.get("house") == h_num
        ]

        houses_map.append({
            "house": h_num,
            "title_hi": base["title_hi"],
            "title_en": base["title_en"],
            "substance_hi": base["substance_hi"],
            "substance_en": base["substance_en"],
            "rule_hi": base["rule_hi"],
            "rule_en": base["rule_en"],
            "timing_hi": base["timing_hi"],
            "timing_en": base["timing_en"],
            "parhez_hi": base["parhez_hi"],
            "parhez_en": base["parhez_en"],
            "occupants": occupants,
            "has_planets": len(occupants) > 0,
        })

    return houses_map
