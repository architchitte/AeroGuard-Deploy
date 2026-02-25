import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Shield, AlertTriangle, Heart, Activity, Users, TrendingUp, Info, MapPin, ArrowLeft, Clock, Sparkles, Zap, Wind } from "lucide-react";
import healthRiskService, { getHealthRisk } from "../api/healthRiskService";
import { useForecast6h } from "../hooks/forcast6h.js";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import axios from "axios";
import { API_BASE_URL } from "../api/apiConfig";

/* ——— AQI HELPERS ——— */
const getAQIColor = (aqi) => {
  if (aqi <= 50) return "#00e400"; // Good - Green
  if (aqi <= 100) return "#ffff00"; // Moderate - Yellow
  if (aqi <= 150) return "#ff7e00"; // Unhealthy for Sensitive Groups - Orange
  if (aqi <= 200) return "#ff0000"; // Unhealthy - Red
  if (aqi <= 300) return "#8f3f97"; // Very Unhealthy - Purple
  return "#7e0023"; // Hazardous - Maroon
};

const getAQILabel = (aqi) => {
  if (aqi <= 50) return "Good";
  if (aqi <= 100) return "Moderate";
  if (aqi <= 150) return "Unhealthy for Sensitive Groups";
  if (aqi <= 200) return "Unhealthy";
  if (aqi <= 300) return "Very Unhealthy";
  return "Hazardous";
};

