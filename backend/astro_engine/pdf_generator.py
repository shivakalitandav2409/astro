"""PDF generator for ASTRO Full Kundali reports (English & Easy Hindi) and Invoices."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from fpdf import FPDF

FONTS_DIR = Path(__file__).resolve().parent / "fonts"
FONT_REGULAR = str(FONTS_DIR / "FreeSans.ttf")
FONT_BOLD = str(FONTS_DIR / "FreeSansBold.ttf")

PLANET_EXPLANATIONS_HI = {
    "Sun": "सूर्य (Sun): आत्म-सम्मान, ऊर्जा, पिता और करियर में प्रतिष्ठा से जुड़ा है।",
    "Moon": "चंद्रमा (Moon): यह आपके मन, भावनाओं, मानसिक शांति और सोच से जुड़ा होता है।",
    "Mars": "मंगल (Mars): आपका साहस, ऊर्जा, इच्छाशक्ति और भाइयों से संबंध दर्शाता है।",
    "Mercury": "बुध (Mercury): बातचीत की कला, तीक्ष्ण बुद्धि, व्यापार और निर्णय क्षमता का कारक है।",
    "Jupiter": "गुरु (Jupiter): जीवन में भाग्य, उच्च शिक्षा, संस्कार, धन और गुरु कृपा का प्रतीक है।",
    "Venus": "शुक्र (Venus): प्रेम, वैवाहिक सुख, कलात्मक रुचि और भौतिक सुख-सुविधाओं का स्वामी है।",
    "Saturn": "शनि (Saturn): मेहनत, अनुशासन, न्याय, कर्म और जीवन के महत्वपूर्ण सबक सिखाता है।",
    "Rahu": "राहु (Rahu): जीवन में अचानक बदलाव, नई सोच, महत्वाकांक्षा और विदेश संपर्कों का संकेत देता है।",
    "Ketu": "केतु (Ketu): आध्यात्मिकता, गहरी सोच, अंतर्ज्ञान और जीवन का आध्यात्मिक निचोड़ है।",
}

PLANET_EXPLANATIONS_EN = {
    "Sun": "Sun: Vitality, self-respect, leadership, and fatherly energy.",
    "Moon": "Moon: Governs your emotional core, instincts, and peace of mind.",
    "Mars": "Mars: Represents courage, initiative, drive, and physical vitality.",
    "Mercury": "Mercury: Powers analytical intellect, business decisions, and speech.",
    "Jupiter": "Jupiter: Illuminates wisdom, fortune, mentorship, and spiritual grace.",
    "Venus": "Venus: Harmonizes relationships, artistic taste, and lifestyle comfort.",
    "Saturn": "Saturn: Instills perseverance, discipline, career karma, and patience.",
    "Rahu": "Rahu: Governs unconventional innovation, ambition, and sudden growth.",
    "Ketu": "Ketu: Connects with detachment, spiritual depth, and inner wisdom.",
}

PLANET_NAMES_HI = {
    "Sun": "सूर्य",
    "Moon": "चंद्रमा",
    "Mars": "मंगल",
    "Mercury": "बुध",
    "Jupiter": "गुरु",
    "Venus": "शुक्र",
    "Saturn": "शनि",
    "Rahu": "राहु",
    "Ketu": "केतु",
}

RASHI_NAMES_HI = [
    "मेष (Aries)", "वृषभ (Taurus)", "मिथुन (Gemini)", "कर्क (Cancer)",
    "सिंह (Leo)", "कन्या (Virgo)", "तुला (Libra)", "वृश्चिक (Scorpio)",
    "धनु (Sagittarius)", "मकर (Capricorn)", "कुंभ (Aquarius)", "मीन (Pisces)",
]

DIGNITY_NAMES_HI = {
    "Exalted": "उच्च (शुभ)",
    "Debilitated": "नीच (सतर्क)",
    "Own Sign": "स्वराशि",
    "Friendly": "मित्र राशि",
    "Neutral / Mixed": "सामान्य",
}

HOUSE_THEMES_HI = {
    1: "स्वभाव, स्वास्थ्य और व्यक्तित्व (Personality & Health)",
    2: "धन, परिवार और वाणी (Wealth & Speech)",
    3: "साहस, पराक्रम और भाई-बहन (Courage & Siblings)",
    4: "घर, माता और मन की शांति (Home & Peace of Mind)",
    5: "शिक्षा, बुद्धि और संतान (Intellect & Children)",
    6: "रोग, ऋण और दिनचर्या (Health & Daily Routine)",
    7: "विवाह, जीवनसाथी और साझेदारी (Marriage & Partnership)",
    8: "आयु, शोध और अचानक परिवर्तन (Longevity & Research)",
    9: "भाग्य, धर्म और उच्च शिक्षा (Luck, Dharma & Travel)",
    10: "करियर, पद-प्रतिष्ठा और कर्म (Career, Status & Action)",
    11: "लाभ, नेटवर्क और इच्छा पूर्ति (Gains & Aspirations)",
    12: "खर्च, विदेश यात्रा और आत्म-चिंतन (Expenses & Liberation)",
}


class AstroPDF(FPDF):
    def __init__(self, is_hindi: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_hindi = is_hindi
        if Path(FONT_REGULAR).exists() and Path(FONT_BOLD).exists():
            self.add_font("FreeSans", "", FONT_REGULAR)
            self.add_font("FreeSans", "B", FONT_BOLD)
            self.font_family_name = "FreeSans"
        else:
            self.font_family_name = "Helvetica"

    def header(self):
        self.set_font(self.font_family_name, "B", 10)
        self.set_text_color(180, 83, 9)
        title = "एस्ट्रो (ASTRO) · संपूर्ण वैदिक एवं लाल किताब जन्म रिपोर्ट" if self.is_hindi else "ASTRO · Complete Vedic & Lal Kitab Birth Chart Report"
        self.cell(0, 7, title, align="L")
        self.set_font(self.font_family_name, "", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 7, "Developed by Shivang Saxena", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(245, 158, 11)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font(self.font_family_name, "", 8)
        self.set_text_color(148, 163, 184)
        left_text = "सटीक गणना: स्विस एफिमरिस (लाहिड़ी अयनांश)" if self.is_hindi else "Calculated via Swiss Ephemeris (Chitrapaksha Lahiri Ayanamsa)"
        self.cell(0, 6, left_text, align="L")
        page_str = f"पृष्ठ {self.page_no()}" if self.is_hindi else f"Page {self.page_no()}"
        self.cell(0, 6, page_str, align="R")


def generate_kundli_pdf(bundle: dict[str, Any], lang: str = "en") -> bytes:
    is_hindi = str(lang).lower().startswith("hi")
    member = bundle["member"]
    chart = bundle["chart"]
    dashas = bundle["dashas"]
    ghar_preds = bundle.get("ghar_predictions", [])

    pdf = AstroPDF(is_hindi=is_hindi)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    fn = pdf.font_family_name

    # Title Banner
    m_name = member.get("name", "User")
    m_dob = member.get("dob", "1990-01-01")
    m_tob = member.get("birth_time") or member.get("tob", "12:00")
    m_place = member.get("place_name") or member.get("place", "New Delhi")
    m_lat = float(member.get("latitude") if member.get("latitude") is not None else member.get("lat", 0.0))
    m_lon = float(member.get("longitude") if member.get("longitude") is not None else member.get("lon", 0.0))

    pdf.set_font(fn, "B", 16)
    pdf.set_text_color(245, 158, 11)
    main_title = f"जन्म पत्रिका एवं संपूर्ण जीवन योजना — {m_name}" if is_hindi else f"Birth Horoscope & Complete Life Plan — {m_name}"
    pdf.cell(pdf.epw, 9, main_title, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font(fn, "", 9.5)
    pdf.set_text_color(51, 65, 85)
    if is_hindi:
        meta_line1 = (
            f"जन्म तिथि: {m_dob} | समय: {m_tob} | "
            f"स्थान: {m_place} ({m_lat:.2f}°N, {m_lon:.2f}°E)"
        )
        meta_line2 = (
            f"लग्न राशि: {chart['ascendant']['rashi']} ({chart['ascendant']['dms']}) | "
            f"अयनांश (लाहिड़ी): {chart['ayanamsa']} | स्तर: पूर्ण योजना (अनलॉक)"
        )
    else:
        meta_line1 = (
            f"Date of Birth: {m_dob} | Time: {m_tob} | "
            f"Place: {m_place} ({m_lat:.2f}°N, {m_lon:.2f}°E)"
        )
        meta_line2 = (
            f"Ascendant (Lagna): {chart['ascendant']['rashi']} ({chart['ascendant']['dms']}) | "
            f"Lahiri Ayanamsa: {chart['ayanamsa']} | Status: Full Plan (Unlocked)"
        )
    pdf.cell(pdf.epw, 6, meta_line1, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(pdf.epw, 6, meta_line2, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Section 1: Planetary Positions
    pdf.set_font(fn, "B", 12)
    pdf.set_text_color(180, 83, 9)
    pdf.cell(pdf.epw, 7, "1. ग्रह स्थिति एवं भाव (Planetary Placements)" if is_hindi else "1. Planetary Placements (Sidereal Lahiri)", new_x="LMARGIN", new_y="NEXT")

    # Table Header
    pdf.set_font(fn, "B", 8.5)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_text_color(15, 23, 42)
    cols = [
        ("ग्रह (Planet)", 26),
        ("भाव (House)", 18),
        ("राशि (Sign)", 40),
        ("अंश (Degree)", 26),
        ("नक्षत्र (Star)", 42),
        ("अवस्था (State)", 38),
    ] if is_hindi else [
        ("Planet", 26),
        ("House", 18),
        ("Zodiac Sign", 40),
        ("Degree", 26),
        ("Nakshatra", 42),
        ("Dignity", 38),
    ]
    for name, w in cols:
        pdf.cell(w, 6.5, name, border=1, fill=True, align="C")
    pdf.ln()

    # Table Rows
    pdf.set_font(fn, "", 8)
    pdf.set_text_color(30, 41, 59)
    for p in chart["planets"]:
        retro = " (व)" if (p["retrograde"] and is_hindi) else (" (R)" if p["retrograde"] else "")
        p_name = f"{PLANET_NAMES_HI.get(p['planet'], p['planet'])}{retro}" if is_hindi else f"{p['planet']}{retro}"
        h_str = f"घर {p['house']}" if is_hindi else f"House {p['house']}"
        r_str = RASHI_NAMES_HI[p["sign_index"] - 1] if is_hindi else p["rashi"]
        deg_str = p["dms"]
        nak_str = f"{p['nakshatra']} (पद {p['pada']})" if is_hindi else f"{p['nakshatra']} (P{p['pada']})"
        dig_str = DIGNITY_NAMES_HI.get(p["dignity"], p["dignity"]) if is_hindi else p["dignity"]

        pdf.cell(26, 6, p_name, border=1, align="L")
        pdf.cell(18, 6, h_str, border=1, align="C")
        pdf.cell(40, 6, r_str, border=1, align="L")
        pdf.cell(26, 6, deg_str, border=1, align="C")
        pdf.cell(42, 6, nak_str, border=1, align="L")
        pdf.cell(38, 6, dig_str, border=1, align="L")
        pdf.ln()

    pdf.ln(3)

    # Section 2: Conversational Planet Guide (Easy Explanation)
    pdf.set_font(fn, "B", 10.5)
    pdf.set_text_color(180, 83, 9)
    pdf.cell(pdf.epw, 6, "सरल भाषा में ग्रहों का प्रभाव (Simple Guide)" if is_hindi else "Simple Guide to Your Key Planets", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(fn, "", 8)
    pdf.set_text_color(51, 65, 85)
    exp_dict = PLANET_EXPLANATIONS_HI if is_hindi else PLANET_EXPLANATIONS_EN
    for pl in ("Sun", "Moon", "Mars", "Jupiter", "Saturn"):
        pdf.multi_cell(pdf.epw, 4.5, f"• {exp_dict[pl]}")

    pdf.ln(3)

    # Section 3: Vimshottari Mahadashas
    pdf.set_font(fn, "B", 12)
    pdf.set_text_color(180, 83, 9)
    pdf.cell(pdf.epw, 7, "2. विंशोत्तरी महादशा चक्र (Vimshottari Dasha Periods)" if is_hindi else "2. Vimshottari Mahadasha Timeline (120 Years)", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font(fn, "", 8)
    pdf.set_text_color(30, 41, 59)
    for md in dashas.get("mahadashas", []):
        mark = " ★ [वर्तमान में सक्रिय]" if (md.get("is_current") and is_hindi) else (" ★ [CURRENTLY RUNNING]" if md.get("is_current") else "")
        pl_label = PLANET_NAMES_HI.get(md["planet"], md["planet"]) if is_hindi else md["planet"]
        yrs_label = f"{md['duration_years']} वर्ष" if is_hindi else f"{md['duration_years']} yrs"
        pdf.cell(
            pdf.epw,
            5.2,
            f"• {pl_label:10s} :  {md['start_date']}  से  {md['end_date']}  ({yrs_label}){mark}",
            new_x="LMARGIN",
            new_y="NEXT",
        )

    pdf.ln(3)

    # Section 4: 12 Houses Analysis & Personalized Lal Kitab Remedies
    pdf.set_font(fn, "B", 12)
    pdf.set_text_color(180, 83, 9)
    pdf.cell(pdf.epw, 7, "3. संपूर्ण 12 भावों का फलादेश एवं लाल किताब उपाय" if is_hindi else "3. Comprehensive 12 Houses Analysis & Lal Kitab Remedies", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font(fn, "", 8)
    for gp in ghar_preds:
        h_num = gp["house"]
        theme = HOUSE_THEMES_HI.get(h_num, gp["theme"]) if is_hindi else gp["theme"]
        pred_text = gp["prediction"]
        remedy_text = gp.get("upay", "")

        pdf.set_font(fn, "B", 8.5)
        pdf.set_text_color(15, 23, 42)
        h_title = f"भाव {h_num} — {theme}" if is_hindi else f"House {h_num} — {theme}"
        pdf.cell(pdf.epw, 5, h_title, new_x="LMARGIN", new_y="NEXT")

        pdf.set_font(fn, "", 7.8)
        pdf.set_text_color(51, 65, 85)
        analysis_label = "विश्लेषण: " if is_hindi else "Analysis: "
        pdf.multi_cell(pdf.epw, 4.2, f"{analysis_label}{pred_text}")

        if remedy_text:
            pdf.set_font(fn, "B", 7.8)
            pdf.set_text_color(180, 83, 9)
            remedy_label = "सुझावित उपाय (Lal Kitab Remedy): " if is_hindi else "Recommended Remedy: "
            pdf.multi_cell(pdf.epw, 4.2, f"{remedy_label}{remedy_text}")

        pdf.ln(1.5)

    pdf.ln(3)

    # Section 4: 9 Ancestral Debts (लाल किताब 9 ऋण)
    debts = bundle.get("ancestral_debts") or []
    if debts:
        pdf.set_font(fn, "B", 12)
        pdf.set_text_color(180, 83, 9)
        pdf.cell(pdf.epw, 7, "4. लाल किताब के 9 ऋण एवं पितृ दोष विश्लेषण" if is_hindi else "4. Lal Kitab 9 Ancestral Debts Analysis", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font(fn, "", 8)
        active_debts = [d for d in debts if d.get("is_active")]
        if not active_debts:
            pdf.set_font(fn, "", 8)
            pdf.set_text_color(22, 101, 52)
            pdf.cell(pdf.epw, 5, "• कुंडली में कोई गंभीर पितृ अथवा पूर्वज ऋण सक्रिय नहीं है। समस्त पूर्वज कृपा बनी हुई है।" if is_hindi else "• No severe ancestral debts detected. Native carries favorable ancestral blessings.", new_x="LMARGIN", new_y="NEXT")
        else:
            for d in active_debts:
                pdf.set_font(fn, "B", 8.5)
                pdf.set_text_color(185, 28, 28)
                d_name = d["name_hi"] if is_hindi else d["name"]
                pdf.cell(pdf.epw, 5, f"• {d_name} (सक्रिय / Active)", new_x="LMARGIN", new_y="NEXT")

                pdf.set_font(fn, "", 7.8)
                pdf.set_text_color(51, 65, 85)
                symp = d["symptoms_hi"] if is_hindi else d["symptoms_en"]
                pdf.multi_cell(pdf.epw, 4.2, f"लक्षण / Sign: {symp}")

                pdf.set_font(fn, "B", 7.8)
                pdf.set_text_color(180, 83, 9)
                col_rem = d["remedy_hi"] if is_hindi else d["remedy_en"]
                pdf.multi_cell(pdf.epw, 4.2, f"सामूहिक पारिवारिक उपाय: {col_rem}")
                pdf.ln(1.5)

    pdf.ln(3)

    # Section 5: Varshphal Parhez & Precautions (वर्षफल परहेज व 40-43 दिन के नियम)
    parhez = bundle.get("parhez") or {}
    if parhez:
        pdf.set_font(fn, "B", 12)
        pdf.set_text_color(180, 83, 9)
        pdf.cell(pdf.epw, 7, f"5. वर्षफल परहेज एवं 40-43 दिवसीय नियम (आयु {parhez.get('running_age', '')} वर्ष)" if is_hindi else f"5. Lal Kitab Annual Precautions & 40-43 Day Rules (Age {parhez.get('running_age', '')})", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font(fn, "B", 8.5)
        pdf.set_text_color(185, 28, 28)
        pdf.cell(pdf.epw, 5, "क्या न करें (सख्त परहेज / Strict Don'ts):" if is_hindi else "Strict Prohibitions (Don'ts):", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font(fn, "", 7.8)
        pdf.set_text_color(51, 65, 85)
        donts = parhez.get("dont_list_hi" if is_hindi else "dont_list_en", [])
        for item in donts:
            pdf.multi_cell(pdf.epw, 4.2, f"  ✗ {item}")

        pdf.ln(1)
        pdf.set_font(fn, "B", 8.5)
        pdf.set_text_color(22, 101, 52)
        pdf.cell(pdf.epw, 5, "40-43 दिवसीय उपाय नियम (Rules of Remedy):" if is_hindi else "Lal Kitab 40-43 Day Rules:", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font(fn, "", 7.8)
        pdf.set_text_color(51, 65, 85)
        rules = parhez.get("day_rules_hi" if is_hindi else "day_rules_en", [])
        for r in rules:
            pdf.multi_cell(pdf.epw, 4.2, f"  ✓ {r}")

    pdf.ln(3)
    pdf.set_font(fn, "B", 8)
    pdf.set_text_color(100, 116, 139)
    notice = (
        "नोट: यह रिपोर्ट स्विस एफिमरिस द्वारा प्राप्त खगोलीय गणनाओं पर आधारित है। उपाय पारंपरिक मार्गदर्शन हेतु हैं।"
        if is_hindi else
        "Note: Planetary positions are calculated using double-precision Swiss Ephemeris. Remedies are traditional guidance."
    )
    pdf.cell(pdf.epw, 5, notice, align="C", new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())


def generate_order_invoice_pdf(order: dict[str, Any], items: list[dict[str, Any]], account: dict[str, Any]) -> bytes:
    pdf = AstroPDF(is_hindi=False)
    pdf.add_page()
    fn = pdf.font_family_name

    pdf.set_font(fn, "B", 15)
    pdf.cell(pdf.epw, 10, "ASTRO & GDV Panel - Tax Invoice", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(fn, "", 10)
    pdf.cell(pdf.epw, 6, f"Order #: {order['order_number']} | Date: {order['created_at'][:10]}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(pdf.epw, 6, f"Customer: {account['name']} ({account.get('email') or account.get('phone')})", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(pdf.epw, 6, f"Payment Ref: {order['razorpay_payment_id'] or order['razorpay_order_id']} | Status: {order['payment_status']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font(fn, "B", 11)
    pdf.cell(pdf.epw, 7, "Line Items", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(fn, "", 10)
    for it in items:
        pdf.cell(pdf.epw, 6, f"- {it['title']} x{it['quantity']}  =  INR {it['unit_price'] * it['quantity']}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    pdf.set_font(fn, "B", 11)
    pdf.cell(pdf.epw, 7, f"Subtotal: INR {order['subtotal']} | Discount: INR {order['discount']} | Credits: INR {order['credits_used']} | GST: INR {order['gst']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(pdf.epw, 8, f"Total Paid: INR {order['total_amount']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    return bytes(pdf.output())
