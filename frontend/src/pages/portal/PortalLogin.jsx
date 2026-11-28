import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, ChevronDown, ChevronUp, Lock, ShieldCheck, Sparkles, UserCheck } from "lucide-react";
import { apiFetch, setStoredToken } from "../../api";
import CitySearchInput from "../../components/CitySearchInput";
import { useApp } from "../../context/AppContext";

export default function PortalLogin() {
  const { refreshAccountState, showToast, lang, t } = useApp();
  const navigate = useNavigate();
  const isHindi = lang === "हिं";

  // Primary Onboarding State (Name, DOB, Time, Place)
  const [name, setName] = useState("");
  const [dob, setDob] = useState("1996-05-15");
  const [birthTime, setBirthTime] = useState("09:30");
  const [place, setPlace] = useState({
    place_name: "New Delhi, Delhi",
    latitude: 28.6139,
    longitude: 77.2090,
    tz_offset: 5.5,
  });
  const [busy, setBusy] = useState(false);

  // Staff / Existing Login Accordion State
  const [showStaffLogin, setShowStaffLogin] = useState(false);
  const [staffMode, setStaffMode] = useState("password"); // password | otp
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);

  async function handlePrimaryContinue(e) {
    e.preventDefault();
    if (!name.trim()) {
      showToast(isHindi ? "कृपया अपना पूरा नाम दर्ज करें।" : "Please enter your full name.", "error");
      return;
    }
    if (!dob || !birthTime) {
      showToast(isHindi ? "कृपया जन्म तिथि और समय चुनें।" : "Please select date and time of birth.", "error");
      return;
    }
    setBusy(true);
    try {
      const res = await apiFetch("/auth/continue", {
        method: "POST",
        body: JSON.stringify({
          name: name.trim(),
          dob,
          birth_time: birthTime,
          place_name: place.place_name,
          latitude: place.latitude,
          longitude: place.longitude,
          tz_offset: place.tz_offset,
          device_label: "Astro Mobile Web",
        }),
      });

      if (res.token) {
        setStoredToken(res.token);
      }
      await refreshAccountState();
      showToast(
        isHindi ? `नमस्ते ${name}, आपकी संपूर्ण कुंडली तैयार है!` : `Welcome ${name}! Your full chart is ready.`,
        "success"
      );
      navigate("/app/kundli");
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setBusy(false);
    }
  }

  async function handleStaffPasswordLogin(e) {
    e.preventDefault();
    try {
      const res = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          identifier,
          password,
          device_label: "Desktop Workstation",
          force_replace: true,
        }),
      });
      setStoredToken(res.token);
      await refreshAccountState();
      showToast(`Welcome back, ${res.account.name}!`, "success");
      if (res.account.role === "crm_agent") navigate("/crm-agent");
      else if (res.account.role === "acharya") navigate("/acharya");
      else navigate("/app");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function handleSendOtp() {
    if (!phone) {
      showToast(isHindi ? "कृपया मोबाइल नंबर दर्ज करें" : "Please enter phone number", "error");
      return;
    }
    try {
      const res = await apiFetch("/auth/otp/send", { method: "POST", body: JSON.stringify({ phone }) });
      setOtpSent(true);
      showToast(`Sandbox OTP: ${res.demo_otp}`, "info");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function handleVerifyOtp(e) {
    e.preventDefault();
    try {
      const res = await apiFetch("/auth/otp/verify", {
        method: "POST",
        body: JSON.stringify({ phone, otp, device_label: "Mobile OTP Web" }),
      });
      setStoredToken(res.token);
      await refreshAccountState();
      showToast("OTP Verified cleanly!", "success");
      navigate("/app");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  return (
    <div className="mx-auto max-w-lg px-4 py-8 md:py-12 animate-fade-up">
      {/* Primary Onboarding Card */}
      <div className="cosmic-card relative overflow-hidden rounded-3xl p-6 md:p-8 space-y-6 border border-amber-500/30 shadow-2xl">
        <div className="text-center space-y-2">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-500/40 bg-amber-500/10 px-3 py-1 text-[11px] font-bold text-amber-300">
            <Sparkles className="h-3.5 w-3.5" /> {isHindi ? "सीधा और सुरक्षित प्रवेश" : "Seamless & Secure Access"}
          </span>
          <h1 className="text-2xl font-extrabold text-white">
            {isHindi ? "लॉगिन / आगे बढ़ें" : "LOGIN / CONTINUE"}
          </h1>
          <p className="text-xs text-slate-300 max-w-sm mx-auto leading-relaxed">
            {isHindi
              ? "अपना जन्म विवरण भरें और अपनी पूरी कुंडली, ग्रह स्थिति तथा सटीक लाल किताब उपाय तुरंत पाएं।"
              : "Enter your birth details to generate and save your accurate Vedic & Lal Kitab horoscope."}
          </p>
        </div>

        <form onSubmit={handlePrimaryContinue} className="space-y-4 text-xs">
          {/* 1. Full Name */}
          <div>
            <label className="block text-slate-300 font-semibold mb-1">
              {isHindi ? "1. आपका पूरा नाम" : "1. Full Name"}
            </label>
            <input
              required
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={isHindi ? "उदा. राहुल शर्मा" : "e.g. Rahul Sharma"}
              className="w-full rounded-2xl border border-slate-700 bg-slate-950/90 px-4 py-3 text-sm text-white placeholder-slate-500 focus:border-amber-400 focus:outline-none"
            />
          </div>

          {/* 2 & 3. DOB and Birth Time */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                {isHindi ? "2. जन्म तिथि" : "2. Date of Birth"}
              </label>
              <input
                required
                type="date"
                value={dob}
                onChange={(e) => setDob(e.target.value)}
                className="w-full rounded-2xl border border-slate-700 bg-slate-950/90 px-3 py-3 text-xs text-white focus:border-amber-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                {isHindi ? "3. जन्म समय" : "3. Time of Birth"}
              </label>
              <input
                required
                type="time"
                value={birthTime}
                onChange={(e) => setBirthTime(e.target.value)}
                className="w-full rounded-2xl border border-slate-700 bg-slate-950/90 px-3 py-3 text-xs text-white focus:border-amber-400 focus:outline-none"
              />
            </div>
          </div>

          {/* 4. Place of Birth */}
          <div>
            <label className="block text-slate-300 font-semibold mb-1">
              {isHindi ? "4. जन्म स्थान (शहर खोजें)" : "4. Place of Birth (City Search)"}
            </label>
            <CitySearchInput
              value={place.place_name}
              latitude={place.latitude}
              longitude={place.longitude}
              tzOffset={place.tz_offset}
              onSelect={(c) =>
                setPlace({
                  place_name: c.place_name,
                  latitude: Number(c.latitude),
                  longitude: Number(c.longitude),
                  tz_offset: Number(c.tz_offset),
                })
              }
              placeholder={isHindi ? "जन्म शहर का नाम लिखें (उदा. इंदौर, मुंबई, दिल्ली)..." : "Type birth city (e.g. Indore, Mumbai, London)..."}
            />
          </div>

          <button
            type="submit"
            disabled={busy}
            className="gold-btn w-full flex items-center justify-center gap-2 rounded-2xl py-3.5 text-sm font-bold shadow-lg transition active:scale-[0.98]"
          >
            <span>{busy ? (isHindi ? "कुंडली तैयार हो रही है..." : "Calculating Chart...") : (isHindi ? "आगे बढ़ें और पूरी कुंडली देखें" : "Continue to My Full Kundli")}</span>
            <ArrowRight className="h-4 w-4" />
          </button>

          <p className="text-[11px] text-center text-slate-400">
            {isHindi
              ? "✓ आपकी जानकारी आपके ब्राउज़र में सुरक्षित रहेगी और दोबारा नहीं भरनी पड़ेगी।"
              : "✓ Your details are saved securely on your device so you never need to re-enter them."}
          </p>
        </form>

        {/* Existing User & Staff Accordion */}
        <div className="border-t border-slate-800 pt-4">
          <button
            type="button"
            onClick={() => setShowStaffLogin(!showStaffLogin)}
            className="w-full flex items-center justify-between text-left text-xs font-semibold text-slate-400 hover:text-amber-300 py-1"
          >
            <span>
              {isHindi
                ? "पुराना खाता या आचार्य / CRM लॉगिन? यहां क्लिक करें"
                : "Existing Account or Acharya / CRM Staff Login?"}
            </span>
            {showStaffLogin ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>

          {showStaffLogin && (
            <div className="mt-4 p-4 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-4 text-xs animate-fade-up">
              <div className="flex gap-2 p-1 rounded-xl bg-slate-900 border border-slate-800">
                <button
                  type="button"
                  onClick={() => setStaffMode("password")}
                  className={`flex-1 py-1.5 rounded-lg font-semibold ${staffMode === "password" ? "bg-amber-500 text-slate-950" : "text-slate-300"}`}
                >
                  Password Login
                </button>
                <button
                  type="button"
                  onClick={() => setStaffMode("otp")}
                  className={`flex-1 py-1.5 rounded-lg font-semibold ${staffMode === "otp" ? "bg-amber-500 text-slate-950" : "text-slate-300"}`}
                >
                  Mobile OTP
                </button>
              </div>

              {staffMode === "password" ? (
                <form onSubmit={handleStaffPasswordLogin} className="space-y-3">
                  <input
                    type="text"
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    placeholder="Email or Phone (e.g. platinum@gdvpanel.local)"
                    className="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white"
                  />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Password (Demo: Demo@1234)"
                    className="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white"
                  />
                  <button type="submit" className="gold-btn w-full rounded-xl py-2 font-bold">
                    Sign In
                  </button>
                </form>
              ) : (
                <form onSubmit={handleVerifyOtp} className="space-y-3">
                  <div className="flex gap-2">
                    <input
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="Mobile Number"
                      className="flex-1 rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white"
                    />
                    <button
                      type="button"
                      onClick={handleSendOtp}
                      className="rounded-xl border border-amber-500/40 px-3 py-2 text-amber-300 font-semibold"
                    >
                      Send OTP
                    </button>
                  </div>
                  {otpSent && <div className="text-emerald-400">Sandbox OTP: 123456</div>}
                  <input
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                    placeholder="Enter 6-digit OTP (123456)"
                    className="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white"
                  />
                  <button type="submit" className="gold-btn w-full rounded-xl py-2 font-bold">
                    Verify OTP
                  </button>
                </form>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
