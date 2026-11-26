import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppProvider, useApp } from "./context/AppContext";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import UpgradeModal from "./components/UpgradeModal";

// Portal pages
import PortalLanding from "./pages/portal/PortalLanding";
import PortalLogin from "./pages/portal/PortalLogin";
import PortalRegistration from "./pages/portal/PortalRegistration";
import CourseDetailsPage from "./pages/portal/CourseDetailsPage";
import ProductServicesPage from "./pages/portal/ProductServicesPage";
import InfoPolicyPages from "./pages/portal/InfoPolicyPages";
import AcharyaWorkspace from "./pages/portal/AcharyaWorkspace";
import CrmConsolePage from "./pages/portal/CrmConsolePage";
import GurujiLivePage from "./pages/portal/GurujiLivePage";

// Consumer App pages
import ConsumerHome from "./pages/app/ConsumerHome";
import KundliWorkbench from "./pages/app/KundliWorkbench";
import DashaExplorer from "./pages/app/DashaExplorer";
import MatchmakingPage from "./pages/app/MatchmakingPage";
import PanchangPage from "./pages/app/PanchangPage";
import ProfilesSavedPage from "./pages/app/ProfilesSavedPage";
import ShopCartPage from "./pages/app/ShopCartPage";
import ConsultMediaPage from "./pages/app/ConsultMediaPage";

function ToastOverlay() {
  const { toast } = useApp();
  if (!toast) return null;
  const color =
    toast.type === "error"
      ? "border-rose-500/50 bg-rose-950/95 text-rose-200"
      : toast.type === "success"
      ? "border-emerald-500/50 bg-emerald-950/95 text-emerald-200"
      : "border-amber-500/50 bg-slate-900/95 text-amber-200";

  return (
    <div className={`fixed top-20 right-4 z-50 rounded-xl border px-4 py-2.5 text-xs font-semibold shadow-2xl ${color}`}>
      {toast.message}
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppProvider>
        <div className="min-h-screen flex flex-col">
          <Navbar />
          <ToastOverlay />
          <UpgradeModal />
          <main className="flex-1">
            <Routes>
              {/* GDVPanel Portal Routes */}
              <Route path="/" element={<PortalLanding />} />
              <Route path="/login" element={<PortalLogin />} />
              <Route path="/registration" element={<PortalRegistration />} />
              <Route path="/registration/:id" element={<PortalRegistration />} />
              <Route path="/courses-details" element={<CourseDetailsPage />} />
              <Route path="/courses-details/:id" element={<CourseDetailsPage />} />
              <Route path="/product_services" element={<ProductServicesPage />} />
              <Route path="/about-us" element={<InfoPolicyPages pageKey="about" />} />
              <Route path="/contact-us" element={<InfoPolicyPages pageKey="contact" />} />
              <Route path="/privacy-policy" element={<InfoPolicyPages pageKey="privacy" />} />
              <Route path="/terms_and_conditions" element={<InfoPolicyPages pageKey="terms" />} />
              <Route path="/return_and_refunds" element={<InfoPolicyPages pageKey="refunds" />} />
              <Route path="/shipping_and_delivery" element={<InfoPolicyPages pageKey="shipping" />} />
              <Route path="/acharya" element={<AcharyaWorkspace />} />
              <Route path="/acharya/*" element={<AcharyaWorkspace />} />
              <Route path="/crm-agent" element={<CrmConsolePage />} />
              <Route path="/crm-registration" element={<CrmConsolePage />} />
              <Route path="/all-transaction" element={<CrmConsolePage />} />
              <Route path="/guruji-live" element={<GurujiLivePage />} />

              {/* AstroScience Consumer App Routes */}
              <Route path="/app" element={<ConsumerHome />} />
              <Route path="/app/kundli" element={<KundliWorkbench />} />
              <Route path="/app/dashas" element={<DashaExplorer />} />
              <Route path="/app/matchmaking" element={<MatchmakingPage />} />
              <Route path="/app/panchang" element={<PanchangPage />} />
              <Route path="/app/profiles" element={<ProfilesSavedPage />} />
              <Route path="/app/shop" element={<ShopCartPage />} />
              <Route path="/app/media" element={<ConsultMediaPage />} />

              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </AppProvider>
    </BrowserRouter>
  );
}
