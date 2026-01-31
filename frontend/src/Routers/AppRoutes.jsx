import { Routes, Route } from "react-router-dom";

import Dashboard from "../pages/Dashboard";
import Heatmap from "../pages/Heatmap";
import Analytics from "../pages/Analytics";
import Personas from "../pages/Personas";
import Alerts from "../pages/Alerts";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/heatmap" element={<Heatmap />} />
      <Route path="/analytics" element={<Analytics />} />
      <Route path="/personas" element={<Personas />} />
      <Route path="/alerts" element={<Alerts />} />
    </Routes>
  );
}
