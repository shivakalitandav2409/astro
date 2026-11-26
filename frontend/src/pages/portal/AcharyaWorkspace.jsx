import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BookOpen, Crown, Download, Laptop, ShieldCheck, UserCheck } from "lucide-react";
import { apiFetch } from "../../api";
import { useApp } from "../../context/AppContext";

export default function AcharyaWorkspace() {
  const { account, members, enrolledCourses, demoLogin, showToast } = useApp();
  const [sessionsInfo, setSessionsInfo] = useState(null);
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    if (account) {
      apiFetch("/auth/sessions").then(setSessionsInfo).catch(() => {});
      apiFetch("/orders").then((r) => setOrders(r.orders || [])).catch(() => {});
    }
  }, [account?.id]);

  async function downloadPdf(memberId) {
    try {
      const blob = await apiFetch(`/kundli/${memberId}/pdf`);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `acharya_kundali_${memberId}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      showToast("Client Kundali PDF downloaded!", "success");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  if (!account) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-12 text-center cosmic-card mt-8 rounded-3xl space-y-4">
        <h1 className="text-xl font-bold text-white">Acharya Workspace (GDVPanel)</h1>
        <p className="text-xs text-slate-300">Sign in as a Gold or Platinum Acharya to access client charts, courses, session limits, and PDFs.</p>
        <div className="flex justify-center gap-3 text-xs">
          <button onClick={() => demoLogin("gold@gdvpanel.local")} className="rounded-xl border border-sky-500/40 bg-sky-500/15 px-4 py-2 font-bold text-sky-300">
            Demo Gold Acharya (1 System)
          </button>
          <button onClick={() => demoLogin("platinum@gdvpanel.local")} className="gold-btn rounded-xl px-4 py-2">
            Demo Platinum Acharya (2 Systems + Unlimited PDFs)
          </button>
        </div>
      </div>
    );
  }

  const isPlatinum = (account.reg_plan_id || 0) >= 2;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 space-y-6 text-xs">
      <div className="cosmic-card rounded-2xl p-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-extrabold text-white">Acharya Panel · {account.name}</h1>
            <span className={`rounded-full px-3 py-0.5 font-bold ${isPlatinum ? "bg-emerald-500/20 text-emerald-300" : "bg-sky-500/20 text-sky-300"}`}>
              {isPlatinum ? "PLATINUM UNLIMITED (2 SYSTEMS)" : account.reg_plan_id === 1 ? "GOLD PLAN (1 SYSTEM)" : account.role.toUpperCase()}
            </span>
          </div>
          <p className="mt-1 text-slate-400">
            Reg Plan ID: {account.reg_plan_id} · Subs Plan ID: {account.subs_plan_id} · Max Simultaneous Systems: {account.max_sessions}
          </p>
        </div>
        <div className="flex gap-2">
          <Link to="/app/kundli" className="gold-btn rounded-xl px-4 py-2">Open Kundli Generator</Link>
          <Link to="/registration" className="rounded-xl border border-slate-700 px-4 py-2 text-white">Manage Plan</Link>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Active Workstation Sessions */}
        <div className="cosmic-card rounded-2xl p-5 space-y-3">
          <div className="font-bold text-amber-300 flex items-center gap-1.5 text-sm">
            <Laptop className="h-4 w-4" /> System Session Allocation (Max {sessionsInfo?.max_sessions || account.max_sessions})
          </div>
          {(sessionsInfo?.sessions || []).slice(0, 5).map((s) => (
            <div key={s.jti} className="flex items-center justify-between rounded-lg bg-slate-900/70 px-3 py-2">
              <div>
                <div className="font-semibold text-white">{s.device_label}</div>
                <div className="text-[10px] text-slate-400">{s.created_at.slice(0, 16)}</div>
              </div>
              <span className={`rounded px-2 py-0.5 text-[10px] font-bold ${s.active ? "bg-emerald-500/20 text-emerald-300" : "bg-slate-800 text-slate-400"}`}>
                {s.active ? "ACTIVE" : "EVICTED"}
              </span>
            </div>
          ))}
        </div>

        {/* Client Profiles + PDF Export */}
        <div className="cosmic-card rounded-2xl p-5 space-y-3">
          <div className="font-bold text-white flex items-center gap-1.5 text-sm">
            <UserCheck className="h-4 w-4 text-amber-400" /> Client Kundli Profiles & PDFs
          </div>
          {members.map((m) => (
            <div key={m.id} className="flex items-center justify-between rounded-lg bg-slate-900/70 px-3 py-2">
              <div>
                <div className="font-bold text-white">{m.name}</div>
                <div className="text-slate-400">{m.dob} · {m.place_name}</div>
              </div>
              <button
                type="button"
                onClick={() => downloadPdf(m.id)}
                className="flex items-center gap-1 rounded-lg border border-amber-500/40 px-2.5 py-1 text-amber-300 hover:bg-amber-500/10"
              >
                <Download className="h-3.5 w-3.5" /> PDF
              </button>
            </div>
          ))}
        </div>

        {/* Enrolled Courses & Billing */}
        <div className="cosmic-card rounded-2xl p-5 space-y-3">
          <div className="font-bold text-white flex items-center gap-1.5 text-sm">
            <BookOpen className="h-4 w-4 text-amber-400" /> My Courses & Billing
          </div>
          <div className="rounded-lg bg-slate-900/70 p-3">
            {enrolledCourses.length > 0 ? (
              <Link to={`/courses-details/${enrolledCourses[0]}`} className="font-bold text-emerald-300 hover:underline">
                Prarambhik Vashistha Jyotish (Enrolled · Open Lectures →)
              </Link>
            ) : (
              <Link to="/courses-details/1" className="text-amber-300 hover:underline">
                Not enrolled yet — Explore Prarambhik Jyotish →
              </Link>
            )}
          </div>
          <div className="space-y-1.5">
            <div className="font-semibold text-slate-300">Recent Portal Transactions ({orders.length})</div>
            {orders.slice(0, 3).map((o) => (
              <div key={o.id} className="flex justify-between rounded bg-slate-900/60 px-2.5 py-1.5">
                <span>{o.order_number}</span>
                <span className="text-amber-300 font-bold">₹{o.total_amount}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
