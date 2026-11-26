import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AlertTriangle, Crown, FolderPlus, Lock, Pencil, Plus, Sparkles, Trash2 } from "lucide-react";
import { apiFetch } from "../../api";
import CitySearchInput from "../../components/CitySearchInput";
import { useApp } from "../../context/AppContext";

export default function ProfilesSavedPage() {
  const { account, members, setActiveMemberId, refreshAccountState, openUpgradeModal, showToast } = useApp();
  const navigate = useNavigate();
  const [folders, setFolders] = useState([]);
  const [preds, setPreds] = useState([]);
  const [selFolderId, setSelFolderId] = useState("");
  const [sentiment, setSentiment] = useState("All");
  const [newFolderName, setNewFolderName] = useState("");
  const [noteTitle, setNoteTitle] = useState("");
  const [noteBody, setNoteBody] = useState("");

  const [editingMember, setEditingMember] = useState(null);
  const [form, setForm] = useState({
    name: "",
    dob: "1996-05-12",
    birth_time: "10:15",
    gender: "Male",
    place_name: "New Delhi, Delhi",
    latitude: 28.6139,
    longitude: 77.2090,
    tz_offset: 5.5,
  });
  const [expireConfirmModal, setExpireConfirmModal] = useState(false);

  async function loadSaved() {
    if (!account) return;
    try {
      const [fRes, pRes] = await Promise.all([
        apiFetch("/saved/folders"),
        apiFetch(`/saved/predictions?${selFolderId ? `folder_id=${selFolderId}&` : ""}sentiment=${sentiment}`),
      ]);
      setFolders(fRes.folders || []);
      setPreds(pRes.predictions || []);
    } catch {
      // ignore
    }
  }

  useEffect(() => {
    setSelFolderId("");
  }, [account?.id]);

  useEffect(() => {
    loadSaved();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [account?.id, selFolderId, sentiment]);

  function startEdit(m) {
    setEditingMember(m);
    setForm({
      name: m.name,
      dob: m.dob,
      birth_time: m.birth_time,
      gender: m.gender,
      place_name: m.place_name,
      latitude: m.latitude,
      longitude: m.longitude,
      tz_offset: m.tz_offset ?? 5.5,
    });
  }

  async function submitProfile(confirmReset = false) {
    if (!account) {
      showToast("Sign in to manage profiles.", "info");
      return;
    }
    if (!form.name.trim()) {
      showToast("Please enter full name.", "error");
      return;
    }
    try {
      if (editingMember) {
        const res = await apiFetch(`/members/${editingMember.id}`, {
          method: "PUT",
          body: JSON.stringify({ ...form, confirm_plan_reset: confirmReset }),
        });
        showToast(res.plan_expired ? "Profile updated; previous Premium plan expired." : "Profile updated", "success");
        setEditingMember(null);
        setExpireConfirmModal(false);
      } else {
        const res = await apiFetch("/members", { method: "POST", body: JSON.stringify(form) });
        setForm((p) => ({ ...p, name: "" }));
        setActiveMemberId(res.member.id);
        showToast("Family profile created (Free tier active)", "success");
      }
      await refreshAccountState();
    } catch (err) {
      if (err.status === 409 && err.detail?.code === "PLAN_EXPIRATION_CONFIRM_REQUIRED") {
        setExpireConfirmModal(true);
      } else {
        showToast(err.message, "error");
      }
    }
  }

  async function deleteProfile(id) {
    try {
      await apiFetch(`/members/${id}`, { method: "DELETE" });
      await refreshAccountState();
      showToast("Profile removed", "info");
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function createFolder(e) {
    e.preventDefault();
    if (!newFolderName.trim()) return;
    try {
      await apiFetch("/saved/folders", {
        method: "POST",
        body: JSON.stringify({ member_id: members[0]?.id || 0, name: newFolderName }),
      });
      setNewFolderName("");
      loadSaved();
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  async function addMadeByYouNote(e) {
    e.preventDefault();
    if (!noteTitle.trim() || !noteBody.trim() || !members[0]) return;
    try {
      let folderId = Number(selFolderId) || folders[0]?.id;
      if (!folderId) {
        const fRes = await apiFetch("/saved/folders", {
          method: "POST",
          body: JSON.stringify({ member_id: members[0].id, name: "Personal Notes" }),
        });
        folderId = fRes.folder.id;
      }
      await apiFetch("/saved/predictions", {
        method: "POST",
        body: JSON.stringify({
          folder_id: folderId,
          member_id: members[0].id,
          title: noteTitle,
          prediction_type: "MadeByYou",
          prediction_text: noteBody,
          sentiment: "MadeByYou",
        }),
      });
      setNoteTitle("");
      setNoteBody("");
      setSentiment("MadeByYou");
      showToast("Saved personal MadeByYou note", "success");
      loadSaved();
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  if (!account) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12 text-center cosmic-card mt-8 rounded-2xl">
        <p className="text-sm text-slate-300">Please sign in (or click Demo Login) to manage Family Profiles &amp; Saved Kundli Predictions.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 grid gap-8 lg:grid-cols-12 animate-fade-up">
      <div className="lg:col-span-5 space-y-6">
        <div className="cosmic-card rounded-3xl p-5 space-y-4">
          <h1 className="text-lg font-extrabold text-white">Family Kundli Profiles</h1>
          <div className="space-y-2.5 text-xs">
            {members.map((m) => (
              <div key={m.id} className="cosmic-hover rounded-2xl border border-slate-800 bg-slate-900/70 p-3 flex items-center justify-between gap-2">
                <div>
                  <div className="font-bold text-white flex flex-wrap items-center gap-1.5">
                    {m.name}
                    {m.plan_id !== 0 ? (
                      <span className="rounded bg-emerald-500/20 px-1.5 py-0.5 text-[10px] text-emerald-300">Premium #{m.plan_id}</span>
                    ) : (
                      <span className="rounded bg-amber-500/15 px-1.5 py-0.5 text-[10px] text-amber-300">Free</span>
                    )}
                  </div>
                  <div className="text-slate-400 mt-0.5">
                    {m.dob} · {m.birth_time} · {m.place_name} · UTC{(m.tz_offset ?? 5.5) >= 0 ? `+${m.tz_offset ?? 5.5}` : m.tz_offset}
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={() => {
                      setActiveMemberId(m.id);
                      navigate("/app/kundli");
                    }}
                    className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-2 py-1 text-[11px] font-semibold text-amber-300 hover:bg-amber-500/20"
                  >
                    Kundli →
                  </button>
                  {m.plan_id === 0 && (
                    <button
                      type="button"
                      onClick={() => openUpgradeModal(`Activate Premium on ${m.name}`, m.id)}
                      className="rounded-lg bg-amber-500/20 px-2 py-1 text-[11px] text-amber-300"
                      title="Upgrade Profile"
                    >
                      <Crown className="h-3.5 w-3.5" />
                    </button>
                  )}
                  <button type="button" onClick={() => startEdit(m)} className="rounded p-1 text-slate-400 hover:text-white" title="Edit">
                    <Pencil className="h-3.5 w-3.5" />
                  </button>
                  <button type="button" onClick={() => deleteProfile(m.id)} className="rounded p-1 text-slate-400 hover:text-rose-400" title="Delete">
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="cosmic-card rounded-3xl p-5 space-y-3 text-xs">
          <div className="flex items-center justify-between">
            <h2 className="font-bold text-amber-300 text-sm">
              {editingMember ? `Edit Profile: ${editingMember.name}` : "Add New Person Profile"}
            </h2>
            {editingMember && (
              <button onClick={() => setEditingMember(null)} className="text-slate-400 hover:text-white">Cancel Edit</button>
            )}
          </div>
          {editingMember?.plan_id !== 0 && editingMember && (
            <div className="flex items-start gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 p-2.5 text-[11px] text-amber-200">
              <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400" />
              <span>Subscribed profile: Gender is locked and changing DOB/time/place expires the active PlanId upon confirmation.</span>
            </div>
          )}
          <input
            placeholder="Full Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-white"
          />
          <div className="grid grid-cols-3 gap-2">
            <input type="date" value={form.dob} onChange={(e) => setForm({ ...form, dob: e.target.value })} className="rounded-xl border border-slate-700 bg-slate-900 px-2 py-2 text-white" />
            <input type="time" value={form.birth_time} onChange={(e) => setForm({ ...form, birth_time: e.target.value })} className="rounded-xl border border-slate-700 bg-slate-900 px-2 py-2 text-white" />
            <select
              disabled={Boolean(editingMember && editingMember.plan_id !== 0)}
              value={form.gender}
              onChange={(e) => setForm({ ...form, gender: e.target.value })}
              className="rounded-xl border border-slate-700 bg-slate-900 px-2 py-2 text-white disabled:opacity-50"
            >
              <option>Male</option>
              <option>Female</option>
            </select>
          </div>
          <CitySearchInput
            value={form.place_name}
            latitude={form.latitude}
            longitude={form.longitude}
            tzOffset={form.tz_offset}
            onSelect={(c) =>
              setForm((p) => ({
                ...p,
                place_name: c.place_name,
                latitude: c.latitude,
                longitude: c.longitude,
                tz_offset: c.tz_offset,
              }))
            }
          />
          <button type="button" onClick={() => submitProfile(false)} className="gold-btn w-full rounded-xl py-2.5">
            {editingMember ? "Save Profile Changes" : "Create Profile & Calculate"}
          </button>
        </div>
      </div>

      <div className="lg:col-span-7 cosmic-card rounded-3xl p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-extrabold text-white">Saved Predictions &amp; Remedy Bookmarks</h2>
          <form onSubmit={createFolder} className="flex gap-2 text-xs">
            <input
              placeholder="New folder name..."
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-1.5 text-white"
            />
            <button type="submit" className="flex items-center gap-1 rounded-xl bg-amber-500/20 px-3 py-1.5 font-semibold text-amber-300">
              <FolderPlus className="h-3.5 w-3.5" /> Add Folder
            </button>
          </form>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs">
          <select
            value={selFolderId}
            onChange={(e) => setSelFolderId(e.target.value)}
            className="rounded-xl border border-slate-700 bg-slate-900 px-2.5 py-1.5 text-white"
          >
            <option value="">All Folders</option>
            {folders.map((f) => (
              <option key={f.id} value={f.id}>{f.name}</option>
            ))}
          </select>
          {["All", "Positive", "Negative", "MadeByYou"].map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setSentiment(s)}
              className={`rounded-xl px-3 py-1.5 font-semibold ${
                sentiment === s ? "bg-amber-500 text-slate-950" : "border border-slate-700 text-slate-300"
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        <form onSubmit={addMadeByYouNote} className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 flex flex-wrap gap-2 text-xs">
          <input
            placeholder="Custom note title (MadeByYou)..."
            value={noteTitle}
            onChange={(e) => setNoteTitle(e.target.value)}
            className="flex-1 min-w-[140px] rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1.5 text-white"
          />
          <input
            placeholder="Observation / insight..."
            value={noteBody}
            onChange={(e) => setNoteBody(e.target.value)}
            className="flex-[2] min-w-[180px] rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1.5 text-white"
          />
          <button type="submit" className="gold-btn rounded-lg px-3 py-1.5 flex items-center gap-1">
            <Plus className="h-3.5 w-3.5" /> Save Note
          </button>
        </form>

        <div className="space-y-3 text-xs">
          {preds.length === 0 ? (
            <p className="text-slate-400 py-8 text-center">No saved predictions in this filter yet.</p>
          ) : (
            preds.map((sp) => (
              <div key={sp.id} className="rounded-xl border border-slate-800 bg-slate-900/70 p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="font-bold text-amber-300">{sp.title}</div>
                  <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] text-slate-300">{sp.sentiment}</span>
                </div>
                <p className="text-slate-200 leading-relaxed">{sp.prediction_text}</p>
                {sp.upay_locked ? (
                  <button
                    type="button"
                    onClick={() => openUpgradeModal("Saved Remedies remain locked on Free Plan profiles.", sp.member_id)}
                    className="flex items-center gap-1.5 rounded-lg bg-rose-500/15 px-3 py-1.5 font-semibold text-rose-300"
                  >
                    <Lock className="h-3.5 w-3.5" /> {sp.upay_text}
                  </button>
                ) : sp.upay_text ? (
                  <div className="rounded-lg bg-emerald-500/10 px-3 py-2 text-emerald-300">
                    Remedy: {sp.upay_text}
                  </div>
                ) : null}
              </div>
            ))
          )}
        </div>
      </div>

      {expireConfirmModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm">
          <div className="cosmic-card animate-fade-up max-w-md rounded-2xl p-6 space-y-4">
            <div className="flex items-center gap-2 text-amber-400 font-bold">
              <AlertTriangle className="h-5 w-5" /> Confirm Plan Expiration
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              If you change the details of this profile then the activated plan will be expired. Are you sure you want to continue?
            </p>
            <div className="flex justify-end gap-2">
              <button onClick={() => setExpireConfirmModal(false)} className="rounded-xl border border-slate-700 px-4 py-1.5 text-xs">Cancel</button>
              <button onClick={() => submitProfile(true)} className="rounded-xl bg-rose-500 px-4 py-1.5 text-xs font-bold text-white">Expire &amp; Update</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
