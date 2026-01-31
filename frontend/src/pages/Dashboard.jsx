import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";
import {
  MapPin, Wind, AlertTriangle, Info, BrainCircuit, Activity, User, ShieldCheck, HeartPulse, Droplets, Thermometer, Gauge, ChevronUp, ChevronDown, CheckCircle, Search
} from "lucide-react";

// --- Comprehensive Mock Data Infrastructure ---

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

// 3. Main Data Store keyed by Location ID
const MOCK_DB = {
  delhi: {
    aqi: { value: 342, category: 'Hazardous', lastUpdated: '10 mins ago' },
    pollutants: [
      { id: 'pm25', name: 'PM2.5', value: 184, unit: 'µg/m³', trend: 'up', isDominant: true },
      { id: 'pm10', name: 'PM10', value: 240, unit: 'µg/m³', trend: 'up' },
      { id: 'no2', name: 'NO2', value: 45, unit: 'ppb', trend: 'stable' },
      { id: 'o3', name: 'O3', value: 12, unit: 'ppb', trend: 'down' },
      { id: 'so2', name: 'SO2', value: 8, unit: 'ppb', trend: 'stable' },
      { id: 'co', name: 'CO', value: 1.2, unit: 'ppm', trend: 'up' }, // Added CO here
    ],
    weather: { wind: '4 km/h', humidity: '42%', temp: '32°C', pressure: '1012 hPa' },
    aiInsight: {
      cause: "AQI is spiking due to crop burning in neighboring regions combined with static wind speeds.",
      factors: ["Stubble Burning", "Low Wind Speed", "Temperature Inversion"],
      context: "Persistent",
    },
    forecast: [
      { time: 'Now', aqi: 342, risk: 'Hazardous' },
      { time: '+1h', aqi: 350, risk: 'Hazardous' },
      { time: '+2h', aqi: 355, risk: 'Hazardous' },
      { time: '+3h', aqi: 340, risk: 'Hazardous' },
      { time: '+4h', aqi: 330, risk: 'Hazardous' },
      { time: '+5h', aqi: 310, risk: 'Very Unhealthy' },
    ],
    healthAdvice: {
      general: "Avoid all outdoor physical activity. Wear N95 masks if travel is essential.",
      vulnerable: "CRITICAL: Stay indoors. Seal windows and run air purifiers on high mode.",
      outdoor: "Suspend all outdoor work immediately. Exposure can lead to acute repository distress."
    }
  },
  mumbai: {
    aqi: { value: 156, category: 'Unhealthy', lastUpdated: '2 mins ago' },
    pollutants: [
      { id: 'pm25', name: 'PM2.5', value: 68, unit: 'µg/m³', trend: 'down', isDominant: true },
      { id: 'pm10', name: 'PM10', value: 110, unit: 'µg/m³', trend: 'stable' },
      { id: 'no2', name: 'NO2', value: 32, unit: 'ppb', trend: 'up' },
      { id: 'o3', name: 'O3', value: 28, unit: 'ppb', trend: 'stable' },
      { id: 'so2', name: 'SO2', value: 5, unit: 'ppb', trend: 'down' },
      { id: 'co', name: 'CO', value: 0.8, unit: 'ppm', trend: 'stable' },
    ],
    weather: { wind: '12 km/h', humidity: '78%', temp: '29°C', pressure: '1008 hPa' },
    aiInsight: {
      cause: "Moderate pollution levels due to coastal humidity trapping vehicular emissions.",
      factors: ["High Humidity", "Evening Traffic"],
      context: "Temporary",
    },
    forecast: [
      { time: 'Now', aqi: 156, risk: 'Unhealthy' },
      { time: '+1h', aqi: 145, risk: 'Unhealthy for Sensitive' },
      { time: '+2h', aqi: 130, risk: 'Unhealthy for Sensitive' },
      { time: '+3h', aqi: 120, risk: 'Unhealthy for Sensitive' },
      { time: '+4h', aqi: 115, risk: 'Moderate' },
      { time: '+5h', aqi: 110, risk: 'Moderate' },
    ],
    healthAdvice: {
      general: "Reduce prolonged or heavy exertion. Take breaks during outdoor activity.",
      vulnerable: "Sensitive groups should move activities indoors.",
      outdoor: "Limit intense activities. Watch for symptoms like coughing."
    }
  },
  bangalore: {
    aqi: { value: 42, category: 'Good', lastUpdated: 'Just now' },
    pollutants: [
      { id: 'pm25', name: 'PM2.5', value: 12, unit: 'µg/m³', trend: 'stable', isDominant: false },
      { id: 'pm10', name: 'PM10', value: 25, unit: 'µg/m³', trend: 'stable' },
      { id: 'no2', name: 'NO2', value: 10, unit: 'ppb', trend: 'down' },
      { id: 'o3', name: 'O3', value: 30, unit: 'ppb', trend: 'up', isDominant: true },
      { id: 'so2', name: 'SO2', value: 2, unit: 'ppb', trend: 'stable' },
      { id: 'co', name: 'CO', value: 0.4, unit: 'ppm', trend: 'stable' },
    ],
    weather: { wind: '15 km/h', humidity: '55%', temp: '24°C', pressure: '1015 hPa' },
    aiInsight: {
      cause: "Air quality is pristine thanks to strong dispersion winds and recent rainfall.",
      factors: ["Precipitation", "Good Ventilation"],
      context: "Stable",
    },
    forecast: [
      { time: 'Now', aqi: 42, risk: 'Good' },
      { time: '+1h', aqi: 45, risk: 'Good' },
      { time: '+2h', aqi: 48, risk: 'Good' },
      { time: '+3h', aqi: 50, risk: 'Moderate' },
      { time: '+4h', aqi: 52, risk: 'Moderate' },
      { time: '+5h', aqi: 55, risk: 'Moderate' },
    ],
    healthAdvice: {
      general: "Great day to be outdoors.",
      vulnerable: "No specific restrictions.",
      outdoor: "Ideal conditions for training or work."
    }
  }
};


