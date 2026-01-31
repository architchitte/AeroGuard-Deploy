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
    <div className="min-h-screen bg-void text-slate-300 pb-10">
      <main className="container mx-auto px-4 pt-6 grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* LEFT */}
        {hasLocation && (
          <div className="lg:col-span-3 space-y-6">

            {/* SEARCH ALWAYS VISIBLE */}
            <LocationSearch onSelect={setSelectedLocation} />

            <div className="glass-panel p-5 rounded-2xl">
              <p className="text-xs uppercase text-slate-500 mb-2">
                Selected Location
              </p>
              <div className="flex items-center gap-2 text-white font-semibold">
                <MapPin size={16} />
                {selectedLocation.name}
              </div>
            </div>

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
        )}
        

        {/* CENTER */}
        {hasLocation && (
          <div className="lg:col-span-6 space-y-6">
            <div className="glass-panel p-8 rounded-3xl">
              <p className={`text-sm font-bold ${theme.color}`}>
                AQI {data.current_aqi.value}
              </p>
              <h2 className="text-8xl font-bold text-white">
                {data.current_aqi.value}
              </h2>
            </div>

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

            <div className="glass-panel p-6 rounded-2xl h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.forecast_6h}>
                  <XAxis dataKey="time" fontSize={10} />
                  <YAxis fontSize={10} />
                  <Tooltip />
                  <Area
                    dataKey="aqi"
                    stroke={theme.stroke}
                    fill={theme.stroke}
                    strokeWidth={3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
        

        {/* RIGHT */}
        {hasLocation && (
                <div className="lg:col-span-3 space-y-6">
                <div className="glass-panel p-1 rounded-2xl h-64">
                  <CityHeatmap
                    lat={selectedLocation.lat}
                    lon={selectedLocation.lon}
                    aqi={data.current_aqi.value}
                  />
                </div>
          </div>)}
      </main>
    </div>
  );
}
