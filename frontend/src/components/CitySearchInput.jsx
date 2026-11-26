import React, { useState } from "react";
import { Check, MapPin } from "lucide-react";
import { apiFetch } from "../api";

export default function CitySearchInput({
  value,
  latitude,
  longitude,
  tzOffset = 5.5,
  onSelect,
  placeholder = "Search birth city (e.g. Indore, Mumbai, London)...",
}) {
  const [query, setQuery] = useState(value || "");
  const [results, setResults] = useState([]);
  const [open, setOpen] = useState(false);

  // Sync when parent resets/changes selected value programmatically
  React.useEffect(() => {
    setQuery(value || "");
  }, [value]);

  async function handleSearch(text) {
    setQuery(text);
    onSelect({
      place_name: text,
      latitude,
      longitude,
      tz_offset: tzOffset,
      picked: false,
    });
    if (text.trim().length < 2) {
      setResults([]);
      setOpen(false);
      return;
    }
    try {
      const res = await apiFetch(`/places/search?q=${encodeURIComponent(text)}`);
      setResults(res.places || []);
      setOpen(true);
    } catch {
      setResults([]);
    }
  }

  function pickCity(pl) {
    const label = `${pl.place_name}, ${pl.state || pl.country}`;
    setQuery(label);
    setOpen(false);
    setResults([]);
    onSelect({
      place_name: label,
      latitude: Number(pl.latitude),
      longitude: Number(pl.longitude),
      tz_offset: Number(pl.tz_offset),
      picked: true,
    });
  }

  return (
    <div className="relative text-xs">
      <div className="relative">
        <MapPin className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-amber-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          onFocus={() => results.length > 0 && setOpen(true)}
          placeholder={placeholder}
          className="w-full rounded-xl border border-slate-700 bg-slate-900/90 pl-8 pr-3 py-2 text-white placeholder-slate-500 focus:border-amber-400 focus:outline-none"
        />
      </div>
      <div className="mt-1 flex items-center justify-between text-[10px] text-slate-400 px-1">
        <span className="flex items-center gap-1 text-emerald-400">
          <Check className="h-3 w-3" /> {Number(latitude).toFixed(2)}°N, {Number(longitude).toFixed(2)}°E · UTC{tzOffset >= 0 ? `+${tzOffset}` : tzOffset}
        </span>
      </div>
      {open && results.length > 0 && (
        <div className="absolute z-30 mt-1 max-h-48 w-full overflow-y-auto rounded-xl border border-amber-500/30 bg-slate-950/98 p-1 shadow-2xl backdrop-blur">
          {results.map((pl) => (
            <button
              key={pl.id}
              type="button"
              onClick={() => pickCity(pl)}
              className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-xs text-slate-200 hover:bg-amber-500/15 hover:text-amber-300"
            >
              <span>
                <strong>{pl.place_name}</strong>, {pl.state} ({pl.country})
              </span>
              <span className="font-mono text-[10px] text-slate-400">
                UTC{pl.tz_offset >= 0 ? `+${pl.tz_offset}` : pl.tz_offset}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
