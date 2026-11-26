import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BookmarkPlus, Download, Lock, Sparkles, Unlock, UserPlus } from "lucide-react";
import { apiFetch } from "../../api";
import CitySearchInput from "../../components/CitySearchInput";
import NorthIndianChart from "../../components/NorthIndianChart";
import { useApp } from "../../context/AppContext";

export default function KundliWorkbench() {
  const { account, activeMember, setActiveMemberId, refreshAccountState, openUpgradeModal, showToast } = useApp();
  const [bundle, setBundle] = useState(null);
  const [chartTab, setChartTab] = useState("lagan");
  const [selectedHouse, setSelectedHouse] = useState(1);
  const [targetYear, setTargetYear] = useState(new Date().getFullYear());
  const [loading, setLoading] = useState(false);
  const [guestMode, setGuestMode] = useState(false);
  const [guestForm, setGuestForm] = useState({
    name: "Instant Chart Native",
    dob: "1995-08-15",
    birth_time: "09:30",
    gender: "Male",
    place_name: "New Delhi, Delhi",
    latitude: 28.6139,
    longitude: 77.2090,
    tz_offset: 5.5,
  });
  const [folders, setFolders] = useState([]);
  const [activeUpay, setActiveUpay] = useState(null);
  const [kalyankariTile, setKalyankariTile] = useState(null);

  useEffect(() => {
    if (account) {
      apiFetch("/saved/folders").then((r) => setFolders(r.folders || [])).catch(() => {});
    }
  }, [account]);

  useEffect(() => {
    if (!guestMode && activeMember) {
      fetchBundle({ member_id: activeMember.id, target_year: targetYear });
    } else if (!activeMember || guestMode) {
      fetchBundle({ ...guestForm, target_year: targetYear });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeMember?.id, activeMember?.plan_id, account?.reg_plan_id, targetYear, guestMode]);

  async function fetchBundle(payload) {
    setLoading(true);
    try {
      const data = await apiFetch("/kundli/bundle", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setBundle(data);
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setLoading(false);
    }
  }

  async function saveGuestAsProfile() {
    if (!account) {
      showToast("Sign in (or click Demo Login) to save a profile and unlock Premium.", "info");
      return;
    }
    try {
      const res = await apiFetch("/members", { method: "POST", body: JSON.stringify(guestForm) });
      await refreshAccountState();
      setActiveMemberId(res.member.id);
      setGuestMode(false);
      showToast(`Saved ${res.member.name}! You can now upgrade or inspect anytime.`, "success");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function handleDownloadPdf() {
    try {
      let blob;
      if (guestMode || !activeMember) {
        blob = await apiFetch("/kundli/custom-pdf", {
          method: "POST",
          body: JSON.stringify({ ...guestForm, target_year: targetYear }),
        });
      } else {
        blob = await apiFetch(`/kundli/${activeMember.id}/pdf`);
      }
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `kundali_${(guestMode ? guestForm.name : activeMember?.name || "report").replace(/\s+/g, "_")}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      showToast("Kundali PDF downloaded", "success");
    } catch (err) {
      openUpgradeModal(err.message);
    }
  }

  async function saveHousePrediction(gp) {
    if (!account || !activeMember || guestMode) {
      showToast("Save this person as a Family Profile first to bookmark predictions.", "info");
      return;
    }
    try {
      let folderId = folders[0]?.id;
      if (!folderId) {
        const fRes = await apiFetch("/saved/folders", {
          method: "POST",
          body: JSON.stringify({ member_id: activeMember.id, name: "My Favorites" }),
        });
        folderId = fRes.folder.id;
        setFolders([fRes.folder]);
      }
      await apiFetch("/saved/predictions", {
        method: "POST",
        body: JSON.stringify({
          folder_id: folderId,
          member_id: activeMember.id,
          title: `House ${gp.house} · ${gp.theme}`,
          prediction_type: "Kundli12GharPrediction",
          prediction_text: gp.prediction,
          upay_id: gp.upay_id,
          upay_text: gp.upay,
          sentiment: "Positive",
        }),
      });
      showToast(`Saved House ${gp.house} prediction to Folder!`, "success");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  const chart = bundle?.chart;
  const housesToShow =
    chartTab === "lagan"
      ? chart?.houses
      : chartTab === "gochar"
      ? chart?.gochar_houses
      : chartTab === "vashist"
      ? chart?.vashist_houses
      : bundle?.varshphal?.houses;

  const planetsInSelHouse = (chart?.planets || []).filter((p) => p.house === selectedHouse);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 space-y-6 animate-fade-up">
      {/* Header */}
      <div className="cosmic-card flex flex-wrap items-center justify-between gap-4 rounded-3xl p-5">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-xl font-extrabold text-white">Kundli Workbench (Swiss Ephemeris Lahiri)</h1>
            <span className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold ${bundle?.access_tier === "premium" ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"}`}>
              {bundle?.access_tier === "premium" ? "PREMIUM UNLOCKED" : "FREE TIER ACTIVE"}
            </span>
          </div>
          {bundle && (
            <p className="mt-1 text-xs text-slate-300">
              {bundle.member.name} · Lagna: <strong className="text-amber-300">{chart?.ascendant?.rashi} ({chart?.ascendant?.dms})</strong> · Ayanamsa: {chart?.ayanamsa}
            </p>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => setGuestMode(!guestMode)}
            className="rounded-xl border border-amber-500/40 bg-amber-500/10 px-3.5 py-2 text-xs font-semibold text-amber-300 hover:bg-amber-500/20"
          >
            {guestMode ? "Use Saved Profile" : "Enter Anyone's Birth Details"}
          </button>
          <input
            type="number"
            min="1950"
            max="2060"
            value={targetYear}
            onChange={(e) => setTargetYear(Number(e.target.value))}
            aria-label="Varshphal Year"
            className="w-24 rounded-xl border border-slate-700 bg-slate-900 px-2.5 py-2 text-xs text-white"
          />
          {activeMember && (
            <button type="button" onClick={handleDownloadPdf} className="gold-btn flex items-center gap-1.5 rounded-xl px-3.5 py-2 text-xs">
              <Download className="h-3.5 w-3.5" /> Kundali PDF
            </button>
          )}
        </div>
      </div>

      {/* Instant Custom Birth Chart Form with City Search & Save Button */}
      {guestMode && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            fetchBundle({ ...guestForm, target_year: targetYear });
          }}
          className="cosmic-card animate-fade-up rounded-2xl p-5 space-y-4 text-xs"
        >
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="font-bold text-amber-300 text-sm">Instant Birth Chart for Anyone (Exact City &amp; Timezone Lookup)</div>
            <button
              type="button"
              onClick={saveGuestAsProfile}
              className="flex items-center gap-1.5 rounded-xl border border-emerald-500/40 bg-emerald-500/15 px-3 py-1.5 font-semibold text-emerald-300 hover:bg-emerald-500/25"
            >
              <UserPlus className="h-3.5 w-3.5" /> Save Profile (to Bookmark / Upgrade Premium)
            </button>
          </div>
          <div className="grid gap-3 md:grid-cols-6 items-start">
            <label className="block md:col-span-2">
              <span className="text-slate-400">Full Name</span>
              <input required value={guestForm.name} onChange={(e) => setGuestForm({ ...guestForm, name: e.target.value })} className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white" />
            </label>
            <label className="block">
              <span className="text-slate-400">DOB</span>
              <input required type="date" value={guestForm.dob} onChange={(e) => setGuestForm({ ...guestForm, dob: e.target.value })} className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-900 px-2.5 py-2 text-white" />
            </label>
            <label className="block">
              <span className="text-slate-400">Time</span>
              <input required type="time" value={guestForm.birth_time} onChange={(e) => setGuestForm({ ...guestForm, birth_time: e.target.value })} className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-900 px-2.5 py-2 text-white" />
            </label>
            <label className="block md:col-span-2">
              <span className="text-slate-400">Birth City (auto lat/lon &amp; UTC)</span>
              <div className="mt-1">
                <CitySearchInput
                  value={guestForm.place_name}
                  latitude={guestForm.latitude}
                  longitude={guestForm.longitude}
                  tzOffset={guestForm.tz_offset}
                  onSelect={(c) =>
                    setGuestForm((p) => ({
                      ...p,
                      place_name: c.place_name,
                      latitude: c.latitude,
                      longitude: c.longitude,
                      tz_offset: c.tz_offset,
                    }))
                  }
                />
              </div>
            </label>
          </div>
          <div className="flex justify-end">
            <button type="submit" className="gold-btn rounded-xl px-5 py-2">Calculate Chart Now</button>
          </div>
        </form>
      )}

      {loading && <div className="text-center text-sm text-amber-300 py-8 animate-pulse">Computing exact planetary ephemeris...</div>}

      {bundle && chart && (
        <div className="grid gap-6 lg:grid-cols-12">
          <div className="lg:col-span-5 space-y-4">
            <div className="flex flex-wrap gap-1.5 rounded-2xl border border-slate-800 bg-slate-950 p-1.5 text-xs">
              {[
                { id: "lagan", label: "Lagan" },
                { id: "gochar", label: "Gochar Transit" },
                { id: "vashist", label: "Vashist" },
                { id: "varshphal", label: `Varshphal (${targetYear})` },
              ].map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setChartTab(t.id)}
                  className={`flex-1 rounded-xl px-2 py-2 font-semibold transition ${
                    chartTab === t.id ? "bg-amber-500 text-slate-950" : "text-slate-300 hover:text-white"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            <NorthIndianChart
              houses={housesToShow}
              title={
                chartTab === "lagan"
                  ? "Lagan (D1 Birth Chart)"
                  : chartTab === "gochar"
                  ? "Gochar (Current Planetary Transits)"
                  : chartTab === "vashist"
                  ? "Lal Kitab Vashist Fixed Chart"
                  : `Annual Varshphal · Running Age ${bundle.varshphal.running_age}`
              }
              selectedHouse={selectedHouse}
              onSelectHouse={setSelectedHouse}
            />

            <div className="cosmic-card rounded-2xl p-4 text-xs space-y-2">
              <div className="font-bold text-amber-300">House {selectedHouse} Planetary Details</div>
              {planetsInSelHouse.length === 0 ? (
                <p className="text-slate-400">No natal planets placed directly in House {selectedHouse}.</p>
              ) : (
                planetsInSelHouse.map((p) => (
                  <div key={p.planet} className="flex items-center justify-between rounded-xl bg-slate-900/70 px-3 py-2">
                    <div>
                      <span className="font-bold text-white">{p.planet}</span>{" "}
                      <span className="text-slate-400">({p.nakshatra} P{p.pada})</span>
                    </div>
                    <div className="text-right">
                      <span className="text-amber-300">{p.dms}</span> ·{" "}
                      <span className={p.is_benefic ? "text-emerald-400" : "text-rose-300"}>{p.dignity}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="lg:col-span-7 space-y-6">
            <div className="cosmic-card rounded-2xl p-5 overflow-x-auto">
              <h2 className="mb-3 text-sm font-bold text-amber-300">Exact Sidereal Planetary Table (Lahiri)</h2>
              <table className="w-full text-left text-xs">
                <thead className="border-b border-slate-800 text-slate-400">
                  <tr>
                    <th className="py-2 pr-3">Graha</th>
                    <th className="py-2 pr-3">House</th>
                    <th className="py-2 pr-3">Rashi (Sign)</th>
                    <th className="py-2 pr-3">Deg</th>
                    <th className="py-2 pr-3">Nakshatra</th>
                    <th className="py-2 pr-3">Navamsa</th>
                    <th className="py-2">Dignity</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/70">
                  {chart.planets.map((p) => (
                    <tr key={p.planet} className="hover:bg-slate-900/50">
                      <td className="py-2 pr-3 font-semibold text-white">
                        {p.planet} {p.retrograde ? <span className="text-rose-400">(R)</span> : ""}
                      </td>
                      <td className="py-2 pr-3 text-amber-300">H{p.house}</td>
                      <td className="py-2 pr-3">{p.rashi}</td>
                      <td className="py-2 pr-3 font-mono">{p.dms}</td>
                      <td className="py-2 pr-3">{p.nakshatra} P{p.pada}</td>
                      <td className="py-2 pr-3 text-slate-300">{p.navamsa_rashi.split(" ")[0]}</td>
                      <td className="py-2">
                        <span className={`rounded px-1.5 py-0.5 text-[10px] ${p.is_benefic ? "bg-emerald-500/15 text-emerald-300" : "bg-rose-500/15 text-rose-300"}`}>
                          {p.dignity}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="cosmic-card rounded-2xl p-5">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-sm font-bold text-amber-300">Kundli Vivaran Desk</h2>
                <span className="text-[11px] text-slate-400">Tiles #8, 9, 10, 20 are Kalyankari Free</span>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                {bundle.vivaran.map((v) => (
                  <div
                    key={v.index_id}
                    onClick={() => {
                      if (v.locked) openUpgradeModal(`Vivaran item '${v.desk}' requires Premium Plan.`);
                      else if (v.kalyankari_exempt) setKalyankariTile(v);
                    }}
                    className={`rounded-xl border p-3 text-xs transition ${
                      v.locked
                        ? "cursor-pointer border-rose-500/30 bg-rose-950/15 hover:border-rose-400"
                        : v.kalyankari_exempt
                        ? "cursor-pointer border-amber-500/40 bg-amber-950/15 hover:border-amber-400"
                        : "border-slate-800 bg-slate-900/70"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white">{v.desk}</span>
                      {v.locked ? (
                        <Lock className="h-3.5 w-3.5 text-rose-400" />
                      ) : v.kalyankari_exempt ? (
                        <span className="rounded bg-amber-500/20 px-1.5 py-0.5 text-[10px] font-bold text-amber-300">Kalyankari Free</span>
                      ) : (
                        <span className="font-semibold text-amber-300">{v.value}</span>
                      )}
                    </div>
                    <p className="mt-1.5 text-slate-400">{v.detail}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {bundle && (
        <div className="space-y-3">
          <h2 className="text-lg font-bold text-white">12-Ghar (House) Predictions &amp; Remedies (Upay)</h2>
          <div className="grid gap-4 md:grid-cols-2">
            {bundle.ghar_predictions.map((gp) => (
              <div key={gp.house} className="cosmic-card cosmic-hover rounded-2xl p-4 text-xs space-y-2.5">
                <div className="flex items-center justify-between">
                  <div className="font-bold text-amber-300 text-sm">House {gp.house} · {gp.theme}</div>
                  <button
                    type="button"
                    onClick={() => saveHousePrediction(gp)}
                    className="flex items-center gap-1 rounded-lg border border-slate-700 px-2 py-1 text-[11px] text-slate-300 hover:border-amber-400"
                  >
                    <BookmarkPlus className="h-3.5 w-3.5" /> Save
                  </button>
                </div>
                <div className="text-[11px] text-slate-400">
                  Sign: {gp.rashi} · Lord: {gp.lord} {gp.planets.length > 0 ? `· Occupants: ${gp.planets.join(", ")}` : ""}
                </div>
                <p className="leading-relaxed text-slate-200">{gp.prediction}</p>

                <div className="pt-1 flex items-center justify-between border-t border-slate-800/80">
                  {gp.upay_locked ? (
                    <button
                      type="button"
                      onClick={() => openUpgradeModal(`Unlock Lal Kitab Remedy for House ${gp.house}.`)}
                      className="flex items-center gap-1.5 rounded-lg bg-rose-500/15 px-3 py-1.5 font-semibold text-rose-300 hover:bg-rose-500/25"
                    >
                      <Lock className="h-3.5 w-3.5" /> View Remedy (Locked on Free Plan)
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() => setActiveUpay(gp)}
                      className="flex items-center gap-1.5 rounded-lg bg-emerald-500/15 px-3 py-1.5 font-semibold text-emerald-300 hover:bg-emerald-500/25"
                    >
                      <Unlock className="h-3.5 w-3.5" /> View Remedy (Upay #{gp.upay_id})
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeUpay && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm">
          <div className="cosmic-card animate-fade-up max-w-md rounded-2xl p-6 space-y-3">
            <div className="flex items-center gap-2 text-emerald-300 font-bold">
              <Sparkles className="h-5 w-5" /> House {activeUpay.house} Lal Kitab Remedy (Upay)
            </div>
            <p className="text-xs leading-relaxed text-slate-200">{activeUpay.upay}</p>
            <div className="flex justify-end">
              <button onClick={() => setActiveUpay(null)} className="gold-btn rounded-xl px-4 py-1.5 text-xs">Done</button>
            </div>
          </div>
        </div>
      )}

      {kalyankariTile && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm">
          <div className="cosmic-card animate-fade-up max-w-md rounded-2xl p-6 space-y-3">
            <div className="flex items-center gap-2 text-amber-300 font-bold">
              <Sparkles className="h-5 w-5" /> {kalyankariTile.desk} (Kalyankari Free #{kalyankariTile.index_id})
            </div>
            <p className="text-xs leading-relaxed text-slate-200">{kalyankariTile.detail}</p>
            <div className="flex justify-end gap-2 pt-2">
              <button onClick={() => setKalyankariTile(null)} className="rounded-xl border border-slate-700 px-4 py-1.5 text-xs text-slate-300">Close</button>
              <Link to="/app/shop" onClick={() => setKalyankariTile(null)} className="gold-btn rounded-xl px-4 py-1.5 text-xs">
                View Kalyankari Puja in Store
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
