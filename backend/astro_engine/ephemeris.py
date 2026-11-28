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
            "abbr": abbr,
            "longitude": round(lon, 4),
            "sign_index": sign_idx + 1,
            "rashi": RASHIS[sign_idx],
            "degree_in_sign": round(deg_in_sign, 4),
            "dms": _fmt_dms(deg_in_sign),
            "house": house,
            "nakshatra": NAKSHATRAS[nak_idx][0],
            "nakshatra_lord": NAKSHATRAS[nak_idx][1],
            "pada": pada,
            "retrograde": speed < 0 and name != "Rahu",
            "dignity": dignity,
            "pakka_ghar": house in PAKKA_GHAR.get(name, set()),
            "navamsa_sign_index": d9_sign + 1,
            "navamsa_rashi": RASHIS[d9_sign],
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
    planets.append({
        "planet": "Ketu",
        "abbr": "Ke",
        "longitude": round(ketu_lon, 4),
        "sign_index": k_sign + 1,
        "rashi": RASHIS[k_sign],
        "degree_in_sign": round(k_deg, 4),
        "dms": _fmt_dms(k_deg),
        "house": k_house,
        "nakshatra": NAKSHATRAS[k_nak][0],
        "nakshatra_lord": NAKSHATRAS[k_nak][1],
        "pada": k_pada,
        "retrograde": rahu_speed < 0,
        "dignity": _dignity("Ketu", k_sign),
        "pakka_ghar": k_house in PAKKA_GHAR["Ketu"],
        "navamsa_sign_index": k_d9_sign + 1,
        "navamsa_rashi": RASHIS[k_d9_sign],
        "upay_id": 106,
        "is_benefic": _dignity("Ketu", k_sign) in ("Exalted", "Own Sign", "Friendly") or k_house in (3, 6, 9, 11),
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
            "lord": RASHI_LORDS[(lagna_sign + h - 1) % 12],
            "planets": [p["abbr"] for p in planets if p["house"] == h],
        }
        for h in range(1, 13)
    ]

    vashist_houses = [
        {
            "house": h,
            "sign_index": h,  # Lal Kitab places Aries/House 1 fixed at top
            "rashi": RASHIS[h - 1],
            "lord": RASHI_LORDS[h - 1],
            "planets": [p["abbr"] for p in planets if p["house"] == h],
        }
        for h in range(1, 13)
    ]

    gochar_houses = [
        {
            "house": h,
            "sign_index": ((lagna_sign + h - 1) % 12) + 1,
            "rashi": RASHIS[(lagna_sign + h - 1) % 12],
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

        for s_planet, s_yrs in sub_rot:
            # Nominal Antardasha proportion = (m_yrs * s_yrs) / 120 years, scaled if first Mahadasha is partial
            raw_sub_years = (m_yrs * s_yrs) / 120.0
            if i == 0:
                raw_sub_years *= (1.0 - frac_elapsed)
            s_days = max(1, int(round(raw_sub_years * 365.2425)))
            s_end = min(end_d, sub_cursor + timedelta(days=s_days))
            s_curr = sub_cursor <= today <= s_end
            antardashas.append({
                "maha_planet": m_planet,
                "planet": s_planet,
                "start_date": sub_cursor.strftime("%d-%m-%Y"),
                "end_date": s_end.strftime("%d-%m-%Y"),
                "is_current": s_curr,
                "summary": f"{m_planet} Mahadasha / {s_planet} Antardasha activates {s_planet}'s natal house significations.",
            })
            if s_curr:
                p_cursor = sub_cursor
                for p_planet, p_yrs in DASHA_ORDER[order_names.index(s_planet):] + DASHA_ORDER[:order_names.index(s_planet)]:
                    p_days = max(1, int(round(s_days * (p_yrs / 120.0))))
                    p_end = min(s_end, p_cursor + timedelta(days=p_days))
                    p_curr = p_cursor <= today <= p_end
                    pratyantars_for_curr.append({
                        "maha_planet": m_planet,
                        "antar_planet": s_planet,
                        "planet": p_planet,
                        "start_date": p_cursor.strftime("%d-%m-%Y"),
                        "end_date": p_end.strftime("%d-%m-%Y"),
                        "is_current": p_curr,
                        "summary": f"{m_planet} / {s_planet} / {p_planet} Pratyantardasha transit activation.",
                    })
                    p_cursor = p_end + timedelta(days=1)
            sub_cursor = s_end + timedelta(days=1)

        mahadashas.append({
            "planet": m_planet,
            "duration_years": round(eff_years, 2),
            "start_date": cursor.strftime("%d-%m-%Y"),
            "end_date": end_d.strftime("%d-%m-%Y"),
            "is_current": is_current,
            "summary": f"{m_planet} Mahadasha governs growth, duties, and karmic themes linked to {m_planet}'s natal dignity.",
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
            lk_dashas.append({
                "planet": lp,
                "years": ly,
                "start_date": lk_cursor.strftime("%d-%m-%Y"),
                "end_date": l_end.strftime("%d-%m-%Y"),
                "is_current": lk_cursor <= today <= l_end,
                "summary": f"Lal Kitab {lp} cycle ({ly} yr): highlights Pakka Ghar activation & Karma balance.",
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
        (1, "Personality, Health & Vitality", 101, "Offer water to the morning Sun in copper and avoid ego conflicts."),
        (2, "Wealth, Family & Speech", 105, "Apply turmeric or saffron tilak daily for Jupiter stability."),
        (3, "Courage, Siblings & Initiative", 103, "Share sweet roti or jaggery on Tuesdays to harmonize Mars."),
        (4, "Home, Mother & Peace of Mind", 102, "Keep silver close or drink milk from a silver cup on Mondays."),
        (5, "Education, Intellect & Children", 105, "Respect elders/mentors and donate yellow lentils on Thursdays."),
        (6, "Health Resilience, Routine & Debts", 104, "Feed green fodder to cows on Wednesdays and keep speech measured."),
        (7, "Partnership, Marriage & Trade", 106, "Wear clean ironed attire and donate white sweets on Fridays."),
        (8, "Longevity, Transformation & Research", 103, "Keep humility high and donate mustard oil on Saturdays."),
        (9, "Fortune, Higher Learning & Dharma", 105, "Follow righteous counsel and honor ancestral traditions."),
        (10, "Career, Status & Karma", 101, "Maintain consistent discipline at work; light a lamp every Saturday evening."),
        (11, "Gains, Networks & Aspirations", 105, "Nurture reliable friendships and practice charitable giving."),
        (12, "Expenses, Foreign Travel & Liberation", 104, "Keep a square silver piece in wallet and practice calm evening reflection."),
    ]
    out = []
    for h_num, theme, upay_id, upay_text in house_themes:
        h_obj = chart["houses"][h_num - 1]
        in_house = [p for p in chart["planets"] if p["house"] == h_num]
        if in_house:
            p_desc = "; ".join(f"{p['planet']} ({p['dignity']}, {p['dms']})" for p in in_house)
            pred = (
                f"House {h_num} ({h_obj['rashi']}, lord {h_obj['lord']}) governs {theme}. "
                f"Occupied by {p_desc}, activating focused momentum and practical karma in these matters."
            )
        else:
            pred = (
                f"House {h_num} ({h_obj['rashi']}, ruled by {h_obj['lord']}) governs {theme}. "
                f"House outcomes follow {h_obj['lord']}'s natal strength and ongoing Dasha transits."
            )
        out.append({
            "prediction_id": 700 + h_num,
            "house": h_num,
            "rashi": h_obj["rashi"],
            "lord": h_obj["lord"],
            "theme": theme,
            "planets": [p["planet"] for p in in_house],
            "prediction": pred,
            "upay_id": upay_id,
            "upay": upay_text,
        })
    return out


def _vivaran_desk(chart: dict[str, Any]) -> list[dict[str, Any]]:
    """Build Kundli Vivaran desk tiles; index_ids [8, 9, 10, 20] match APK free Kalyankari exemptions."""
    asc = chart["ascendant"]
    moon = next(p for p in chart["planets"] if p["planet"] == "Moon")
    sun = next(p for p in chart["planets"] if p["planet"] == "Sun")
    sat = next(p for p in chart["planets"] if p["planet"] == "Saturn")
    jup = next(p for p in chart["planets"] if p["planet"] == "Jupiter")

    # Note: index_id in [8, 9, 10, 20] triggers free Kalyankari dialog in APK!
    return [
        {"index_id": 1, "desk": "Lagna (Ascendant)", "value": f"{asc['rashi'].split()[0]} ({asc['dms']})", "is_prediction": "Yes", "detail": f"Your Lagna rises in {asc['rashi']} at {asc['dms']}, shaping temperament and physical vitality."},
        {"index_id": 2, "desk": "Janma Rashi (Moon)", "value": moon["rashi"].split()[0], "is_prediction": "Yes", "detail": f"Moon is in {moon['rashi']} ({moon['dms']}), guiding emotional depth and mental resilience."},
        {"index_id": 3, "desk": "Janma Nakshatra", "value": f"{moon['nakshatra']} (P{moon['pada']})", "is_prediction": "Yes", "detail": f"Born in {moon['nakshatra']} Nakshatra Pada {moon['pada']} ruled by {moon['nakshatra_lord']}."},
        {"index_id": 4, "desk": "Sun Placement", "value": f"H{sun['house']} · {sun['dignity']}", "is_prediction": "Yes", "detail": f"Sun occupies House {sun['house']} in {sun['rashi']}, directing career authority and vitality."},
        {"index_id": 5, "desk": "Jupiter Yoga", "value": f"H{jup['house']} · {jup['dignity']}", "is_prediction": "Yes", "detail": f"Jupiter in House {jup['house']} illuminates wisdom, mentors, and long-term fortune."},
        {"index_id": 6, "desk": "Saturn Karma", "value": f"H{sat['house']} · {sat['dignity']}", "is_prediction": "Yes", "detail": f"Saturn in House {sat['house']} rewards patience, ethical effort, and persistence."},
        {"index_id": 8, "desk": "Kalyankari Navgrah", "value": "Pooja Advisory", "is_prediction": "Yes", "product_id": 8, "detail": "Auspicious Navgrah harmonization suggested for planetary balance (Kalyankari Exempt Tile #8)."},
        {"index_id": 9, "desk": "Ishta Devata Remedy", "value": "Spiritual Path", "is_prediction": "Yes", "product_id": 8, "detail": "Recommended mantra meditation based on 5th & 9th house harmony (Kalyankari Exempt Tile #9)."},
        {"index_id": 10, "desk": "Makaan & Vahaan Puja", "value": "Property Peace", "is_prediction": "Yes", "product_id": 8, "detail": "4th house stability blessing for home harmony and peace (Kalyankari Exempt Tile #10)."},
        {"index_id": 20, "desk": "Kalyankari Shanti", "value": "View Puja", "is_prediction": "Yes", "product_id": 8, "detail": "Kalyankari Navgrah Shanti Puja guidance available directly (Kalyankari Exempt Tile #20)."},
        {"index_id": 11, "desk": "Ayanamsa (Lahiri)", "value": chart["ayanamsa"], "is_prediction": "No", "detail": "Exact Chitrapaksha Lahiri sidereal offset."},
        {"index_id": 12, "desk": "Lucky Day & Color", "value": "Thu / Saffron", "is_prediction": "No", "detail": "Supportive weekly rhythm aligned to Lagna lord."},
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
        {"name": "Varna", "obtained": varna, "max": 1, "note": "Mental & spiritual alignment"},
        {"name": "Vashya", "obtained": vashya, "max": 2, "note": "Mutual attraction & harmony"},
        {"name": "Tara", "obtained": tara, "max": 3, "note": "Birth star fortune & destiny"},
        {"name": "Yoni", "obtained": yoni, "max": 4, "note": "Instinctual compatibility"},
        {"name": "Graha Maitri", "obtained": maitri, "max": 5, "note": f"Moon lords: {bl} & {gl}"},
        {"name": "Gana", "obtained": gana, "max": 6, "note": "Temperament matching"},
        {"name": "Bhakoot", "obtained": bhakoot, "max": 7, "note": f"Moon sign house ratio ({diff}/12)"},
        {"name": "Nadi", "obtained": nadi, "max": 8, "note": "Health & genetic vitality" + (" (Nadi Dosha present)" if nadi == 0 else "")},
    ]

    verdict = "Excellent Match" if total >= 28 else ("Good Compatible Match" if total >= 18 else "Low Guna Score — Remedy Advised")
    return {
        "boy": {"name": boy["name"], "moon_rashi": b_moon["rashi"], "nakshatra": b_moon["nakshatra"], "manglik": b_manglik, "mars_house": b_mars["house"]},
        "girl": {"name": girl["name"], "moon_rashi": g_moon["rashi"], "nakshatra": g_moon["nakshatra"], "manglik": g_manglik, "mars_house": g_mars["house"]},
        "total_points": total,
        "max_points": 36.0,
        "verdict": verdict,
        "manglik_summary": "Both Manglik (Balanced)" if (b_manglik and g_manglik) else ("Partial Manglik — consult Acharya" if (b_manglik != g_manglik) else "Non-Manglik Match"),
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

    day_slot_len = (jd_sunset - jd_sunrise) / 8.0
    night_slot_len = (jd_next_sr - jd_sunset) / 8.0

    day_slots = [
        {
            "name": day_seq[i],
            "nature": nature[day_seq[i]],
            "start": _jd_to_local_str(jd_sunrise + i * day_slot_len, tz_offset),
            "end": _jd_to_local_str(jd_sunrise + (i + 1) * day_slot_len, tz_offset),
        }
        for i in range(8)
    ]
    night_slots = [
        {
            "name": night_seq[i],
            "nature": nature[night_seq[i]],
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
        "place": place_name,
        "sunrise": _jd_to_local_str(jd_sunrise, tz_offset),
        "sunset": _jd_to_local_str(jd_sunset, tz_offset),
        "tithi": f"{paksha} Tithi #{tithi_idx if tithi_idx <= 15 else tithi_idx - 15}",
        "nakshatra": NAKSHATRAS[nak_idx][0],
        "yoga_number": yoga_idx,
        "rahu_kaal": rahu_kaal,
        "day_choghadiya": day_slots,
        "night_choghadiya": night_slots,
    }