export default function Dashboard() {
  const [selectedLocation, setSelectedLocation] = useState(LOCATIONS[0]);
  const [selectedPersona, setSelectedPersona] = useState(PERSONAS[0].id);
  const [searchTerm, setSearchTerm] = useState("");

  const filteredLocations = useMemo(() => {
    if (!searchTerm) return LOCATIONS;
    return LOCATIONS.filter(loc => loc.name.toLowerCase().includes(searchTerm.toLowerCase()));
  }, [searchTerm]);

  // Derived Data
  const currentData = MOCK_DB[selectedLocation.id];
  const derivedRisk = currentData.aqi.category; // Simple mapping for now

  // Helper for dynamic colors
  const getTheme = (aqi) => {
    if (aqi <= 50) return { color: "text-neon-teal", bg: "bg-teal-500/10", border: "border-teal-500/20", stroke: "#14b8a6" };
    if (aqi <= 100) return { color: "text-yellow-400", bg: "bg-yellow-500/10", border: "border-yellow-500/20", stroke: "#facc15" };
    if (aqi <= 200) return { color: "text-orange-500", bg: "bg-orange-500/10", border: "border-orange-500/20", stroke: "#f97316" };
    return { color: "text-neon-red", bg: "bg-red-500/10", border: "border-red-500/20", stroke: "#ef4444" };
  };

  const theme = getTheme(currentData.aqi.value);

  return (
    <div className="min-h-screen bg-void text-slate-300 pb-10">

      <main className="container mx-auto px-4 pt-6 grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* --- LEFT COLUMN: CONTROLS --- */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
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
                {selectedLocation.lat.toFixed(2)}, {selectedLocation.lon.toFixed(2)}
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
                      setSearchTerm(""); // Optional: clear search on select
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
                <span className="text-lg font-bold text-white">{currentData.weather.wind}</span>
                <span className="text-[10px] text-slate-500 uppercase">Wind</span>
              </div>
              <div className="p-3 bg-white/5 rounded-xl border border-white/5 flex flex-col items-center text-center">
                <Droplets className="w-5 h-5 text-blue-400 mb-2" />
                <span className="text-lg font-bold text-white">{currentData.weather.humidity}</span>
                <span className="text-[10px] text-slate-500 uppercase">Humidity</span>
              </div>
              <div className="p-3 bg-white/5 rounded-xl border border-white/5 flex flex-col items-center text-center">
                <Thermometer className="w-5 h-5 text-orange-400 mb-2" />
                <span className="text-lg font-bold text-white">{currentData.weather.temp}</span>
                <span className="text-[10px] text-slate-500 uppercase">Temp</span>
              </div>
              <div className="p-3 bg-white/5 rounded-xl border border-white/5 flex flex-col items-center text-center">
                <Gauge className="w-5 h-5 text-purple-400 mb-2" />
                <span className="text-lg font-bold text-white leading-tight">{currentData.weather.pressure}</span>
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
                    <AlertTriangle size={12} /> {derivedRisk} Risk
                  </span>
                  <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                    <CheckCircle size={10} /> UPDATED {currentData.aqi.lastUpdated.toUpperCase()}
                  </span>
                </div>
                <div className="flex items-baseline gap-2">
                  <h2 className={`text-8xl font-display font-bold text-white tracking-tighter drop-shadow-lg`}>
                    {currentData.aqi.value}
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
                      {currentData.healthAdvice[selectedPersona]}
                    </p>
                    <div className="mt-3 pt-3 border-t border-white/5 text-[10px] text-slate-500 flex items-center gap-1">
                      <Info size={10} /> Aligned with WHO Standards
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
            {currentData.pollutants.map((pollutant) => (
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
                  {pollutant.trend === 'stable' && <span>•</span>}
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
            <div className="h-[180px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={currentData.forecast}>
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
            <div className="absolute inset-0 bg-slate-900" />
            <div className={`absolute inset-0 opacity-60 bg-[radial-gradient(circle_at_50%_50%,${theme.stroke}00,transparent_70%)] group-hover:opacity-100 transition-opacity`} />
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_40%_60%,rgba(20,184,166,0.2),rgba(2,6,23,0)_60%)] animate-pulse" />

            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none z-10">
              <div className="w-12 h-12 rounded-full border border-white/20 bg-black/40 backdrop-blur-md flex items-center justify-center mb-2">
                <MapPin className="text-white w-6 h-6" />
              </div>
              <p className="text-xs font-medium text-white tracking-widest uppercase">Live Heatmap</p>
            </div>
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
                  {currentData.aiInsight.cause}
                </p>

                <div className="space-y-2">
                  <div className="flex flex-wrap gap-2">
                    {currentData.aiInsight.factors.map((factor, i) => (
                      <span key={i} className="text-[10px] font-medium px-2 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 rounded-md">
                        {factor}
                      </span>
                    ))}
                  </div>
                  <p className="text-[10px] text-slate-500 mt-2">
                    Context: <span className="text-slate-300">{currentData.aiInsight.context}</span>
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