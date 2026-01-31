import { Routes, Route } from "react-router-dom";

import Layout from "../Components/layout/Layout";
import LandingPage from "../pages/LandingPage";
import Dashboard from "../pages/Dashboard";
import Heatmap from "../pages/Heatmap";
import Analytics from "../pages/Analytics";
import Personas from "../pages/Personas";
import Alerts from "../pages/Alerts";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route
        path="/dashboard"
        element={
          <Layout>
            <Dashboard />
          </Layout>
        }
      />
      <Route
        path="/heatmap"
        element={
          <Layout>
            <Heatmap />
          </Layout>
        }
      />
      <Route
        path="/analytics"
        element={
          <Layout>
            <Analytics />
          </Layout>
        }
      />
      <Route
        path="/personas"
        element={
          <Layout>
            <Personas />
          </Layout>
        }
      />
      <Route
        path="/alerts"
        element={
          <Layout>
            <Alerts />
          </Layout>
        }
      />
    </Routes>
  );
}
