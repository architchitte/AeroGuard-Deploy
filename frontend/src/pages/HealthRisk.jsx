import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Shield, AlertTriangle, Heart, Activity, Users, TrendingUp, Info, MapPin, ArrowLeft, Clock, Sparkles } from "lucide-react";
import healthRiskService, { getHealthRisk } from "../api/healthRiskService";
import { useForecast6h } from "../hooks/forcast6h.js";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

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
    <div className="min-h-screen bg-[#101525] p-5">
      <div className="max-w-6xl mx-auto space-y-5">

        {/* Header */}
        <div className="text-center space-y-3">
          <div className="flex items-center justify-center gap-3">
            <button onClick={() => navigate("/dashboard")}
              className="p-1.5 rounded-lg glass-panel hover:border-[#B51A2B]/40 transition-colors">
              <ArrowLeft className="w-4 h-4 text-[#FFA586]" />
            </button>
            <h1 className="text-3xl font-black text-[#FFA586]">Health Risk Assessment</h1>
          </div>
          <p className="text-[#FFA586] text-sm">AI-powered personalized health guidance based on real-time air quality</p>
          {activeLocation && (
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#242F49] border border-[#384358]/30">
              <MapPin className="w-3 h-3 text-[#B51A2B]" />
              <span className="text-xs font-bold text-[#B51A2B]">{activeLocation}</span>
            </div>
          )}
        </div>

        {/* Location Picker */}
        {!activeLocation && (
          <div className="glass-card rounded-2xl p-6 max-w-xl mx-auto">
            <div className="text-center mb-5">
              <MapPin className="w-8 h-8 text-[#B51A2B] mx-auto mb-2" />
              <h2 className="text-base font-bold text-[#FFA586]">Select a Location</h2>
              <p className="text-xs text-[#FFA586] mt-1">Get personalized health advice for your area</p>
            </div>
            <form onSubmit={(e) => { e.preventDefault(); if (searchInput.trim()) setActiveLocation(searchInput.trim()); }} className="flex gap-2">
              <input type="text" value={searchInput} onChange={(e) => setSearchInput(e.target.value)}
                placeholder="e.g. Delhi, Mumbai…"
                className="flex-1 px-3 py-2.5 rounded-xl bg-[#101525] border border-[#384358]/30 text-[#FFA586] text-sm focus:outline-none focus:border-[#B51A2B]/60 transition-colors" />
              <button type="submit" disabled={!searchInput.trim()}
                className="px-5 py-2.5 bg-[#B51A2B] hover:bg-[#B51A2B]/80 disabled:opacity-40 text-white font-black text-sm rounded-xl transition-all">
                Analyze
              </button>
            </form>
            <div className="mt-4 pt-4 border-t border-[#384358]/15">
              <p className="text-[9px] text-[#9BA3AF] text-center uppercase tracking-widest mb-3">Popular Cities</p>
              <div className="flex flex-wrap justify-center gap-2">
                {["Delhi", "Mumbai", "Bangalore", "Chennai"].map(city => (
                  <button key={city} onClick={() => setActiveLocation(city)}
                    className="px-3 py-1 rounded-full bg-[#242F49] hover:bg-[#384358]/20 text-[10px] text-[#FFA586] transition-colors border border-[#384358]/20">
                    {city}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Persona + AQI Controls */}
        {activeLocation && (
          <div className="glass-card rounded-2xl p-5 space-y-5">
            {aqiData && (
              <div className="p-4 rounded-xl bg-[#242F49] border border-[#384358]/30">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-[9px] text-[#9BA3AF] uppercase tracking-wider mb-1">Real-time AQI</p>
                    <p className="text-4xl font-black text-[#FFA586]">{aqiData.aqi}</p>
                    <p className="text-xs text-[#FFA586] mt-0.5">{aqiData.category}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-[9px] text-[#9BA3AF] mb-0.5">Location</p>
                    <p className="text-xs text-[#FFA586] font-bold">{activeLocation}</p>
                    <p className="text-[9px] text-[#9BA3AF] mt-0.5">{new Date().toLocaleTimeString()}</p>
                  </div>
                </div>
              </div>
            )}
            <div className="space-y-2">
              <label className="text-[9px] font-black text-[#FFA586] uppercase tracking-widest">Select Persona</label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {personas.map(p => {
                  const Ic = p.icon;
                  const sel = selectedPersona === p.id;
                  return (
                    <button key={p.id} onClick={() => setSelectedPersona(p.id)}
                      className={`p-3 rounded-xl border-2 transition-all text-center ${sel ? "border-[#B51A2B] bg-[#B51A2B]/10" : "border-[#384358]/20 bg-[#101525]/60 hover:border-[#384358]/50"}`}>
                      <Ic className={`w-4 h-4 mx-auto mb-1.5 ${sel ? "text-[#B51A2B]" : "text-[#9BA3AF]"}`} />
                      <p className={`text-[10px] font-bold ${sel ? "text-[#FFA586]" : "text-[#9BA3AF]"}`}>{p.label}</p>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="glass-card rounded-2xl p-5 border border-red-500/20 bg-red-500/5 text-center">
            <AlertTriangle className="w-6 h-6 text-red-400 mx-auto mb-2" />
            <p className="text-red-400 text-sm font-medium">{error}</p>
            <button onClick={fetchHealthRisk} className="mt-3 px-4 py-1.5 glass-panel rounded-lg text-[#FFA586] text-xs transition-colors hover:border-[#384358]/50">
              Retry
            </button>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="glass-card rounded-2xl p-10 text-center">
            <div className="w-10 h-10 border-4 border-[#384358]/30 border-t-[#B51A2B] rounded-full animate-spin mx-auto mb-3" />
            <p className="text-[#FFA586] text-xs">Analyzing health risk…</p>
          </div>
        )}

        {/* Results */}
        {activeLocation && !loading && healthData && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Risk Overview */}
            <div className="lg:col-span-1">
              <div className={`glass-card rounded-2xl p-6 text-center space-y-4 bg-gradient-to-br ${riskColor(healthData.aqi?.risk_level)} bg-opacity-5`}>
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-white/5 backdrop-blur-sm mx-auto">
                  {healthData.aqi?.risk_level?.toLowerCase() === "low"
                    ? <Shield className="w-5 h-5 text-[#B51A2B]" />
                    : healthData.aqi?.risk_level?.toLowerCase() === "moderate"
                      ? <Info className="w-5 h-5 text-orange-400" />
                      : <AlertTriangle className="w-5 h-5 text-red-500" />}
                </div>
                <div>
                  <h3 className="text-2xl font-black text-[#FFA586]">{healthData.aqi?.category}</h3>
                  <p className="text-[10px] text-[#FFA586] uppercase tracking-wider">{healthData.aqi?.risk_level} Risk</p>
                </div>
                <div className="pt-3 border-t border-white/10">
                  <p className="text-[9px] text-[#9BA3AF] mb-1">AQI</p>
                  <p className="text-4xl font-black text-[#FFA586]">{healthData.aqi?.value}</p>
                </div>
                <div className="space-y-1.5">
                  <div className="flex justify-between text-[10px]">
                    <span className="text-[#9BA3AF]">Primary Pollutant</span>
                    <span className="text-[#FFA586] font-bold">{healthData.aqi?.primary_pollutant}</span>
                  </div>
                  <div className="flex justify-between text-[10px]">
                    <span className="text-[#9BA3AF]">Model</span>
                    <span className="text-[#FFA586] font-bold capitalize">{healthData.model_source}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Assessment + Recommendations */}
            <div className="lg:col-span-2 space-y-4">
              <div className="glass-card rounded-2xl p-5 space-y-3">
                <h3 className="text-sm font-black text-[#FFA586] flex items-center gap-2">
                  <Heart className="w-4 h-4 text-[#FFA586]" /> Health Assessment
                </h3>
                <p className="text-xs text-[#FFA586] leading-relaxed">{healthData.health_assessment?.description}</p>
                {healthData.health_assessment?.cautionary_statement && (
                  <div className="p-3 rounded-xl bg-yellow-500/8 border border-yellow-500/20">
                    <p className="text-xs text-yellow-300"><strong>Caution:</strong> {healthData.health_assessment.cautionary_statement}</p>
                  </div>
                )}
                {healthData.health_assessment?.health_implications?.length > 0 && (
                  <ul className="space-y-1">
                    {healthData.health_assessment.health_implications.map((imp, i) => (
                      <li key={i} className="text-xs text-[#FFA586] flex items-start gap-1.5">
                        <span className="text-[#B51A2B] mt-0.5">•</span><span>{imp}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="glass-card rounded-2xl p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-black text-[#FFA586] flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-[#B51A2B]" /> Recommendations
                  </h3>
                  <span className="px-2 py-0.5 rounded-full bg-[#242F49] border border-[#384358]/30 text-[9px] font-black text-[#B51A2B] uppercase">{selectedPersona}</span>
                </div>
                {healthData.persona_advice && (
                  <div className="p-3 rounded-xl bg-[#242F49] border border-[#384358]/30">
                    <div className="flex items-center gap-1.5 mb-1">
                      <Sparkles className="w-3 h-3 text-[#FFA586]" />
                      <p className="text-[9px] font-black text-[#FFA586] uppercase">Personalized Insight</p>
                    </div>
                    <p className="text-xs text-[#FFA586] leading-relaxed">{healthData.persona_advice.advice || healthData.persona_advice}</p>
                  </div>
                )}
                <div className="p-3 rounded-xl bg-[#B51A2B]/8 border border-[#384358]/25">
                  <p className="text-xs text-[#FFA586]">{healthData.recommendations?.general_advice}</p>
                </div>
                {healthData.recommendations?.precautions?.length > 0 && (
                  <ul className="space-y-1.5">
                    {healthData.recommendations.precautions.map((p, i) => (
                      <li key={i} className="text-xs text-[#FFA586] flex items-start gap-2 p-2.5 rounded-lg bg-[#101525]/60">
                        <Shield className="w-3 h-3 text-[#B51A2B] mt-0.5 shrink-0" /><span>{p}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {/* Forecast */}
              <div className="glass-card rounded-2xl p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-black text-[#FFA586] flex items-center gap-2">
                    <Clock className="w-4 h-4 text-[#FFA586]" /> 6-Hour Trend
                  </h3>
                  {forecast6h.length > 0 && (
                    <div className={`px-2 py-0.5 rounded text-[9px] font-black uppercase ${forecast6h[forecast6h.length - 1].aqi > forecast6h[0].aqi ? "text-red-500 bg-red-500/10" : "text-[#B51A2B] bg-[#B51A2B]/10"}`}>
                      {forecast6h[forecast6h.length - 1].aqi > forecast6h[0].aqi ? "Worsening" : "Improving"}
                    </div>
                  )}
                </div>
                <div className="h-52">
                  {forecastLoading ? (
                    <div className="flex items-center justify-center h-full">
                      <div className="w-8 h-8 border-4 border-[#384358]/30 border-t-[#B51A2B] rounded-full animate-spin" />
                    </div>
                  ) : forecast6h.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={forecast6h}>
                        <defs>
                          <linearGradient id="hrGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#B51A2B" stopOpacity={0.25} />
                            <stop offset="95%" stopColor="#B51A2B" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <XAxis dataKey="hour" stroke="#384358" fontSize={9} />
                        <YAxis stroke="#384358" fontSize={9} />
                        <Tooltip contentStyle={{ backgroundColor: "#242F49", border: "1px solid #384358", borderRadius: "10px", color: "#FFA586", fontSize: "10px" }} />
                        <Area type="monotone" dataKey="aqi" stroke="#B51A2B" fill="url(#hrGrad)" strokeWidth={2} />
                      </AreaChart>
                    </ResponsiveContainer>
                  ) : <p className="text-center text-[#9BA3AF] text-xs py-12">Trend data temporarily unavailable</p>}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer note */}
        {healthData && (
          <div className="glass-card rounded-xl p-3 text-center">
            <p className="text-[9px] text-[#9BA3AF]">
              ML health risk model &nbsp;•&nbsp; Confidence:
              <span className="text-[#B51A2B] font-bold capitalize ml-1">{healthData.model_confidence}</span>
              &nbsp;•&nbsp; Updated: {new Date(healthData.timestamp).toLocaleString()}
            </p>
          </div>
        )}

      </div>
    </div>
  );
}

export default HealthRisk;
