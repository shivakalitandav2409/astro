import React, { useEffect, useState } from "react";
import { Download, MapPin, Music, ShoppingBag, Tag, Trash2, Volume2 } from "lucide-react";
import { apiFetch } from "../../api";
import { useApp } from "../../context/AppContext";

export default function ShopCartPage() {
  const { account, refreshAccountState, setPlayingAudio, showToast } = useApp();
  const [products, setProducts] = useState([]);
  const [filterType, setFilterType] = useState("all");
  const [cart, setCart] = useState({ items: [], subtotal: 0, reward_credits: 0 });
  const [orders, setOrders] = useState([]);
  const [addresses, setAddresses] = useState([]);
  const [couponCode, setCouponCode] = useState("ASTRO10");
  const [discountAmt, setDiscountAmt] = useState(0);
  const [useCredits, setUseCredits] = useState(false);
  const [pendingOrder, setPendingOrder] = useState(null);
  const [addrForm, setAddrForm] = useState({
    full_name: "Aarav Sharma",
    phone: "9800000001",
    line1: "C-11/20 Mayapuri",
    pincode: "110064",
    city: "New Delhi",
    state: "Delhi",
  });

  async function loadAll() {
    try {
      const pRes = await apiFetch(`/products${filterType !== "all" ? `?type=${filterType}` : ""}`);
      setProducts(pRes.products || []);
      if (account) {
        const [cRes, oRes, aRes] = await Promise.all([
          apiFetch("/cart"),
          apiFetch("/orders"),
          apiFetch("/addresses"),
        ]);
        setCart(cRes);
        setOrders(oRes.orders || []);
        setAddresses(aRes.addresses || []);
      }
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  useEffect(() => {
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [account?.id, filterType]);

  async function addToCart(pid) {
    if (!account) {
      showToast("Please sign in to add remedies to your cart.", "info");
      return;
    }
    try {
      const res = await apiFetch("/cart", { method: "POST", body: JSON.stringify({ product_id: pid, quantity: 1 }) });
      setCart(res);
      await refreshAccountState();
      showToast("Added to cart", "success");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function removeCartItem(cid) {
    const res = await apiFetch(`/cart/${cid}`, { method: "DELETE" });
    setCart(res);
    await refreshAccountState();
  }

  async function handleApplyCoupon() {
    try {
      const res = await apiFetch("/cart/apply-coupon", { method: "POST", body: JSON.stringify({ code: couponCode }) });
      setDiscountAmt(res.discount_amount);
      showToast(`Coupon ${res.code} applied (-₹${res.discount_amount})`, "success");
    } catch (err) {
      setDiscountAmt(0);
      showToast(err.message, "error");
    }
  }

  async function handlePincodeBlur() {
    if (addrForm.pincode.trim().length === 6) {
      try {
        const res = await apiFetch(`/pincodes/${addrForm.pincode.trim()}`);
        setAddrForm((prev) => ({ ...prev, city: res.district || res.place_name, state: res.state }));
        showToast(`PIN ${res.pincode} → ${res.place_name}, ${res.state}`, "info");
      } catch {
        // optional
      }
    }
  }

  async function saveAddress(e) {
    e.preventDefault();
    if (!account) return;
    await apiFetch("/addresses", { method: "POST", body: JSON.stringify(addrForm) });
    showToast("Address saved", "success");
    loadAll();
  }

  const maxRedeemable = Math.min(100, account?.credits_balance || 0);

  async function checkoutCart() {
    try {
      const res = await apiFetch("/checkout/create-order", {
        method: "POST",
        body: JSON.stringify({
          order_type: "shop",
          coupon_code: discountAmt > 0 ? couponCode : null,
          credits_to_use: useCredits ? maxRedeemable : 0,
        }),
      });
      setPendingOrder(res.order);
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function confirmPayment() {
    if (!pendingOrder) return;
    try {
      await apiFetch("/checkout/verify", {
        method: "POST",
        body: JSON.stringify({ order_id: pendingOrder.id, simulate_status: "paid" }),
      });
      setPendingOrder(null);
      setDiscountAmt(0);
      await refreshAccountState();
      await loadAll();
      showToast("Order confirmed & 2% Cosmic Credits earned!", "success");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function downloadInvoice(orderId, num) {
    const blob = await apiFetch(`/orders/${orderId}/invoice.pdf`);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `invoice_${num}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  }

  async function cancelShopOrder(orderId) {
    try {
      await apiFetch(`/orders/${orderId}/cancel`, { method: "POST" });
      showToast("Order cancelled", "info");
      loadAll();
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 space-y-8">
      {/* Store Filters */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-white">Astro Remedies, Kits, Puja & Free Mantras</h1>
          <p className="text-xs text-slate-400">Free Bhajans/Mantras stream directly in browser WAV audio without purchase.</p>
        </div>
        <div className="flex flex-wrap gap-2 text-xs">
          {[
            { id: "all", label: "All" },
            { id: "remedy", label: "Remedies & Yantras" },
            { id: "book", label: "Lal Kitab Books" },
            { id: "kit", label: "Kundli Files" },
            { id: "service", label: "Kalyankari Puja" },
            { id: "bhajan", label: "Free Bhajans" },
            { id: "mantra", label: "Free Mantras" },
          ].map((f) => (
            <button
              key={f.id}
              type="button"
              onClick={() => setFilterType(f.id)}
              className={`rounded-xl px-3 py-1.5 font-semibold ${
                filterType === f.id ? "bg-amber-500 text-slate-950" : "border border-slate-700 text-slate-300"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Product Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {products.map((p) => (
          <div key={p.id} className="cosmic-card flex flex-col justify-between rounded-2xl p-4 text-xs space-y-3">
            <div>
              <div className="flex items-center justify-between">
                <span className="rounded bg-amber-500/15 px-2 py-0.5 text-[10px] font-bold text-amber-300">
                  {p.category_name}
                </span>
                <span className="font-mono text-[10px] text-slate-400">{p.sku}</span>
              </div>
              <h3 className="mt-2 text-sm font-bold text-white">{p.title}</h3>
              <p className="mt-1 text-slate-400 leading-relaxed">{p.description}</p>
            </div>
            <div className="flex items-center justify-between border-t border-slate-800 pt-3">
              {p.is_audio ? (
                <>
                  <span className="font-bold text-emerald-400">FREE DEVOTIONAL AUDIO</span>
                  <button
                    type="button"
                    onClick={() => setPlayingAudio({ title: p.title, url: `/api/audio/${p.id}.wav` })}
                    className="flex items-center gap-1.5 rounded-xl bg-emerald-500/20 px-3 py-1.5 font-bold text-emerald-300 hover:bg-emerald-500/30"
                  >
                    <Volume2 className="h-3.5 w-3.5" /> Listen Now
                  </button>
                </>
              ) : (
                <>
                  <div>
                    <span className="text-base font-extrabold text-amber-400">₹{p.price}</span>{" "}
                    <span className="line-through text-slate-500">₹{p.mrp}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => addToCart(p.id)}
                    className="gold-btn flex items-center gap-1 rounded-xl px-3.5 py-1.5"
                  >
                    <ShoppingBag className="h-3.5 w-3.5" /> Add
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Cart, Coupons & Addresses */}
      {account && (
        <div className="grid gap-6 lg:grid-cols-12 text-xs">
          <div className="lg:col-span-6 cosmic-card rounded-2xl p-5 space-y-4">
            <h2 className="text-base font-bold text-white">Your Cart & Sandbox Checkout</h2>
            {cart.items.length === 0 ? (
              <p className="text-slate-400">Cart is empty. Add any Yantra, Book, or Puja above.</p>
            ) : (
              <>
                <div className="space-y-2">
                  {cart.items.map((it) => (
                    <div key={it.cart_id} className="flex items-center justify-between rounded-lg bg-slate-900/70 px-3 py-2">
                      <div>
                        <div className="font-semibold text-white">{it.title}</div>
                        <div className="text-slate-400">Qty: {it.quantity} × ₹{it.price}</div>
                      </div>
                      <button onClick={() => removeCartItem(it.cart_id)} className="text-slate-400 hover:text-rose-400">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input value={couponCode} onChange={(e) => setCouponCode(e.target.value)} className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-white" />
                  <button type="button" onClick={handleApplyCoupon} className="rounded-lg border border-amber-500/40 px-3 py-1.5 font-semibold text-amber-300">
                    Apply Coupon
                  </button>
                </div>
                <label className="flex items-center gap-2 text-slate-300">
                  <input type="checkbox" disabled={maxRedeemable === 0} checked={useCredits && maxRedeemable > 0} onChange={(e) => setUseCredits(e.target.checked)} />
                  <span>Redeem {maxRedeemable} Cosmic Reward Credits (-₹{maxRedeemable}) · Available: ₹{account.credits_balance}</span>
                </label>
                <div className="border-t border-slate-800 pt-3 flex items-center justify-between font-bold text-sm">
                  <span>Payable Total:</span>
                  <span className="text-amber-400">₹{Math.max(0, cart.subtotal - discountAmt - (useCredits ? maxRedeemable : 0))}</span>
                </div>
                <button type="button" onClick={checkoutCart} className="gold-btn w-full rounded-xl py-2.5">
                  Proceed to Razorpay Test Checkout
                </button>
              </>
            )}

            {pendingOrder && (
              <div className="rounded-xl border border-emerald-500/40 bg-emerald-950/20 p-4 space-y-2">
                <div className="font-bold text-emerald-300">Confirm Simulated Payment: {pendingOrder.order_number}</div>
                <div>Amount: ₹{pendingOrder.total_amount}</div>
                <button type="button" onClick={confirmPayment} className="gold-btn rounded-xl px-4 py-2">
                  Complete Test Payment
                </button>
              </div>
            )}
          </div>

          {/* Delivery Addresses w/ Pincode Lookup & Order History */}
          <div className="lg:col-span-6 space-y-6">
            <form onSubmit={saveAddress} className="cosmic-card rounded-2xl p-5 space-y-3">
              <h2 className="text-base font-bold text-white flex items-center gap-1.5">
                <MapPin className="h-4 w-4 text-amber-400" /> Delivery Address (PIN Autofill)
              </h2>
              <div className="grid grid-cols-2 gap-2">
                <input placeholder="Full Name" value={addrForm.full_name} onChange={(e) => setAddrForm({ ...addrForm, full_name: e.target.value })} className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-white" />
                <input placeholder="PIN e.g. 110064" value={addrForm.pincode} onBlur={handlePincodeBlur} onChange={(e) => setAddrForm({ ...addrForm, pincode: e.target.value })} className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-white" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <input placeholder="City" value={addrForm.city} onChange={(e) => setAddrForm({ ...addrForm, city: e.target.value })} className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-white" />
                <input placeholder="State" value={addrForm.state} onChange={(e) => setAddrForm({ ...addrForm, state: e.target.value })} className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-white" />
              </div>
              <button type="submit" className="rounded-lg border border-slate-700 px-4 py-1.5 text-amber-300 hover:border-amber-400">
                Save Address ({addresses.length} stored)
              </button>
            </form>

            <div className="cosmic-card rounded-2xl p-5 space-y-3">
              <h2 className="text-base font-bold text-white">Order History & Tax Invoices</h2>
              {orders.length === 0 ? (
                <p className="text-slate-400">No orders placed yet.</p>
              ) : (
                orders.map((o) => (
                  <div key={o.id} className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-slate-900/70 px-3 py-2">
                    <div>
                      <div className="font-bold text-white">{o.order_number} · {o.title}</div>
                      <div className="text-slate-400">₹{o.total_amount} · {o.payment_status}</div>
                    </div>
                    <div className="flex items-center gap-1.5">
                      {o.order_kind === "product" && o.payment_status !== "Cancelled" && (
                        <button
                          type="button"
                          onClick={() => cancelShopOrder(o.id)}
                          className="rounded border border-rose-500/40 px-2 py-1 text-rose-300 hover:bg-rose-500/10"
                        >
                          Cancel
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => downloadInvoice(o.id, o.order_number)}
                        className="flex items-center gap-1 rounded border border-amber-500/40 px-2.5 py-1 text-amber-300"
                      >
                        <Download className="h-3.5 w-3.5" /> Invoice PDF
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
