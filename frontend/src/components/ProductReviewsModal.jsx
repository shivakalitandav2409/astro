import React, { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { CheckCircle2, Star, XCircle } from "lucide-react";
import { apiFetch } from "../api";

export default function ProductReviewsModal({ product, onClose, isHindi = true }) {
  const [reviewsData, setReviewsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [rating, setRating] = useState(5);
  const [reviewText, setReviewText] = useState("");
  const [reviewerName, setReviewerName] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");

  async function loadReviews() {
    if (!product?.id) return;
    try {
      const res = await apiFetch(`/products/${product.id}/reviews`);
      setReviewsData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadReviews();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [product?.id]);

  async function handleSubmitReview(e) {
    e.preventDefault();
    if (!reviewText.trim()) return;
    setSubmitting(true);
    try {
      await apiFetch(`/products/${product.id}/reviews`, {
        method: "POST",
        body: JSON.stringify({
          account_name: reviewerName.trim() || "Verified Buyer",
          rating,
          review_text: reviewText.trim(),
        }),
      });
      setSuccessMsg(isHindi ? "आपकी समीक्षा सफलतापूर्वक दर्ज हो गई है!" : "Review submitted successfully!");
      setReviewText("");
      loadReviews();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  }

  if (!product) return null;

  return createPortal(
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/85 p-3 sm:p-4 backdrop-blur-md animate-fade-up overflow-y-auto">
      <div className="cosmic-card w-full max-w-lg rounded-3xl p-5 sm:p-6 space-y-4 border border-amber-500/40 shadow-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <span>{product.title}</span>
            </h3>
            <div className="flex items-center gap-2 mt-1">
              <div className="flex items-center text-amber-400">
                {[1, 2, 3, 4, 5].map((s) => (
                  <Star
                    key={s}
                    className={`h-3.5 w-3.5 ${
                      s <= Math.round(reviewsData?.average_rating || 5)
                        ? "fill-amber-400 text-amber-400"
                        : "text-slate-600"
                    }`}
                  />
                ))}
              </div>
              <span className="text-xs font-bold text-amber-300">
                {reviewsData?.average_rating || "5.0"} / 5
              </span>
              <span className="text-[11px] text-slate-400">
                ({reviewsData?.total_reviews || 0} {isHindi ? "समीक्षाएं" : "reviews"})
              </span>
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

        {/* Reviews List */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
            {isHindi ? "ग्राहकों के वास्तविक अनुभव" : "Verified Customer Reviews"}
          </h4>

          {loading && (
            <div className="py-4 text-center text-xs text-amber-300 animate-pulse">
              {isHindi ? "समीक्षाएं लोड हो रही हैं..." : "Loading reviews..."}
            </div>
          )}

          {!loading && reviewsData?.reviews?.length === 0 && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 text-center text-slate-400 text-xs">
              {isHindi ? "इस उत्पाद पर अभी कोई समीक्षा नहीं है। पहली समीक्षा आप लिखें!" : "No reviews yet. Be the first to share your experience!"}
            </div>
          )}

          {!loading &&
            reviewsData?.reviews?.map((rev) => (
              <div
                key={rev.id}
                className="rounded-2xl border border-slate-800 bg-slate-900/70 p-3.5 space-y-1.5 text-xs"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <span className="font-bold text-white">{rev.account_name}</span>
                    {rev.verified_buyer ? (
                      <span className="rounded bg-emerald-500/20 px-1.5 py-0.2 text-[9px] font-bold text-emerald-300 flex items-center gap-0.5">
                        <CheckCircle2 className="h-2.5 w-2.5" /> {isHindi ? "सत्यापित खरीददार" : "Verified"}
                      </span>
                    ) : null}
                  </div>
                  <div className="flex items-center text-amber-400">
                    {[1, 2, 3, 4, 5].map((s) => (
                      <Star
                        key={s}
                        className={`h-3 w-3 ${
                          s <= rev.rating ? "fill-amber-400 text-amber-400" : "text-slate-600"
                        }`}
                      />
                    ))}
                  </div>
                </div>
                <p className="text-slate-200 text-[11px] leading-relaxed">{rev.review_text}</p>
                <div className="text-[10px] text-slate-500">{rev.created_at}</div>
              </div>
            ))}
        </div>

        {/* Add Review Form */}
        <form onSubmit={handleSubmitReview} className="rounded-2xl border border-amber-500/30 bg-amber-950/15 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-amber-300">
              {isHindi ? "अपनी समीक्षा व अनुभव साझा करें" : "Write a Customer Review"}
            </span>
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setRating(s)}
                  className="focus:outline-none"
                >
                  <Star
                    className={`h-4 w-4 transition hover:scale-110 ${
                      s <= rating ? "fill-amber-400 text-amber-400" : "text-slate-600"
                    }`}
                  />
                </button>
              ))}
            </div>
          </div>

          <div className="grid gap-2">
            <input
              type="text"
              placeholder={isHindi ? "आपका नाम (वैकल्पिक)" : "Your Name (Optional)"}
              value={reviewerName}
              onChange={(e) => setReviewerName(e.target.value)}
              className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-white focus:border-amber-400 focus:outline-none"
            />
            <textarea
              rows="2.5"
              placeholder={
                isHindi
                  ? "इस उपाय या यंत्र का आपके जीवन में क्या प्रभाव रहा? (लिखें)..."
                  : "How did this remedy or yantra positively impact your life?..."
              }
              value={reviewText}
              onChange={(e) => setReviewText(e.target.value)}
              required
              className="rounded-xl border border-slate-700 bg-slate-900 p-2.5 text-xs text-white focus:border-amber-400 focus:outline-none"
            />
          </div>

          {successMsg && (
            <div className="text-emerald-300 text-xs font-medium">{successMsg}</div>
          )}

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={submitting}
              className="gold-btn rounded-xl px-4 py-1.5 text-xs font-bold"
            >
              {submitting ? (isHindi ? "सबमिट हो रहा है..." : "Submitting...") : isHindi ? "समीक्षा सबमिट करें" : "Submit Review"}
            </button>
          </div>
        </form>
      </div>
    </div>,
    document.body
  );
}
