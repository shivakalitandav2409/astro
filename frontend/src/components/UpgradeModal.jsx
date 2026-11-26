import React, { useEffect, useState } from "react";
import { CheckCircle2, Crown, ShieldCheck, X } from "lucide-react";
import { apiFetch } from "../api";
import { useApp } from "../context/AppContext";

export default function UpgradeModal() {
  const {
    account,
    members,
    upgradeModal,
    setUpgradeModal,
    refreshAccountState,
    showToast,
  } = useApp();
  const [plans, setPlans] = useState([]);
  const [selectedPlanId, setSelectedPlanId] = useState(137);
  const [step, setStep] = useState("select"); // select | razorpay
  const [pendingOrder, setPendingOrder] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (upgradeModal.open) {
      setStep("select");
      setPendingOrder(null);
      apiFetch("/plans?scope=consumer_sub")
        .then((res) => setPlans(res.plans || []))
        .catch(() => {});
    }
  }, [upgradeModal.open]);

  if (!upgradeModal.open) return null;

  const targetMember =
    members.find((m) => m.id === upgradeModal.memberId) || members[0] || null;

  async function startCheckout() {
    if (!account || !targetMember) {
      showToast("Please sign in first to upgrade a profile.", "error");
      return;
    }
    setBusy(true);
    try {
      const res = await apiFetch("/checkout/create-order", {
        method: "POST",
        body: JSON.stringify({
          order_type: "subscription",
          member_id: targetMember.id,
          plan_id: selectedPlanId,
        }),
      });
      setPendingOrder(res.order);
      setStep("razorpay");
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setBusy(false);
    }
  }

  async function completeSandboxPayment(simulateStatus = "paid") {
    if (!pendingOrder) return;
    setBusy(true);
    try {
      await apiFetch("/checkout/verify", {
        method: "POST",
        body: JSON.stringify({
          order_id: pendingOrder.id,
          simulate_status: simulateStatus,
        }),
      });
      await refreshAccountState();
      showToast("Subscription Activated! Premium unlocked.", "success");
      setUpgradeModal({ open: false, memberId: null, reason: "" });
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm">
      <div className="cosmic-card relative w-full max-w-2xl rounded-2xl p-6">
        <button
          type="button"
          onClick={() => setUpgradeModal({ open: false, memberId: null, reason: "" })}
          className="absolute right-4 top-4 rounded-lg p-1 text-slate-400 hover:text-white"
        >
          <X className="h-5 w-5" />
        </button>

        {step === "select" ? (
          <>
            <div className="flex items-center gap-2 text-amber-400">
              <Crown className="h-6 w-6" />
              <h2 className="text-lg font-bold">Activate AstroScience Membership Plan</h2>
            </div>
            {upgradeModal.reason && (
              <p className="mt-2 rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-xs text-amber-200">
                {upgradeModal.reason}
              </p>
            )}
            <p className="mt-2 text-xs text-slate-300">
              Plans attach per family profile ({targetMember?.name || "Select profile"}). Current tier:{" "}
              <span className="font-semibold text-amber-300">{targetMember?.plan_name || "Free Plan"}</span>.
            </p>

            <div className="mt-4 grid gap-3 md:grid-cols-3">
              {plans.map((pl) => {
                const chosen = selectedPlanId === pl.id;
                return (
                  <button
                    key={pl.id}
                    type="button"
                    onClick={() => setSelectedPlanId(pl.id)}
                    className={`flex flex-col justify-between rounded-xl border p-3.5 text-left transition ${
                      chosen
                        ? "border-amber-400 bg-amber-500/10"
                        : "border-slate-700 bg-slate-900/70 hover:border-slate-500"
                    }`}
                  >
                    <div>
                      {pl.is_popular ? (
                        <span className="mb-1 inline-block rounded bg-amber-500 px-1.5 py-0.5 text-[10px] font-bold text-slate-950">
                          MOST POPULAR
                        </span>
                      ) : null}
                      <div className="text-sm font-bold text-white">{pl.name}</div>
                      <div className="mt-1 text-xl font-extrabold text-amber-400">₹{pl.total_price}</div>
                      <ul className="mt-2 space-y-1 text-[11px] text-slate-300">
                        {pl.benefits.slice(0, 3).map((b, i) => (
                          <li key={i} className="flex items-start gap-1">
                            <CheckCircle2 className="mt-0.5 h-3 w-3 shrink-0 text-emerald-400" />
                            <span>{b}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </button>
                );
              })}
            </div>

            <div className="mt-5 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setUpgradeModal({ open: false, memberId: null, reason: "" })}
                className="rounded-xl border border-slate-700 px-4 py-2 text-xs text-slate-300"
              >
                Continue Free
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={startCheckout}
                className="gold-btn rounded-xl px-5 py-2 text-xs"
              >
                {busy ? "Creating Order..." : "Proceed to Sandbox Checkout"}
              </button>
            </div>
          </>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-emerald-400">
              <ShieldCheck className="h-6 w-6" />
              <h2 className="text-lg font-bold">Razorpay Test Checkout (Simulated Safe Mode)</h2>
            </div>
            <div className="rounded-xl border border-slate-700 bg-slate-900 p-4 text-xs space-y-1.5">
              <div>Order Number: <span className="font-mono text-amber-300">{pendingOrder?.order_number}</span></div>
              <div>Razorpay Test Order ID: <span className="font-mono text-slate-200">{pendingOrder?.razorpay_order_id}</span></div>
              <div>Item: <span className="text-white">{pendingOrder?.title}</span></div>
              <div className="text-base font-bold text-amber-400 pt-1">Amount Payable: ₹{pendingOrder?.total_amount}</div>
            </div>
            <div className="flex justify-end gap-2">
              <button
                type="button"
                disabled={busy}
                onClick={() => completeSandboxPayment("failed")}
                className="rounded-xl border border-rose-500/40 bg-rose-500/10 px-4 py-2 text-xs text-rose-300"
              >
                Simulate Failure
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() => completeSandboxPayment("paid")}
                className="gold-btn rounded-xl px-5 py-2 text-xs"
              >
                {busy ? "Verifying..." : "Pay & Unlock Now (UPI/Card Test)"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
