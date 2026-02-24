import { useState, useEffect } from "react";
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
} from "recharts";
import {
  Wind, Droplets, CloudRain,
  RefreshCw, ArrowRight, MapPin, Search, Home,
} from "lucide-react";

import { useAQIData } from "../hooks/useAQIData";
import LocationSearch from "../Components/LocationSelector";
import AeroIntelligenceBriefing from "../Components/AeroIntelligenceBriefing";
import PersonalizedHealthAdvice from "../Components/PersonalizedHealthAdvice";
import AdvancedAnalytics from "../Components/AdvancedAnalytics";
import { useForecast6h } from "../hooks/forcast6h.js";
import { useLocation, useNavigate } from "react-router-dom";

/* ——— Pollutant Config ——— */
const POLLUTANT_CONFIG = {
  pm25: { name: "PM2.5", unit: "µg/m³", icon: Droplets, emoji: "💨" },
  pm10: { name: "PM10", unit: "µg/m³", icon: Wind, emoji: "🌫️" },
  no2: { name: "NO₂", unit: "ppb", icon: CloudRain, emoji: "🟡" },
  o3: { name: "O₃", unit: "ppb", icon: Wind, emoji: "🌀" },
  so2: { name: "SO₂", unit: "ppb", icon: Droplets, emoji: "⚗️" },
  co: { name: "CO", unit: "ppm", icon: CloudRain, emoji: "☁️" },
};

/* ——— AQI band helpers ——— */
const AQI_BANDS = [
  { max: 50, label: "Good", emoji: "🟢", color: "#B51A2B", glow: "rgba(181,26,43,0.35)", bg: "from-[#B51A2B]/20 to-transparent" },
  { max: 100, label: "Moderate", emoji: "🟡", color: "#f59e0b", glow: "rgba(245,158,11,0.35)", bg: "from-yellow-500/20 to-transparent" },
  { max: 200, label: "Unhealthy", emoji: "🟠", color: "#f97316", glow: "rgba(249,115,22,0.35)", bg: "from-orange-500/20 to-transparent" },
  { max: 300, label: "Very Unhealthy", emoji: "🔴", color: "#ef4444", glow: "rgba(239,68,68,0.35)", bg: "from-red-500/20 to-transparent" },
  { max: 9999, label: "Hazardous", emoji: "☠️", color: "#a855f7", glow: "rgba(168,85,247,0.35)", bg: "from-purple-500/20 to-transparent" },
];

const getAqiBand = (aqi) => AQI_BANDS.find(b => aqi <= b.max) || AQI_BANDS[0];

/* ——— Forecast custom tooltip ——— */
const ForecastTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  const val = payload[0].value;
  const band = getAqiBand(val);
  return (
    <div className="bg-[#101525] border border-[#384358]/40 rounded-xl px-3 py-2 shadow-2xl text-[10px] backdrop-blur-xl">
      <p className="text-[#FFA586] font-black uppercase mb-1">{label}</p>
      <div className="flex items-center gap-1.5">
        <span className="text-base">{band.emoji}</span>
        <span className="font-black text-sm" style={{ color: band.color }}>{val} AQI</span>
      </div>
      <p className="text-[#9BA3AF] mt-0.5">{band.label}</p>
    </div>
  );
};

