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
import LocationSearch from "../Components/LocationSelector";

/* -------------------- PERSONAS -------------------- */

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

/* =================================================== */

export default function Dashboard() {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [selectedPersona, setSelectedPersona] = useState("general");

  /* ✅ HOOK IS ALWAYS CALLED */
  const { data, loading, error } = useAQIData(
    selectedLocation?.name ?? null,
    selectedPersona
  );

  /* ---------------- LOADING ---------------- */

  if (loading) {
    return (
      <div className="min-h-screen bg-void flex items-center justify-center text-slate-400">
        <Activity className="w-10 h-10 animate-pulse text-neon-teal mb-3" />
        <p>Analyzing Atmospheric Conditions…</p>
      </div>
    );
  }

  /* ---------------- ERROR ---------------- */

  if (error) {
    return (
      <div className="min-h-screen bg-void flex items-center justify-center text-red-400">
        <AlertTriangle className="w-8 h-8 mr-2" />
        {error}
      </div>
    );
  }

  /* ---------------- LANDING STATE ---------------- */

  if (!selectedLocation) {
    return (
      <div className="min-h-screen bg-void flex items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(20,184,166,0.08),_transparent_60%)]" />

        <div className="relative z-10 text-center max-w-xl px-4">
          <p className="text-xs uppercase tracking-widest text-slate-500 mb-3">
            Air Quality Intelligence
          </p>

          <h1 className="text-5xl font-bold text-white mb-4">
            Explore Air Quality
          </h1>

          <p className="text-slate-400 mb-8">
            Search any city or area to view real-time AQI, pollution heatmaps,
            health risks, and forecasts.
          </p>

          <LocationSearch onSelect={setSelectedLocation} />

          <p className="mt-6 text-xs text-slate-500">
            Try <span className="text-slate-300">Mumbai</span>,{" "}
            <span className="text-slate-300">Delhi</span>,{" "}
            <span className="text-slate-300">Bangalore</span>
          </p>
        </div>
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

  /* ---------------- POLLUTANTS ---------------- */

  const pollutants = Object.entries(data.pollutants).map(([key, val]) => ({
    id: key,
    name: POLLUTANT_CONFIG[key]?.name || key,
    value: val.value,
    unit: POLLUTANT_CONFIG[key]?.unit || "",
  }));

  /* ================= DASHBOARD ================= */

  return (
    <div className="min-h-screen bg-void text-slate-300 pb-10">
      <main className="container mx-auto px-4 pt-6 grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* LEFT */}
        <div className="lg:col-span-3 space-y-6">

          {/* SEARCH – ALWAYS VISIBLE */}
          <LocationSearch
            onSelect={(loc) => {
              setSelectedLocation(loc);
            }}
          />

          {/* SELECTED LOCATION */}
          <div className="glass-panel p-5 rounded-2xl">
            <p className="text-xs uppercase text-slate-500 mb-2">
              Selected Location
            </p>
            <div className="flex items-center gap-2 text-white font-semibold">
              <MapPin size={16} />
              {selectedLocation.name}
            </div>
          </div>

          {/* PERSONA */}
          <div className="glass-panel p-5 rounded-2xl">
            <label className="text-xs uppercase text-slate-500 mb-3 block">
              Health Profile
            </label>
            {PERSONAS.map((p) => (
              <button
                key={p.id}
                onClick={() => setSelectedPersona(p.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 ${
                  selectedPersona === p.id
                    ? "bg-indigo-500/20 text-white"
                    : "hover:bg-white/5 text-slate-400"
                }`}
              >
                <p.icon size={18} />
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* CENTER */}
        <div className="lg:col-span-6 space-y-6">

          {/* AQI */}
          <div className="glass-panel p-8 rounded-3xl">
            <p className={`text-sm font-bold ${theme.color}`}>
              AQI {data.current_aqi.value}
            </p>
            <h2 className="text-8xl font-bold text-white">
              {data.current_aqi.value}
            </h2>
            <p className="text-xs text-slate-500 mt-2">
              Updated{" "}
              {new Date(data.current_aqi.updated_at).toLocaleTimeString()}
            </p>
          </div>

          {/* POLLUTANTS */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {pollutants.map((p) => (
              <div key={p.id} className="glass-panel p-4 rounded-xl">
                <p className="text-xs text-slate-400">{p.name}</p>
                <p className="text-2xl font-bold text-white">
                  {p.value} <span className="text-xs">{p.unit}</span>
                </p>
              </div>
            ))}
          </div>

          {/* FORECAST */}
          <div className="glass-panel p-6 rounded-2xl h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.forecast_6h}>
                <defs>
                  <linearGradient id="aqiGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={theme.stroke} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={theme.stroke} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" fontSize={10} />
                <YAxis fontSize={10} />
                <Tooltip />
                <Area
                  dataKey="aqi"
                  stroke={theme.stroke}
                  fill="url(#aqiGrad)"
                  strokeWidth={3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* RIGHT */}
        <div className="lg:col-span-3 space-y-6">
          <div className="glass-panel p-1 rounded-2xl h-64">
            <CityHeatmap
              lat={data.location.lat}
              lon={data.location.lon}
              aqi={data.current_aqi.value}
            />
          </div>

          <div className="glass-panel p-6 rounded-2xl border-l-4 border-indigo-500">
            <h4 className="text-sm font-bold text-white mb-2">
              AI Analysis
            </h4>
            <p className="text-xs text-slate-400">
              {data.risk_assessment.ai_explanation}
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
