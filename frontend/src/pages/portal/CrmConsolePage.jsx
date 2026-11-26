import React, { useEffect, useState } from "react";
import { Briefcase, IndianRupee, UserPlus, Users } from "lucide-react";
import { apiFetch } from "../../api";
import { useApp } from "../../context/AppContext";

export default function CrmConsolePage() {
  const { account, demoLogin, showToast } = useApp();
  const [overview, setOverview] = useState(null);
  const [clientForm, setClientForm] = useState({ client_name: "", client_phone: "", client_email: "", plan_id: 2, city: "Jaipur" });

  async function loadCrm() {
    if (!account || account.role !== "crm_agent") return;
    try {
      const data = await apiFetch("/crm/overview");
      setOverview(data);
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  useEffect(() => {
    loadCrm();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [account?.id, account?.role]);

  async function registerClient(e) {
    e.preventDefault();
    try {
      const res = await apiFetch("/crm/register-client", { method: "POST", body: JSON.stringify(clientForm) });
      showToast(`Registered! Order ${res.order_number} (Default pw: ${res.default_password})`, "success");
      setClientForm({ client_name: "", client_phone: "", client_email: "", plan_id: 2, city: "Jaipur" });
      loadCrm();
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  if (!account || account.role !== "crm_agent") {
    return (
      <div className="mx-auto max-w-3xl px-4 py-12 text-center cosmic-card mt-8 rounded-3xl space-y-4">
        <Briefcase className="mx-auto h-8 w-8 text-amber-400" />
        <h1 className="text-xl font-bold text-white">GDVPanel CRM Agent Console</h1>
        <p className="text-xs text-slate-300">Requires CRM Agent role (`/crm-agent`, `/crm-registration`, `/all-transaction`).</p>
        <button onClick={() => demoLogin("crm@gdvpanel.local")} className="gold-btn rounded-xl px-5 py-2.5 text-xs">
          Switch to CRM Agent Persona
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 space-y-6 text-xs">
      <div className="cosmic-card rounded-2xl p-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white">CRM Agent Console · Leads, Registrations & All Transactions</h1>
          <p className="text-slate-400 mt-1">Signed in as {account.name}</p>
        </div>
        <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-right">
          <div className="text-[11px] text-emerald-200">Total Sandbox Revenue</div>
          <div className="text-xl font-extrabold text-emerald-400">₹{overview?.total_revenue ?? 0}</div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        {/* Offline Client Registration */}
        <form onSubmit={registerClient} className="lg:col-span-4 cosmic-card rounded-2xl p-5 space-y-3">
          <h2 className="font-bold text-amber-300 flex items-center gap-1.5 text-sm">
            <UserPlus className="h-4 w-4" /> Register Acharya Client (CRM Offline)
          </h2>
          <input required placeholder="Client Full Name" value={clientForm.client_name} onChange={(e) => setClientForm({ ...clientForm, client_name: e.target.value })} className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
          <input required placeholder="Phone (unique)" value={clientForm.client_phone} onChange={(e) => setClientForm({ ...clientForm, client_phone: e.target.value })} className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
          <input placeholder="Email" value={clientForm.client_email} onChange={(e) => setClientForm({ ...clientForm, client_email: e.target.value })} className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
          <select value={clientForm.plan_id} onChange={(e) => setClientForm({ ...clientForm, plan_id: Number(e.target.value) })} className="w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white">
            <option value={1}>Gold Plan (₹8,496 · 1 System)</option>
            <option value={2}>Platinum Plan (₹34,100 · 2 Systems + PDFs)</option>
          </select>
          <button type="submit" className="gold-btn w-full rounded-xl py-2.5">Register & Issue CRM Order ID</button>
        </form>

        {/* All Transactions & Leads */}
        <div className="lg:col-span-8 space-y-6">
          <div className="cosmic-card rounded-2xl p-5 overflow-x-auto">
            <h2 className="font-bold text-white mb-3 text-sm">All Transactions (`/all-transaction`)</h2>
            <table className="w-full text-left">
              <thead className="border-b border-slate-800 text-slate-400">
                <tr><th className="py-2">Order #</th><th className="py-2">Account</th><th className="py-2">Item</th><th className="py-2">Amount</th><th className="py-2">Status</th></tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {(overview?.transactions || []).map((t) => (
                  <tr key={t.id}>
                    <td className="py-2 font-mono text-amber-300">{t.order_number}</td>
                    <td className="py-2">{t.account_name}</td>
                    <td className="py-2">{t.title}</td>
                    <td className="py-2 font-bold">₹{t.total_amount}</td>
                    <td className="py-2 text-emerald-300">{t.payment_status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="cosmic-card rounded-2xl p-5 space-y-2">
            <h2 className="font-bold text-white text-sm">Visitor Leads ({overview?.leads?.length || 0})</h2>
            {(overview?.leads || []).map((ld) => (
              <div key={ld.id} className="flex justify-between rounded-lg bg-slate-900/70 px-3 py-2">
                <span><strong>{ld.name}</strong> ({ld.city}) · {ld.contact}</span>
                <span className="text-amber-300">Study: {ld.study_astro} · Pro: {ld.pro_astro}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
