import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BookmarkPlus, Download, Lock, Sparkles, Unlock, UserPlus } from "lucide-react";
import { apiFetch } from "../../api";
import CitySearchInput from "../../components/CitySearchInput";
import NorthIndianChart from "../../components/NorthIndianChart";
import { useApp } from "../../context/AppContext";

export default function KundliWorkbench() {
  const {
    account,
    activeMember,
    setActiveMemberId,
    refreshAccountState,
    openUpgradeModal,
    showToast,
    lang,
    t,
  } = useApp();
  const isHindi = lang === "हिं";
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
  const [downloadLangModal, setDownloadLangModal] = useState(false);
  const [downloading, setDownloading] = useState(false);

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

  async function executeDownloadPdf(chosenLang = "en") {
    setDownloading(true);
    try {
      let blob;
      if (guestMode || !activeMember) {
        blob = await apiFetch(`/kundli/custom-pdf?lang=${chosenLang}`, {
          method: "POST",
          body: JSON.stringify({ ...guestForm, target_year: targetYear }),
        });
      } else {
        blob = await apiFetch(`/kundli/${activeMember.id}/pdf?lang=${chosenLang}`);
      }
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const langSuffix = chosenLang === "hi" ? "_Hindi" : "_English";
      a.download = `kundali_${(guestMode ? guestForm.name : activeMember?.name || "report").replace(/\s+/g, "_")}${langSuffix}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      showToast(chosenLang === "hi" ? "हिंदी कुंडली PDF डाउनलोड हो गई!" : "Kundali PDF report downloaded!", "success");
      setDownloadLangModal(false);
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setDownloading(false);
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
            <h1 className="text-xl font-extrabold text-white">
              {isHindi ? "कुंडली कार्यशाला (स्वीस एफिमेरिस लाहिरी)" : "Kundli Workbench (Swiss Ephemeris Lahiri)"}
            </h1>
            <span className="rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-[11px] font-bold text-emerald-300">
              {isHindi ? "संपूर्ण योजना सक्रिय" : "FULL PLAN ACTIVE"}
            </span>
          </div>
          {bundle && (
            <p className="mt-1 text-xs text-slate-300">
              {bundle.member.name} · {isHindi ? "लग्न" : "Lagna"}:{" "}
              <strong className="text-amber-300">
                {isHindi ? chart?.ascendant?.rashi_hi || chart?.ascendant?.rashi : chart?.ascendant?.rashi} ({chart?.ascendant?.dms})
              </strong>{" "}
              · {isHindi ? "अयनांश" : "Ayanamsa"}: {chart?.ayanamsa}
            </p>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => setGuestMode(!guestMode)}
            className="rounded-xl border border-amber-500/40 bg-amber-500/10 px-3.5 py-2 text-xs font-semibold text-amber-300 hover:bg-amber-500/20"
          >
            {guestMode
              ? isHindi
                ? "सहेजी गई प्रोफ़ाइल देखें"
                : "Use Saved Profile"
              : isHindi
              ? "किसी का भी जन्म विवरण भरें"
              : "Enter Anyone's Birth Details"}
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
          <button
            type="button"
            onClick={() => setDownloadLangModal(true)}
            className="gold-btn flex items-center gap-1.5 rounded-xl px-3.5 py-2 text-xs"
            title={isHindi ? "पूरी कुंडली PDF डाउनलोड करें" : "Download Full Kundali PDF Report"}
          >
            <Download className="h-3.5 w-3.5" />{" "}
            {isHindi ? "पूरी कुंडली PDF डाउनलोड करें" : "Download Full Plan PDF"}
          </button>
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
            <div className="font-bold text-amber-300 text-sm">
              {isHindi
                ? "किसी का भी तुरंत जन्म चक्र देखें (सटीक शहर व समय-क्षेत्र गणना)"
                : "Instant Birth Chart for Anyone (Exact City & Timezone Lookup)"}
            </div>
            <button
              type="button"
              onClick={saveGuestAsProfile}
              className="flex items-center gap-1.5 rounded-xl border border-emerald-500/40 bg-emerald-500/15 px-3 py-1.5 font-semibold text-emerald-300 hover:bg-emerald-500/25"
            >
              <UserPlus className="h-3.5 w-3.5" /> {isHindi ? "प्रोफ़ाइल सहेजें" : "Save Profile"}
            </button>
          </div>
          <div className="grid gap-3 md:grid-cols-6 items-start">
            <label className="block md:col-span-2">
              <span className="text-slate-400">{isHindi ? "पूरा नाम" : "Full Name"}</span>
              <input
                required
                value={guestForm.name}
                onChange={(e) => setGuestForm({ ...guestForm, name: e.target.value })}
                className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white"
              />
            </label>
            <label className="block">
              <span className="text-slate-400">{isHindi ? "जन्म तिथि" : "DOB"}</span>
              <input
                required
                type="date"
                value={guestForm.dob}
                onChange={(e) => setGuestForm({ ...guestForm, dob: e.target.value })}
                className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-900 px-2.5 py-2 text-white"
              />
            </label>
            <label className="block">
              <span className="text-slate-400">{isHindi ? "जन्म समय" : "Time"}</span>
              <input
                required
                type="time"
                value={guestForm.birth_time}
                onChange={(e) => setGuestForm({ ...guestForm, birth_time: e.target.value })}
                className="mt-1 w-full rounded-xl border border-slate-700 bg-slate-900 px-2.5 py-2 text-white"
              />
            </label>
            <label className="block md:col-span-2">
              <span className="text-slate-400">
                {isHindi ? "जन्म स्थान / शहर (अक्षांश/देशांतर स्वतः)" : "Birth City (auto lat/lon & UTC)"}
              </span>
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
            <button type="submit" className="gold-btn rounded-xl px-5 py-2">
              {isHindi ? "कुंडली अभी देखें" : "Calculate Chart Now"}
            </button>
          </div>
        </form>
      )}

      {loading && (
        <div className="text-center text-sm text-amber-300 py-8 animate-pulse">
          {isHindi ? "सटीक खगोलीय ग्रह स्थिति की गणना हो रही है..." : "Computing exact planetary ephemeris..."}
        </div>
      )}

      {bundle && chart && (
        <div className="grid gap-6 lg:grid-cols-12">
          <div className="lg:col-span-5 space-y-4">
            <div className="flex flex-wrap gap-1.5 rounded-2xl border border-slate-800 bg-slate-950 p-1.5 text-xs">
              {[
                { id: "lagan", label: isHindi ? "लग्न" : "Lagan" },
                { id: "gochar", label: isHindi ? "गोचर" : "Gochar Transit" },
                { id: "vashist", label: isHindi ? "वशिष्ठ" : "Vashist" },
                { id: "varshphal", label: isHindi ? `वर्षफल (${targetYear})` : `Varshphal (${targetYear})` },
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
              isHindi={isHindi}
              title={
                chartTab === "lagan"
                  ? isHindi ? "लग्न कुंडली (D1 जन्म चक्र)" : "Lagan (D1 Birth Chart)"
                  : chartTab === "gochar"
                  ? isHindi ? "गोचर (वर्तमान ग्रह स्थिति)" : "Gochar (Current Planetary Transits)"
                  : chartTab === "vashist"
                  ? isHindi ? "लाल किताब वशिष्ठ निश्चित चक्र" : "Lal Kitab Vashist Fixed Chart"
                  : isHindi ? `वार्षिक वर्षफल · आयु वर्ष ${bundle.varshphal.running_age}` : `Annual Varshphal · Running Age ${bundle.varshphal.running_age}`
              }
              selectedHouse={selectedHouse}
              onSelectHouse={setSelectedHouse}
            />

            <div className="cosmic-card rounded-2xl p-4 text-xs space-y-2">
              <div className="font-bold text-amber-300">
                {isHindi ? `भाव ${selectedHouse} में स्थित ग्रहों का विवरण` : `House ${selectedHouse} Planetary Details`}
              </div>
              {planetsInSelHouse.length === 0 ? (
                <p className="text-slate-400">
                  {isHindi
                    ? `भाव ${selectedHouse} में कोई जन्मकालीन ग्रह स्थित नहीं है।`
                    : `No natal planets placed directly in House ${selectedHouse}.`}
                </p>
              ) : (
                planetsInSelHouse.map((p) => (
                  <div key={p.planet} className="flex items-center justify-between rounded-xl bg-slate-900/70 px-3 py-2">
                    <div>
                      <span className="font-bold text-white">{isHindi ? p.planet_hi || p.planet : p.planet}</span>{" "}
                      <span className="text-slate-400">
                        ({p.nakshatra} {isHindi ? "चरण" : "P"}{p.pada})
                      </span>
                    </div>
                    <div className="text-right">
                      <span className="text-amber-300 font-mono">{p.dms}</span> ·{" "}
                      <span className={p.is_benefic ? "text-emerald-400 font-medium" : "text-rose-300 font-medium"}>
                        {isHindi ? p.dignity_hi || p.dignity : p.dignity}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="lg:col-span-7 space-y-6">
            <div className="cosmic-card rounded-2xl p-4 sm:p-5">
              <h2 className="mb-3 text-sm font-bold text-amber-300">
                {isHindi ? "शुद्ध निरयण ग्रह स्थिति (लाहिरी)" : "Exact Sidereal Planetary Placements (Lahiri)"}
              </h2>

              {/* Mobile Card View (No Horizontal Scrolling) */}
              <div className="sm:hidden grid gap-2.5">
                {chart.planets.map((p) => (
                  <div key={p.planet} className="rounded-xl border border-slate-800 bg-slate-900/80 p-3 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <div className="font-bold text-white text-sm flex items-center gap-1.5">
                        <span>{isHindi ? p.planet_hi || p.planet : p.planet}</span>
                        {p.retrograde && (
                          <span className="rounded bg-rose-500/20 px-1 py-0.5 text-[9px] text-rose-300 font-bold">
                            {isHindi ? "व" : "R"}
                          </span>
                        )}
                      </div>
                      <span className="rounded-lg bg-amber-500/20 px-2 py-0.5 text-xs font-bold text-amber-300">
                        {isHindi ? `भाव ${p.house}` : `House ${p.house}`}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-slate-300">
                      <span>{isHindi ? p.rashi_hi || p.rashi : p.rashi}</span>
                      <span className="font-mono text-amber-200">{p.dms}</span>
                    </div>
                    <div className="flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-800/80 pt-1.5">
                      <span>
                        {p.nakshatra} ({isHindi ? "चरण" : "P"}{p.pada})
                      </span>
                      <span className={`font-semibold ${p.is_benefic ? "text-emerald-400" : "text-amber-400"}`}>
                        {isHindi ? p.dignity_hi || p.dignity : p.dignity}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Desktop Table View */}
              <div className="hidden sm:block overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="border-b border-slate-800 text-slate-400">
                    <tr>
                      <th className="py-2 pr-3">{isHindi ? "ग्रह" : "Graha"}</th>
                      <th className="py-2 pr-3">{isHindi ? "भाव" : "House"}</th>
                      <th className="py-2 pr-3">{isHindi ? "राशि" : "Rashi (Sign)"}</th>
                      <th className="py-2 pr-3">{isHindi ? "अंश" : "Deg"}</th>
                      <th className="py-2 pr-3">{isHindi ? "नक्षत्र" : "Nakshatra"}</th>
                      <th className="py-2 pr-3">{isHindi ? "नवांश" : "Navamsa"}</th>
                      <th className="py-2">{isHindi ? "अवस्था" : "Dignity"}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/70">
                    {chart.planets.map((p) => (
                      <tr key={p.planet} className="hover:bg-slate-900/50">
                        <td className="py-2 pr-3 font-semibold text-white">
                          {isHindi ? p.planet_hi || p.planet : p.planet}{" "}
                          {p.retrograde ? <span className="text-rose-400">({isHindi ? "व" : "R"})</span> : ""}
                        </td>
                        <td className="py-2 pr-3 text-amber-300">{isHindi ? `भाव ${p.house}` : `H${p.house}`}</td>
                        <td className="py-2 pr-3">{isHindi ? p.rashi_hi || p.rashi : p.rashi}</td>
                        <td className="py-2 pr-3 font-mono">{p.dms}</td>
                        <td className="py-2 pr-3">
                          {p.nakshatra} {isHindi ? "चरण" : "P"}{p.pada}
                        </td>
                        <td className="py-2 pr-3 text-slate-300">
                          {isHindi
                            ? (p.navamsa_rashi_hi || p.navamsa_rashi).split(" ")[0]
                            : p.navamsa_rashi.split(" ")[0]}
                        </td>
                        <td className="py-2">
                          <span
                            className={`rounded px-1.5 py-0.5 text-[10px] ${
                              p.is_benefic ? "bg-emerald-500/15 text-emerald-300" : "bg-rose-500/15 text-rose-300"
                            }`}
                          >
                            {isHindi ? p.dignity_hi || p.dignity : p.dignity}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="cosmic-card rounded-2xl p-5">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-sm font-bold text-amber-300">
                  {isHindi ? "कुंडली विवरण डेस्क" : "Kundli Vivaran Desk"}
                </h2>
                <span className="text-[11px] text-slate-400">
                  {isHindi ? "कल्याणकारी निःशुल्क मार्गदर्शन एवं आध्यात्मिक उपाय" : "Tiles #8, 9, 10, 20 are Kalyankari Free"}
                </span>
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
                      <span className="font-bold text-white">{isHindi ? v.desk_hi || v.desk : v.desk}</span>
                      {v.locked ? (
                        <Lock className="h-3.5 w-3.5 text-rose-400" />
                      ) : v.kalyankari_exempt ? (
                        <span className="rounded bg-amber-500/20 px-1.5 py-0.5 text-[10px] font-bold text-amber-300">
                          {isHindi ? "कल्याणकारी निःशुल्क" : "Kalyankari Free"}
                        </span>
                      ) : (
                        <span className="font-semibold text-amber-300">{isHindi ? v.value_hi || v.value : v.value}</span>
                      )}
                    </div>
                    <p className="mt-1.5 text-slate-400 leading-relaxed">{isHindi ? v.detail_hi || v.detail : v.detail}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {bundle && (
        <div className="space-y-3">
          <h2 className="text-lg font-bold text-white">
            {isHindi ? "12 भाव (घर) फलकथन एवं लाल किताब उपाय" : "12-Ghar (House) Predictions & Remedies (Upay)"}
          </h2>
          <div className="grid gap-4 md:grid-cols-2">
            {bundle.ghar_predictions.map((gp) => (
              <div key={gp.house} className="cosmic-card cosmic-hover rounded-2xl p-4 text-xs space-y-2.5">
                <div className="flex items-center justify-between">
                  <div className="font-bold text-amber-300 text-sm">
                    {isHindi ? `भाव ${gp.house} · ${gp.theme_hi || gp.theme}` : `House ${gp.house} · ${gp.theme}`}
                  </div>
                  <button
                    type="button"
                    onClick={() => saveHousePrediction(gp)}
                    className="flex items-center gap-1 rounded-lg border border-slate-700 px-2 py-1 text-[11px] text-slate-300 hover:border-amber-400"
                  >
                    <BookmarkPlus className="h-3.5 w-3.5" /> {isHindi ? "सहेजें" : "Save"}
                  </button>
                </div>
                <div className="text-[11px] text-slate-400">
                  {isHindi
                    ? `राशि: ${gp.rashi_hi || gp.rashi} · स्वामी: ${gp.lord_hi || gp.lord} ${
                        gp.planets_hi?.length ? `· स्थित ग्रह: ${gp.planets_hi.join(", ")}` : ""
                      }`
                    : `Sign: ${gp.rashi} · Lord: ${gp.lord} ${gp.planets.length > 0 ? `· Occupants: ${gp.planets.join(", ")}` : ""}`}
                </div>
                <p className="leading-relaxed text-slate-200">{isHindi ? gp.prediction_hi || gp.prediction : gp.prediction}</p>

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
                      <Unlock className="h-3.5 w-3.5" />{" "}
                      {isHindi ? `उपाय देखें (उपाय #${gp.upay_id})` : `View Remedy (Upay #${gp.upay_id})`}
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
              <Sparkles className="h-5 w-5" />{" "}
              {isHindi
                ? `भाव ${activeUpay.house} लाल किताब उपाय (Upay)`
                : `House ${activeUpay.house} Lal Kitab Remedy (Upay)`}
            </div>
            <p className="text-xs leading-relaxed text-slate-200">
              {isHindi ? activeUpay.upay_hi || activeUpay.upay : activeUpay.upay}
            </p>
            <div className="flex justify-end">
              <button onClick={() => setActiveUpay(null)} className="gold-btn rounded-xl px-4 py-1.5 text-xs">
                {isHindi ? "ठीक है" : "Done"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Choose Your Report Language Modal */}
      {downloadLangModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-md animate-fade-up">
          <div className="cosmic-card w-full max-w-md rounded-3xl p-6 text-center space-y-5 border border-amber-500/40 shadow-2xl">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-500/15 text-amber-400">
              <Download className="h-7 w-7 animate-bounce" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Choose Your Report Language</h3>
              <p className="mt-1 text-xs text-amber-200/80 font-medium">अपनी पूरी कुंडली रिपोर्ट की भाषा चुनें</p>
              <p className="mt-2 text-[11px] text-slate-400">
                Detailed Swiss Ephemeris calculations, 12-house analysis &amp; personalized Lal Kitab remedies.
              </p>
            </div>

            <div className="space-y-3 pt-1">
              <button
                type="button"
                disabled={downloading}
                onClick={() => executeDownloadPdf("hi")}
                className="w-full flex items-center justify-between rounded-2xl border border-amber-500/50 bg-gradient-to-r from-amber-500/20 to-orange-500/15 p-4 text-left transition hover:scale-[1.02] hover:border-amber-400"
              >
                <div>
                  <div className="font-bold text-amber-300 text-sm">हिंदी में डाउनलोड करें</div>
                  <div className="text-[11px] text-slate-300">सरल हिंदी में ग्रह प्रभाव और सटीक उपाय</div>
                </div>
                <span className="rounded-xl bg-amber-500 px-3 py-1 text-xs font-bold text-slate-950">
                  {downloading ? "तैयार हो रहा है..." : "PDF (हिं)"}
                </span>
              </button>

              <button
                type="button"
                disabled={downloading}
                onClick={() => executeDownloadPdf("en")}
                className="w-full flex items-center justify-between rounded-2xl border border-slate-700 bg-slate-900/80 p-4 text-left transition hover:scale-[1.02] hover:border-slate-500"
              >
                <div>
                  <div className="font-bold text-white text-sm">Download in English</div>
                  <div className="text-[11px] text-slate-400">Conversational English explanations &amp; analysis</div>
                </div>
                <span className="rounded-xl bg-slate-800 px-3 py-1 text-xs font-bold text-slate-200">
                  {downloading ? "Generating..." : "PDF (En)"}
                </span>
              </button>
            </div>

            <div className="pt-2">
              <button
                type="button"
                disabled={downloading}
                onClick={() => setDownloadLangModal(false)}
                className="rounded-xl px-5 py-2 text-xs font-semibold text-slate-400 hover:text-white"
              >
                Cancel / रद्द करें
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
