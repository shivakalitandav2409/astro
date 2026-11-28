import React, { useEffect, useState } from "react";
import { Bell, BookOpen, Coins, HelpCircle, MessageSquare, PhoneCall, Play, Sparkles, ThumbsUp, Video, XCircle } from "lucide-react";
import { apiFetch } from "../../api";
import { useApp } from "../../context/AppContext";
import SpeechButton from "../../components/SpeechButton";

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
  const [activeVideo, setActiveVideo] = useState(null);
  const [activeBlog, setActiveBlog] = useState(null);

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
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Video className="h-4 w-4 text-amber-400" /> गुरुजी वीडियो लेक्चर्स व प्रवचन
            </h2>
            <span className="text-[11px] text-slate-400">Recorded & Live Sessions</span>
          </div>
          {videos.map((v) => (
            <div key={v.id} className="rounded-xl border border-slate-800 bg-slate-900/70 p-3.5 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-white text-sm">{v.title}</span>
                <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] text-slate-300 font-mono">
                  {v.duration}
                </span>
              </div>
              <p className="text-slate-300 leading-relaxed text-[11px]">{v.summary}</p>
              <div className="flex items-center justify-between pt-1 border-t border-slate-800/80">
                <button
                  type="button"
                  onClick={() => setActiveVideo(v)}
                  className="flex items-center gap-1.5 rounded-lg border border-amber-500/40 bg-amber-500/15 px-3 py-1 text-[11px] font-bold text-amber-300 hover:bg-amber-500/25 transition"
                >
                  <Play className="h-3 w-3 fill-amber-300" /> वीडियो देखें (Play Lecture)
                </button>
                <button
                  type="button"
                  onClick={() => apiFetch(`/videos/${v.id}/like`, { method: "POST" }).then(loadMedia)}
                  className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-amber-300"
                >
                  <ThumbsUp className="h-3.5 w-3.5" /> {v.likes}
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="cosmic-card rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-amber-400" /> ज्योतिषीय ब्लॉग व गोचर लेख
            </h2>
            <span className="text-[11px] text-slate-400">Authoritative Insights</span>
          </div>
          {blogs.map((b) => (
            <div key={b.id} className="rounded-xl border border-slate-800 bg-slate-900/70 p-3.5 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-bold text-amber-300 text-sm">{b.title}</span>
                <span className="rounded bg-amber-500/15 px-2 py-0.5 text-[10px] font-semibold text-amber-400">
                  {b.category}
                </span>
              </div>
              <p className="text-slate-300 text-[11px] line-clamp-2 leading-relaxed">{b.content}</p>
              <div className="flex items-center justify-between pt-1 border-t border-slate-800/80">
                <button
                  type="button"
                  onClick={() => setActiveBlog(b)}
                  className="text-amber-300 font-bold hover:underline text-[11px]"
                >
                  पूरा लेख पढ़ें व सुनें (Read Article) →
                </button>
                <div className="flex items-center gap-2">
                  <SpeechButton text={`${b.title}. ${b.content}`} lang="hi" />
                  <button
                    type="button"
                    onClick={() => apiFetch(`/blogs/${b.id}/like`, { method: "POST" }).then(loadMedia)}
                    className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-amber-300"
                  >
                    <ThumbsUp className="h-3.5 w-3.5" /> {b.likes}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Credits, Notifications & FAQs + Feedback */}
      <div className="grid gap-6 md:grid-cols-3">
        {account ? (
          <div className="cosmic-card rounded-2xl p-5 space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="font-bold text-amber-300 flex items-center gap-1.5">
                <Coins className="h-4 w-4 text-amber-400" /> एस्ट्रो कॉइन्स (Astro Coins Wallet)
              </h3>
              <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-[10px] font-bold text-amber-300">
                100 Coins = ₹50
              </span>
            </div>
            <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-3 flex items-center justify-between">
              <div>
                <span className="text-[10px] text-slate-400 block uppercase font-bold">सक्रिय कॉइन्स बैलेंस</span>
                <span className="text-lg font-black text-amber-300">{credits.balance} कॉइन्स</span>
              </div>
              <div className="text-right">
                <span className="text-[10px] text-slate-400 block uppercase font-bold">डिस्काउंट मूल्य</span>
                <span className="text-sm font-bold text-emerald-400">≈ ₹{(credits.balance * 0.5).toFixed(0)}</span>
              </div>
            </div>
            <div className="space-y-1.5 max-h-48 overflow-y-auto">
              <span className="text-[10px] text-slate-400 uppercase font-bold block">सिक्कों का इतिहास (Ledger)</span>
              {credits.ledger.map((l) => (
                <div key={l.id} className="flex justify-between border-b border-slate-800/80 py-1 text-[11px]">
                  <span className="text-slate-300 truncate max-w-[180px]">{l.reason}</span>
                  <span className={l.delta >= 0 ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                    {l.delta >= 0 ? `+${l.delta}` : l.delta}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="cosmic-card rounded-2xl p-5 space-y-3 border border-amber-500/30">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="font-bold text-amber-300 flex items-center gap-1.5">
                <Coins className="h-4 w-4 text-amber-400" /> एस्ट्रो कॉइन्स (Astro Coins Wallet)
              </h3>
              <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-[10px] font-bold text-amber-300">
                100 Coins = ₹50
              </span>
            </div>
            <div className="rounded-xl border border-amber-500/30 bg-amber-950/20 p-3 flex items-center justify-between">
              <div>
                <span className="text-[10px] text-slate-400 block uppercase font-bold">स्वागत बोनस (Welcome Bonus)</span>
                <span className="text-lg font-black text-amber-300">250 कॉइन्स</span>
              </div>
              <div className="text-right">
                <span className="text-[10px] text-slate-400 block uppercase font-bold">डिस्काउंट मूल्य</span>
                <span className="text-sm font-bold text-emerald-400">≈ ₹125</span>
              </div>
            </div>
            <p className="text-[11px] text-slate-300">
              प्रत्येक नई कुंडली, दैनिक राशिफल और उपाय ऑर्डर पर अतिरिक्त सिक्के मिलते हैं।
            </p>
            <button
              type="button"
              onClick={() => demoLogin("consumer@astro.local")}
              className="gold-btn w-full rounded-xl py-2 text-xs font-bold"
            >
              डेमो लॉगिन करें व कॉइन्स देखें
            </button>
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

      {/* Guruji Video Lecture Playback Modal */}
      {activeVideo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-3 sm:p-4 backdrop-blur-md animate-fade-up overflow-y-auto">
          <div className="cosmic-card w-full max-w-2xl rounded-3xl p-5 sm:p-6 space-y-4 border border-amber-500/40 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Video className="h-4 w-4 text-amber-400" /> {activeVideo.title}
                </h3>
                <p className="text-[11px] text-slate-400">{activeVideo.category} · {activeVideo.duration}</p>
              </div>
              <button
                type="button"
                onClick={() => setActiveVideo(null)}
                className="rounded-xl border border-slate-700 bg-slate-900 p-1.5 text-slate-400 hover:text-white"
              >
                <XCircle className="h-5 w-5" />
              </button>
            </div>

            {/* Video Player Container */}
            <div className="relative aspect-video w-full rounded-2xl bg-slate-950 border border-slate-800 flex flex-col items-center justify-center p-6 text-center space-y-3">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/40 animate-pulse">
                <Play className="h-8 w-8 fill-amber-400 ml-1" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">{activeVideo.title}</h4>
                <p className="text-xs text-amber-200 mt-1">गुरदेव जी.डी. वशिष्ठ जी द्वारा प्रमाणित ज्योतिषीय प्रवचन</p>
                <p className="text-[11px] text-slate-400 mt-2 max-w-md">
                  {activeVideo.summary}
                </p>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-slate-800">
              <button
                type="button"
                onClick={() => apiFetch(`/videos/${activeVideo.id}/like`, { method: "POST" }).then(loadMedia)}
                className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-amber-300"
              >
                <ThumbsUp className="h-3.5 w-3.5" /> Like ({activeVideo.likes})
              </button>
              <button
                type="button"
                onClick={() => setActiveVideo(null)}
                className="gold-btn rounded-xl px-5 py-2 text-xs font-bold"
              >
                बंद करें (Close)
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Jyotish Blog Article Reader Modal with TTS */}
      {activeBlog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-3 sm:p-4 backdrop-blur-md animate-fade-up overflow-y-auto">
          <div className="cosmic-card w-full max-w-2xl rounded-3xl p-5 sm:p-6 space-y-4 border border-amber-500/40 shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <span className="rounded bg-amber-500/15 px-2 py-0.5 text-[10px] font-bold text-amber-400 uppercase">
                  {activeBlog.category}
                </span>
                <h3 className="text-base font-bold text-white mt-1">
                  {activeBlog.title}
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <SpeechButton text={`${activeBlog.title}. ${activeBlog.content}`} lang="hi" />
                <button
                  type="button"
                  onClick={() => setActiveBlog(null)}
                  className="rounded-xl border border-slate-700 bg-slate-900 p-1.5 text-slate-400 hover:text-white"
                >
                  <XCircle className="h-5 w-5" />
                </button>
              </div>
            </div>

            <div className="prose prose-invert max-w-none text-slate-200 text-xs leading-relaxed space-y-3">
              <p className="text-sm font-medium text-amber-200/90 leading-relaxed border-l-2 border-amber-500 pl-3">
                {activeBlog.summary || activeBlog.title}
              </p>
              <p className="leading-relaxed whitespace-pre-line">
                {activeBlog.content}
              </p>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-slate-800">
              <div className="text-[11px] text-slate-400">
                प्रकाशित: {activeBlog.published_at || "हालिया"}
              </div>
              <button
                type="button"
                onClick={() => setActiveBlog(null)}
                className="gold-btn rounded-xl px-5 py-2 text-xs font-bold"
              >
                पढ़ लिया (Done)
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
