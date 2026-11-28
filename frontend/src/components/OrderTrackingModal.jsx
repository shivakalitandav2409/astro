import React, { useEffect, useState } from "react";
import { CheckCircle2, Clock, Package, Truck, XCircle, ShieldCheck } from "lucide-react";
import { apiFetch } from "../api";

export default function OrderTrackingModal({ orderId, onClose, isHindi = true }) {
  const [tracking, setTracking] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (orderId) {
      apiFetch(`/orders/${orderId}/tracking`)
        .then(setTracking)
        .catch((e) => console.error(e))
        .finally(() => setLoading(false));
    }
  }, [orderId]);

  if (!orderId) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-3 sm:p-4 backdrop-blur-md animate-fade-up overflow-y-auto">
      <div className="cosmic-card w-full max-w-lg rounded-3xl p-5 sm:p-6 space-y-4 border border-amber-500/40 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-amber-500/15 text-amber-400">
              <Truck className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                {isHindi ? "ऑर्डर लाइव ट्रैकिंग टाइमलाइन" : "Order Live Tracking Timeline"}
              </h3>
              <p className="text-[11px] text-slate-400">
                {tracking ? `${tracking.order_number} · ${tracking.courier}` : "Loading tracking details..."}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl border border-slate-700 bg-slate-900 p-1.5 text-slate-400 hover:text-white transition"
          >
            <XCircle className="h-5 w-5" />
          </button>
        </div>

        {loading && (
          <div className="py-8 text-center text-xs text-amber-300 animate-pulse">
            {isHindi ? "ट्रैकिंग स्थिति लोड हो रही है..." : "Loading tracking status..."}
          </div>
        )}

        {tracking && (
          <div className="space-y-4">
            {/* Courier & AWB Banner */}
            <div className="flex flex-wrap items-center justify-between gap-2 rounded-2xl border border-amber-500/30 bg-amber-950/20 p-3.5 text-xs">
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 block">
                  {isHindi ? "ट्रैकिंग AWB नंबर" : "Tracking AWB Code"}
                </span>
                <span className="font-mono text-sm font-bold text-amber-300">
                  {tracking.awb_number}
                </span>
              </div>
              <div className="text-right">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">
                  {isHindi ? "अपेक्षित डिलीवरी" : "Estimated Delivery"}
                </span>
                <span className="text-xs font-bold text-emerald-300">
                  {tracking.estimated_delivery}
                </span>
              </div>
            </div>

            {/* 4-Step Vertical Timeline */}
            <div className="relative pl-6 space-y-5 border-l-2 border-slate-800 ml-3">
              {tracking.timeline.map((step) => {
                const isDone = step.completed;
                return (
                  <div key={step.step} className="relative">
                    {/* Step Icon */}
                    <div
                      className={`absolute -left-[31px] top-0 flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${
                        isDone
                          ? "bg-emerald-500 text-slate-950 shadow-md shadow-emerald-500/30"
                          : "border border-slate-700 bg-slate-900 text-slate-400"
                      }`}
                    >
                      {isDone ? <CheckCircle2 className="h-4 w-4" /> : step.step}
                    </div>

                    <div className="space-y-1">
                      <div className="flex flex-wrap items-center justify-between gap-1">
                        <span className={`text-xs font-bold ${isDone ? "text-white" : "text-slate-400"}`}>
                          {isHindi ? step.title_hi : step.title_en}
                        </span>
                        <span className="text-[10px] text-slate-400">{step.time}</span>
                      </div>
                      <p className="text-[11px] text-slate-300 leading-relaxed">
                        {isHindi ? step.description_hi : step.description_en}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div className="flex justify-end pt-2 border-t border-slate-800">
          <button
            type="button"
            onClick={onClose}
            className="gold-btn rounded-xl px-5 py-2 text-xs font-bold"
          >
            {isHindi ? "बंद करें" : "Close"}
          </button>
        </div>
      </div>
    </div>
  );
}
