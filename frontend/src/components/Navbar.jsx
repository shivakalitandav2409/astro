import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  Bell,
  ChevronDown,
  Crown,
  Globe,
  LogOut,
  Menu,
  ShoppingCart,
  UserCheck,
  X,
} from "lucide-react";
import { useApp } from "../context/AppContext";

export default function Navbar() {
  const {
    account,
    members,
    activeMember,
    setActiveMemberId,
    cartCount,
    unreadNotifs,
    lang,
    setLang,
    demoLogin,
    logout,
  } = useApp();
  const loc = useLocation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [personaOpen, setPersonaOpen] = useState(false);

  const isAppMode = loc.pathname.startsWith("/app");

  const portalLinks = [
    { to: "/", label: "Overview" },
    { to: "/registration", label: "Plans" },
    { to: "/courses-details", label: "Course" },
    { to: "/acharya", label: "Acharya" },
    { to: "/crm-agent", label: "CRM" },
    { to: "/guruji-live", label: "Live" },
  ];

  const appLinks = [
    { to: "/app", label: lang === "En" ? "Home" : "होम" },
    { to: "/app/kundli", label: lang === "En" ? "Kundli" : "कुंडली" },
    { to: "/app/dashas", label: lang === "En" ? "Dashas" : "दशा" },
    { to: "/app/matchmaking", label: lang === "En" ? "Match" : "मिलान" },
    { to: "/app/panchang", label: lang === "En" ? "Panchang" : "पंचांग" },
    { to: "/app/profiles", label: lang === "En" ? "Profiles" : "प्रोफ़ाइल" },
    { to: "/app/shop", label: lang === "En" ? "Store" : "स्टोर" },
    { to: "/app/media", label: lang === "En" ? "Acharyas" : "आचार्य" },
  ];

  const links = isAppMode ? appLinks : portalLinks;

  const personas = [
    { id: "consumer@astro.local", label: "Consumer (Free + Premium Profiles)", badge: "App" },
    { id: "gold@gdvpanel.local", label: "Gold Acharya (1-System Limit)", badge: "Gold" },
    { id: "platinum@gdvpanel.local", label: "Platinum Acharya (2-Sys + Unlimited PDFs)", badge: "Platinum" },
    { id: "crm@gdvpanel.local", label: "CRM Agent Console", badge: "CRM" },
  ];

  return (
    <header className="sticky top-0 z-40 border-b border-amber-500/20 bg-slate-950/90 backdrop-blur-lg">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-2.5">
        <div className="flex items-center gap-3">
          <Link to={isAppMode ? "/app" : "/"} className="flex items-center gap-2.5 group">
            <img
              src="/astro-emblem.png"
              alt="ASTRO Logo"
              className="h-9 w-9 rounded-full object-cover shadow-lg ring-1 ring-amber-400/50 transition duration-300 group-hover:scale-105 group-hover:ring-amber-300"
            />
            <div className="hidden sm:block">
              <div className="text-sm font-extrabold tracking-wider text-amber-400 leading-tight">ASTRO</div>
              <div className="text-[10px] text-slate-400 leading-none">Explore the Cosmos &amp; Destiny</div>
            </div>
          </Link>

          {/* Clean Mode Toggle */}
          <div className="hidden sm:flex items-center rounded-xl border border-slate-800 bg-slate-900/90 p-0.5 text-xs">
            <button
              type="button"
              onClick={() => navigate("/")}
              className={`rounded-lg px-3 py-1.5 font-semibold transition ${
                !isAppMode ? "bg-amber-500 text-slate-950 shadow" : "text-slate-300 hover:text-white"
              }`}
            >
              Portal
            </button>
            <button
              type="button"
              onClick={() => navigate("/app")}
              className={`rounded-lg px-3 py-1.5 font-semibold transition ${
                isAppMode ? "bg-amber-500 text-slate-950 shadow" : "text-slate-300 hover:text-white"
              }`}
            >
              Kundli App
            </button>
          </div>
        </div>

        {/* Desktop Nav */}
        <nav className="hidden xl:flex items-center gap-1">
          {links.map((lk) => {
            const active = loc.pathname === lk.to;
            return (
              <Link
                key={lk.to}
                to={lk.to}
                className={`rounded-xl px-3 py-1.5 text-xs font-semibold transition ${
                  active
                    ? "bg-amber-500/15 text-amber-300 border border-amber-500/35"
                    : "text-slate-300 hover:bg-slate-800/80 hover:text-white"
                }`}
              >
                {lk.label}
              </Link>
            );
          })}
        </nav>

        {/* Right Controls */}
        <div className="flex items-center gap-2">
          {account && members.length > 0 && (
            <select
              aria-label="Active Member Profile"
              value={activeMember?.id || ""}
              onChange={(e) => setActiveMemberId(Number(e.target.value))}
              className="hidden md:block max-w-[185px] rounded-xl border border-amber-500/30 bg-slate-900 px-2.5 py-1.5 text-xs font-medium text-slate-100 focus:border-amber-400 focus:outline-none"
            >
              {members.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name} · {m.plan_id ? "Premium" : "Free"}
                </option>
              ))}
            </select>
          )}

          {/* Quick Demo Switcher Dropdown */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setPersonaOpen(!personaOpen)}
              className="hidden sm:flex items-center gap-1 rounded-xl border border-slate-700/80 bg-slate-900/90 px-2.5 py-1.5 text-xs text-slate-200 hover:border-amber-400/60"
            >
              <Crown className="h-3.5 w-3.5 text-amber-400" />
              <span>Switch Demo</span>
              <ChevronDown className="h-3 w-3 text-slate-400" />
            </button>
            {personaOpen && (
              <div className="absolute right-0 mt-2 w-72 rounded-2xl border border-amber-500/30 bg-slate-950/98 p-2 shadow-2xl backdrop-blur z-50 animate-fade-up">
                <div className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Instant Sandbox Personas
                </div>
                {personas.map((p) => (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => {
                      setPersonaOpen(false);
                      demoLogin(p.id);
                    }}
                    className="flex w-full items-center justify-between rounded-xl px-2.5 py-2 text-left text-xs text-slate-200 hover:bg-amber-500/15 hover:text-amber-300"
                  >
                    <span>{p.label}</span>
                    <span className="rounded bg-amber-500/20 px-1.5 py-0.5 text-[10px] font-bold text-amber-300">
                      {p.badge}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={() => setLang(lang === "En" ? "हिं" : "En")}
            className="flex items-center gap-1 rounded-xl border border-slate-700/80 bg-slate-900/90 px-2.5 py-1.5 text-xs text-slate-200 hover:border-amber-400/60"
            title="Switch Language"
          >
            <Globe className="h-3.5 w-3.5 text-amber-400" />
            <span>{lang}</span>
          </button>

          <Link
            to="/app/shop"
            className="relative rounded-xl border border-slate-700/80 bg-slate-900/90 p-1.5 text-slate-200 hover:border-amber-400/60"
            title="Store & Cart"
          >
            <ShoppingCart className="h-4 w-4" />
            {cartCount > 0 && (
              <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-amber-500 px-1 text-[10px] font-bold text-slate-950">
                {cartCount}
              </span>
            )}
          </Link>

          {account && (
            <Link
              to="/app/media"
              className="relative rounded-xl border border-slate-700/80 bg-slate-900/90 p-1.5 text-slate-200 hover:border-amber-400/60"
              title="Notifications"
            >
              <Bell className="h-4 w-4" />
              {unreadNotifs > 0 && (
                <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-rose-500 px-1 text-[10px] font-bold text-white">
                  {unreadNotifs}
                </span>
              )}
            </Link>
          )}

          {account ? (
            <div className="flex items-center gap-1.5 rounded-xl border border-amber-500/35 bg-amber-500/10 px-2.5 py-1 text-xs">
              <UserCheck className="h-3.5 w-3.5 text-amber-400" />
              <span className="hidden sm:inline font-semibold text-amber-200 max-w-[100px] truncate">{account.name}</span>
              <button type="button" onClick={logout} className="ml-1 text-slate-400 hover:text-rose-400" title="Logout">
                <LogOut className="h-3.5 w-3.5" />
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => demoLogin("consumer@astro.local")}
                className="gold-btn rounded-xl px-3 py-1.5 text-xs"
              >
                Demo Login
              </button>
              <Link
                to="/login"
                className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200 hover:border-amber-400"
              >
                Sign In
              </Link>
            </div>
          )}

          <button
            type="button"
            onClick={() => setMenuOpen(!menuOpen)}
            className="xl:hidden rounded-xl border border-slate-700 p-1.5 text-slate-200"
            aria-label="Toggle Menu"
          >
            {menuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {menuOpen && (
        <div className="xl:hidden border-t border-slate-800 bg-slate-950 px-4 py-3 space-y-2.5 animate-fade-up">
          <div className="flex gap-2">
            <button onClick={() => { navigate("/"); setMenuOpen(false); }} className="flex-1 rounded-xl bg-slate-800 py-2 text-xs font-semibold">
              Portal
            </button>
            <button onClick={() => { navigate("/app"); setMenuOpen(false); }} className="gold-btn flex-1 rounded-xl py-2 text-xs">
              Kundli App
            </button>
          </div>
          <div className="grid grid-cols-2 gap-1.5">
            {links.map((lk) => (
              <Link key={lk.to} to={lk.to} onClick={() => setMenuOpen(false)} className="rounded-xl border border-slate-800 px-3 py-2 text-xs text-slate-200">
                {lk.label}
              </Link>
            ))}
          </div>
          <div className="border-t border-slate-800 pt-2 grid grid-cols-2 gap-1.5 text-[11px]">
            {personas.map((p) => (
              <button
                key={p.id}
                onClick={() => { setMenuOpen(false); demoLogin(p.id); }}
                className="rounded-lg bg-slate-900 px-2 py-1.5 text-left text-amber-300"
              >
                {p.badge}: {p.label.split("(")[0]}
              </button>
            ))}
          </div>
        </div>
      )}
    </header>
  );
}
