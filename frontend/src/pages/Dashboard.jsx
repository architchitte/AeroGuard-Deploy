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
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 ${selectedPersona === p.id
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
            <div className="relative overflow-hidden glass-panel p-8 rounded-3xl border border-white/10">
              {/* Background Glow */}
              <div className={`absolute -top-24 -right-24 w-64 h-64 blur-[120px] rounded-full opacity-20 ${theme.color.includes('teal') ? 'bg-teal-500' :
                theme.color.includes('yellow') ? 'bg-yellow-500' :
                  theme.color.includes('orange') ? 'bg-orange-500' : 'bg-red-500'
                }`}></div>

              <div className="flex justify-between items-start">
                <div>
                  <p className={`text-xs font-bold uppercase tracking-widest mb-1 ${theme.color}`}>
                    Real-Time Air Quality
                  </p>
                  <h2 className="text-8xl font-display font-black text-white leading-tight">
                    {data.current_aqi.value}
                  </h2>
                </div>
                <div className={`px-4 py-2 rounded-2xl border ${theme.color.replace('text', 'border')}/30 bg-white/5`}>
                  <p className={`text-sm font-bold ${theme.color}`}>{data.current_aqi.category}</p>
                </div>
              </div>
              <p className="text-xs text-slate-500 mt-4 flex items-center gap-1.5">
                <Activity size={12} className="text-neon-teal" />
                Updated: {new Date(data.current_aqi.updated_at).toLocaleTimeString()}
              </p>
            </div>

            <AeroIntelligenceBriefing
              city={selectedLocation.name}
              persona={selectedPersona}
            />

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {pollutants.map((p) => (
                <div key={p.id} className="group glass-panel p-5 rounded-2xl border border-white/5 hover:border-white/20 transition-all duration-300">
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">{p.name}</p>
                  <div className="flex items-end justify-between">
                    <p className="text-3xl font-display font-bold text-white leading-none">
                      {p.value}
                    </p>
                    <span className="text-[10px] text-slate-500 mb-1">{p.unit}</span>
                  </div>
                  <div className="w-full bg-white/5 h-1 rounded-full mt-3 overflow-hidden">
                    <div
                      className={`h-full transition-all duration-1000 ${p.value > 100 ? 'bg-orange-500' : 'bg-neon-teal'
                        }`}
                      style={{ width: `${Math.min(100, (p.value / 250) * 100)}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>

            <div className="glass-panel p-6 rounded-3xl border border-white/10">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Activity className="text-neon-teal" size={16} /> 8-Hour Predictive Analytics
                </h3>
                <span className="text-[10px] text-slate-500 font-medium px-2 py-0.5 rounded-full border border-white/5">Auto-Scaling Axis</span>
              </div>
              <div className="h-64 min-h-[256px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data.forecast_8h}>
                    <defs>
                      <linearGradient id="colorAqi" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={theme.stroke} stopOpacity={0.3} />
                        <stop offset="95%" stopColor={theme.stroke} stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis
                      dataKey="time"
                      fontSize={10}
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: '#64748b' }}
                      dy={10}
                    />
                    <YAxis
                      fontSize={10}
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: '#64748b' }}
                      dx={-10}
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#020617', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', fontSize: '12px' }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Area
                      type="monotone"
                      dataKey="aqi"
                      stroke={theme.stroke}
                      fillOpacity={1}
                      fill="url(#colorAqi)"
                      strokeWidth={3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
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
