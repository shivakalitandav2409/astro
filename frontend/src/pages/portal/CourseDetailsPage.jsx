import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Award, CheckCircle2, Lock, PlayCircle, Users } from "lucide-react";
import { apiFetch } from "../../api";
import { useApp } from "../../context/AppContext";

export default function CourseDetailsPage() {
  const { id } = useParams();
  const courseId = Number(id) || 1;
  const { account, refreshAccountState, setPlayingAudio, demoLogin, showToast } = useApp();
  const [course, setCourse] = useState(null);
  const [activeVideo, setActiveVideo] = useState(null);
  const [pendingOrder, setPendingOrder] = useState(null);

  async function loadCourse() {
    try {
      const data = await apiFetch(`/courses/${courseId}`);
      setCourse(data);
      const firstOpen = data.videos?.find((v) => !v.locked);
      if (firstOpen) setActiveVideo(firstOpen);
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  useEffect(() => {
    loadCourse();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseId, account?.id]);

  async function buyCourse() {
    try {
      if (!account) {
        await demoLogin("consumer@astro.local");
      }
      const res = await apiFetch("/checkout/create-order", { method: "POST", body: JSON.stringify({ order_type: "course", course_id: courseId }) });
      setPendingOrder(res.order);
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function confirmCoursePayment() {
    try {
      await apiFetch("/checkout/verify", { method: "POST", body: JSON.stringify({ order_id: pendingOrder.id, simulate_status: "paid" }) });
      setPendingOrder(null);
      await refreshAccountState();
      await loadCourse();
      showToast("Enrolled! All 14 lectures unlocked.", "success");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  if (!course) return <div className="p-8 text-center text-xs text-slate-400">Loading course...</div>;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 space-y-8 text-xs">
      <div className="cosmic-card rounded-3xl p-6 md:p-8 grid gap-6 md:grid-cols-12 items-center">
        <div className="md:col-span-8 space-y-3">
          <div className="flex flex-wrap gap-2">
            <span className="rounded bg-amber-500/20 px-2.5 py-0.5 font-bold text-amber-300">SKU #{course.sku}</span>
            <span className="rounded bg-slate-800 px-2.5 py-0.5 text-slate-300">{course.lectures_count} Lectures · {course.duration_days} Days</span>
            <span className="rounded bg-emerald-500/15 px-2.5 py-0.5 text-emerald-300">★ {course.rating} ({course.reviews} reviews)</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white">{course.title}</h1>
          <p className="text-slate-300 leading-relaxed">{course.description}</p>
          <div className="text-slate-400">Instructor: <strong className="text-amber-300">{course.instructor_name}</strong> · {course.instructor_bio}</div>
        </div>

        <div className="md:col-span-4 rounded-2xl border border-amber-500/30 bg-slate-950 p-5 space-y-3">
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-amber-400">₹{course.price}</span>
            <span className="line-through text-slate-500">₹{course.original_price}</span>
          </div>
          {course.is_enrolled ? (
            <div className="rounded-xl bg-emerald-500/15 px-4 py-2.5 text-center font-bold text-emerald-300">
              Enrolled · All 14 Lectures Open
            </div>
          ) : (
            <button onClick={buyCourse} className="gold-btn w-full rounded-xl py-2.5">Enroll Now (₹11,000)</button>
          )}
          {pendingOrder && (
            <button onClick={confirmCoursePayment} className="w-full rounded-xl bg-emerald-600 py-2 font-bold text-white">
              Complete Test Razorpay Payment ({pendingOrder.order_number})
            </button>
          )}
        </div>
      </div>

      {/* Curriculum Player + 14 Lectures */}
      <div className="grid gap-6 lg:grid-cols-12">
        <div className="lg:col-span-5 cosmic-card rounded-2xl p-5 space-y-4">
          <h2 className="text-base font-bold text-amber-300">Active Lesson Player</h2>
          {activeVideo ? (
            <div className="space-y-3">
              <div className="rounded-xl border border-amber-500/30 bg-slate-950 p-5 text-center space-y-3">
                <PlayCircle className="mx-auto h-10 w-10 text-amber-400" />
                <div className="font-bold text-white text-sm">{activeVideo.title}</div>
                <div className="text-slate-400">Duration: {activeVideo.duration}</div>
                <button
                  onClick={() => setPlayingAudio({ title: activeVideo.title, url: activeVideo.stream_url })}
                  className="gold-btn rounded-xl px-4 py-2"
                >
                  Play Lesson Audio/Stream
                </button>
              </div>
              <p className="text-slate-300 leading-relaxed">{activeVideo.summary}</p>
            </div>
          ) : (
            <p className="text-slate-400">Select the free preview lecture (#1) or enroll to watch all 14 lectures.</p>
          )}

          <div className="border-t border-slate-800 pt-3 space-y-1.5">
            <div className="font-bold text-white">Learning Outcomes</div>
            {course.learning_outcomes?.map((lo, i) => (
              <div key={i} className="flex items-start gap-1.5 text-slate-300"><CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0 mt-0.5" />{lo}</div>
            ))}
          </div>
        </div>

        <div className="lg:col-span-7 cosmic-card rounded-2xl p-5 space-y-2.5">
          <h2 className="text-base font-bold text-white">Curriculum ({course.videos?.length || 0} Farman Lectures)</h2>
          {course.videos?.map((v) => (
            <button
              key={v.id}
              type="button"
              onClick={() => {
                if (v.locked) showToast("Enroll in the course to unlock this lecture.", "info");
                else setActiveVideo(v);
              }}
              className={`flex w-full items-center justify-between rounded-xl border px-3.5 py-2.5 text-left transition ${
                activeVideo?.id === v.id ? "border-amber-400 bg-amber-500/10" : "border-slate-800 bg-slate-900/70"
              }`}
            >
              <div className="flex items-center gap-2.5">
                {v.locked ? <Lock className="h-4 w-4 text-rose-400" /> : <PlayCircle className="h-4 w-4 text-emerald-400" />}
                <div>
                  <div className="font-semibold text-white">{v.sequence_no}. {v.title}</div>
                  <div className="text-[11px] text-slate-400">{v.is_preview ? "Free Preview" : "Course Lecture"} · {v.duration}</div>
                </div>
              </div>
              <span className="text-[11px] text-amber-300">{v.locked ? "Locked" : "Open"}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
