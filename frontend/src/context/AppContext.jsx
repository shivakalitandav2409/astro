import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { apiFetch, getStoredToken, setStoredToken } from "../api";
import { translations } from "../locales/translations";

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [account, setAccount] = useState(null);
  const [members, setMembers] = useState([]);
  const [activeMemberId, setActiveMemberId] = useState(null);
  const [enrolledCourses, setEnrolledCourses] = useState([]);
  const [cartCount, setCartCount] = useState(0);
  const [unreadNotifs, setUnreadNotifs] = useState(0);
  const [lang, setLangState] = useState(() => localStorage.getItem("astro_lang") || "En");
  const [loadingAuth, setLoadingAuth] = useState(true);
  const [upgradeModal, setUpgradeModal] = useState({ open: false, memberId: null, reason: "" });
  const [playingAudio, setPlayingAudio] = useState(null);
  const [toast, setToast] = useState(null);

  const setLang = useCallback((newLang) => {
    setLangState(newLang);
    localStorage.setItem("astro_lang", newLang);
  }, []);

  const t = useCallback((key) => {
    return translations[lang]?.[key] || translations["En"]?.[key] || key;
  }, [lang]);

  const showToast = useCallback((message, type = "info") => {
    setToast({ message, type, id: Date.now() });
    setTimeout(() => {
      setToast((prev) => (prev && Date.now() - prev.id >= 3400 ? null : prev));
    }, 3600);
  }, []);

  const refreshAccountState = useCallback(async () => {
    const token = getStoredToken();
    if (!token) {
      setAccount(null);
      setMembers([]);
      setCartCount(0);
      setUnreadNotifs(0);
      setEnrolledCourses([]);
      setLoadingAuth(false);
      return;
    }
    try {
      const me = await apiFetch("/auth/me");
      setAccount(me.account);
      setEnrolledCourses(me.enrolled_course_ids || []);
      const [mRes, nRes] = await Promise.all([
        apiFetch("/members"),
        apiFetch("/notifications"),
      ]);
      setMembers(mRes.members || []);
      setActiveMemberId((prev) => {
        if (prev && (mRes.members || []).some((m) => m.id === prev)) return prev;
        return mRes.members?.[0]?.id || null;
      });
      setUnreadNotifs((nRes.notifications || []).filter((n) => !n.is_read).length);
    } catch {
      setStoredToken("");
      setAccount(null);
      setMembers([]);
    } finally {
      setLoadingAuth(false);
    }
  }, []);

  useEffect(() => {
    refreshAccountState();
  }, [refreshAccountState]);

  const demoLogin = useCallback(
    async (identifier, password = "Demo@1234", deviceLabel = "Unified Web") => {
      const res = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          identifier,
          password,
          device_label: deviceLabel,
          force_replace: true,
        }),
      });
      setStoredToken(res.token);
      await refreshAccountState();
      showToast(`Signed in as ${res.account.name}`, "success");
      return res;
    },
    [refreshAccountState, showToast]
  );

  const logout = useCallback(async () => {
    try {
      await apiFetch("/auth/logout", { method: "POST" });
    } catch {
      // ignore
    }
    setStoredToken("");
    setAccount(null);
    setMembers([]);
    setActiveMemberId(null);
    showToast("Logged out cleanly", "info");
  }, [showToast]);

  const activeMember = members.find((m) => m.id === activeMemberId) || members[0] || null;

  const openUpgradeModal = useCallback(
    (reason = "", memberId = null) => {
      setUpgradeModal({
        open: true,
        memberId: memberId || activeMember?.id || null,
        reason,
      });
    },
    [activeMember]
  );

  return (
    <AppContext.Provider
      value={{
        account,
        members,
        activeMember,
        activeMemberId,
        setActiveMemberId,
        enrolledCourses,
        cartCount,
        unreadNotifs,
        lang,
        setLang,
        t,
        loadingAuth,
        refreshAccountState,
        demoLogin,
        logout,
        upgradeModal,
        setUpgradeModal,
        openUpgradeModal,
        playingAudio,
        setPlayingAudio,
        toast,
        showToast,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  return useContext(AppContext);
}
