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
import AdvancedAnalytics from "../Components/AdvancedAnalytics";
import PollutantDetails from "../Components/PollutantDetails";
import { useForecast6h } from "../hooks/forcast6h.js";

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

  // ✅ Hooks ALWAYS called unconditionally
  const { data, loading, error } = useAQIData(
    selectedLocation?.name ?? null,
    selectedPersona
  );

  const { forecast6h, loading: forecastLoading } = useForecast6h(selectedLocation);

  /* ============================
     1️⃣ SEARCH SCREEN (NO LOCATION SELECTED)
     ============================ */
  if (!selectedLocation) {
    return (
      <div className="min-h-screen bg-void flex items-center justify-center px-4">
        <div className="max-w-xl text-center">
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
     2️⃣ LOADING STATE
     ============================ */
  if (loading) {
    return (
      <div className="min-h-screen bg-void flex flex-col items-center justify-center text-slate-400">
        <Activity className="w-10 h-10 animate-pulse text-neon-teal mb-3" />
        <p>Analyzing Atmospheric Conditions…</p>
      </div>
    );
  }

  /* ============================
     3️⃣ ERROR STATE
     ============================ */
  if (error) {
    return (
      <div className="min-h-screen bg-void flex items-center justify-center">
        <div className="flex items-center gap-2 text-red-400">
          <AlertTriangle className="w-8 h-8" />
          <p>{error}</p>
        </div>
      </div>
    );
  }

  /* ============================
     4️⃣ NO DATA
     ============================ */
  if (!data) return null;

  /* ---------------- THEME BASED ON AQI ---------------- */
  const getTheme = (aqi) => {
    if (aqi <= 50) return { color: "text-neon-teal", stroke: "#14b8a6" };
    if (aqi <= 100) return { color: "text-yellow-400", stroke: "#facc15" };
    if (aqi <= 200) return { color: "text-orange-500", stroke: "#f97316" };
    return { color: "text-red-500", stroke: "#ef4444" };
  };

  const theme = getTheme(data.current_aqi.value);

  /* ---------------- POLLUTANTS PROCESSING ---------------- */
  const pollutants = data?.pollutants
    ? Object.entries(data.pollutants).map(([key, val]) => ({
        id: key,
        name: POLLUTANT_CONFIG[key]?.name || key.toUpperCase(),
        value: typeof val === "object" ? val.value : val,
        unit: POLLUTANT_CONFIG[key]?.unit || "",
      }))
    : [];

  /* ============================
     5️⃣ MAIN DASHBOARD
     ============================ */
  return (
    <div className="min-h-screen bg-void text-slate-300 flex flex-col">
      {/* ================= MAIN CONTENT ================= */}
      <main className="flex-1 container mx-auto px-4 sm:px-6 pt-10 pb-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 lg:gap-6">
          
          {/* ================= LEFT SIDEBAR ================= */}
          <aside className="lg:col-span-3 space-y-5">
            {/* LOCATION SEARCH */}
            <div className="glass-panel p-5 rounded-xl">
              <LocationSearch onSelect={setSelectedLocation} />
            </div>

            {/* SELECTED LOCATION */}
            <div className="glass-panel p-5 rounded-xl">
              <p className="text-xs uppercase text-slate-500 mb-2 tracking-wider font-medium">
                Selected Location
              </p>
              <div className="flex items-center gap-2 text-white font-semibold text-sm">
                <MapPin size={16} className="text-neon-teal" />
                <span>{selectedLocation.name}</span>
              </div>
            </div>

            {/* HEALTH PROFILE (COMMENTED OUT) */}
            {/* <div className="glass-panel p-5 rounded-xl">
              <p className="text-xs uppercase text-slate-500 mb-3 tracking-wider font-medium">
                Health Profile
              </p>
              <div className="space-y-1.5">
                {PERSONAS.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => setSelectedPersona(p.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 ${
                      selectedPersona === p.id
                        ? "bg-indigo-500/20 text-white shadow-lg shadow-indigo-500/10 border border-indigo-500/30"
                        : "hover:bg-white/5 text-slate-400 hover:text-slate-300 border border-transparent"
                    }`}
                  >
                    <p.icon size={18} />
                    <span className="text-sm font-medium">{p.label}</span>
                  </button>
                ))}
              </div>
            </div> */}
          </aside>

          {/* ================= CENTER COLUMN ================= */}
          <section className="lg:col-span-6 space-y-5">
            {/* AQI HERO CARD */}
            <div className="relative glass-panel p-8 rounded-2xl border border-white/10 overflow-hidden">
              {/* Glow Effect */}
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

              <div className="relative flex justify-between items-start">
                <div className="space-y-2">
                  <p className={`text-xs font-bold uppercase tracking-widest ${theme.color}`}>
                    Real-Time AQI
                  </p>
                  <h2 className="text-7xl font-black text-white leading-none">
                    {data.current_aqi.value}
                  </h2>
                </div>

                <div className={`px-4 py-2 rounded-xl border ${theme.color.replace("text", "border")}/30 bg-white/5 backdrop-blur-sm`}>
                  <p className={`text-sm font-bold ${theme.color}`}>
                    {data.current_aqi.category}
                  </p>
                </div>
              </div>

              <div className="relative flex items-center gap-2 mt-4 pt-3 border-t border-white/5">
                <Activity size={12} className="text-neon-teal" />
                <p className="text-xs text-slate-500">
                  Updated {new Date(data.current_aqi.updated_at).toLocaleTimeString()}
                </p>
              </div>
            </div>

            {/* AI BRIEFING */}
            <div className="glass-panel p-6 rounded-2xl border border-white/10">
              <AeroIntelligenceBriefing
                city={selectedLocation.name}
                // persona={selectedPersona}
              />
            </div>

            {/* POLLUTANTS GRID */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {pollutants.map((p) => {
                const SAFE_LIMITS = {
                  pm25: 60,
                  pm10: 100,
                  no2: 40,
                  o3: 70,
                  so2: 20,
                  co: 2,
                };

                const limit = SAFE_LIMITS[p.id] ?? 100;
                const percent = Math.min(100, (p.value / limit) * 100);

                const barColor =
                  percent > 75
                    ? "bg-red-500"
                    : percent > 50
                    ? "bg-orange-500"
                    : "bg-neon-teal";

                return (
                  <div key={p.id} className="glass-panel p-5 rounded-xl space-y-3">
                    <p className="text-[10px] uppercase tracking-widest text-slate-500 font-semibold">
                      {p.name}
                    </p>

                    <div className="flex justify-between items-end">
                      <p className="text-3xl font-bold text-white leading-none">
                        {p.value}
                      </p>
                      <span className="text-xs text-slate-500 pb-0.5">{p.unit}</span>
                    </div>

                    <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-500 ${barColor}`}
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* FORECAST CHART */}
            <div className="glass-panel p-6 rounded-2xl border border-white/10">
              <div className="flex justify-between items-center mb-4 pb-3 border-b border-white/5">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Activity size={16} className="text-neon-teal" />
                  <span>Next 6 Hours AQI Prediction</span>
                </h3>
                <span className="text-[10px] text-slate-500 uppercase tracking-wider">
                  Location-based forecast
                </span>
              </div>

              <div className="h-64">
                {forecastLoading ? (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-xs text-slate-500">Generating forecast…</p>
                  </div>
                ) : forecast6h.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                      data={forecast6h.map(item => ({
                        time: item.hour,   // 🔥 FIX
                        aqi: item.aqi
                      }))}
                    >
                      <defs>
                        <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor={theme.stroke} stopOpacity={0.35} />
                          <stop offset="95%" stopColor={theme.stroke} stopOpacity={0} />
                        </linearGradient>
                      </defs>

                      <XAxis
                        dataKey="time"
                        tick={{ fill: "#64748b", fontSize: 10 }}
                      />
                      <YAxis
                        tick={{ fill: "#64748b", fontSize: 10 }}
                      />
                      <Tooltip />

                      <Area
                        type="monotone"
                        dataKey="aqi"
                        stroke={theme.stroke}
                        strokeWidth={3}
                        fill="url(#forecastGradient)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-xs text-slate-500">Forecast data unavailable</p>
                  </div>
                )}
              </div>
            </div>  

            {/* ADVANCED ANALYTICS */}
            <AdvancedAnalytics
              location={selectedLocation}
              persona={selectedPersona}
            />
          </section>

          {/* ================= RIGHT SIDEBAR ================= */}
          <aside className="lg:col-span-3 space-y-5">
            {/* HEATMAP */}
            <div className="glass-panel p-3 rounded-2xl sticky top-24">
              <div className="h-[360px] w-full">
                <CityHeatmap
                  lat={selectedLocation.lat}
                  lon={selectedLocation.lon}
                  aqi={data.current_aqi.value}
                />
              </div>
            </div>

            {/* PERSONALIZED HEALTH ADVICE */}
            <div className="glass-panel rounded-2xl overflow-hidden">
              <PersonalizedHealthAdvice />
            </div>
          </aside>
        </div>
      </main>

      {/* ================= FOOTER ================= */}
      <footer className="mt-auto border-t border-white/5 py-6 text-center text-xs text-slate-500">
        <p>© 2026 AeroGuard AI Systems</p>
        <p className="mt-1">Data indicative • Not for medical diagnosis</p>
      </footer>
    </div>
  );
}