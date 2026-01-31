import { useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  MapPin,
  Activity,
  AlertTriangle,
  User,
  HeartPulse,
} from "lucide-react";

import { useAQIData } from "../hooks/useAQIData";
import CityHeatmap from "../Components/CityHeatmap";
import LocationSearch from "../components/LocationSelector";
import AeroIntelligenceBriefing from "../Components/AeroIntelligenceBriefing";
import PersonalizedHealthAdvice from "../components/PersonalizedHealthAdvice";
import ContributingFactors from "../Components/ContributingFactors";


/* ---------------- PERSONAS ---------------- */

const PERSONAS = [
  { id: "general", label: "General Public", icon: User },
  { id: "vulnerable", label: "Children / Elderly", icon: HeartPulse },
  { id: "outdoor", label: "Outdoor Workers / Athletes", icon: Activity },
];

const POLLUTANT_CONFIG = {
  pm25: { name: "PM2.5", unit: "µg/m³" },
  pm10: { name: "PM10", unit: "µg/m³" },
  no2: { name: "NO2", unit: "ppb" },
  o3: { name: "O3", unit: "ppb" },
  so2: { name: "SO2", unit: "ppb" },
  co: { name: "CO", unit: "ppm" },
};

export default function Dashboard() {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [selectedPersona, setSelectedPersona] = useState("general");

  const hasLocation = !!selectedLocation;

  // ✅ Hook ALWAYS called
  const { data, loading, error } = useAQIData(
    selectedLocation?.name ?? null,
    selectedPersona
  );
  /* ============================
     1️⃣ SEARCH SCREEN (HIGHEST PRIORITY)
     ============================ */
  if (!selectedLocation) {
    return (
      <div className="min-h-screen bg-void flex items-center justify-center">
        <div className="max-w-xl text-center px-4">
          <h1 className="text-5xl font-bold text-white mb-4">
            Explore Air Quality
          </h1>

          <p className="text-slate-400 mb-8">
            Search any city or area to view real-time AQI,
            pollution heatmaps, and health insights.
          </p>

          <LocationSearch onSelect={setSelectedLocation} />
        </div>
      </div>
    );
  }

  /* ============================
     2️⃣ LOADING (ONLY AFTER LOCATION)
     ============================ */
  if (loading) {
    return (
      <div className="min-h-screen bg-void flex items-center justify-center text-slate-400">
        <Activity className="w-10 h-10 animate-pulse text-neon-teal mb-3" />
        <p>Analyzing Atmospheric Conditions…</p>
      </div>
    );
  }

  /* ============================
     3️⃣ ERROR
     ============================ */
  if (error) {
    return (
      <div className="min-h-screen bg-void flex items-center justify-center text-red-400">
        <AlertTriangle className="w-8 h-8 mr-2" />
        {error}
      </div>
    );
  }

  if (!data) return null;

  /* ---------------- THEME ---------------- */

  const getTheme = (aqi) => {
    if (aqi <= 50) return { color: "text-neon-teal", stroke: "#14b8a6" };
    if (aqi <= 100) return { color: "text-yellow-400", stroke: "#facc15" };
    if (aqi <= 200) return { color: "text-orange-500", stroke: "#f97316" };
    return { color: "text-red-500", stroke: "#ef4444" };
  };

  const theme = getTheme(data.current_aqi.value);

  const pollutants = Object.entries(data.pollutants).map(([key, val]) => ({
    id: key,
    name: POLLUTANT_CONFIG[key]?.name || key,
    value: val.value,
    unit: POLLUTANT_CONFIG[key]?.unit || "",
  }));

  /* ---------------- DASHBOARD ---------------- */

  return (
    <div className="min-h-screen bg-void text-slate-300 flex flex-col">

      {/* ================= MAIN ================= */}
      <main className="flex-1 container mx-auto px-6 pt-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

          {/* ================= LEFT ================= */}
          <aside className="lg:col-span-3 space-y-6">

            {/* SEARCH */}
            <div className="glass-panel p-4 rounded-xl">
              <LocationSearch onSelect={setSelectedLocation} />
            </div>

            {/* LOCATION */}
            <div className="glass-panel p-4 rounded-xl">
              <p className="text-xs uppercase text-slate-500 mb-1">
                Selected Location
              </p>
              <div className="flex items-center gap-2 text-white font-semibold">
                <MapPin size={14} />
                {selectedLocation.name}
              </div>
            </div>

            {/* HEALTH PROFILE */}
            {/* <div className="glass-panel p-4 rounded-xl space-y-1">
              <p className="text-xs uppercase text-slate-500 mb-2">
                Health Profile
              </p>

              {PERSONAS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setSelectedPersona(p.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-md transition ${
                    selectedPersona === p.id
                      ? "bg-indigo-500/20 text-white"
                      : "hover:bg-white/5 text-slate-400"
                  }`}
                >
                  <p.icon size={16} />
                  {p.label}
                </button>
              ))}
            </div> */}

          </aside>

          {/* ================= CENTER ================= */}
          <section className="lg:col-span-6 space-y-6">

            {/* AQI HERO */}
            <div className="relative glass-panel p-8 rounded-2xl border border-white/10 h-[280px]">
              <div
                className={`absolute -top-20 -right-20 w-56 h-56 blur-[120px] opacity-20 ${
                  theme.color.includes("teal")
                    ? "bg-teal-500"
                    : theme.color.includes("yellow")
                    ? "bg-yellow-500"
                    : theme.color.includes("orange")
                    ? "bg-orange-500"
                    : "bg-red-500"
                }`}
              />

              <div className="flex justify-between items-start">
                <div>
                  <p className={`text-xs uppercase tracking-widest mb-1 ${theme.color}`}>
                    Real-Time AQI
                  </p>
                  <h2 className="text-7xl font-black text-white">
                    {data.current_aqi.value}
                  </h2>
                </div>

                <div className={`px-3 py-1 rounded-xl border ${theme.color.replace("text","border")}/30 bg-white/5`}>
                  <p className={`text-sm font-bold ${theme.color}`}>
                    {data.current_aqi.category}
                  </p>
                </div>
              </div>

              <p className="text-xs text-slate-500 mt-3 flex items-center gap-2">
                <Activity size={12} className="text-neon-teal" />
                Updated {new Date(data.current_aqi.updated_at).toLocaleTimeString()}
              </p>
            </div>

            {/* AI BRIEFING */}
            <div className="lg:col-span-9 glass-panel p-8 rounded-3xl border border-white/10">
              <AeroIntelligenceBriefing
                city={selectedLocation.name}
                // persona={selectedPersona}
              />
            </div>

            {/* POLLUTANTS */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {pollutants.map((p) => (
                <div key={p.id} className="glass-panel p-4 rounded-xl">
                  <p className="text-[10px] uppercase text-slate-500 mb-1">
                    {p.name}
                  </p>

                  <div className="flex justify-between items-end">
                    <p className="text-2xl font-bold text-white">
                      {p.value}
                    </p>
                    <span className="text-xs text-slate-500">{p.unit}</span>
                  </div>

                  <div className="w-full bg-white/5 h-1 rounded-full mt-2">
                    <div
                      className={`h-full ${
                        p.value > 100 ? "bg-orange-500" : "bg-neon-teal"
                      }`}
                      style={{ width: `${Math.min(100, (p.value / 250) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* FORECAST */}
            <div className="glass-panel p-6 rounded-2xl">
              <div className="flex justify-between items-center mb-3 border-b border-white/5 pb-2">
                <h3 className="text-sm font-bold text-white">
                  8-Hour Predictive Analytics
                </h3>
                <span className="text-[10px] text-slate-500">
                  Auto-Scaling Axis
                </span>
              </div>

              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  {/* chart unchanged */}
                </ResponsiveContainer>
              </div>
            </div>

          </section>

          {/* ================= RIGHT ================= */}
          <aside className="lg:col-span-3 space-y-6">

            {/* HEATMAP */}
            <div className="glass-panel p-2 rounded-2xl h-[360px] sticky top-24">
              <CityHeatmap
                lat={selectedLocation.lat}
                lon={selectedLocation.lon}
                aqi={data.current_aqi.value}
              />
            </div>

            {/* PERSONALIZED ADVICE */}
            <div className="glass-panel rounded-2xl p-0">
              <PersonalizedHealthAdvice />
            </div>

          </aside>

        </div>
      </main>

      {/* ================= FOOTER ================= */}
      <footer className="mt-16 border-t border-white/5 py-6 text-center text-xs text-slate-500">
        <p>© 2026 AeroGuard AI Systems</p>
        <p className="mt-1">Data indicative • Not for medical diagnosis</p>
      </footer>
    </div>
  );
}  