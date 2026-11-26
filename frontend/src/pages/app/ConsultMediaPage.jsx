import React, { useEffect, useState } from "react";
import { Bell, BookOpen, Coins, HelpCircle, MessageSquare, PhoneCall, ThumbsUp, Video } from "lucide-react";
import { apiFetch } from "../../api";
import { useApp } from "../../context/AppContext";

export default function ConsultMediaPage() {
  const { account, openUpgradeModal, refreshAccountState, showToast } = useApp();
  const [acharyas, setAcharyas] = useState([]);
  const [suggTab, setSuggTab] = useState("All");
  const [suggestions, setSuggestions] = useState([]);
  const [blogs, setBlogs] = useState([]);
  const [videos, setVideos] = useState([]);
  const [faqs, setFaqs] = useState([]);
  const [credits, setCredits] = useState({ balance: 0, ledger: [] });
  const [notifs, setNotifs] = useState([]);
  const [feedbackMsg, setFeedbackMsg] = useState("");
  const [commentText, setCommentText] = useState({});

  async function loadMedia() {
    try {
      const [aRes, sRes, bRes, vRes, fRes] = await Promise.all([
        apiFetch("/acharyas"),
        apiFetch(`/acharya-suggestions?tab=${suggTab}`),
        apiFetch("/blogs"),
        apiFetch("/videos"),
        apiFetch("/faqs"),
      ]);
      setAcharyas(aRes.acharyas || []);
      setSuggestions(sRes.suggestions || []);
      setBlogs(bRes.blogs || []);
      setVideos(vRes.videos || []);
      setFaqs(fRes.faqs || []);
      if (account) {
        const [cr, nf] = await Promise.all([apiFetch("/credits"), apiFetch("/notifications")]);
        setCredits(cr);
        setNotifs(nf.notifications || []);
      }
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  useEffect(() => {
    loadMedia();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [account?.id, suggTab]);

  async function callAcharya(id) {
    if (!account) {
      showToast("Please sign in to queue a consultation call.", "info");
      return;
    }
    const res = await apiFetch(`/acharyas/${id}/request-call`, { method: "POST" });
    showToast(`Call Queued (${res.bridge_ref}) with ${res.acharya.name}`, "success");
    refreshAccountState();
  }

  async function postBlogComment(blogId) {
    if (!account || !commentText[blogId]?.trim()) return;
    await apiFetch(`/blogs/${blogId}/comment`, {
      method: "POST",
      body: JSON.stringify({ comment_text: commentText[blogId] }),
    });
    setCommentText((p) => ({ ...p, [blogId]: "" }));
    loadMedia();
  }

  async function submitFeedback(e) {
    e.preventDefault();
    if (!account || !feedbackMsg.trim()) return;
    await apiFetch("/feedback", { method: "POST", body: JSON.stringify({ message: feedbackMsg, rating: 5 }) });
    setFeedbackMsg("");
    showToast("Thank you for your feedback!", "success");
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 space-y-8 text-xs">
      {/* Acharyas Click-to-Call */}
      <div className="space-y-4">
        <h1 className="text-xl font-extrabold text-white">Consult Senior Vashistha Acharyas & Media</h1>
        <div className="grid gap-4 md:grid-cols-3">
          {acharyas.map((a) => (
            <div key={a.id} className="cosmic-card rounded-2xl p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-white">{a.name}</span>
                <span className="rounded bg-amber-500/20 px-2 py-0.5 text-[10px] font-bold text-amber-300">★ {a.rating}</span>
              </div>
              <div className="text-amber-300">{a.specialty}</div>
              <div className="text-slate-400">{a.languages} · {a.experience_years} yrs exp</div>
              <button
                type="button"
                onClick={() => callAcharya(a.id)}
                className="gold-btn mt-2 flex w-full items-center justify-center gap-1.5 rounded-xl py-2"
              >
                <PhoneCall className="h-3.5 w-3.5" /> Request Callback
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Acharya Suggestions 3-Tab Showcase */}
      <div className="cosmic-card rounded-2xl p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-base font-bold text-amber-300">Acharya Suggestions (Service / Product / Lal Kitab File)</h2>
          <div className="flex gap-1.5">
            {["All", "Service", "Product", "File"].map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setSuggTab(t)}
                className={`rounded-lg px-3 py-1 font-semibold ${suggTab === t ? "bg-amber-500 text-slate-950" : "border border-slate-700 text-slate-300"}`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>
        <div className="grid gap-3 md:grid-cols-3">
          {suggestions.map((s) => (
            <div key={s.id} className="rounded-xl border border-slate-800 bg-slate-900/70 p-3.5 space-y-2">
              <span className="rounded bg-amber-500/15 px-2 py-0.5 text-[10px] uppercase font-bold text-amber-300">{s.suggestion_type}</span>
              <div className="font-bold text-white text-sm">{s.title}</div>
              <p className="text-slate-400">{s.notes}</p>
              {s.report_summary && <p className="rounded bg-slate-950 p-2 text-emerald-300">{s.report_summary}</p>}
              {s.linked_plan_id > 0 && (
                <button onClick={() => openUpgradeModal(s.notes)} className="text-amber-300 font-semibold hover:underline">
                  Unlock Suggested Plan →
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Videos & Blogs */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="cosmic-card rounded-2xl p-5 space-y-3">
          <h2 className="text-base font-bold text-white flex items-center gap-2"><Video className="h-4 w-4 text-amber-400" /> Spiritual Videos</h2>
          {videos.map((v) => (
            <div key={v.id} className="rounded-xl border border-slate-800 bg-slate-900/70 p-3 space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white">{v.title}</span>
                <span className="text-slate-400">{v.duration}</span>
              </div>
              <p className="text-slate-400">{v.summary}</p>
              <button
                type="button"
                onClick={() => apiFetch(`/videos/${v.id}/like`, { method: "POST" }).then(loadMedia)}
                className="flex items-center gap-1 text-amber-300 hover:underline"
              >
                <ThumbsUp className="h-3.5 w-3.5" /> {v.likes} Likes
              </button>
            </div>
          ))}
        </div>

        <div className="cosmic-card rounded-2xl p-5 space-y-3">
          <h2 className="text-base font-bold text-white flex items-center gap-2"><BookOpen className="h-4 w-4 text-amber-400" /> Jyotish Blogs & Comments</h2>
          {blogs.map((b) => (
            <div key={b.id} className="rounded-xl border border-slate-800 bg-slate-900/70 p-3 space-y-2">
              <div className="font-bold text-amber-300">{b.title}</div>
              <p className="text-slate-300">{b.content}</p>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => apiFetch(`/blogs/${b.id}/like`, { method: "POST" }).then(loadMedia)}
                  className="flex items-center gap-1 text-amber-300"
                >
                  <ThumbsUp className="h-3.5 w-3.5" /> {b.likes} Likes
                </button>
                <span className="text-slate-400">{b.comments?.length || 0} comments</span>
              </div>
              {b.comments?.length > 0 && (
                <div className="space-y-1 rounded-lg bg-slate-950/60 p-2">
                  {b.comments.slice(0, 3).map((cm) => (
                    <div key={cm.id} className="text-[11px] text-slate-300">
                      <strong className="text-amber-300">{cm.account_name}:</strong> {cm.comment}
                    </div>
                  ))}
                </div>
              )}
              {account && (
                <div className="flex gap-2">
                  <input
                    placeholder="Add a comment..."
                    value={commentText[b.id] || ""}
                    onChange={(e) => setCommentText((p) => ({ ...p, [b.id]: e.target.value }))}
                    className="flex-1 rounded border border-slate-700 bg-slate-950 px-2.5 py-1 text-white"
                  />
                  <button onClick={() => postBlogComment(b.id)} className="rounded bg-amber-500/20 px-3 py-1 font-semibold text-amber-300">Post</button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Credits, Notifications & FAQs + Feedback */}
      <div className="grid gap-6 md:grid-cols-3">
        {account && (
          <div className="cosmic-card rounded-2xl p-5 space-y-2">
            <h3 className="font-bold text-amber-300 flex items-center gap-1.5"><Coins className="h-4 w-4" /> Reward Credits: ₹{credits.balance}</h3>
            {credits.ledger.map((l) => (
              <div key={l.id} className="flex justify-between border-b border-slate-800 py-1.5">
                <span className="text-slate-300">{l.reason}</span>
                <span className={l.delta >= 0 ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                  {l.delta >= 0 ? `+${l.delta}` : l.delta}
                </span>
              </div>
            ))}
          </div>
        )}

        {account && (
          <div className="cosmic-card rounded-2xl p-5 space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-white flex items-center gap-1.5"><Bell className="h-4 w-4 text-amber-400" /> Notifications</h3>
              <button onClick={() => apiFetch("/notifications/read-all", { method: "POST" }).then(() => { loadMedia(); refreshAccountState(); })} className="text-amber-300 hover:underline">Mark read</button>
            </div>
            {notifs.map((n) => (
              <div key={n.id} className="rounded-lg bg-slate-900/70 p-2.5">
                <div className="font-bold text-white">{n.title}</div>
                <div className="text-slate-400">{n.body}</div>
              </div>
            ))}
          </div>
        )}

        <div className="cosmic-card rounded-2xl p-5 space-y-3">
          <h3 className="font-bold text-white flex items-center gap-1.5"><HelpCircle className="h-4 w-4 text-amber-400" /> FAQs & Support</h3>
          {faqs.map((f) => (
            <div key={f.id} className="border-b border-slate-800 pb-2">
              <div className="font-semibold text-amber-200">{f.question}</div>
              <div className="text-slate-400 mt-0.5">{f.answer}</div>
            </div>
          ))}
          {account && (
            <form onSubmit={submitFeedback} className="space-y-2 pt-1">
              <textarea
                rows="2"
                placeholder="Share feedback with Guruji team..."
                value={feedbackMsg}
                onChange={(e) => setFeedbackMsg(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-900 p-2 text-white"
              />
              <button type="submit" className="gold-btn w-full rounded-lg py-1.5">Submit Feedback</button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
