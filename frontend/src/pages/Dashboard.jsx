import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";
import {
  MapPin, Wind, AlertTriangle, Info, BrainCircuit, Activity, User, ShieldCheck, HeartPulse, Droplets, Thermometer, Gauge, ChevronUp, ChevronDown, CheckCircle, Search
} from "lucide-react";
import { useAQIData } from "../hooks/useAQIData";
import CityHeatmap from "../Components/CityHeatmap";

// 1. Locations with Coordinates
const LOCATIONS = [
  { id: 'delhi', name: 'Delhi', lat: 28.7041, lon: 77.1025 },
  { id: 'mumbai', name: 'Mumbai', lat: 19.0760, lon: 72.8777 },
  { id: 'bangalore', name: 'Bangalore', lat: 12.9716, lon: 77.5946 },
];

// 2. Personas with ID logic
const PERSONAS = [
  { id: 'general', label: 'General Public', icon: User },
  { id: 'vulnerable', label: 'Children / Elderly', icon: HeartPulse },
  { id: 'outdoor', label: 'Outdoor Workers / Athletes', icon: Activity },
];

const POLLUTANT_CONFIG = {
  pm25: { name: 'PM2.5', unit: 'µg/m³' },
  pm10: { name: 'PM10', unit: 'µg/m³' },
  no2: { name: 'NO2', unit: 'ppb' },
  o3: { name: 'O3', unit: 'ppb' },
  so2: { name: 'SO2', unit: 'ppb' },
  co: { name: 'CO', unit: 'ppm' },
};

