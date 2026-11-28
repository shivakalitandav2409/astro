import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Compass, Flame, HeartHandshake, Home, Moon } from "lucide-react";
import { useApp } from "../context/AppContext";

export default function MobileBottomNav() {
  const loc = useLocation();
  const { lang, t } = useApp();

  const items = [
    { to: "/app", label: t("home"), icon: Home },
    { to: "/app/kundli", label: t("kundli"), icon: Compass },
    { to: "/app/dashas", label: t("dashas"), icon: Flame },
    { to: "/app/matchmaking", label: t("matchmaking"), icon: HeartHandshake },
    { to: "/app/panchang", label: t("panchang"), icon: Moon },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 block sm:hidden border-t border-amber-500/20 bg-slate-950/98 backdrop-blur-xl px-2 py-1.5 shadow-2xl safe-area-pb">
      <div className="flex items-center justify-around">
        {items.map((item) => {
          const Icon = item.icon;
          const active = loc.pathname === item.to;
          return (
            <Link
              key={item.to}
              to={item.to}
              className={`flex flex-col items-center justify-center min-w-[56px] min-h-[44px] rounded-xl px-2 py-1 text-[10px] font-medium transition active:scale-95 ${
                active ? "text-amber-400 font-bold" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Icon className={`h-4 w-4 mb-0.5 transition-transform ${active ? "text-amber-400 scale-110" : ""}`} />
              <span className="leading-tight">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
