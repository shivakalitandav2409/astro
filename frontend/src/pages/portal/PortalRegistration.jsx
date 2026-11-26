import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { CheckCircle2, Crown, ShieldCheck } from "lucide-react";
import { apiFetch } from "../../api";
import { useApp } from "../../context/AppContext";

export default function PortalRegistration() {
  const { id } = useParams();
  const { account, refreshAccountState, showToast } = useApp();
  const navigate = useNavigate();
  const [plans, setPlans] = useState([]);
  const [selectedPlanId, setSelectedPlanId] = useState(Number(id) || 2);
  const [form, setForm] = useState({ name: "", phone: "", email: "", pincode: "110064", city: "New Delhi", state: "Delhi" });
  const [pendingOrder, setPendingOrder] = useState(null);

  useEffect(() => {
    apiFetch("/plans?scope=portal_reg").then((r) => setPlans(r.plans || [])).catch(() => {});
  }, []);

  useEffect(() => {
    if (id) setSelectedPlanId(Number(id));
  }, [id]);

  async function onPinBlur() {
    if (form.pincode.trim().length === 6) {
      try {
        const res = await apiFetch(`/pincodes/${form.pincode.trim()}`);
        setForm((p) => ({ ...p, city: res.district || res.place_name, state: res.state }));
      } catch {
        // ignore
      }
    }
  }

  async function createRegOrder(e) {
    e.preventDefault();
    if (!account) {
      showToast("Please sign in first (or click Demo Login) before completing checkout.", "info");
      return;
    }
    try {
      const res = await apiFetch("/checkout/create-order", {
        method: "POST",
        body: JSON.stringify({ order_type: "portal_registration", plan_id: selectedPlanId, reg_details: form }),
      });
      setPendingOrder(res.order);
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function verifyPayment() {
    try {
      await apiFetch("/checkout/verify", { method: "POST", body: JSON.stringify({ order_id: pendingOrder.id, simulate_status: "paid" }) });
      await refreshAccountState();
      showToast("GDVPanel Registration Activated!", "success");
      navigate("/acharya");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  const chosen = plans.find((p) => p.id === selectedPlanId) || plans[0];

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 space-y-8">
      <div className="text-center">
        <h1 className="text-2xl font-extrabold text-white">GDVPanel Acharya Registration & Plan Upgrade</h1>
        <p className="text-xs text-slate-400 mt-1">Select Gold (₹8,496 / 1 System) or Platinum (₹34,100 / 2 Simultaneous Systems + Unlimited PDFs).</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {plans.map((pl) => (
          <button
            key={pl.id}
            type="button"
            onClick={() => setSelectedPlanId(pl.id)}
            className={`cosmic-card rounded-2xl p-5 text-left transition ${selectedPlanId === pl.id ? "border-amber-400 ring-1 ring-amber-400" : ""}`}
          >
            <div className="flex justify-between font-bold text-white text-lg">
              <span>{pl.name}</span>
              <span className="text-amber-400">₹{pl.total_price}</span>
            </div>
            <div className="text-xs text-sky-300 mt-1">Max Systems: {pl.max_systems} · CRM SKU #{pl.crm_sku}</div>
            <ul className="mt-3 space-y-1.5 text-xs text-slate-300">
              {pl.benefits.map((b, i) => (
                <li key={i} className="flex items-start gap-1.5"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0 mt-0.5" />{b}</li>
              ))}
            </ul>
          </button>
        ))}
      </div>

      <form onSubmit={createRegOrder} className="cosmic-card rounded-2xl p-6 space-y-4 text-xs">
        <h2 className="text-base font-bold text-amber-300">Practice Registration Details ({chosen?.name})</h2>
        <div className="grid gap-3 md:grid-cols-3">
          <input required placeholder="Acharya / Center Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
          <input required placeholder="Mobile" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
          <input required placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
          <input required placeholder="PIN Code" value={form.pincode} onBlur={onPinBlur} onChange={(e) => setForm({ ...form, pincode: e.target.value })} className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
          <input required placeholder="City" value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
          <input required placeholder="State" value={form.state} onChange={(e) => setForm({ ...form, state: e.target.value })} className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
        </div>
        <button type="submit" className="gold-btn rounded-xl px-6 py-2.5">Create Sandbox Registration Order (₹{chosen?.total_price || "..."})</button>
      </form>

      {pendingOrder && (
        <div className="cosmic-card rounded-2xl border-emerald-500/40 p-5 flex flex-wrap items-center justify-between gap-4 text-xs">
          <div>
            <div className="font-bold text-emerald-300 text-sm">Order Ready: {pendingOrder.order_number}</div>
            <div>Razorpay Ref: {pendingOrder.razorpay_order_id} · Total: ₹{pendingOrder.total_amount}</div>
          </div>
          <button onClick={verifyPayment} className="gold-btn rounded-xl px-5 py-2">Confirm Payment & Activate Acharya Workspace</button>
        </div>
      )}
    </div>
  );
}
