import React, { useEffect, useState } from "react";
import { Radio, Users, Volume2 } from "lucide-react";
import { apiFetch } from "../../api";
import { useApp } from "../../context/AppContext";

export default function GurujiLivePage() {
  const { setPlayingAudio } = useApp();
  const [live, setLive] = useState(null);

  useEffect(() => {
    apiFetch("/guruji-live").then(setLive).catch(() => {});
  }, []);

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 space-y-6 text-xs">
      <div className="cosmic-card rounded-3xl p-8 space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-rose-400 font-bold">
            <Radio className="h-5 w-5 animate-pulse" /> GURUJI LIVE STUDIO (`/guruji-live`)
          </div>
          <span className="flex items-center gap-1.5 rounded-full bg-rose-500/20 px-3 py-1 font-bold text-rose-300">
            <Users className="h-3.5 w-3.5" /> {live?.viewer_count || 318} Live Attendees
          </span>
        </div>

        <h1 className="text-2xl font-extrabold text-white">{live?.session_title || "Lal Kitab & Vashistha Jyotish Live Satsang"}</h1>
        <p className="text-sm text-slate-300">
          Host: <strong className="text-amber-300">{live?.host || "Gurudev GD Vashist Ji"}</strong> · Topic: {live?.topic}
        </p>

        <div className="rounded-2xl border border-amber-500/30 bg-slate-950 p-10 text-center space-y-4">
          <Volume2 className="mx-auto h-12 w-12 text-amber-400" />
          <div className="text-sm font-semibold text-white">Interactive Vedic Discourse Broadcast Channel</div>
          <button
            type="button"
            onClick={() => setPlayingAudio({ title: live?.session_title || "Guruji Live Stream", url: live?.audio_stream || "/api/audio/9.wav" })}
            className="gold-btn rounded-xl px-6 py-2.5 text-xs"
          >
            Join Live Audio Stream
          </button>
        </div>
      </div>
    </div>
  );
}