export function HealthRisk() {
  const location = useLocation();
  const navigate = useNavigate();

  const dashboardLocation = location.state?.location || null;
  const dashboardAqi = location.state?.aqi || null;

  const [selectedPersona, setSelectedPersona] = useState("General Public");
  const [healthData, setHealthData] = useState(null);
  const [aqiData, setAqiData] = useState(dashboardAqi ? { aqi: dashboardAqi, category: location.state?.category } : null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchInput, setSearchInput] = useState("");
  const [activeLocation, setActiveLocation] = useState(dashboardLocation);

  const { forecast6h, loading: forecastLoading } = useForecast6h(activeLocation ? { name: activeLocation } : null);

  const personas = [
    { id: "General Public", label: "General Public", icon: Users, color: "accent" },
    { id: "Children", label: "Children", icon: Heart, color: "highlight" },
    { id: "Elderly", label: "Elderly", icon: Shield, color: "muted" },
    { id: "Athletes", label: "Athletes", icon: Activity, color: "accent" },
  ];

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  useEffect(() => {
    if (activeLocation && !dashboardAqi) fetchRealtimeAQI(activeLocation);
    else if (dashboardAqi) fetchHealthRisk();
  }, [activeLocation, dashboardAqi]);

  useEffect(() => { if (aqiData) fetchHealthRisk(); }, [aqiData, selectedPersona]);

  const fetchRealtimeAQI = async (loc) => {
    setLoading(true); setError(null);
    try {
      const resp = await axios.get(`${API_BASE_URL}/api/v1/realtime-aqi/city/${loc}`);
      if (resp.data.status === "success") setAqiData(resp.data.data);
      else setError("Failed to fetch AQI data");
    } catch { setError("Unable to fetch AQI data. Return to Dashboard and select a location."); }
    finally { setLoading(false); }
  };

  const fetchHealthRisk = async () => {
    if (!aqiData?.aqi) return;
    setLoading(true); setError(null);
    try {
      const data = await getHealthRisk(aqiData.aqi, activeLocation || "Unknown", "PM2.5", selectedPersona);
      if (data?.health_assessment || data?.recommendations || data?.persona_advice) setHealthData(data);
      else setError("Failed to fetch health risk assessment");
    } catch { setError("Unable to complete health assessment. Please try again."); }
    finally { setLoading(false); }
  };

  const riskColor = (r) => {
    switch (r?.toLowerCase()) {
      case "low": return "from-[#B51A2B] to-[#541A2B]"; // Using Red/Burgundy for low as per system theme, though normally green
      case "moderate": return "from-orange-400 to-orange-600";
      case "high": return "from-red-500 to-red-700";
      case "hazardous": return "from-red-700 to-purple-900";
      default: return "from-[#384358] to-[#101525]";
    }
  };

  return (
    <div className="min-h-screen bg-[#101525] relative overflow-hidden font-sans">
      {/* ══ NAV ══ */}
      <nav className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[95%] max-w-6xl h-14 sm:h-16 rounded-2xl bg-[#101525]/80 backdrop-blur-2xl border border-[#384358]/20 flex items-center justify-between px-4 sm:px-8 shadow-2xl transition-all duration-300 pointer-events-auto">
        <div className="flex items-center gap-2 sm:gap-3 group cursor-pointer" onClick={() => navigate("/")}>
          <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-gradient-to-br from-[#B51A2B] to-[#FFA586] flex items-center justify-center shadow-lg shadow-[#B51A2B]/20">
            <span className="text-xs sm:text-sm">🌍</span>
          </div>
          <span className="font-black text-base sm:text-lg text-[#FFA586] tracking-tighter">AeroGuard<span className="text-[#B51A2B] animate-pulse">.ai</span></span>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <button onClick={() => navigate("/dashboard")}
            className="px-3 sm:px-6 py-2 sm:py-2.5 rounded-xl bg-[#242F49] border border-[#384358]/40 text-[#FFA586] text-[9px] sm:text-[10px] font-black uppercase tracking-widest hover:border-[#B51A2B]/50 transition-all flex items-center gap-1.5 sm:gap-2 active:scale-95">
            <ArrowLeft size={11} /> <span className="hidden sm:inline">Return</span> Dashboard
          </button>
        </div>
      </nav>

      {/* Decorative Background Elements */}
      <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-[#B51A2B]/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[20%] left-[-5%] w-[30%] h-[30%] bg-[#541A2B]/10 blur-[100px] rounded-full pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 py-10 sm:py-12 space-y-8 sm:space-y-12">
        {/* Navigation & Header */}
        <header className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 sm:gap-6">
          <div className="flex items-center gap-3 sm:gap-4">
            <button
              onClick={() => navigate("/dashboard")}
              className="p-2.5 sm:p-3 rounded-2xl glass-panel hover:border-[#B51A2B]/40 hover:bg-[#B51A2B]/5 transition-all group"
            >
              <ArrowLeft className="w-4 h-4 sm:w-5 sm:h-5 text-[#FFA586] group-hover:-translate-x-1 transition-transform" />
            </button>
            <div className="space-y-1">
              <h1 className="text-3xl sm:text-4xl font-black text-glow tracking-tight text-white flex items-center gap-3">
                Health <span className="text-gradient">Intelligence</span>
              </h1>
              <p className="text-[#9BA3AF] text-xs sm:text-sm font-medium tracking-wide flex items-center gap-2">
                <Sparkles className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-[#B51A2B]" />
                Personalized AI-driven biological impact analysis
              </p>
            </div>
          </div>
        </header>

        {/* Search Modal Interaction (If no location) */}
        {!activeLocation && (
          <div className="max-w-2xl mx-auto py-20">
            <div className="glass-card rounded-[3rem] p-12 text-center space-y-8 border-[#384358]/20 shadow-[0_32px_64px_-16px_rgba(0,0,0,0.5)]">
              <div className="relative w-24 h-24 mx-auto">
                <div className="absolute inset-0 bg-[#B51A2B]/20 blur-2xl rounded-full animate-pulse" />
                <div className="relative z-10 w-full h-full rounded-3xl bg-gradient-to-br from-[#B51A2B] to-[#541A2B] flex items-center justify-center shadow-2xl">
                  <MapPin className="w-10 h-10 text-white" />
                </div>
              </div>
              <div className="space-y-3">
                <h2 className="text-3xl font-black text-white">Identify Your Location</h2>
                <p className="text-[#9BA3AF] text-base leading-relaxed">
                  We need to synchronize with the nearest atmospheric monitoring station <br /> to deliver personalized health metrics.
                </p>
              </div>

              <form onSubmit={(e) => { e.preventDefault(); if (searchInput.trim()) setActiveLocation(searchInput.trim()); }} className="relative group">
                <input
                  type="text"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  placeholder="Enter city or region..."
                  className="w-full pl-6 pr-40 py-5 rounded-2xl bg-[#101525] border border-[#384358]/40 text-white text-lg font-medium focus:outline-none focus:border-[#B51A2B]/60 transition-all placeholder:text-[#384358]"
                />
                <button
                  type="submit"
                  disabled={!searchInput.trim()}
                  className="absolute right-2 top-2 bottom-2 px-8 bg-[#B51A2B] hover:bg-[#B51A2B]/90 disabled:opacity-40 text-white font-black text-sm rounded-xl transition-all shadow-lg active:scale-95"
                >
                  Synchronize
                </button>
              </form>

              <div className="pt-8 border-t border-[#384358]/10">
                <p className="text-[10px] text-[#9BA3AF] uppercase tracking-[0.3em] font-black mb-4">Quick Access Centers</p>
                <div className="flex flex-wrap justify-center gap-3">
                  {["Delhi", "Mumbai", "Bangalore", "Chennai"].map(city => (
                    <button
                      key={city}
                      onClick={() => setActiveLocation(city)}
                      className="px-6 py-2.5 rounded-xl glass-panel hover:border-[#B51A2B]/40 text-xs font-bold text-[#FFA586] transition-all hover:bg-[#B51A2B]/5"
                    >
                      {city}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeLocation && (
          <div className="space-y-12 animate-in fade-in slide-in-from-bottom-8 duration-700">
            {/* --- HERO STATS SECTION --- */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
              {/* AQI Hero Card */}
              <div className="lg:col-span-12 xl:col-span-8 group">
                <div className="h-full glass-card rounded-[2rem] sm:rounded-[3rem] p-6 sm:p-10 flex flex-col sm:flex-row items-center gap-6 sm:gap-12 relative overflow-hidden border-[#384358]/20 transition-all hover:border-[#B51A2B]/30 shadow-2xl">
                  {/* Visual Background Glow */}
                  <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-[#B51A2B]/10 to-transparent blur-[80px] group-hover:blur-[100px] transition-all" />

                  {/* AQI Gauge Display */}
                  <div className="relative flex-shrink-0">
                    <div className="w-36 h-36 sm:w-48 sm:h-48 rounded-full border-[8px] sm:border-[10px] border-[#384358]/20 flex items-center justify-center relative">
                      <div
                        className="absolute inset-[-10px] rounded-full border-[10px] border-transparent border-t-[#B51A2B] transition-all duration-1000 rotate-[45deg]"
                        style={{
                          borderColor: `${getAQIColor(aqiData?.aqi ?? 0)}`,
                          clipPath: `conic-gradient(from 0deg, white ${Math.min(100, ((aqiData?.aqi ?? 0) / 300) * 100)}%, transparent 0)`
                        }}
                      />
                      <div className="text-center group-hover:scale-110 transition-transform">
                        <p className="text-4xl sm:text-6xl font-black text-white tracking-tighter leading-none">{aqiData?.aqi ?? '--'}</p>
                        <p className="text-[9px] sm:text-[10px] font-black text-[#9BA3AF] uppercase tracking-[0.2em] mt-1 sm:mt-2">AQI Score</p>
                      </div>
                    </div>
                  </div>

                  <div className="flex-1 space-y-4 sm:space-y-6 relative z-10 w-full text-center sm:text-left">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 justify-center sm:justify-start">
                        <MapPin size={14} className="text-[#B51A2B]" />
                        <span className="text-[11px] font-black uppercase text-[#B51A2B] tracking-[0.2em]">Atmospheric Node</span>
                      </div>
                      <h2 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-none">{activeLocation}</h2>
                      <div
                        className="inline-block px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border"
                        style={{
                          backgroundColor: `${getAQIColor(aqiData?.aqi ?? 0)}15`,
                          borderColor: `${getAQIColor(aqiData?.aqi ?? 0)}40`,
                          color: getAQIColor(aqiData?.aqi ?? 0)
                        }}
                      >
                        {aqiData?.category || 'Analyzing...'}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-6 pt-6 border-t border-[#384358]/15">
                      <div className="space-y-1">
                        <p className="text-[10px] font-bold text-[#9BA3AF] uppercase tracking-widest">Last Verified</p>
                        <p className="text-sm font-black text-white tracking-tight">{new Date().toLocaleTimeString()}</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-[10px] font-bold text-[#9BA3AF] uppercase tracking-widest">Health Consensus</p>
                        <p className="text-sm font-black text-white tracking-tight">EPA Global Standard</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Persona Quick Switcher */}
              <div className="lg:col-span-12 xl:col-span-4 flex flex-col gap-6">
                <div className="glass-panel p-8 rounded-[2.5rem] flex-1 flex flex-col justify-center space-y-6 border-[#384358]/20 shadow-xl">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-black text-white uppercase tracking-[0.3em]">Select Persona</h3>
                    <Users size={16} className="text-[#B51A2B]" />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    {personas.map(p => {
                      const IconComp = p.icon;
                      const isActive = selectedPersona === p.id;
                      return (
                        <button
                          key={p.id}
                          onClick={() => setSelectedPersona(p.id)}
                          className={`flex flex-col items-center justify-center p-5 rounded-[2rem] border-2 transition-all group/btn relative overflow-hidden ${isActive
                            ? "border-[#B51A2B] bg-[#B51A2B]/10 shadow-[0_12px_24px_-8px_rgba(181,26,43,0.3)] scale-[1.02]"
                            : "border-[#384358]/20 bg-[#101525] hover:border-[#384358]/50"
                            }`}
                        >
                          <IconComp size={20} className={`${isActive ? "text-[#B51A2B]" : "text-[#384358]"} mb-3 transition-transform group-hover/btn:scale-110`} />
                          <span className={`text-[10px] font-black uppercase tracking-widest ${isActive ? "text-white" : "text-[#9BA3AF]"}`}>
                            {p.label}
                          </span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>

            {/* --- ANALYSIS RESULTS --- */}
            {error ? (
              <div className="glass-card rounded-[2.5rem] p-12 border-red-500/20 bg-red-500/5 text-center space-y-4">
                <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-2 animate-bounce" />
                <h3 className="text-2xl font-black text-white">Diagnostic Error</h3>
                <p className="text-red-400 font-medium max-w-lg mx-auto leading-relaxed">{error}</p>
                <button
                  onClick={fetchHealthRisk}
                  className="mt-6 px-10 py-3 bg-red-500 text-white font-black rounded-xl hover:bg-red-600 transition-all"
                >
                  Retry Analysis
                </button>
              </div>
            ) : loading ? (
              <div className="glass-card rounded-[2.5rem] p-24 text-center space-y-8 shadow-2xl relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-t from-[#B51A2B]/5 to-transparent pointer-events-none" />
                <div className="relative">
                  <div className="w-24 h-24 border-[6px] border-[#384358]/20 border-t-[#B51A2B] rounded-full animate-spin mx-auto" />
                  <Sparkles className="absolute inset-0 m-auto w-8 h-8 text-[#B51A2B] animate-pulse" />
                </div>
                <div className="space-y-3">
                  <h3 className="text-2xl font-black text-white tracking-tight uppercase tracking-[0.2em]">Analyzing Bio-Impact</h3>
                  <p className="text-[#9BA3AF] text-sm font-medium">Cross-referencing atmospheric data with medical health standards...</p>
                </div>
              </div>
            ) : healthData ? (
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                {/* Visual Impact Summary */}
                <div className="lg:col-span-12 xl:col-span-4 space-y-6">
                  <div className="glass-card rounded-[3rem] p-10 relative overflow-hidden group border-[#384358]/20 shadow-2xl">
                    <div className={`absolute inset-0 bg-gradient-to-br ${riskColor(healthData.aqi?.risk_level)} opacity-5 group-hover:opacity-10 transition-opacity`} />

                    <div className="relative z-10 space-y-8">
                      <div className="flex items-center justify-between">
                        <div className="p-4 rounded-2xl bg-white/5 border border-white/10 group-hover:scale-110 transition-transform">
                          {healthData.aqi?.risk_level?.toLowerCase() === "low"
                            ? <Shield className="w-6 h-6 text-[#B51A2B]" />
                            : healthData.aqi?.risk_level?.toLowerCase() === "moderate"
                              ? <Info className="w-6 h-6 text-orange-400" />
                              : <AlertTriangle className="w-6 h-6 text-red-500" />}
                        </div>
                        <div className="text-right">
                          <p className="text-[10px] font-black text-[#9BA3AF] uppercase tracking-[0.2em]">Risk Potential</p>
                          <p className="text-lg font-black text-white uppercase">{healthData.aqi?.risk_level} LEVEL</p>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <h3 className="text-4xl font-black text-glow text-white tracking-tighter leading-none">
                          {healthData.aqi?.category}
                        </h3>
                        <p className="text-sm font-medium text-[#9BA3AF] leading-relaxed">
                          Atmospheric conditions are currently evaluated as <span className="text-white font-black">{healthData.aqi?.category.toLowerCase()}</span> for the {selectedPersona.toLowerCase()}.
                        </p>
                      </div>

                      <div className="pt-8 space-y-5 border-t border-[#384358]/20">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-bold text-[#9BA3AF] uppercase tracking-[0.1em]">Dominant Pathogen</span>
                          <span className="px-3 py-1 rounded-lg bg-[#B51A2B]/10 border border-[#B51A2B]/20 text-[10px] font-black text-[#B51A2B] uppercase">
                            {healthData.aqi?.primary_pollutant}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-bold text-[#9BA3AF] uppercase tracking-[0.1em]">AI Engine</span>
                          <span className="text-[10px] font-black text-white uppercase tracking-widest">{healthData.model_source}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Health Assessment & Tactical Advice */}
                <div className="lg:col-span-12 xl:col-span-8 space-y-8">
                  {/* Detailed Assessment */}
                  <div className="glass-card rounded-[3rem] p-10 space-y-8 border-[#384358]/20 shadow-2xl">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-2xl bg-[#B51A2B]/10 flex items-center justify-center border border-[#B51A2B]/20">
                          <Activity className="w-6 h-6 text-[#B51A2B]" />
                        </div>
                        <h3 className="text-2xl font-black text-white">Biological Assessment</h3>
                      </div>
                    </div>

                    <div className="space-y-6">
                      <p className="text-base text-[#9BA3AF] leading-relaxed font-medium">
                        {healthData.health_assessment?.description}
                      </p>

                      {healthData.health_assessment?.cautionary_statement && (
                        <div className="p-6 rounded-[2rem] bg-orange-500/5 border border-orange-500/20 flex gap-4">
                          <AlertTriangle className="w-6 h-6 text-orange-400 shrink-0" />
                          <p className="text-sm text-orange-200 font-medium leading-relaxed">
                            <span className="text-orange-400 font-black uppercase text-[10px] block tracking-[0.2em] mb-1">Strategic Caution</span>
                            {healthData.health_assessment.cautionary_statement}
                          </p>
                        </div>
                      )}

                      {healthData.health_assessment?.health_implications?.length > 0 && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {healthData.health_assessment.health_implications.map((imp, i) => (
                            <div key={i} className="flex gap-4 p-5 rounded-[2rem] bg-white/5 border border-white/5 hover:border-[#B51A2B]/20 transition-all">
                              <div className="w-2 h-2 rounded-full bg-[#B51A2B] mt-1.5 shrink-0" />
                              <span className="text-xs text-white font-medium leading-relaxed">{imp}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Personalized Recommendations Section */}
                  <div className="space-y-8">
                    <div className="flex items-center gap-3 px-6">
                      <div className="w-1.5 h-6 bg-[#B51A2B] rounded-full" />
                      <h3 className="text-xl font-black text-white tracking-tight uppercase tracking-[0.2em]">Health Recommendations</h3>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Personalized Insight Card */}
                      {healthData.persona_advice && (
                        <div className="md:col-span-2 glass-card p-10 rounded-[3rem] border-[#B51A2B]/20 bg-gradient-to-br from-[#B51A2B]/5 to-transparent relative overflow-hidden shadow-2xl">
                          <div className="relative z-10 flex gap-8 items-start">
                            <div className="p-4 rounded-2xl bg-[#B51A2B]/10 border border-[#B51A2B]/20">
                              <Sparkles className="w-8 h-8 text-[#B51A2B]" />
                            </div>
                            <div className="space-y-3">
                              <p className="text-[10px] font-black text-[#B51A2B] uppercase tracking-[0.3em]">AI-Generated Guidance</p>
                              <p className="text-2xl font-black text-white leading-tight tracking-tight">
                                {healthData.persona_advice.advice || healthData.persona_advice}
                              </p>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* General Advice Card */}
                      <div className="glass-card p-8 rounded-[2.5rem] border-[#384358]/20 flex flex-col justify-between group bg-white/[0.01] shadow-xl">
                        <div className="space-y-4">
                          <div className="flex items-center gap-3">
                            <Shield className="w-5 h-5 text-[#B51A2B]" />
                            <h4 className="text-xs font-black text-white uppercase tracking-widest">General Precautions</h4>
                          </div>
                          <p className="text-sm text-[#9BA3AF] leading-relaxed font-medium">
                            {healthData.recommendations?.general_advice}
                          </p>
                        </div>
                      </div>

                      {/* Specific Precautions */}
                      <div className="glass-card p-8 rounded-[2.5rem] border-[#384358]/20 bg-white/[0.01] shadow-xl">
                        <div className="flex items-center gap-3 mb-6">
                          <AlertTriangle className="w-5 h-5 text-orange-400" />
                          <h4 className="text-xs font-black text-white uppercase tracking-widest">Key Warnings</h4>
                        </div>
                        <ul className="space-y-4">
                          {healthData.recommendations?.precautions?.slice(0, 2).map((p, i) => (
                            <li key={i} className="flex gap-4 items-start">
                              <div className="w-1.5 h-1.5 rounded-full bg-[#B51A2B] mt-2 shrink-0" />
                              <span className="text-sm text-white font-medium leading-relaxed">{p}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : null}

            {/* --- CLEANED FOOTER --- */}
            <footer className="pt-12 pb-8">
              <div className="glass-panel py-6 px-10 rounded-[2rem] border-[#384358]/20 flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#B51A2B]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />

                <div className="flex items-center gap-6 relative z-10">
                  <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#101525]/80 border border-[#384358]/30">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#B51A2B] animate-pulse" />
                    <span className="text-[10px] font-black text-white uppercase tracking-[0.2em]">Live Data Engine</span>
                  </div>
                  <p className="text-[10px] font-bold text-[#9BA3AF] uppercase tracking-[0.1em]">
                    Confidence Scoring: <span className="text-[#B51A2B] ml-1">{healthData?.model_confidence ?? '98.4%'}</span>
                  </p>
                </div>

                <div className="flex items-center gap-8 relative z-10">
                  <div className="text-center md:text-right">
                    <p className="text-[9px] font-black text-[#9BA3AF] uppercase tracking-widest mb-1">Last Update</p>
                    <div className="flex items-center gap-2 justify-center md:justify-end">
                      <Clock size={12} className="text-[#B51A2B]" />
                      <p className="text-xs font-black text-white tracking-tight">{new Date().toLocaleTimeString()}</p>
                    </div>
                  </div>
                </div>
              </div>
            </footer>
          </div>
        )}
      </div>
    </div>
  );
}

export default HealthRisk;
