import React, { useEffect, useState } from "react";
import { Volume2, VolumeX } from "lucide-react";

export default function SpeechButton({
  text,
  lang = "auto", // "auto" | "hi" | "en"
  className = "",
  size = "sm", // "sm" | "md"
}) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [supported, setSupported] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      setSupported(true);
    }
  }, []);

  useEffect(() => {
    return () => {
      if (typeof window !== "undefined" && window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  if (!supported || !text) return null;

  function toggleSpeech(e) {
    e.stopPropagation();
    if (!window.speechSynthesis) return;

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    // Cancel any previous speech
    window.speechSynthesis.cancel();

    // Determine target language
    let targetLang = "en-US";
    if (lang === "hi" || (lang === "auto" && /[\u0900-\u097F]/.test(text))) {
      targetLang = "hi-IN";
    }

    // Clean text of markdown formatting/asterisks for natural speech
    const cleanText = text
      .replace(/[*_#`~[\]()]/g, "")
      .replace(/\s+/g, " ")
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = targetLang;
    utterance.rate = targetLang === "hi-IN" ? 0.95 : 1.0;
    utterance.pitch = 1.0;

    // Pick appropriate voice if available
    const voices = window.speechSynthesis.getVoices();
    if (voices && voices.length > 0) {
      const matchedVoice = voices.find((v) => v.lang.startsWith(targetLang.slice(0, 2)));
      if (matchedVoice) {
        utterance.voice = matchedVoice;
      }
    }

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  }

  const iconSize = size === "sm" ? "h-3.5 w-3.5" : "h-4 w-4";

  return (
    <button
      type="button"
      onClick={toggleSpeech}
      title={isSpeaking ? "आवाज़ बंद करें / Stop Voice" : "बोलकर सुनाएं / Listen to Voice (TTS)"}
      className={`inline-flex items-center gap-1 rounded-lg border p-1 text-[11px] font-semibold transition ${
        isSpeaking
          ? "border-amber-400 bg-amber-500/25 text-amber-300 animate-pulse"
          : "border-slate-800 bg-slate-900/80 text-slate-400 hover:border-slate-600 hover:text-amber-300"
      } ${className}`}
    >
      {isSpeaking ? (
        <>
          <VolumeX className={`${iconSize} text-amber-400`} />
          <span className="hidden sm:inline text-[10px] text-amber-300">बंद करें</span>
        </>
      ) : (
        <>
          <Volume2 className={iconSize} />
          <span className="hidden sm:inline text-[10px]">सुनाएं</span>
        </>
      )}
    </button>
  );
}
