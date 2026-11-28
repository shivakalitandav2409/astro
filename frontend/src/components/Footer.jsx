import React from "react";
import { Link } from "react-router-dom";
import { Mail, MapPin, Phone } from "lucide-react";
import { useApp } from "../context/AppContext";

export default function Footer() {
  const { lang } = useApp();
  const isHindi = lang === "हिं";

  return (
    <footer className="mt-16 border-t border-slate-800 bg-slate-950/95 py-8 text-xs text-slate-400">
      <div className="mx-auto grid max-w-7xl gap-8 px-4 md:grid-cols-3">
        {/* Brand & Address */}
        <div>
          <div className="flex items-center gap-2.5">
            <img
              src="/astro-emblem.png"
              alt="ASTRO Logo"
              className="h-8 w-8 rounded-full ring-1 ring-amber-400/50"
            />
            <div>
              <div className="text-sm font-bold text-amber-400">
                {isHindi ? "ASTRO · एस्ट्रो" : "ASTRO"}
              </div>
              <div className="text-[10px] text-slate-400">
                {isHindi ? "सटीक वैदिक एवं लाल किताब ज्योतिष" : "Explore the Cosmos & Destiny"}
              </div>
            </div>
          </div>
          <p className="mt-2.5 leading-relaxed text-slate-400">
            {isHindi
              ? "शुद्ध खगोलीय स्वीस एफिमेरिस (चित्रापक्ष लाहिरी अयनांश) द्वारा संचालित संपूर्ण वैदिक कुंडली, 12 भाव फलकथन एवं लाल किताब उपाय।"
              : "High-precision Swiss Ephemeris Chitrapaksha Lahiri calculations for Vedic horoscopes, 12-house analysis, and Lal Kitab remedies."}
          </p>
          <div className="mt-3 space-y-1 text-[11px] text-slate-400">
            <p className="flex items-center gap-1.5">
              <MapPin className="h-3.5 w-3.5 text-amber-400 shrink-0" /> Plot No. C-11/20, Mayapuri, New Delhi
            </p>
            <p className="flex items-center gap-1.5">
              <Phone className="h-3.5 w-3.5 text-amber-400 shrink-0" /> +91-9266469991
            </p>
            <p className="flex items-center gap-1.5">
              <Mail className="h-3.5 w-3.5 text-amber-400 shrink-0" /> support@astrounified.local
            </p>
          </div>
        </div>

        {/* Core Astrology Services */}
        <div>
          <div className="font-semibold text-slate-200 mb-2.5 text-xs tracking-wider uppercase">
            {isHindi ? "प्रमुख ज्योतिषीय सेवाएं" : "Core Astrology Suite"}
          </div>
          <ul className="space-y-2">
            <li>
              <Link to="/app/kundli" className="hover:text-amber-300 transition">
                {isHindi ? "जन्म कुंडली एवं 12 भाव विवरण" : "Kundli Charts & 12-House Vivaran"}
              </Link>
            </li>
            <li>
              <Link to="/app/dashas" className="hover:text-amber-300 transition">
                {isHindi ? "विंशोत्तरी एवं लाल किताब 35 साला दशा" : "Vimshottari & Lal Kitab 35-Yr Dasha"}
              </Link>
            </li>
            <li>
              <Link to="/app/matchmaking" className="hover:text-amber-300 transition">
                {isHindi ? "36 गुण मिलान एवं मांगलिक विचार" : "36-Point Ashtakoot Matchmaking"}
              </Link>
            </li>
            <li>
              <Link to="/app/panchang" className="hover:text-amber-300 transition">
                {isHindi ? "दैनिक चौघड़िया पंचांग एवं राहु काल" : "Choghadiya Panchang & Rahu Kaal"}
              </Link>
            </li>
          </ul>
        </div>

        {/* Legal & About */}
        <div>
          <div className="font-semibold text-slate-200 mb-2.5 text-xs tracking-wider uppercase">
            {isHindi ? "सूचना एवं नीतियां" : "About & Legal"}
          </div>
          <ul className="space-y-2">
            <li>
              <Link to="/about-us" className="hover:text-amber-300 transition">
                {isHindi ? "हमारे बारे में" : "About Us"}
              </Link>
            </li>
            <li>
              <Link to="/contact-us" className="hover:text-amber-300 transition">
                {isHindi ? "संपर्क करें" : "Contact Us"}
              </Link>
            </li>
            <li>
              <Link to="/privacy-policy" className="hover:text-amber-300 transition">
                {isHindi ? "गोपनीयता नीति (Privacy Policy)" : "Privacy Policy"}
              </Link>
            </li>
            <li>
              <Link to="/terms_and_conditions" className="hover:text-amber-300 transition">
                {isHindi ? "नियम एवं शर्तें (Terms & Conditions)" : "Terms & Conditions"}
              </Link>
            </li>
            <li>
              <Link to="/login" className="hover:text-amber-300 transition">
                {isHindi ? "स्टाफ / आचार्य लॉगिन" : "Staff / Acharya Login"}
              </Link>
            </li>
          </ul>
        </div>
      </div>

      <div className="mx-auto mt-8 max-w-7xl border-t border-slate-800/80 px-4 pt-4 flex flex-col sm:flex-row items-center justify-between gap-2 text-[11px] text-slate-500">
        <div>© {new Date().getFullYear()} ASTRO · All rights reserved.</div>
        <div>
          Developed by <span className="font-semibold text-amber-400">Shivang Saxena</span>
        </div>
      </div>
    </footer>
  );
}
