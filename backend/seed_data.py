"""Initial database seed data mirroring GDVPanel + AstroScience entities."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone

from .database import db_session, init_db


def hash_password(password: str) -> str:
    return hashlib.sha256(f"astro_unified_salt::{password}".encode("utf-8")).hexdigest()


PLACES_SEED = [
    ("New Delhi", "Central Delhi", "Delhi", "India", "110001", 28.6139, 77.2090, 5.5),
    ("Mayapuri, West Delhi", "West Delhi", "Delhi", "India", "110064", 28.6239, 77.1193, 5.5),
    ("Gurugram", "Gurugram", "Haryana", "India", "122001", 28.4595, 77.0266, 5.5),
    ("Noida", "Gautam Buddha Nagar", "Uttar Pradesh", "India", "201301", 28.5355, 77.3910, 5.5),
    ("Faridabad", "Faridabad", "Haryana", "India", "121001", 28.4089, 77.3178, 5.5),
    ("Ghaziabad", "Ghaziabad", "Uttar Pradesh", "India", "201001", 28.6692, 77.4538, 5.5),
    ("Mumbai", "Mumbai City", "Maharashtra", "India", "400001", 19.0760, 72.8777, 5.5),
    ("Pune", "Pune", "Maharashtra", "India", "411001", 18.5204, 73.8567, 5.5),
    ("Nagpur", "Nagpur", "Maharashtra", "India", "440001", 21.1458, 79.0882, 5.5),
    ("Nashik", "Nashik", "Maharashtra", "India", "422001", 19.9975, 73.7898, 5.5),
    ("Jaipur", "Jaipur", "Rajasthan", "India", "302001", 26.9124, 75.7873, 5.5),
    ("Jodhpur", "Jodhpur", "Rajasthan", "India", "342001", 26.2389, 73.0243, 5.5),
    ("Udaipur", "Udaipur", "Rajasthan", "India", "313001", 24.5854, 73.7125, 5.5),
    ("Kota", "Kota", "Rajasthan", "India", "324001", 25.2138, 75.8648, 5.5),
    ("Bengaluru", "Bengaluru Urban", "Karnataka", "India", "560001", 12.9716, 77.5946, 5.5),
    ("Mysuru", "Mysuru", "Karnataka", "India", "570001", 12.2958, 76.6394, 5.5),
    ("Mangaluru", "Dakshina Kannada", "Karnataka", "India", "575001", 12.9141, 74.8560, 5.5),
    ("Varanasi", "Varanasi", "Uttar Pradesh", "India", "221001", 25.3176, 82.9739, 5.5),
    ("Lucknow", "Lucknow", "Uttar Pradesh", "India", "226001", 26.8467, 80.9462, 5.5),
    ("Kanpur", "Kanpur Nagar", "Uttar Pradesh", "India", "208001", 26.4499, 80.3319, 5.5),
    ("Agra", "Agra", "Uttar Pradesh", "India", "282001", 27.1767, 78.0081, 5.5),
    ("Prayagraj", "Prayagraj", "Uttar Pradesh", "India", "211001", 25.4358, 81.8463, 5.5),
    ("Meerut", "Meerut", "Uttar Pradesh", "India", "250001", 28.9845, 77.7064, 5.5),
    ("Ayodhya", "Ayodhya", "Uttar Pradesh", "India", "224123", 26.7922, 82.1998, 5.5),
    ("Mathura", "Mathura", "Uttar Pradesh", "India", "281001", 27.4924, 77.6737, 5.5),
    ("Ahmedabad", "Ahmedabad", "Gujarat", "India", "380001", 23.0225, 72.5714, 5.5),
    ("Surat", "Surat", "Gujarat", "India", "395001", 21.1702, 72.8311, 5.5),
    ("Vadodara", "Vadodara", "Gujarat", "India", "390001", 22.3072, 73.1812, 5.5),
    ("Rajkot", "Rajkot", "Gujarat", "India", "360001", 22.3039, 70.8022, 5.5),
    ("Kolkata", "Kolkata", "West Bengal", "India", "700001", 22.5726, 88.3639, 5.5),
    ("Siliguri", "Darjeeling", "West Bengal", "India", "734001", 26.7271, 88.3953, 5.5),
    ("Chennai", "Chennai", "Tamil Nadu", "India", "600001", 13.0827, 80.2707, 5.5),
    ("Coimbatore", "Coimbatore", "Tamil Nadu", "India", "641001", 11.0168, 76.9558, 5.5),
    ("Madurai", "Madurai", "Tamil Nadu", "India", "625001", 9.9252, 78.1198, 5.5),
    ("Hyderabad", "Hyderabad", "Telangana", "India", "500001", 17.3850, 78.4867, 5.5),
    ("Visakhapatnam", "Visakhapatnam", "Andhra Pradesh", "India", "530001", 17.6868, 83.2185, 5.5),
    ("Vijayawada", "Krishna", "Andhra Pradesh", "India", "520001", 16.5062, 80.6480, 5.5),
    ("Chandigarh", "Chandigarh", "Chandigarh", "India", "160001", 30.7333, 76.7794, 5.5),
    ("Amritsar", "Amritsar", "Punjab", "India", "143001", 31.6340, 74.8723, 5.5),
    ("Ludhiana", "Ludhiana", "Punjab", "India", "141001", 30.9010, 75.8573, 5.5),
    ("Jalandhar", "Jalandhar", "Punjab", "India", "144001", 31.3260, 75.5762, 5.5),
    ("Patna", "Patna", "Bihar", "India", "800001", 25.5941, 85.1376, 5.5),
    ("Ranchi", "Ranchi", "Jharkhand", "India", "834001", 23.3441, 85.3096, 5.5),
    ("Bhopal", "Bhopal", "Madhya Pradesh", "India", "462001", 23.2599, 77.4126, 5.5),
    ("Indore", "Indore", "Madhya Pradesh", "India", "452001", 22.7196, 75.8577, 5.5),
    ("Gwalior", "Gwalior", "Madhya Pradesh", "India", "474001", 26.2183, 78.1828, 5.5),
    ("Jabalpur", "Jabalpur", "Madhya Pradesh", "India", "482001", 23.1815, 79.9864, 5.5),
    ("Raipur", "Raipur", "Chhattisgarh", "India", "492001", 21.2514, 81.6296, 5.5),
    ("Bhubaneswar", "Khordha", "Odisha", "India", "751001", 20.2961, 85.8245, 5.5),
    ("Guwahati", "Kamrup", "Assam", "India", "781001", 26.1445, 91.7362, 5.5),
    ("Kochi", "Ernakulam", "Kerala", "India", "682001", 9.9312, 76.2673, 5.5),
    ("Thiruvananthapuram", "Thiruvananthapuram", "Kerala", "India", "695001", 8.5241, 76.9366, 5.5),
    ("Dehradun", "Dehradun", "Uttarakhand", "India", "248001", 30.3165, 78.0322, 5.5),
    ("Haridwar", "Haridwar", "Uttarakhand", "India", "249401", 29.9457, 78.1642, 5.5),
    ("Shimla", "Shimla", "Himachal Pradesh", "India", "171001", 31.1048, 77.1734, 5.5),
    ("Jammu", "Jammu", "Jammu & Kashmir", "India", "180001", 32.7266, 74.8570, 5.5),
    ("Srinagar", "Srinagar", "Jammu & Kashmir", "India", "190001", 34.0837, 74.7973, 5.5),
    ("Panaji", "North Goa", "Goa", "India", "403001", 15.4909, 73.8278, 5.5),
    ("Kathmandu", "Kathmandu", "Bagmati", "Nepal", "44600", 27.7172, 85.3240, 5.75),
    ("London", "Greater London", "England", "United Kingdom", "EC1A", 51.5074, -0.1278, 0.0),
    ("New York", "New York", "NY", "United States", "10001", 40.7128, -74.0060, -5.0),
    ("Los Angeles", "Los Angeles", "CA", "United States", "90001", 34.0522, -118.2437, -8.0),
    ("Toronto", "Ontario", "ON", "Canada", "M5H", 43.6532, -79.3832, -5.0),
    ("Dubai", "Dubai", "Dubai", "UAE", "00000", 25.2048, 55.2708, 4.0),
    ("Singapore", "Singapore", "Central", "Singapore", "018956", 1.3521, 103.8198, 8.0),
    ("Sydney", "New South Wales", "NSW", "Australia", "2000", -33.8688, 151.2093, 10.0),
]


def seed_all() -> None:
    init_db()
    now = datetime.now(timezone.utc).isoformat()
    next_year = (datetime.now(timezone.utc) + timedelta(days=365)).strftime("%Y-%m-%d")

    with db_session() as conn:
        # Ensure expanded pan-India & global place index even on pre-existing DBs
        existing_places = {r[0] for r in conn.execute("SELECT place_name FROM places_pincodes").fetchall()}
        missing_places = [p for p in PLACES_SEED if p[0] not in existing_places]
        if missing_places:
            conn.executemany(
                """
                INSERT INTO places_pincodes
                (place_name, district, state, country, pincode, latitude, longitude, tz_offset)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                missing_places,
            )

        if conn.execute("SELECT COUNT(*) FROM registration_plans").fetchone()[0] > 0:
            return

        # 2. GDVPanel Plans + Consumer Premium Plans
        plans = [
            (
                1,
                "Gold Registration + Advance Course",
                "portal_reg",
                "GOLD PLAN REGISTRATION",
                "778",
                3,
                5100,
                2100,
                1296,
                8496,
                45,
                1,
                json.dumps([
                    "View Kundali Charts, Desk Values and Planet status",
                    "View Mahadasha and Lal Kitab Dasha predictions",
                    "Kundali based Q&A",
                    "Save Kundali profiles in cloud folders",
                    "Login allowed on 1 system at a time",
                    "Registration Fee: ₹5,100 + Recurring: ₹2,100/mo = ₹7,200 (Excl. GST)",
                ]),
                0,
            ),
            (
                2,
                "Platinum Registration + Advance Course",
                "portal_reg",
                "PLATINUM PLAN REGISTRATION",
                "777",
                4,
                31000,
                3100,
                0,
                34100,
                45,
                2,
                json.dumps([
                    "All features of Gold Registration Plan",
                    "Vashist Jyotish 1 Year file (PDF)",
                    "Download & Redownload unlimited Kundali files",
                    "Occupation, Health, Married Life, Child etc. (PDF)",
                    "Simultaneous login allowed on 2 systems",
                    "Registration Fee: ₹31,000 + Recurring: ₹3,100/mo = ₹34,100 (Incl. GST)",
                ]),
                1,
            ),
            (
                101,
                "AstroScience Premium — 3 Months",
                "consumer_sub",
                "APP_PREMIUM_3M",
                "301",
                101,
                499,
                0,
                0,
                499,
                90,
                5,
                json.dumps([
                    "All Free Plan Features (Charts, Current Dasha, 12 Ghar)",
                    "All Past & Future Mahadasha, Antardasha & Lal Kitab Predictions",
                    "All Horoscope Categories (Marriage, Child, Foreign Trip, Property)",
                    "Full Lal Kitab Remedies (Upay) & Kundli Vivaran Predictions",
                ]),
                0,
            ),
            (
                102,
                "Lal Kitab Amrit — 1 Year Premium",
                "consumer_sub",
                "APP_PREMIUM_1Y",
                "136",
                102,
                1499,
                0,
                0,
                1499,
                365,
                5,
                json.dumps([
                    "All 3-Month Premium Features for 1 Full Year",
                    "Unlimited Vivaran Predictions & Horoscope Categories",
                    "Downloadable Yearly Varshphal & Remedy Guidance",
                ]),
                0,
            ),
            (
                137,
                "Lal Kitab Amrit — 2 Years Premium",
                "consumer_sub",
                "APP_PREMIUM_2Y",
                "137",
                137,
                2499,
                0,
                0,
                2499,
                730,
                5,
                json.dumps([
                    "2 Years Full Premium Access per Selected Profile",
                    "All Past/Future Dasha Timelines, Upay Remedies & Vivaran Tiles",
                    "Priority Acharya Consultation & Digital Lal Kitab PDF",
                ]),
                1,
            ),
        ]
        conn.executemany(
            """
            INSERT INTO registration_plans
            (id, name, plan_scope, crm_name, crm_sku, mapped_subscription_plan_id,
             base_fee, recurring_fee, gst, total_price, duration_days, max_systems,
             features_json, is_popular)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            plans,
        )

        # 3. Course & 14 Lectures matching GDVPanel API structure
        conn.execute(
            """
            INSERT INTO courses
            (id, title, sku, instructor_name, instructor_bio, rating, reviews, students,
             duration_days, lectures_count, level, language, price, original_price, phone,
             description, learning_outcomes_json, requirements_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                1,
                "Prarambhik Vashistha Jyotish",
                "548",
                "Gurudev G.D Vashist",
                "40+ years of experience. Expertise in Astrology",
                "5.00",
                1247,
                1200,
                90,
                14,
                "Beginners",
                "Hindi",
                11000,
                21000,
                "+91-9266469991",
                "To learn astrology, all you need is the right start — and this is it. Learn the science and become a Vashist Astrologer (90-day online portal access + Lal Kitab Amrit Part 1 book).",
                json.dumps([
                    "राशी, ग्रह और घरों की जानकारी (फरमान-1)",
                    "लाल किताब व्याकरण और मूल सिद्धांत",
                    "35 साला चक्कर, सोए हुए ग्रह और भाव",
                    "शुभ-अशुभ ग्रह और मंगल बद विश्लेषण",
                    "पक्के घर 1 से 12 के नियम और उपाय",
                ]),
                json.dumps([
                    "Designed for curious minds and aspiring astrologers seeking structured Lal Kitab & Vashist Jyotish foundations."
                ]),
            ),
        )
        lecture_titles = [
            ("फरमान-1: राशी, ग्रह और कुंडली आधार", "01:05:26", 1),
            ("वशिष्ठ ज्योतिष फरमान - 2: भाव व दृष्टि नियम", "00:58:00", 0),
            ("वशिष्ठ ज्योतिष फरमान - 3: सोए हुए ग्रह", "00:59:52", 0),
            ("वशिष्ठ ज्योतिष फरमान - 4: 35 साला चक्कर", "01:08:52", 0),
            ("वशिष्ठ ज्योतिष फरमान - 5: मंगल नेक व बद", "01:44:00", 0),
            ("वशिष्ठ ज्योतिष फरमान - 6: वर्षफल निर्माण", "01:39:59", 0),
            ("वशिष्ठ ज्योतिष फरमान - 7: पक्के घर 1 से 4", "01:35:33", 0),
            ("वशिष्ठ ज्योतिष फरमान - 8: पक्के घर 5 से 8", "01:35:36", 0),
            ("वशिष्ठ ज्योतिष फरमान - 9: पक्के घर 9 से 12", "01:32:25", 0),
            ("वशिष्ठ ज्योतिष फरमान - 10: ऋण व पितृ दोष", "01:28:43", 0),
            ("वशिष्ठ ज्योतिष फरमान - 11: विवाह व संतान योग", "01:31:33", 0),
            ("वशिष्ठ ज्योतिष फरमान - 12: व्यापार व करियर", "01:29:53", 0),
            ("वशिष्ठ ज्योतिष फरमान - 13: स्वास्थ्य व दशा फल", "01:30:49", 0),
            ("वशिष्ठ ज्योतिष फरमान - 14: सटीक लाल किताब उपाय", "01:09:39", 0),
        ]
        for idx, (lt, dur, prev) in enumerate(lecture_titles, 1):
            conn.execute(
                """
                INSERT INTO course_videos
                (id, course_id, sequence_no, section_title, title, duration, is_preview, summary)
                VALUES (?, 1, ?, 'फरमान', ?, ?, ?, ?)
                """,
                (idx + 6, idx, lt, dur, prev, f"Lecture {idx} covering practical Lal Kitab & Vashist Jyotish principles."),
            )

        # 4. Horoscope Categories matching APK IDs (3, 5, 7, 10, 44, etc.)
        cats = [
            (3, "marriage", "Marriage & Love", "विवाह और प्रेम", 1, "marriage", "Marital harmony, partner traits, love vs arranged yogas"),
            (5, "child", "Child & Progeny", "संतान सुख", 1, "child", "Progeny prospects, timing, and child well-being"),
            (44, "matchmaking", "Match Making", "कुंडली मिलान", 1, None, "36-point Ashtakoot Guna Milan & Dosha analysis"),
            (7, "foreign-trip", "Foreign Travel", "विदेश यात्रा", 1, None, "9th & 12th house overseas settlement & travel periods"),
            (10, "property", "Property & Vehicle", "मकान और वाहन योग", 1, None, "4th house real estate, home & vehicle timing"),
            (1, "career", "Career & Business", "करियर और व्यापार", 1, None, "10th house profession, job change & business profits"),
            (2, "health", "Health & Vitality", "स्वास्थ्य", 1, None, "6th/8th house constitution & preventive remedies"),
            (4, "finance", "Wealth & Finance", "धन और वित्त", 1, None, "2nd & 11th house Dhan Yoga and savings cycles"),
        ]
        conn.executemany(
            """
            INSERT INTO horoscope_categories
            (id, slug, title, title_hi, requires_premium, has_sub_dialog, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            cats,
        )

        # 5. Products, Remedies (UpayId linked), Books & Free Bhajans/Mantras
        prods = [
            (1, "remedy", "Remedies & Yantras", "Surya Tamra Yantra (Brass/Copper)", 550, 750, "REM-101", 101, 0, 0, 0.0, 1, "Energized Solar Yantra for 1st/10th house Sun strength."),
            (2, "remedy", "Remedies & Yantras", "Chandra Pearl Moti Mala", 900, 1200, "REM-102", 102, 0, 0, 0.0, 1, "Calms lunar afflictions and mental stress."),
            (3, "remedy", "Remedies & Yantras", "Mangal Bad Nivaran Kit", 1100, 1500, "REM-103", 103, 0, 0, 0.0, 1, "Traditional Lal Kitab Mars remedy set with honey-pot & Sindoor."),
            (4, "remedy", "Remedies & Yantras", "Budh Durga Beesa Yantra", 750, 999, "REM-104", 104, 0, 0, 0.0, 1, "Strengthens Mercury speech, intellect, and business decisions."),
            (5, "remedy", "Remedies & Yantras", "Guru Kesar Tilak & Pukhraj Kit", 1450, 1900, "REM-105", 105, 0, 0, 0.0, 1, "Supports Jupiter wisdom, education, and auspicious growth."),
            (6, "book", "Kundli & Books", "Lal Kitab Amrit - Vashist Jyotish (Part 1)", 850, 1100, "BK-201", 106, 0, 0, 0.0, 1, "Printed foundational Lal Kitab Amrit treatise by Gurudev G.D. Vashist."),
            (7, "kit", "Kundli & Books", "Personalized Hardbound Vashist Kundli File", 2100, 2600, "LK-301", 0, 12, 0, 0.0, 1, "Complete printed & PDF Lal Kitab Amrit life predictions + personalized Upay."),
            (8, "service", "Kalyankari Puja", "Kalyankari Navgrah Shanti Puja", 3100, 4100, "PJ-401", 20, 0, 0, 0.0, 1, "Vedic planetary pacification ritual performed by senior Acharyas."),
            (9, "bhajan", "Bhajans & Mantras", "Gayatri Mantra (108 Chants Sacred Resonance)", 0, 0, "AUD-01", 0, 0, 1, 432.0, 1, "Free devotional Mantra audio — playable without purchase."),
            (10, "mantra", "Bhajans & Mantras", "Maha Mrityunjaya Vedic Chanting", 0, 0, "AUD-02", 0, 0, 1, 528.0, 1, "Free healing Shiva Mantra harmonic audio."),
            (11, "bhajan", "Bhajans & Mantras", "Hanuman Chalisa Instrumental Meditation", 0, 0, "AUD-03", 0, 0, 1, 396.0, 1, "Free peaceful evening prayer composition."),
        ]
        conn.executemany(
            """
            INSERT INTO products
            (id, category_slug, category_name, title, price, mrp, sku, upay_id, plan_type,
             is_audio, audio_freq, in_stock_india, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            prods,
        )

        # 6. Coupons, Acharyas, Blogs, Videos, FAQs
        conn.executemany(
            "INSERT INTO coupons (code, discount_percent, max_discount, description) VALUES (?, ?, ?, ?)",
            [
                ("ASTRO10", 10, 500, "10% off on Store Remedies & Books"),
                ("GURUJI20", 20, 1000, "20% off on Puja & Kundli Files"),
            ],
        )

        conn.executemany(
            "INSERT INTO acharyas (id, name, specialty, languages, experience_years, phone, available, rating) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (1, "Acharya Devendra Sharma", "Lal Kitab & Career Remedies", "Hindi, English", 18, "+91-9821397676", 1, "4.9"),
                (2, "Acharya Meenakshi Joshi", "Marriage, Child & Matchmaking", "Hindi, English, Gujarati", 14, "+91-9266469991", 1, "4.9"),
                (3, "Acharya Raghavendra Shastri", "Varshphal, Vastu & Gemstones", "Hindi, Sanskrit", 22, "+91-9821397676", 1, "4.8"),
            ],
        )

        conn.executemany(
            "INSERT INTO blogs (id, title, category, summary, content, likes, published_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (1, "Understanding Lal Kitab Pakka Ghar (Fixed Houses 1–12)", "Lal Kitab", "How each planet carries a permanent lordship in Lal Kitab independent of sign rulers.", "In Lal Kitab Vashist Jyotish, houses 1 through 12 map to fixed planetary significators (Sun in 1, Jupiter in 2/5/9/12, Mars in 3/8, Moon in 4, Mercury/Ketu in 6, Venus/Mercury in 7, Saturn in 8/10/11, Rahu in 12). Analyzing dormancy ('Soya Grah') and planetary aspects reveals actionable remedies.", 84, "2026-11-10"),
                (2, "How Vimshottari Mahadasha & Antardasha Shape Career Timing", "Vedic Dasha", "Interpreting Moon Nakshatra balance at birth and sub-period activations.", "Vimshottari Dasha divides a 120-year cycle across 9 planets starting from your natal Moon Nakshatra degree. When Mahadasha and Antardasha lords form supportive trines (1/5/9) or angles (1/4/7/10) from Lagna, breakthroughs manifest naturally.", 67, "2026-11-18"),
            ],
        )

        conn.executemany(
            "INSERT INTO videos (id, category, title, duration, is_live, likes, summary) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (1, "Lal Kitab Basics", "Why Planets Become Benefic or Malefic in Birth Charts", "18:40", 0, 142, "Core principles of planetary friendship and house placement."),
                (2, "Weekly Forecast", "Gochar Planetary Transits & Remedies This Month", "24:15", 0, 95, "Real-time transit impact on Moon signs and practical remedies."),
                (3, "Guruji Live", "Live Q&A Session: Prarambhik Jyotish & Career Guidance", "55:00", 1, 310, "Recorded & live interactive studio stream."),
            ],
        )

        conn.executemany(
            "INSERT INTO faqs (id, scope, question, answer) VALUES (?, ?, ?, ?)",
            [
                (1, "portal", "What is the difference between Gold and Platinum GDVPanel plans?", "Gold (₹5,100 reg + ₹2,100/mo) supports single-system login with charts, desk values, and dashas. Platinum (₹31,000 reg + ₹3,100/mo) adds simultaneous 2-system login, unlimited Kundali PDF downloads, and Vashist Jyotish 1-Year files."),
                (2, "app", "How does Free vs. Premium work in the AstroScience app?", "Plans attach per family member profile (PlanId). Free profiles get full Lagan/Gochar/Vashist/Varshphal charts, current running Dashas, and 12 Ghar predictions. Premium unlocks all past/future Dashas, Lal Kitab Remedies (Upay), locked Horoscope Categories, and full Kundli Vivaran predictions."),
                (3, "app", "What happens if I edit a Premium profile's birth details?", "Because a subscription is bound to one birth chart, updating DOB, time, gender, or place on a subscribed profile expires its active PlanId after confirmation."),
            ],
        )

        conn.executemany(
            "INSERT INTO product_reviews (product_id, account_name, rating, review_text, verified_buyer, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            [
                (1, "Vikram Rathore", 5, "लाल किताब अमृत फाइल से मिले उपायों से व्यापार में अभूतपूर्व प्रगति हुई। बहुत सटीक गणना है।", 1, "2026-11-20"),
                (1, "Sunita Mehra", 5, "Excellent personalized report with clear remedies. Guruji's methods are truly divine.", 1, "2026-11-22"),
                (2, "Ramesh Chandra", 5, "सूर्य तांबे का सिक्का उपाय करने के 40 दिन के भीतर कार्यक्षेत्र में स्थिरता आई।", 1, "2026-11-15"),
                (3, "Deepak Verma", 5, "शुद्ध चांदी का चौकोर टुकड़ा बहुत ही उच्च गुणवत्ता का है। सर्टिफाइड प्रोडक्ट।", 1, "2026-11-18"),
                (4, "Pooja Gupta", 5, "मंगल बद किट ने मानसिक तनाव और पारिवारिक कलह को पूर्णतः शांत कर दिया। धन्यवाद वशिष्ठ ज्योतिष।", 1, "2026-11-25"),
            ],
        )

        # 7. Pre-seeded Demo Accounts (Free Consumer, Premium Consumer, Acharya Gold, Acharya Platinum)
        # Note: Distinct sandbox demo accounts, not third-party production credentials.
        pw = hash_password("Demo@1234")
        demo_accounts = [
            # id=1: Consumer account with 1 Free Member + 1 Premium Member
            ("consumer", "Aarav Sharma", "consumer@astro.local", "9800000001", "+91", pw, "user", None, 0, 0, 5, 1, "En", 500, now),
            # id=2: Acharya Gold (1 system limit!)
            ("acharya", "Acharya Gold Demo", "gold@gdvpanel.local", "9800000002", "+91", pw, "acharya", "CRM-GOLD-101", 1, 3, 1, 1, "En", 300, now),
            # id=3: Acharya Platinum (2 systems simultaneous limit + Course #1!)
            ("acharya", "Acharya Platinum Demo", "platinum@gdvpanel.local", "9800000003", "+91", pw, "acharya", "CRM-PLAT-202", 2, 4, 2, 1, "En", 1200, now),
            # id=4: CRM Agent
            ("crm", "Priya Verma (CRM Agent)", "crm@gdvpanel.local", "9800000004", "+91", pw, "crm_agent", "CRM-AG-01", 2, 4, 3, 1, "En", 0, now),
        ]
        conn.executemany(
            """
            INSERT INTO accounts
            (account_type, name, email, phone, country_code, password_hash, role, crm_order_id,
             reg_plan_id, subs_plan_id, max_sessions, is_meet_enabled, language, credits_balance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            demo_accounts,
        )

        # Family Members under Consumer Demo (id=1): Primary Free + Spouse Premium
        conn.executemany(
            """
            INSERT INTO family_members
            (account_id, name, gender, dob, birth_time, place_name, state_name, country_name,
             latitude, longitude, tz_offset, is_primary, plan_id, plan_name, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (1, "Aarav Sharma (Free Profile)", "Male", "1995-08-15", "09:30", "New Delhi", "Delhi", "India", 28.6139, 77.2090, 5.5, 1, 0, "Free Plan", None),
                (1, "Ananya Sharma (Premium Profile)", "Female", "1997-03-22", "14:15", "Jaipur", "Rajasthan", "India", 26.9124, 75.7873, 5.5, 0, 137, "Lal Kitab Amrit - 2 Years", next_year),
                (2, "Client Chart - Rohan Mehta", "Male", "1990-11-04", "06:45", "Mumbai", "Maharashtra", "India", 19.0760, 72.8777, 5.5, 1, 102, "Gold Portal Chart", next_year),
                (3, "Client Chart - Kavya Nair", "Female", "1992-05-19", "18:20", "Bengaluru", "Karnataka", "India", 12.9716, 77.5946, 5.5, 1, 137, "Platinum Unlimited Chart", next_year),
            ],
        )

        # Seed Course Enrollment & Acharya Suggestions
        conn.execute(
            "INSERT INTO course_enrollments (account_id, course_id, enrolled_at, expires_at) VALUES (3, 1, ?, ?)",
            (now, (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()),
        )

        conn.executemany(
            "INSERT INTO acharya_suggestions (member_id, suggestion_type, title, notes, linked_product_id, linked_plan_id, report_summary) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (1, "service", "Recommended: Lal Kitab Amrit 2 Years", "Unlock your upcoming Shani & Guru Antardasha remedies in one tap.", 0, 137, ""),
                (1, "product", "Recommended Remedy: Surya Tamra Yantra", "Acharya Devendra recommends strengthening your Lagna/10th Sun.", 1, 0, ""),
                (1, "file", "Personalized Vashist Kundli Assessment PDF", "Notes from your consultation covering career stability and Venus period.", 0, 0, "Ascendant highlights strong 10th-house activity. Maintain focus on Saturn discipline and morning meditation."),
            ],
        )

        # Saved folders + prediction for Demo account
        conn.execute(
            "INSERT INTO saved_folders (account_id, member_id, name, created_at) VALUES (1, 1, 'Career & Wealth', ?)",
            (now,),
        )
        conn.execute(
            """
            INSERT INTO saved_predictions
            (folder_id, account_id, member_id, title, prediction_type, sentiment, prediction_text, upay_id, upay_text, created_at)
            VALUES (1, 1, 1, 'House 10 Career Yoga', 'Kundli12GharPrediction', 'Positive',
                    'Strong Karma-bhava influence supports leadership and steady institutional recognition.', 101,
                    'Offer water to the rising Sun in a copper vessel and install Surya Tamra Yantra.', ?)
            """,
            (now,),
        )

        conn.executemany(
            "INSERT INTO notifications (account_id, title, body, is_read, created_at) VALUES (?, ?, ?, 0, ?)",
            [
                (1, "Welcome to AstroUnified", "Switch between Aarav (Free) and Ananya (Premium) profiles to inspect exact tier gating.", now),
                (1, "Choghadiya Panchang Ready", "Daily planetary transits and auspicious timings are calculated live for your city.", now),
            ],
        )

        conn.execute(
            "INSERT INTO reward_ledger (account_id, delta, reason, created_at) VALUES (1, 500, 'Welcome Bonus Credits', ?)",
            (now,),
        )

        # Seed Address and Order for Demo Account (Aarav Sharma)
        conn.execute(
            """
            INSERT INTO addresses (account_id, address_type, full_name, phone, line1, line2, pincode, city, state, country)
            VALUES (1, 'Home', 'Aarav Sharma', '9800000001', 'C-11/20 Mayapuri', '', '110064', 'New Delhi', 'Delhi', 'India')
            """
        )
        conn.execute(
            """
            INSERT INTO orders (order_number, account_id, member_id, order_kind, title, subtotal, discount, credits_used, gst, total_amount, payment_method, payment_status, razorpay_order_id, razorpay_payment_id, created_at)
            VALUES ('ORD-2026-8829', 1, 1, 'product', 'Surya Tamra Yantra (Energized)', 550, 0, 0, 0, 550, 'Razorpay Sandbox', 'Paid', 'order_sim_8829', 'pay_sim_8829', ?)
            """,
            (now,),
        )
