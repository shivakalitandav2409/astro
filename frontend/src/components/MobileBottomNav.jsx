import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Compass, Flame, HeartHandshake, Home, Moon, User } from "lucide-react";

export default function MobileBottomNav() {
  const loc = useLocation();
  const isAppMode = loc.pathname.startsWith("/app");

  const portalNav = [
    { to: "/", label: "Overview", icon: Home },
    { to: "/courses-details", label: "Courses", icon: Flame },
    { to: "/acharya", label: "Acharya", icon: Compass },
    { to: "/crm-agent", label: "CRM", icon: User },
  ];

  const appNav = [
    { to: "/app", label: "Home", icon: Home },
    { to: "/app/kundli", label: "Kundli", icon: Compass },
    { to: "/app/dashas", label: "Dashas", icon: Flame },
    { to: "/app/matchmaking", label: "Match", icon: HeartHandshake },
    { to: "/app/panchang", label: "Panchang", icon: Moon },
  ];

  const items = isAppMode ? appNav : portalNav;

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 block sm:hidden border-t border-amber-500/20 bg-slate-950/95 backdrop-blur-lg px-2 py-1.5 shadow-2xl">
      <div className="flex items-center justify-around">
        {items.map((item) => {
          const Icon = item.icon;
          const active = loc.pathname === item.to;
          return (
            <Link
              key={item.to}
              to={item.to}
              className={`flex flex-col items-center justify-center rounded-xl px-2.5 py-1 text-[10px] font-medium transition ${
                active ? "text-amber-400 font-bold" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Icon className={`h-4 w-4 mb-0.5 ${active ? "text-amber-400 scale-110" : ""}`} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
