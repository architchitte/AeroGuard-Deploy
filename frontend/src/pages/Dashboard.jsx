import { useState, useEffect } from "react";
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
  TrendingUp,
  Wind,
  Droplets,
  CloudRain,
} from "lucide-react";

import { useAQIData } from "../hooks/useAQIData";
// CityHeatmap removed in favor of PollutionHeatmap
import LocationSearch from "../Components/LocationSelector";
import AeroIntelligenceBriefing from "../Components/AeroIntelligenceBriefing";
import PersonalizedHealthAdvice from "../Components/PersonalizedHealthAdvice";
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
  pm25: { name: "PM2.5", unit: "µg/m³", icon: Droplets },
  pm10: { name: "PM10", unit: "µg/m³", icon: Wind },
  no2: { name: "NO₂", unit: "ppb", icon: CloudRain },
  o3: { name: "O₃", unit: "ppb", icon: Wind },
  so2: { name: "SO₂", unit: "ppb", icon: Droplets },
  co: { name: "CO", unit: "ppm", icon: CloudRain },
};

import { useLocation } from "react-router-dom";

export default function Dashboard() {
  const locationState = useLocation();
  const [selectedLocation, setSelectedLocation] = useState(locationState.state?.selectedLocation || null);
  const [selectedPersona, setSelectedPersona] = useState("general");

  // Sync state if navigation occurs with new state
  useEffect(() => {
    if (locationState.state?.selectedLocation) {
      setSelectedLocation(locationState.state.selectedLocation);
    }
  }, [locationState.state?.selectedLocation]);

  // ✅ Hooks ALWAYS called unconditionally
  const { data, loading, error } = useAQIData(
    selectedLocation?.name ?? null,
    selectedPersona,
    selectedLocation?.lat ?? null,
    selectedLocation?.lon ?? null
  );

  const { forecast6h, summary, loading: forecastLoading } = useForecast6h(selectedLocation);

  useEffect(() => {
    // Forecast data updated
  }, [forecast6h]);

  /* ============================
     1️⃣ SEARCH SCREEN (NO LOCATION SELECTED)
     ============================ */
  if (!selectedLocation) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center px-4 relative overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(16,185,129,0.15),_transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom,_rgba(34,211,238,0.12),_transparent_50%)]" />

        {/* Floating Particles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(15)].map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-cyan-400/30 rounded-full animate-float"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${10 + Math.random() * 10}s`,
              }}
            />
          ))}
        </div>

        <div className="max-w-2xl text-center relative z-10 space-y-8">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 border border-emerald-500/20 backdrop-blur-sm animate-fade-in">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-semibold text-emerald-300 tracking-wide">AI-Powered Air Quality Intelligence</span>
          </div>

          {/* Headline */}
          <div className="space-y-4 animate-slide-up">
            <h1 className="text-6xl md:text-7xl font-black text-white leading-tight">
              Breathe
              <span className="block bg-gradient-to-r from-cyan-400 via-emerald-400 to-cyan-500 bg-clip-text text-transparent animate-gradient-x">
                with Confidence
              </span>
            </h1>
            <p className="text-lg md:text-xl text-slate-400 leading-relaxed max-w-lg mx-auto">
              Real-time air quality monitoring powered by next-generation predictive AI.
              Know what you breathe, wherever you are.
            </p>
          </div>

          {/* Search */}
          <div className="animate-fade-in-delayed">
            <LocationSearch onSelect={setSelectedLocation} />
          </div>
        </div>

        <style>{`
          @keyframes float {
            0%, 100% { transform: translateY(0px) translateX(0px); opacity: 0.3; }
            50% { transform: translateY(-20px) translateX(10px); opacity: 0.6; }
          }
          @keyframes gradient-x {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
          }
          @keyframes fade-in {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
          }
          @keyframes slide-up {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
          }
          .animate-float { animation: float linear infinite; }
          .animate-gradient-x { 
            background-size: 200% 200%;
            animation: gradient-x 3s ease infinite;
          }
          .animate-fade-in { animation: fade-in 0.8s ease-out; }
          .animate-fade-in-delayed { animation: fade-in 0.8s ease-out 0.3s backwards; }
          .animate-slide-up { animation: slide-up 0.8s ease-out 0.1s backwards; }
        `}</style>
      </div>
    );
  }

  /* ============================
     2️⃣ LOADING STATE (OLD SIMPLE VERSION)
     ============================ */
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex flex-col items-center justify-center text-slate-400">
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
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center px-4">
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
    if (aqi <= 50) return {
      color: "text-emerald-400",
      stroke: "#10b981",
      glow: "bg-emerald-500",
      border: "border-emerald-500/30",
      gradient: "from-emerald-500/20 to-cyan-500/20"
    };
    if (aqi <= 100) return {
      color: "text-yellow-400",
      stroke: "#facc15",
      glow: "bg-yellow-500",
      border: "border-yellow-500/30",
      gradient: "from-yellow-500/20 to-orange-500/20"
    };
    if (aqi <= 200) return {
      color: "text-orange-500",
      stroke: "#f97316",
      glow: "bg-orange-500",
      border: "border-orange-500/30",
      gradient: "from-orange-500/20 to-red-500/20"
    };
    return {
      color: "text-red-500",
      stroke: "#ef4444",
      glow: "bg-red-500",
      border: "border-red-500/30",
      gradient: "from-red-500/20 to-pink-500/20"
    };
  };

  const theme = getTheme(data.current_aqi.value);

  /* ---------------- POLLUTANTS PROCESSING ---------------- */
  const pollutants = data?.pollutants
    ? Object.entries(data.pollutants).map(([key, val]) => ({
      id: key,
      name: POLLUTANT_CONFIG[key]?.name || key.toUpperCase(),
      value: typeof val === "object" ? val.value : val,
      unit: POLLUTANT_CONFIG[key]?.unit || "",
      icon: POLLUTANT_CONFIG[key]?.icon || Wind,
    }))
    : [];

  /* ============================
     5️⃣ MAIN DASHBOARD
     ============================ */
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-300 flex flex-col relative overflow-hidden">
      {/* Ambient Background */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,_rgba(16,185,129,0.08),_transparent_50%)] pointer-events-none" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,_rgba(34,211,238,0.08),_transparent_50%)] pointer-events-none" />

      {/* ================= MAIN CONTENT ================= */}
      <main className="flex-1 container mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-12 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 lg:gap-6">

          {/* ================= LEFT SIDEBAR ================= */}
          <aside className="lg:col-span-3 space-y-5">
            {/* LOCATION SEARCH */}
            <div className="glass-panel p-5 rounded-xl border border-white/10 hover:border-white/20 transition-all duration-300">
              <LocationSearch onSelect={setSelectedLocation} />
            </div>

            {/* SELECTED LOCATION */}
            <div className="glass-panel p-5 rounded-xl border border-white/10 group hover:border-emerald-500/30 hover:shadow-lg hover:shadow-emerald-500/5 transition-all duration-300">
              <p className="text-[10px] uppercase text-slate-500 mb-3 tracking-widest font-bold">
                Current Location
              </p>
              <div className="flex items-center gap-2.5 text-white font-bold text-sm">
                <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 border border-emerald-500/30">
                  <MapPin size={14} className="text-emerald-400" />
                </div>
                <span className="group-hover:text-emerald-400 transition-colors">{selectedLocation.name}</span>
              </div>
            </div>
          </aside>

          {/* ================= CENTER COLUMN ================= */}
          <section className="lg:col-span-6 space-y-5">
            {/* AQI HERO CARD */}
            <div className="relative glass-panel p-8 lg:p-10 rounded-3xl border border-white/10 overflow-hidden group hover:border-white/20 transition-all duration-500 hover:shadow-2xl hover:shadow-emerald-500/10">
              {/* Animated Glow */}
              <div className={`absolute -top-24 -right-24 w-72 h-72 ${theme.glow} blur-[140px] opacity-20 group-hover:opacity-30 transition-opacity duration-700`} />

              {/* Gradient Overlay */}
              <div className={`absolute inset-0 bg-gradient-to-br ${theme.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

              <div className="relative flex justify-between items-start">
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${theme.glow} animate-pulse`} />
                    <p className={`text-xs font-black uppercase tracking-widest ${theme.color}`}>
                      Real-Time AQI
                    </p>
                  </div>
                  <h2 className="text-8xl font-black text-white leading-none tracking-tight group-hover:scale-105 transition-transform duration-300">
                    {data.current_aqi.value}
                  </h2>
                  <div className="flex items-center gap-2">
                    <TrendingUp size={14} className={theme.color} />
                    <span className={`text-xs font-semibold ${theme.color}`}>Live Monitor</span>
                  </div>
                </div>

                <div className={`px-5 py-3 rounded-2xl border ${theme.border} bg-gradient-to-br from-white/5 to-white/0 backdrop-blur-xl shadow-lg`}>
                  <p className={`text-base font-black ${theme.color} tracking-wide`}>
                    {data.current_aqi.category}
                  </p>
                </div>
              </div>

              <div className="relative flex items-center gap-2 mt-6 pt-4 border-t border-white/10">
                <Activity size={12} className="text-emerald-400 animate-pulse" />
                <p className="text-xs text-slate-400 font-medium">
                  Last updated {new Date(data.current_aqi.updated_at).toLocaleTimeString()}
                </p>
              </div>
            </div>

            {/* AI BRIEFING */}
            <div className="glass-panel p-6 lg:p-7 rounded-2xl border border-white/10 hover:border-cyan-500/30 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/5">
              <AeroIntelligenceBriefing
                city={selectedLocation.name}
              />
            </div>

            {/* FORECAST CHART - MOVED UP */}
            <div className="glass-panel p-6 lg:p-7 rounded-2xl border border-white/10 hover:border-emerald-500/30 transition-all duration-300">
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mb-5 pb-4 border-b border-white/10">
                <h3 className="text-base font-black text-white flex items-center gap-2.5">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 border border-emerald-500/30">
                    <Activity size={16} className="text-emerald-400" />
                  </div>
                  <span>6-Hour AQI Forecast</span>
                </h3>
                <div className="flex items-center gap-2">
                  {forecast6h.length > 0 && !forecastLoading && (
                    <div className={`px-2 py-1 rounded text-[10px] font-bold uppercase ${forecast6h[forecast6h.length - 1].aqi > forecast6h[0].aqi ? 'text-red-400 bg-red-400/10' : 'text-emerald-400 bg-emerald-400/10'
                      }`}>
                      {forecast6h[forecast6h.length - 1].aqi > forecast6h[0].aqi ? 'Rising' : 'Improving'}
                    </div>
                  )}
                  <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold px-3 py-1.5 rounded-full bg-white/5 border border-white/10">
                    Predictive Hybrid AI
                  </span>
                </div>
              </div>

              <div className="h-72">
                {forecastLoading ? (
                  <div className="flex flex-col items-center justify-center h-full gap-3">
                    <Activity className="w-8 h-8 text-emerald-400 animate-spin" />
                    <p className="text-sm text-slate-400 font-medium">Generating predictive models…</p>
                  </div>
                ) : forecast6h.length > 0 ? (
                  <>
                    <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
                      <AreaChart
                        data={forecast6h.map(item => ({
                          time: item.hour,
                          aqi: item.aqi
                        }))}
                      >
                        <defs>
                          <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={theme.stroke} stopOpacity={0.4} />
                            <stop offset="95%" stopColor={theme.stroke} stopOpacity={0} />
                          </linearGradient>
                        </defs>

                        <XAxis
                          dataKey="time"
                          tick={{ fill: "#94a3b8", fontSize: 11, fontWeight: 600 }}
                          stroke="#334155"
                          strokeWidth={1}
                        />
                        <YAxis
                          tick={{ fill: "#94a3b8", fontSize: 11, fontWeight: 600 }}
                          stroke="#334155"
                          strokeWidth={1}
                          domain={[0, 'auto']}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: 'rgba(15, 23, 42, 0.95)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '12px',
                            padding: '12px',
                            boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
                          }}
                          labelStyle={{ color: '#fff', fontWeight: 'bold', fontSize: '12px' }}
                          itemStyle={{ color: theme.stroke, fontWeight: 'bold' }}
                        />

                        <Area
                          type="monotone"
                          dataKey="aqi"
                          stroke={theme.stroke}
                          strokeWidth={3}
                          fill="url(#forecastGradient)"
                          animationDuration={1000}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                    {summary?.explanation && (
                      <div className="mt-4 p-3 rounded-lg bg-white/5 border border-white/10">
                        <p className="text-xs text-slate-400 leading-relaxed">
                          <span className="text-emerald-400 font-bold mr-2">AI Analysis:</span>
                          {summary.explanation}
                        </p>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-sm text-slate-400">Atmospheric forecast unavailable</p>
                  </div>
                )}
              </div>
            </div>

            {/* POLLUTANTS GRID */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {pollutants.map((p, index) => {
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
                    ? "bg-gradient-to-r from-red-500 to-pink-500"
                    : percent > 50
                      ? "bg-gradient-to-r from-orange-500 to-yellow-500"
                      : "bg-gradient-to-r from-emerald-500 to-cyan-500";

                const IconComponent = p.icon;

                return (
                  <div
                    key={p.id}
                    className="glass-panel p-5 rounded-xl space-y-3 border border-white/10 hover:border-white/20 hover:-translate-y-1 transition-all duration-300 hover:shadow-xl group"
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <div className="flex items-center justify-between">
                      <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">
                        {p.name}
                      </p>
                      <div className="p-1.5 rounded-lg bg-white/5 group-hover:bg-white/10 transition-colors">
                        <IconComponent size={12} className="text-slate-400 group-hover:text-emerald-400 transition-colors" />
                      </div>
                    </div>

                    <div className="flex justify-between items-end">
                      <p className="text-3xl font-black text-white leading-none group-hover:text-emerald-400 transition-colors">
                        {p.value}
                      </p>
                      <span className="text-xs text-slate-500 pb-0.5 font-medium">{p.unit}</span>
                    </div>

                    <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all duration-700 ${barColor} shadow-lg`}
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>

            {/* ADVANCED ANALYTICS */}
            <AdvancedAnalytics
              location={selectedLocation}
              persona={selectedPersona}
            />
          </section>

          {/* ================= RIGHT SIDEBAR ================= */}
          <aside className="lg:col-span-3 space-y-6">
            {/* PERSONALIZED HEALTH ADVICE */}
            <div className="glass-panel rounded-2xl overflow-hidden border border-white/10 hover:border-emerald-500/30 transition-all duration-300">
              <PersonalizedHealthAdvice
                aqi={data?.current_aqi?.value || 100}
                location={selectedLocation?.name || 'Your Area'}
              />
            </div>

            {/* POLLUTANT DETAILS - Moved from sidebar if exists */}
            <PollutantDetails pollutants={pollutants} />
          </aside>
        </div>

      </main>

      {/* ================= FOOTER ================= */}
      <footer className="mt-auto border-t border-white/10 py-8 text-center text-xs text-slate-500 relative z-10 backdrop-blur-sm">
        <div className="flex flex-col items-center gap-2">
          <p className="font-semibold">© 2026 AeroGuard AI Systems</p>
          <p className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Data indicative • Not for medical diagnosis
          </p>
        </div>
      </footer>
    </div>
  );
}