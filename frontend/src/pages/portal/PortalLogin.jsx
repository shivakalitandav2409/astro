import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { KeyRound, PhoneCall, ShieldAlert, ShieldCheck } from "lucide-react";
import { apiFetch, setStoredToken } from "../../api";
import { useApp } from "../../context/AppContext";

export default function PortalLogin() {
  const { refreshAccountState, showToast } = useApp();
  const navigate = useNavigate();
  const [mode, setMode] = useState("password"); // password | otp | register
  const [identifier, setIdentifier] = useState("platinum@gdvpanel.local");
  const [password, setPassword] = useState("Demo@1234");
  const [deviceLabel, setDeviceLabel] = useState("Desktop Workstation #1");
  const [forceReplace, setForceReplace] = useState(false);
  const [limitAlert, setLimitAlert] = useState(null);

  const [phone, setPhone] = useState("9800000001");
  const [otp, setOtp] = useState("123456");
  const [otpSent, setOtpSent] = useState(false);

  const [regName, setRegName] = useState("");
  const [regEmail, setRegEmail] = useState("");
  const [regPhone, setRegPhone] = useState("");

  async function handlePasswordLogin(e, overrideReplace = forceReplace) {
    e?.preventDefault();
    setLimitAlert(null);
    try {
      const res = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          identifier,
          password,
          device_label: deviceLabel,
          force_replace: overrideReplace,
        }),
      });
      setStoredToken(res.token);
      await refreshAccountState();
      showToast(`Welcome ${res.account.name}!`, "success");
      if (res.account.role === "crm_agent") navigate("/crm-agent");
      else if (res.account.role === "acharya") navigate("/acharya");
      else navigate("/app");
    } catch (err) {
      if (err.status === 409 && err.detail?.code === "SESSION_LIMIT_REACHED") {
        setLimitAlert(err.detail);
      } else {
        showToast(err.message, "error");
      }
    }
  }

  async function handleSendOtp() {
    const res = await apiFetch("/auth/otp/send", { method: "POST", body: JSON.stringify({ phone }) });
    setOtpSent(true);
    showToast(`Sandbox OTP: ${res.demo_otp}`, "info");
  }

  async function handleVerifyOtp(e) {
    e.preventDefault();
    try {
      const res = await apiFetch("/auth/otp/verify", {
        method: "POST",
        body: JSON.stringify({ phone, otp, device_label: "Consumer OTP Web" }),
      });
      setStoredToken(res.token);
      await refreshAccountState();
      showToast("OTP Verified!", "success");
      navigate("/app");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function handleRegister(e) {
    e.preventDefault();
    try {
      const res = await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify({ name: regName, email: regEmail, phone: regPhone, password }),
      });
      setStoredToken(res.token);
      await refreshAccountState();
      showToast("Account created!", "success");
      navigate("/app");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  return (
    <div className="mx-auto max-w-xl px-4 py-10">
      <div className="cosmic-card rounded-3xl p-6 md:p-8 space-y-6">
        <div>
          <h1 className="text-2xl font-extrabold text-white">Unified Sign In (Portal & App)</h1>
          <p className="text-xs text-slate-400 mt-1">
            Supports Acharya/CRM Email+Password (with strict Gold 1-system vs Platinum 2-system session limits) and Mobile OTP.
          </p>
        </div>

        <div className="flex gap-2 rounded-xl border border-slate-800 bg-slate-950 p-1 text-xs">
          {[
            { id: "password", label: "Password Login" },
            { id: "otp", label: "Mobile OTP (APK)" },
            { id: "register", label: "New Account" },
          ].map((m) => (
            <button
              key={m.id}
              type="button"
              onClick={() => setMode(m.id)}
              className={`flex-1 rounded-lg py-2 font-semibold ${mode === m.id ? "bg-amber-500 text-slate-950" : "text-slate-300"}`}
            >
              {m.label}
            </button>
          ))}
        </div>

        {mode === "password" && (
          <form onSubmit={(e) => handlePasswordLogin(e, forceReplace)} className="space-y-4 text-xs">
            <label className="block">
              <span className="text-slate-300">Email or Phone</span>
              <input value={identifier} onChange={(e) => setIdentifier(e.target.value)} className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
            </label>
            <label className="block">
              <span className="text-slate-300">Password (Demo: Demo@1234)</span>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
            </label>
            <label className="block">
              <span className="text-slate-300">Device / System Label</span>
              <input value={deviceLabel} onChange={(e) => setDeviceLabel(e.target.value)} className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
            </label>
            <label className="flex items-center gap-2 text-slate-400">
              <input type="checkbox" checked={forceReplace} onChange={(e) => setForceReplace(e.target.checked)} />
              <span>Automatically take over oldest active session if plan limit is reached</span>
            </label>

            {limitAlert && (
              <div className="rounded-xl border border-rose-500/40 bg-rose-950/20 p-3 space-y-2 text-rose-200">
                <div className="flex items-center gap-1.5 font-bold"><ShieldAlert className="h-4 w-4" /> {limitAlert.code}</div>
                <p>{limitAlert.message}</p>
                <button
                  type="button"
                  onClick={() => handlePasswordLogin(null, true)}
                  className="gold-btn rounded-lg px-3 py-1.5 text-xs"
                >
                  Force Login & Evict Oldest Session
                </button>
              </div>
            )}

            <button type="submit" className="gold-btn w-full rounded-xl py-2.5">Sign In</button>
          </form>
        )}

        {mode === "otp" && (
          <form onSubmit={handleVerifyOtp} className="space-y-4 text-xs">
            <div className="flex gap-2">
              <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="Mobile Number" className="flex-1 rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
              <button type="button" onClick={handleSendOtp} className="rounded-xl border border-amber-500/40 px-4 py-2 font-semibold text-amber-300">Send OTP</button>
            </div>
            {otpSent && <div className="text-emerald-300">Sandbox OTP generated: <strong>123456</strong></div>}
            <input value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="Enter 6-digit OTP (123456)" className="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
            <button type="submit" className="gold-btn w-full rounded-xl py-2.5">Verify OTP & Enter App</button>
          </form>
        )}

        {mode === "register" && (
          <form onSubmit={handleRegister} className="space-y-3 text-xs">
            <input required placeholder="Full Name" value={regName} onChange={(e) => setRegName(e.target.value)} className="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
            <input required placeholder="Email" value={regEmail} onChange={(e) => setRegEmail(e.target.value)} className="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
            <input required placeholder="Phone" value={regPhone} onChange={(e) => setRegPhone(e.target.value)} className="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
            <input required type="password" placeholder="Password (min 6 chars)" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
            <button type="submit" className="gold-btn w-full rounded-xl py-2.5">Create Unified Account</button>
          </form>
        )}
      </div>
    </div>
  );
}