export default function Dashboard() {
  const [selectedLocation, setSelectedLocation] = useState(LOCATIONS[0]);
  const [selectedPersona, setSelectedPersona] = useState(PERSONAS[0].id);
  const [searchTerm, setSearchTerm] = useState("");

  const { data, loading, error } = useAQIData(selectedLocation.name, selectedPersona);

  const filteredLocations = useMemo(() => {
    if (!searchTerm) return LOCATIONS;
    return LOCATIONS.filter(loc => loc.name.toLowerCase().includes(searchTerm.toLowerCase()));
  }, [searchTerm]);

  const getTheme = (aqi) => {
    if (aqi <= 50) return { color: "text-neon-teal", bg: "bg-teal-500/10", border: "border-teal-500/20", stroke: "#14b8a6" };
    if (aqi <= 100) return { color: "text-yellow-400", bg: "bg-yellow-500/10", border: "border-yellow-500/20", stroke: "#facc15" };
    if (aqi <= 200) return { color: "text-orange-500", bg: "bg-orange-500/10", border: "border-orange-500/20", stroke: "#f97316" };
    return { color: "text-neon-red", bg: "bg-red-500/10", border: "border-red-500/20", stroke: "#ef4444" };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-void flex items-center justify-center text-slate-400">
        <div className="animate-pulse flex flex-col items-center">
          <Activity className="w-10 h-10 mb-4 text-neon-teal" />
          <p>Analyzing Atmospheric Conditions...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-void flex items-center justify-center text-red-400">
        <div className="text-center p-6 border border-red-500/20 bg-red-500/10 rounded-2xl">
          <AlertTriangle className="w-10 h-10 mb-2 mx-auto" />
          <p>Critical System Error</p>
          <p className="text-sm text-slate-400 mt-2">{error}</p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  // Transform API data to Component state
  const currentRisk = data.risk_assessment.level;
  const theme = getTheme(data.current_aqi.value);

  const formattedPollutants = Object.entries(data.pollutants).map(([key, info]) => ({
    id: key,
    name: POLLUTANT_CONFIG[key]?.name || key.toUpperCase(),
    value: info.value,
    unit: POLLUTANT_CONFIG[key]?.unit || '',
    trend: info.trend,
    isDominant: false // Logic could be added here to find max value
  }));

  // Simple dominant logic: highest value pollutant
  const maxVal = Math.max(...formattedPollutants.map(p => p.value));
  formattedPollutants.forEach(p => p.isDominant = p.value === maxVal);


  return (
    <div className="min-h-screen bg-void text-slate-300 pb-10">

      <main className="container mx-auto px-4 pt-6 grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* --- LEFT COLUMN: CONTROLS --- */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }} /* Changed to animate to ensure it plays on load? whileInView is safer usually but animate works on mount */
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="lg:col-span-3 space-y-6"
        >
          {/* Location Selector */}
          <div className="glass-panel p-5 rounded-2xl">
            <div className="flex items-center justify-between mb-4">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Select Region</label>
              <span className="text-[10px] bg-white/5 px-2 py-0.5 rounded text-slate-400 font-mono">
                {data.location?.lat?.toFixed(2) || selectedLocation.lat.toFixed(2)}, {data.location?.lon?.toFixed(2) || selectedLocation.lon.toFixed(2)}
              </span>
            </div>

            {/* Search Input */}
            <div className="relative mb-3">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 w-4 h-4" />
              <input
                type="text"
                placeholder="Search city..."
                className="w-full bg-black/20 border border-white/10 rounded-lg pl-9 pr-3 py-2 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-neon-teal focus:ring-1 focus:ring-neon-teal/50 transition-all"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <div className="space-y-2 max-h-[200px] overflow-y-auto pr-1 custom-scrollbar">
              {filteredLocations.length > 0 ? (
                filteredLocations.map(loc => (
                  <button
                    key={loc.id}
                    onClick={() => {
                      setSelectedLocation(loc);
                      setSearchTerm("");
                    }}
                    className={`w-full flex items-center justify-between px-4 py-3 rounded-lg text-sm transition-all ${selectedLocation.id === loc.id
                      ? 'bg-neon-teal/10 text-neon-teal border border-neon-teal/20 shadow-[0_0_15px_-5px_rgba(20,184,166,0.3)]'
                      : 'hover:bg-white/5 text-slate-400'
                      }`}
                  >
                    <span className="flex items-center gap-2">
                      <MapPin size={14} /> {loc.name}
                    </span>
                    {selectedLocation.id === loc.id && <div className="h-2 w-2 rounded-full bg-neon-teal animate-pulse" />}
                  </button>
                ))
              ) : (
                <div className="text-center py-4 text-xs text-slate-600 italic">
                  No locations found.
                </div>
              )}
            </div>
          </div>

          {/* Persona Selector */}
          <div className="glass-panel p-5 rounded-2xl">
            <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 block">Health Profile</label>
            <div className="flex flex-col gap-2">
              {PERSONAS.map(p => (
                <button
                  key={p.id}
                  onClick={() => setSelectedPersona(p.id)}
                  className={`relative flex items-center gap-3 px-4 py-3 rounded-lg transition-all border ${selectedPersona === p.id
                    ? 'bg-indigo-500/20 border-indigo-500/30 text-white'
                    : 'border-transparent hover:bg-white/5 text-slate-500'
                    }`}
                >
                  <p.icon size={18} className={selectedPersona === p.id ? 'text-indigo-400' : 'text-slate-600'} />
                  <span className="text-sm font-medium">{p.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Weather Context */}
          <div className="glass-panel p-5 rounded-2xl">
            <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4 block flex items-center gap-2">
              <Wind size={12} /> Local Conditions
            </label>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-white/5 rounded-xl border border-white/5 flex flex-col items-center text-center">
                <Wind className="w-5 h-5 text-slate-400 mb-2" />
                <span className="text-lg font-bold text-white">{data.weather.wind_speed} <span className="text-xs font-normal">km/h</span></span>
                <span className="text-[10px] text-slate-500 uppercase">Wind</span>
              </div>
              <div className="p-3 bg-white/5 rounded-xl border border-white/5 flex flex-col items-center text-center">
                <Droplets className="w-5 h-5 text-blue-400 mb-2" />
                <span className="text-lg font-bold text-white">{data.weather.humidity} <span className="text-xs font-normal">%</span></span>
                <span className="text-[10px] text-slate-500 uppercase">Humidity</span>
              </div>
              <div className="p-3 bg-white/5 rounded-xl border border-white/5 flex flex-col items-center text-center">
                <Thermometer className="w-5 h-5 text-orange-400 mb-2" />
                <span className="text-lg font-bold text-white">{data.weather.temp} <span className="text-xs font-normal">°C</span></span>
                <span className="text-[10px] text-slate-500 uppercase">Temp</span>
              </div>
              <div className="p-3 bg-white/5 rounded-xl border border-white/5 flex flex-col items-center text-center">
                <Gauge className="w-5 h-5 text-purple-400 mb-2" />
                <span className="text-lg font-bold text-white leading-tight">{data.weather.pressure} <span className="text-xs font-normal">hPa</span></span>
                <span className="text-[10px] text-slate-500 uppercase">Pressure</span>
              </div>
            </div>
          </div>
        </motion.div>


        {/* --- MIDDLE COLUMN: CORE METRICS --- */}
        <div className="lg:col-span-6 space-y-6">

          {/* A. Real-Time AQI Card */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className={`relative overflow-hidden rounded-3xl p-8 border ${theme.border} ${theme.bg} backdrop-blur-xl shadow-2xl`}
          >
            <div className="relative z-10 flex flex-col md:flex-row justify-between gap-8">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-black/40 backdrop-blur-md border border-white/10 ${theme.color}`}>
                    <AlertTriangle size={12} /> {currentRisk} Risk
                  </span>
                  <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                    <CheckCircle size={10} /> UPDATED {new Date(data.current_aqi.updated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <div className="flex items-baseline gap-2">
                  <h2 className={`text-8xl font-display font-bold text-white tracking-tighter drop-shadow-lg`}>
                    {data.current_aqi.value}
                  </h2>
                  <span className="text-xl font-medium text-slate-400">AQI</span>
                </div>
              </div>

              {/* B. Dynamic Health Risk & Advice */}
              <div className="flex-1 bg-black/20 backdrop-blur-md rounded-2xl p-5 border border-white/10 flex flex-col justify-center">
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-xl bg-black/40 ${theme.color}`}>
                    <ShieldCheck size={24} />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-1">Health Advisory</p>
                    <p className="text-sm text-white font-medium leading-relaxed">
                      {data.risk_assessment.recommendation}
                    </p>
                    <div className="mt-3 pt-3 border-t border-white/5 text-[10px] text-slate-500 flex items-center gap-1">
                      <Info size={10} /> Aligned with {data.risk_assessment.standard_aligned || 'WHO'} Standards
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Decorative BG */}
            <div className="absolute -right-10 -top-10 opacity-10 pointer-events-none mix-blend-overlay">
              <Wind size={250} className="text-white" />
            </div>
          </motion.div>

          {/* D. Primary Pollutants Grid */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="grid grid-cols-2 md:grid-cols-3 gap-4"
          >
            {formattedPollutants.map((pollutant) => (
              <div
                key={pollutant.id}
                className={`glass-panel p-4 rounded-2xl border ${pollutant.isDominant ? 'border-indigo-500/50 bg-indigo-500/10' : 'border-white/5'}`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className={`text-sm font-bold ${pollutant.isDominant ? 'text-indigo-300' : 'text-slate-400'}`}>
                    {pollutant.name}
                  </span>
                  {pollutant.isDominant && <span className="text-[10px] bg-indigo-500 text-white px-1.5 py-0.5 rounded">Major</span>}
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-2xl font-display font-bold text-white">{pollutant.value}</span>
                  <span className="text-[10px] text-slate-500">{pollutant.unit}</span>
                </div>
                <div className={`flex items-center gap-1 mt-2 text-xs font-medium ${pollutant.trend === 'up' ? 'text-red-400' : pollutant.trend === 'down' ? 'text-green-400' : 'text-slate-500'}`}>
                  {pollutant.trend === 'up' && <ChevronUp size={12} />}
                  {pollutant.trend === 'down' && <ChevronDown size={12} />}
                  {pollutant.trend === 'flat' && <span>•</span>}
                  <span className="capitalize">{pollutant.trend}</span>
                </div>
              </div>
            ))}
          </motion.div>

          {/* F. 6-Hour Forecast Timeline */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="glass-panel p-6 rounded-2xl"
          >
            <h3 className="text-sm font-semibold text-slate-300 mb-6 flex items-center gap-2">
              <Activity size={16} className={theme.color} /> 6-Hour Forecast Trend
            </h3>
            <div className="h-[180px] w-full min-h-[180px]">
              {data.forecast_6h && data.forecast_6h.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data.forecast_6h}>
                    <defs>
                      <linearGradient id="colorAqi" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={theme.stroke} stopOpacity={0.3} />
                        <stop offset="95%" stopColor={theme.stroke} stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="time" stroke="#64748b" fontSize={10} axisLine={false} tickLine={false} />
                    <YAxis stroke="#64748b" fontSize={10} axisLine={false} tickLine={false} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#020617', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px' }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Area type="monotone" dataKey="aqi" stroke={theme.stroke} fill="url(#colorAqi)" strokeWidth={3} />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full w-full flex items-center justify-center text-slate-500 text-xs">
                  Forecast data unavailable
                </div>
              )}
            </div>
          </motion.div>

        </div>


        {/* --- RIGHT COLUMN: ADVANCED INSIGHTS --- */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="lg:col-span-3 space-y-6"
        >
          {/* Hyper-Local Heatmap Simulator */}
          <div className="glass-panel p-1 rounded-2xl h-64 relative overflow-hidden group">
            <CityHeatmap
              lat={data.location.lat}
              lon={data.location.lon}
              aqi={data.current_aqi.value}
            />
          </div>

          {/* C. Human-Readable AI Insight */}
          <div className="bg-gradient-to-br from-indigo-900/20 to-void glass-panel p-6 rounded-2xl relative overflow-hidden border-l-4 border-indigo-500">
            <div className="flex items-start gap-4">
              <div className="bg-indigo-500/20 p-2.5 rounded-xl">
                <BrainCircuit className="w-6 h-6 text-indigo-400" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white mb-2">AI Analysis</h4>
                <p className="text-xs text-indigo-200/90 leading-relaxed mb-4">
                  {data.risk_assessment.ai_explanation}
                </p>

                <div className="space-y-2">
                  <div className="flex flex-wrap gap-2">
                    {data.risk_assessment.contributing_factors.map((factor, i) => (
                      <span key={i} className="text-[10px] font-medium px-2 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 rounded-md">
                        {factor}
                      </span>
                    ))}
                  </div>
                  <p className="text-[10px] text-slate-500 mt-2">
                    Context: <span className="text-slate-300">{data.risk_assessment.context}</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

      </main>
    </div>
  );
}