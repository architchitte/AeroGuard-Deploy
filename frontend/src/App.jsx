import { Routes, Route, useLocation } from "react-router-dom";
import Navbar from "./Components/Navbar";

import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import HealthRisk from "./pages/HealthRisk";

function AppLayout() {
  const location = useLocation();

  const isLanding = location.pathname === "/";
  const isDashboard = location.pathname === "/dashboard";

  return (
    <div className="bg-void min-h-screen text-slate-300 overflow-x-hidden">
      <Navbar variant={isLanding ? "landing" : "dashboard"} />

      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/health-risk" element={<HealthRisk />} />
      </Routes>
    </div>
  );
}

export default AppLayout;
