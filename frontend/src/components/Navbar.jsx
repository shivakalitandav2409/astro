import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  Bell,
  Globe,
  LogOut,
  Menu,
  ShoppingCart,
  Sparkles,
  User,
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
    lang,
    setLang,
    t,
    logout,
  } = useApp();
  const loc = useLocation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const isAppMode = loc.pathname.startsWith("/app");
  const isHindi = lang === "हिं";

  const appLinks = [
    { to: "/app", label: t("home") },
    { to: "/app/kundli", label: t("kundli") },
    { to: "/app/dashas", label: t("dashas") },
    { to: "/app/matchmaking", label: t("matchmaking") },
    { to: "/app/panchang", label: t("panchang") },
  ];

  const mobileLinks = [
    { to: "/app", label: t("home") },
    { to: "/app/kundli", label: t("kundli") },
    { to: "/app/dashas", label: t("dashas") },
    { to: "/app/matchmaking", label: t("matchmaking") },
    { to: "/app/panchang", label: t("panchang") },
    { to: "/app/profiles", label: t("profiles") },
    { to: "/app/shop", label: t("store") },
  ];

  return (
    <header className="sticky top-0 z-40 border-b border-amber-500/20 bg-slate-950/90 backdrop-blur-lg">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-2.5">
        {/* Brand Logo & Name */}
        <div className="flex items-center gap-3">
          <Link to="/app" className="flex items-center gap-2.5 group">
            <img
              src="/astro-emblem.png"
              alt="ASTRO Logo"
              className="h-9 w-9 rounded-full object-cover shadow-lg ring-1 ring-amber-400/50 transition duration-300 group-hover:scale-105 group-hover:ring-amber-300"
            />
            <div>
              <div className="text-sm font-extrabold tracking-wider text-amber-400 leading-tight">
                {isHindi ? "ASTRO · एस्ट्रो" : "ASTRO"}
              </div>
              <div className="text-[10px] text-slate-400 leading-none">
                {isHindi ? "सटीक वैदिक एवं लाल किताब ज्योतिष" : "Explore the Cosmos & Destiny"}
              </div>
            </div>
          </Link>
        </div>

        {/* Desktop Nav Links */}
        <nav className="hidden lg:flex items-center gap-1">
          {appLinks.map((lk) => {
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
              className="hidden md:block max-w-[170px] rounded-xl border border-amber-500/30 bg-slate-900 px-2.5 py-1.5 text-xs font-medium text-slate-100 focus:border-amber-400 focus:outline-none"
            >
              {members.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name}
                </option>
              ))}
            </select>
          )}

          {/* Simple Language Toggle */}
          <button
            type="button"
            onClick={() => setLang(lang === "En" ? "हिं" : "En")}
            className="flex items-center gap-1 rounded-xl border border-slate-700/80 bg-slate-900/90 px-2.5 py-1.5 text-xs font-semibold text-slate-200 hover:border-amber-400/60"
            title="Switch Language (English / हिंदी)"
          >
            <Globe className="h-3.5 w-3.5 text-amber-400" />
            <span>{lang === "En" ? "हिं" : "En"}</span>
          </button>

          {/* Store Cart */}
          <Link
            to="/app/shop"
            className="relative rounded-xl border border-slate-700/80 bg-slate-900/90 p-1.5 text-slate-200 hover:border-amber-400/60"
            title={t("store")}
          >
            <ShoppingCart className="h-4 w-4" />
            {cartCount > 0 && (
              <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-amber-500 px-1 text-[10px] font-bold text-slate-950">
                {cartCount}
              </span>
            )}
          </Link>

          {/* Single Clear Login / Continue Button vs Profile */}
          {account ? (
            <div className="flex items-center gap-1.5 rounded-xl border border-amber-500/35 bg-amber-500/10 px-2.5 py-1 text-xs">
              <UserCheck className="h-3.5 w-3.5 text-amber-400" />
              <span className="hidden sm:inline font-semibold text-amber-200 max-w-[90px] truncate">
                {activeMember?.name || account.name}
              </span>
              <button
                type="button"
                onClick={logout}
                className="ml-1 text-slate-400 hover:text-rose-400 transition"
                title={t("logout")}
              >
                <LogOut className="h-3.5 w-3.5" />
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="gold-btn flex items-center gap-1.5 rounded-xl px-3.5 py-1.5 text-xs font-bold shadow-md transition"
            >
              <User className="h-3.5 w-3.5" />
              <span>{t("login_continue")}</span>
            </Link>
          )}

          {/* Mobile Hamburger Toggle */}
          <button
            type="button"
            onClick={() => setMenuOpen(!menuOpen)}
            className="lg:hidden rounded-xl border border-slate-700 p-1.5 text-slate-200"
            aria-label="Toggle Menu"
          >
            {menuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {menuOpen && (
        <div className="lg:hidden border-t border-slate-800 bg-slate-950 px-4 py-3 space-y-3 animate-fade-up">
          <div className="grid grid-cols-2 gap-2 text-xs">
            {mobileLinks.map((lk) => (
              <Link
                key={lk.to}
                to={lk.to}
                onClick={() => setMenuOpen(false)}
                className={`rounded-xl border px-3 py-2 text-center font-medium transition ${
                  loc.pathname === lk.to
                    ? "border-amber-500/40 bg-amber-500/15 text-amber-300 font-bold"
                    : "border-slate-800 bg-slate-900/70 text-slate-200"
                }`}
              >
                {lk.label}
              </Link>
            ))}
          </div>

          {!account && (
            <Link
              to="/login"
              onClick={() => setMenuOpen(false)}
              className="gold-btn flex w-full items-center justify-center gap-2 rounded-xl py-2.5 text-xs font-bold shadow"
            >
              <User className="h-3.5 w-3.5" />
              <span>{t("login_continue")}</span>
            </Link>
          )}

          <div className="border-t border-slate-800/80 pt-2 flex items-center justify-between text-[11px] text-slate-400">
            <Link to="/about-us" onClick={() => setMenuOpen(false)} className="hover:text-amber-300">
              {isHindi ? "हमारे बारे में" : "About & Credits"}
            </Link>
            <Link to="/login" onClick={() => setMenuOpen(false)} className="hover:text-amber-300">
              {isHindi ? "स्टाफ लॉगिन" : "Staff Login"}
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