export default function Dashboard() {
  const routerLocation = useLocation();
  const navigate = useNavigate();
  const [selectedLocation, setSelectedLocation] = useState(routerLocation.state?.selectedLocation || null);
  const selectedPersona = "general";
  const [profileOpen, setProfileOpen] = useState(false);
  const [spinning, setSpinning] = useState(false);

  useEffect(() => {
    if (routerLocation.state?.selectedLocation) setSelectedLocation(routerLocation.state.selectedLocation);
  }, [routerLocation.state?.selectedLocation]);

  const { data, loading, error } = useAQIData(
    selectedLocation?.name ?? null, selectedPersona,
    selectedLocation?.lat ?? null, selectedLocation?.lon ?? null
  );
  const { forecast6h } = useForecast6h(selectedLocation);

  /* ——— LANDING SCREEN (SEARCH) ——— */
  if (!selectedLocation) return (
    <div className="min-h-screen bg-[#101525] text-[#FFA586] overflow-x-hidden flex flex-col">
      <header className="fixed top-5 inset-x-0 z-50 px-4 sm:px-8 pointer-events-none">
        <div className="max-w-[1440px] mx-auto w-full h-16 bg-[#101525]/85 backdrop-blur-2xl border border-[#384358]/25 rounded-2xl flex items-center justify-between px-6 shadow-2xl pointer-events-auto transition-all">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#B51A2B] to-[#FFA586] flex items-center justify-center shadow-lg cursor-pointer" onClick={() => navigate("/")}>
              <span className="text-xs">🌍</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[7px] uppercase font-black tracking-[0.2em] text-[#D1A5A5]">📍 System Status</span>
              <span className="text-[11px] font-black text-[#FFA586] tracking-tight">Awaiting Node Selection...</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 p-1 rounded-xl bg-[#242F49]/40 border border-[#384358]/20 pr-2">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#101525]/50 border border-[#384358]/20">
                <div className="w-1 h-1 rounded-full bg-[#B51A2B] animate-pulse" />
                <span className="text-[9px] font-black uppercase tracking-wider text-[#B51A2B]">Live <span className="text-[#FFA586] cursive-accent normal-case tracking-normal">Monitoring</span></span>
              </div>
              <div className="h-4 w-[1px] bg-[#384358]/40 mx-0.5" />
              <button
                onClick={() => navigate("/")}
                className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-[#B51A2B]/20 transition-all text-[#FFA586]" title="Home">
                <Home size={12} />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 flex items-center justify-center px-4 relative overflow-hidden pt-20">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-[#B51A2B]/10 blur-[140px] rounded-full animate-pulse" />
        <div className="absolute bottom-[-15%] right-[-10%] w-[55%] h-[55%] bg-[#541A2B]/8 blur-[160px] rounded-full animate-pulse" style={{ animationDelay: "1.5s" }} />
        <div className="absolute inset-0 opacity-[0.035]"
          style={{ backgroundImage: "radial-gradient(circle,#FFA586 1px,transparent 1px)", backgroundSize: "32px 32px" }} />

        <div className="max-w-xl w-full text-center relative z-10 space-y-8">
          <div className="space-y-4">
            <div className="text-5xl animate-bounce">🌍</div>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#242F49] border border-[#384358]/40">
              <div className="w-1.5 h-1.5 rounded-full bg-[#B51A2B] shadow-[0_0_8px_#B51A2B] animate-pulse" />
              <span className="text-[10px] font-black uppercase tracking-[0.2em] text-[#B51A2B]">⚡ Atmospheric Intelligence Engine</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-black text-[#FFA586] leading-[0.95] tracking-tighter font-display text-glow">
              Know the Air&nbsp;<br />
              <span className="text-gradient py-1 italic">
                You Breathe. 💨
              </span>
            </h1>
          </div>

          <div className="glass-card p-2 rounded-2xl shadow-2xl border-[#384358]/30">
            <LocationSearch onSelect={setSelectedLocation} />
          </div>

          <div className="flex flex-wrap justify-center gap-2">
            {[
              { city: "Delhi", flag: "🏙️" },
              { city: "Mumbai", flag: "🌊" },
              { city: "Bangalore", flag: "🌿" },
              { city: "Hyderabad", flag: "💎" },
            ].map(({ city, flag }) => (
              <button key={city}
                onClick={() => setSelectedLocation({ name: city, lat: 28.61, lon: 77.20 })}
                className="px-3 py-1.5 rounded-full border border-[#384358]/30 hover:border-[#B51A2B]/60 hover:bg-[#242F49] transition-all text-xs font-bold text-[#FFA586] hover:text-[#B51A2B] flex items-center gap-1.5">
                <span>{flag}</span>{city}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  /* ——— LOADING ——— */
  if (loading) return (
    <div className="min-h-screen bg-[#101525] flex flex-col items-center justify-center gap-4">
      <div className="text-4xl animate-spin">🌀</div>
      <div className="w-48 h-1 bg-[#242F49] rounded-full overflow-hidden">
        <div className="h-full bg-gradient-to-r from-[#B51A2B] to-[#FFA586] rounded-full animate-pulse w-2/3" />
      </div>
      <span className="text-[#B51A2B] font-black tracking-widest text-[10px] uppercase">🛰️ Calibrating Sensors…</span>
    </div>
  );

  /* ——— ERROR ——— */
  if (error) return (
    <div className="min-h-screen bg-[#101525] flex flex-col items-center justify-center p-8 text-center gap-4">
      <div className="text-5xl">⚡</div>
      <h3 className="text-xl font-black text-[#FFA586]">📡 Sync Interrupted</h3>
      <p className="text-[#FFA586] max-w-md text-sm">{error}</p>
      <button onClick={() => window.location.reload()}
        className="px-5 py-2.5 glass-panel rounded-xl hover:border-[#B51A2B]/40 transition-all font-bold text-[#FFA586] text-sm flex items-center gap-2">
        <RefreshCw size={14} /> Retry Handshake
      </button>
    </div>
  );

  if (!data) return null;

  const band = getAqiBand(data.current_aqi.value);
  const aqi = data.current_aqi.value;
  const trend = (forecast6h.length > 1)
    ? (forecast6h[forecast6h.length - 1].aqi > forecast6h[0].aqi ? "📈 Rising" : "📉 Falling")
    : "📊 Stable";

  return (
    <div className="min-h-screen bg-[#101525] text-[#FFA586] overflow-x-hidden flex flex-col">

      {/* ══ AMBIENT BG ══ */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-1/4 w-[600px] h-[400px] opacity-25 blur-[120px] rounded-full transition-all duration-2000"
          style={{ background: `radial-gradient(ellipse, ${band.glow}, transparent)` }} />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[300px] opacity-15 blur-[100px] rounded-full"
          style={{ background: `radial-gradient(ellipse, ${band.glow}, transparent)` }} />
      </div>

      {/* ══ HEADER ══ */}
      <header className="fixed top-3 sm:top-5 inset-x-0 z-50 px-3 sm:px-8 pointer-events-none">
        <div className="max-w-[1440px] mx-auto w-full h-14 sm:h-16 bg-[#101525]/85 backdrop-blur-2xl border border-[#384358]/25 rounded-2xl flex items-center justify-between px-3 sm:px-6 shadow-2xl pointer-events-auto transition-all">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#B51A2B] to-[#FFA586] flex items-center justify-center shadow-lg cursor-pointer" onClick={() => navigate("/")}>
              <span className="text-xs">🌍</span>
            </div>
            <div className="flex flex-col">
              <span className="text-[7px] uppercase font-black tracking-[0.2em] text-[#D1A5A5] hidden sm:block">📍 Real-time Link</span>
              <span className="text-[10px] sm:text-[11px] font-black text-[#FFA586] truncate max-w-[80px] sm:max-w-[180px] tracking-tight">{selectedLocation.name}</span>
            </div>
            <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-full border border-[#B51A2B]/30 bg-[#B51A2B]/10 ml-2">
              <span className="text-xs">{band.emoji}</span>
              <span className="text-[8px] font-black uppercase tracking-widest" style={{ color: band.color }}>{band.label}</span>
            </div>
          </div>

          <div className="flex-1 max-w-[140px] sm:max-w-[200px] md:max-w-xs mx-2 sm:mx-4">
            <LocationSearch onSelect={setSelectedLocation} />
          </div>

          {/* ── Action Cluster ── */}
          <div className="flex items-center gap-1.5 sm:gap-2 p-1 rounded-xl bg-[#242F49]/40 border border-[#384358]/20">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#101525]/50 border border-[#384358]/20">
              <div className="w-1 h-1 rounded-full bg-[#B51A2B] animate-pulse" />
              <span className="text-[9px] font-black uppercase tracking-wider text-[#B51A2B]">Live <span className="text-[#FFA586] cursive-accent normal-case tracking-normal">Monitoring</span></span>
            </div>

            <div className="h-4 w-[1px] bg-[#384358]/40 mx-0.5 hidden sm:block" />

            <button
              title="Force Resync"
              onClick={() => { setSpinning(true); setTimeout(() => window.location.reload(), 350); }}
              className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg flex items-center justify-center hover:bg-[#B51A2B]/20 transition-all text-[#FFA586]">
              <RefreshCw size={11} className={spinning ? "animate-spin" : ""} />
            </button>

            <div className="h-4 w-[1px] bg-[#384358]/40 mx-0.5" />

            <div className="relative">
              <button
                onClick={() => setProfileOpen(o => !o)}
                className={`w-7 h-7 sm:w-8 sm:h-8 rounded-lg flex items-center justify-center transition-all ${profileOpen ? 'bg-[#B51A2B] text-white' : 'hover:bg-[#B51A2B]/20 text-[#9BA3AF]'}`}>
                <span className="text-xs italic font-black">{selectedLocation.name[0]}</span>
              </button>

              {profileOpen && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setProfileOpen(false)} />
                  <div className="absolute right-0 top-11 z-50 w-52 glass-card border border-[#384358]/35 rounded-2xl py-3 shadow-[0_10px_40px_rgba(0,0,0,0.6)] backdrop-blur-3xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                    <div className="px-5 mb-3">
                      <p className="text-[8px] font-black text-[#B51A2B] uppercase tracking-[0.2em]">Atmospheric Node</p>
                      <p className="text-sm font-black text-[#FFA586] truncate">{selectedLocation.name}</p>
                    </div>

                    <div className="h-[1px] bg-[#384358]/20 mb-2" />

                    <button onClick={() => { setProfileOpen(false); setSelectedLocation(null); }}
                      className="w-full flex items-center gap-3 px-5 py-2.5 hover:bg-[#B51A2B]/10 transition-all text-left">
                      <Search size={12} className="text-[#B51A2B]" />
                      <span className="text-[10px] font-black uppercase tracking-widest text-[#FFA586]">Switch Node</span>
                    </button>

                    <button onClick={() => { setProfileOpen(false); navigate("/"); }}
                      className="w-full flex items-center gap-3 px-5 py-2.5 hover:bg-[#B51A2B]/10 transition-all text-left">
                      <Home size={12} className="text-[#FFA586]" />
                      <span className="text-[10px] font-black uppercase tracking-widest text-[#FFA586]">Return Base</span>
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* ══ MAIN GRID ══ */}
      <main className="pt-20 pb-10 px-3 sm:px-4 md:px-8 max-w-[1440px] mx-auto relative z-10 w-full flex-1">

        {/* ── ROW 1: AQI HERO + FORECAST (hero features side by side) ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 mb-4">

          {/* ▶ AQI HERO — 4 cols */}
          <div className="lg:col-span-4 glass-card rounded-3xl p-5 sm:p-7 relative overflow-hidden group"
            style={{ background: `linear-gradient(135deg, ${band.color}12 0%, rgba(36,47,73,0.8) 60%)` }}>
            <div className="absolute -top-20 -right-20 w-56 h-56 blur-[90px] rounded-full opacity-20 group-hover:opacity-40 transition-all duration-700"
              style={{ background: band.color }} />
            <div className="relative z-10">
              <div className="flex items-center gap-2 mb-4">
                <span className="text-xl">{band.emoji}</span>
                <div className="px-2.5 py-1 rounded-full border text-[9px] font-black uppercase tracking-wider"
                  style={{ borderColor: band.color + "50", color: band.color, background: band.color + "15" }}>
                  Live AQI
                </div>
              </div>
              <div className="flex items-end gap-2 mb-3">
                <h2 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black leading-none tracking-tighter text-[#FFA586] font-display text-glow"
                  style={{ textShadow: `0 0 40px ${band.color}60` }}>
                  {aqi}
                </h2>
                <div className="mb-2 flex flex-col gap-1">
                  <span className="text-[10px] font-black uppercase text-[#D1A5A5]">US-EPA</span>
                  <span className="text-xl">{trend.split(" ")[0]}</span>
                </div>
              </div>
              <div className="px-3 py-1.5 rounded-xl inline-flex items-center gap-2"
                style={{ background: band.color + "20", border: `1px solid ${band.color}30` }}>
                <span className="font-black text-xs" style={{ color: band.color }}>{band.label}</span>
              </div>

              {/* AQI Bar */}
              <div className="mt-5 space-y-1.5">
                <div className="flex justify-between text-[9px] font-black uppercase text-[#FFA586]">
                  <span>0</span><span>100</span><span>200</span><span>300+</span>
                </div>
                <div className="h-2 w-full bg-[#101525]/60 rounded-full border border-[#384358]/20 overflow-hidden">
                  <div className="h-full rounded-full transition-all duration-1000"
                    style={{
                      width: `${Math.min((aqi / 400) * 100, 100)}%`,
                      background: `linear-gradient(to right, #B51A2B, ${band.color})`
                    }} />
                </div>
              </div>

              <div className="mt-5 flex justify-between items-center pt-3 border-t border-[#384358]/15 text-[9px] font-bold text-[#9BA3AF] uppercase">
                <span>🏙️ {data.location?.city || selectedLocation.name}</span>
                <span className="text-[#B51A2B]">✅ Verified</span>
              </div>
            </div>
          </div>

          {/* ▶ 6H FORECAST HERO — 8 cols */}
          <div className="lg:col-span-8 glass-card rounded-3xl p-7 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-48 h-48 blur-[100px] opacity-10 rounded-full bg-[#B51A2B]" />
            <div className="relative z-10 h-full flex flex-col">
              <div className="flex justify-between items-start mb-5">
                <div className="space-y-1">
                  <div className="flex items-center gap-2.5">
                    <span className="text-xl">⏱️</span>
                    <h3 className="card-title text-base uppercase tracking-wide">6-Hour AQI Forecast</h3>
                    <div className="w-1.5 h-1.5 rounded-full bg-[#B51A2B] animate-pulse" />
                  </div>
                  <p className="text-[10px] text-[#9BA3AF] font-medium ml-8">
                    📡 AI-predicted atmospheric trajectory for the next 6 hours
                  </p>
                </div>
                <div className={`px-3 py-1.5 rounded-full text-[9px] font-black uppercase flex items-center justify-center sm:justify-start gap-1.5
                  ${forecast6h.length > 1 && forecast6h[forecast6h.length - 1].aqi > forecast6h[0].aqi
                    ? "bg-red-500/10 border border-red-500/30 text-red-400"
                    : "bg-[#B51A2B]/10 border border-[#384358]/30 text-[#B51A2B]"}`}>
                  {trend}
                </div>
              </div>

              <div className="flex-1 min-h-[160px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={forecast6h} margin={{ top: 5, right: 10, left: -30, bottom: 0 }}>
                    <defs>
                      <linearGradient id="foreGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#B51A2B" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#B51A2B" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="hour" tick={{ fill: "#9BA3AF", fontSize: 9, fontWeight: 800 }}
                      axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: "#9BA3AF", fontSize: 9 }} axisLine={false} tickLine={false} />
                    <Tooltip content={<ForecastTooltip />} />
                    <Area type="monotone" dataKey="aqi" stroke="#B51A2B" strokeWidth={2.5}
                      fill="url(#foreGrad)" dot={{ fill: "#B51A2B", r: 3, strokeWidth: 0 }}
                      activeDot={{ r: 5, fill: "#B51A2B", stroke: "#FFA586", strokeWidth: 2 }} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Forecast hour tiles — responsive grid columns */}
              {forecast6h.length > 0 && (
                <div className="grid mt-5 gap-3 grid-cols-3 sm:grid-cols-3 md:grid-cols-6">
                  {forecast6h.map((f, i) => {
                    const fb = getAqiBand(f.aqi);
                    return (
                      <div key={i}
                        className="relative flex flex-col items-center gap-1.5 py-4 rounded-2xl border backdrop-blur-sm
                                      transition-all duration-300 hover:-translate-y-1.5 hover:shadow-lg cursor-default group overflow-hidden"
                        style={{
                          borderColor: fb.color + "35",
                          background: `linear-gradient(160deg, ${fb.color}14 0%, rgba(36,47,73,0.7) 100%)`,
                          boxShadow: `0 0 0 0 ${fb.color}00`,
                        }}
                        onMouseEnter={e => e.currentTarget.style.boxShadow = `0 8px 24px -4px ${fb.color}35`}
                        onMouseLeave={e => e.currentTarget.style.boxShadow = "none"}>
                        {/* Glow dot top */}
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-[2px] rounded-full opacity-70 group-hover:opacity-100 transition-opacity"
                          style={{ background: fb.color }} />
                        <span className="text-[10px] font-black uppercase tracking-wider"
                          style={{ color: fb.color + "CC" }}>{f.hour}</span>
                        <span className="text-2xl leading-none">{fb.emoji}</span>
                        <span className="text-lg font-black leading-none" style={{ color: fb.color }}>{f.aqi}</span>
                        <span className="text-[9px] font-bold text-[#9BA3AF] uppercase tracking-wide">{fb.label.split(" ")[0]}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

        </div>

        {/* ── ROW 2: ANALYTICS + AI BRIEFING ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 mb-4">

          {/* ▶ ADVANCED ANALYTICS — 8 cols */}
          <div className="lg:col-span-8 glass-card rounded-3xl p-5 sm:p-7 relative overflow-hidden">
            <div className="absolute -bottom-10 -left-10 w-40 h-40 bg-[#FFA586]/5 blur-[60px] rounded-full" />
            <div className="flex items-center gap-2 mb-5 relative">
              <span className="text-lg">📊</span>
              <h3 className="card-title text-base uppercase tracking-wide">Deep Analytics & <span className="cursive-accent normal-case tracking-normal">XAI</span></h3>
              <div className="ml-auto flex items-center gap-1.5 text-[9px] font-black text-[#B51A2B] uppercase">
                <div className="w-1.5 h-1.5 rounded-full bg-[#B51A2B] animate-pulse" />
                Real-time
              </div>
            </div>
            <AdvancedAnalytics location={selectedLocation} persona={selectedPersona} />
          </div>

          {/* ▶ AI BRIEFING — 4 cols */}
          <div className="lg:col-span-4 glass-card rounded-3xl p-5 sm:p-7 relative overflow-hidden group"
            style={{ background: "linear-gradient(135deg, rgba(181,26,43,0.08) 0%, rgba(36,47,73,0.85) 100%)" }}>
            <div className="absolute -top-10 -right-10 w-36 h-36 bg-[#B51A2B]/10 blur-[60px] rounded-full" />
            <div className="flex items-center gap-2 mb-5 relative">
              <span className="text-lg">🤖</span>
              <h3 className="card-title text-base uppercase tracking-wide">AI Briefing</h3>
              <div className="ml-auto w-5 h-5 rounded-full border border-[#B51A2B]/30 bg-[#B51A2B]/10 flex items-center justify-center">
                <span className="text-[8px]">✨</span>
              </div>
            </div>
            <AeroIntelligenceBriefing city={selectedLocation.name} />
          </div>

        </div>

        {/* ── ROW 3: POLLUTANTS + HEALTH ADVICE ── */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">

          {/* ▶ POLLUTANT GRID — 8 cols */}
          <div className="lg:col-span-8">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-lg">🔬</span>
              <h3 className="text-base font-black text-[#FFA586] uppercase tracking-wide">Pollutant Breakdown</h3>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-3 gap-4">
              {Object.entries(data.pollutants).map(([key, val]) => {
                const cfg = POLLUTANT_CONFIG[key] || { name: key.toUpperCase(), icon: Wind, unit: "µg/m³", emoji: "🌬️" };
                const valNum = typeof val === "object" ? val.value : val;
                return (
                  <div key={key}
                    className="glass-card rounded-2xl p-4 hover:border-[#B51A2B]/40 hover:-translate-y-1 transition-all duration-300 group cursor-default relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-12 h-12 bg-[#B51A2B]/5 blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
                    <div className="flex justify-between items-center mb-4">
                      <span className="text-xl">{cfg.emoji}</span>
                      <span className="card-title text-[10px] uppercase tracking-widest px-2 py-0.5 rounded-full bg-[#101525]/60">
                        {cfg.name}
                      </span>
                    </div>
                    <div className="flex items-end justify-between">
                      <h4 className="text-3xl font-black text-[#FFA586] group-hover:text-[#B51A2B] transition-colors tracking-tighter">
                        {valNum}
                      </h4>
                      <span className="text-[10px] font-black text-[#FFA586] mb-1 uppercase">{cfg.unit}</span>
                    </div>
                    {/* Mini progress bar */}
                    <div className="mt-3 h-1 w-full bg-[#101525]/60 rounded-full overflow-hidden">
                      <div className="h-full rounded-full transition-all duration-1000 bg-gradient-to-r from-[#B51A2B] to-[#FFA586]"
                        style={{ width: `${Math.min((valNum / 200) * 100, 100)}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* ▶ HEALTH ADVICE — 4 cols */}
          <div className="lg:col-span-4 glass-card rounded-3xl p-6 relative overflow-hidden">
            <div className="absolute bottom-0 left-0 w-32 h-32 bg-[#B51A2B]/5 blur-[50px] rounded-full" />
            <div className="flex items-center gap-2 mb-4 relative">
              <span className="text-lg">🛡️</span>
              <h3 className="card-title text-base uppercase tracking-wide">Health <span className="cursive-accent normal-case tracking-normal">Guard</span></h3>
              <button
                onClick={() => navigate("/health-risk", { state: { location: selectedLocation.name, aqi } })}
                className="ml-auto flex items-center gap-1 px-2 py-1 rounded-lg glass-panel border-[#384358]/20 hover:border-[#B51A2B]/40 transition-all text-[8px] font-black text-[#FFA586] hover:text-[#B51A2B]">
                Full Report <ArrowRight size={9} />
              </button>
            </div>
            <PersonalizedHealthAdvice aqi={aqi} location={selectedLocation.name} hideLink />
          </div>

        </div>

      </main>

      {/* ══ FOOTER ══ */}
      <footer className="py-4 sm:py-6 px-4 sm:px-8 border-t border-[#384358]/15 flex flex-col sm:flex-row justify-between items-center gap-3 sm:gap-0 bg-[#101525]/70 backdrop-blur-md relative z-10 text-center sm:text-left">
        <div className="flex items-center gap-2 text-[9px] font-black uppercase tracking-widest text-[#9BA3AF] justify-center sm:justify-start">
          <span>🌍</span>
          <span className="cursive-accent text-lg normal-case tracking-normal">AeroGuard</span> <span className="ml-1">Intelligence</span>
        </div>
        <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-4 text-[9px] font-black uppercase tracking-widest">
          <span className="flex items-center gap-1.5 text-[#B51A2B]">
            <div className="w-1.5 h-1.5 rounded-full bg-[#B51A2B] animate-pulse" />
            Systems Online
          </span>
          <span className="text-[#9BA3AF]">✅ AI Validated</span>
          <span className="text-[#9BA3AF]">© 2026</span>
        </div>
      </footer>
    </div>
  );
}
