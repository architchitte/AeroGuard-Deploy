import { useState, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Circle,
  CircleMarker,
  Tooltip,
  useMap
} from "react-leaflet";
import { useNavigate } from "react-router-dom";
import "leaflet/dist/leaflet.css";
import {
  Maximize,
  ZoomIn,
  Globe,
  Wind,
  Droplets,
  CloudRain,
  Activity,
  ChevronRight,
  ChevronLeft,
  X,
  MapPin,
  TrendingUp
} from "lucide-react";

import LocationSearch from "../Components/LocationSelector";
import { fetchAQI, fetchMapData } from "../api/aqi";
import HeatmapLayer from "./HeatmapLayer";  // Custom heatmap component


/* ================= MAP CONTROLLER ================= */

function MapController({ center, zoom }) {
  const map = useMap();

  useEffect(() => {
    if (!center) return;
    map.flyTo(center, zoom, { animate: true, duration: 1.5 });
  }, [center, zoom, map]);

  return null;
}

/* ================= AQI HELPERS ================= */

const getAQIColor = (aqi) => {
  if (aqi <= 50) return "#14b8a6";
  if (aqi <= 100) return "#facc15";
  if (aqi <= 150) return "#f97316";
  if (aqi <= 200) return "#ef4444";
  if (aqi <= 300) return "#7f1d1d";
  return "#450a0a";
};

const getAQILabel = (aqi) => {
  if (aqi <= 50) return "Good";
  if (aqi <= 100) return "Moderate";
  if (aqi <= 150) return "Unhealthy for Sensitive Groups";
  if (aqi <= 200) return "Unhealthy";
  if (aqi <= 300) return "Very Unhealthy";
  return "Hazardous";
}

/* ================= CONSTANTS ================= */

const FAMOUS_PLACES = [
  // Major Metros
  { name: "New Delhi", lat: 28.6139, lon: 77.2090 },
  { name: "Mumbai", lat: 19.0760, lon: 72.8777 },
  { name: "Bengaluru", lat: 12.9716, lon: 77.5946 },
  { name: "Hyderabad", lat: 17.3850, lon: 78.4867 },
  { name: "Chennai", lat: 13.0827, lon: 80.2707 },
  { name: "Kolkata", lat: 22.5726, lon: 88.3639 },
  { name: "Pune", lat: 18.5204, lon: 73.8567 },
  { name: "Ahmedabad", lat: 23.0225, lon: 72.5714 },

  // State Capitals & Major Support
  { name: "Amaravati", lat: 16.57, lon: 80.37 },
  { name: "Itanagar", lat: 27.06, lon: 93.61 },
  { name: "Dispur", lat: 26.14, lon: 91.78 },
  { name: "Patna", lat: 25.59, lon: 85.14 },
  { name: "Raipur", lat: 21.25, lon: 81.63 },
  { name: "Panaji", lat: 15.49, lon: 73.82 },
  { name: "Gandhinagar", lat: 23.22, lon: 72.65 },
  { name: "Chandigarh", lat: 30.73, lon: 76.78 },
  { name: "Shimla", lat: 31.10, lon: 77.17 },
  { name: "Ranchi", lat: 23.34, lon: 85.30 },
  { name: "Thiruvananthapuram", lat: 8.52, lon: 76.94 },
  { name: "Bhopal", lat: 23.26, lon: 77.41 },
  { name: "Imphal", lat: 24.81, lon: 93.95 },
  { name: "Shillong", lat: 25.57, lon: 91.88 },
  { name: "Aizawl", lat: 23.73, lon: 92.72 },
  { name: "Kohima", lat: 25.67, lon: 94.11 },
  { name: "Bhubaneswar", lat: 20.27, lon: 85.82 },
  { name: "Jaipur", lat: 26.92, lon: 75.78 },
  { name: "Gangtok", lat: 27.33, lon: 88.61 },
  { name: "Agartala", lat: 23.83, lon: 91.27 },
  { name: "Lucknow", lat: 26.85, lon: 80.95 },
  { name: "Dehradun", lat: 30.32, lon: 78.03 },
  { name: "Srinagar", lat: 34.08, lon: 74.79 },
  { name: "Leh", lat: 34.17, lon: 77.58 },
  { name: "Visakhapatnam", lat: 17.68, lon: 83.22 },
  { name: "Kanpur", lat: 26.45, lon: 80.33 },
  { name: "Nagpur", lat: 21.15, lon: 79.08 },
  { name: "Surat", lat: 21.17, lon: 72.83 }
];

/* ================= MAIN ================= */

export default function PollutionHeatmap({ externalLocation, onLocationSelect }) {
  const INDIA_CENTER = [22.3511, 78.6677];
  const navigate = useNavigate();

  const [location, setLocation] = useState(externalLocation || null);
  const [center, setCenter] = useState(INDIA_CENTER);
  const [zoom, setZoom] = useState(5);
  const [isPanelOpen, setIsPanelOpen] = useState(true);
  const [lastSync, setLastSync] = useState(new Date());
  const [hubData, setHubData] = useState([]);

  // Sync with external location if provided
  useEffect(() => {
    if (externalLocation) {
      setLocation(externalLocation);
      setCenter([externalLocation.lat, externalLocation.lon]);
      setZoom(10);
      setIsPanelOpen(true);
    }
  }, [externalLocation]);

  const [aqi, setAqi] = useState(null);
  const [stations, setStations] = useState([]);
  const [loadingStations, setLoadingStations] = useState(false);
  const color = getAQIColor(aqi ?? 0);

  // 1. Fetch Nationwide & Hub Data
  const loadData = async () => {
    try {
      setLoadingStations(true);
      const [mapData, ...hubs] = await Promise.all([
        fetchMapData(),
        ...FAMOUS_PLACES.map(p => fetchAQI(p.lat, p.lon).catch(() => null))
      ]);

      setStations(mapData);
      setHubData(FAMOUS_PLACES.map((p, i) => ({ ...p, aqi: hubs[i]?.aqi || 100 })));
      setLastSync(new Date());
    } catch (err) {
      console.error("Data sync failed:", err);
    } finally {
      setLoadingStations(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5 * 60 * 1000); // Poll every 5 mins
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!location) return;

    const loadAQI = async () => {
      try {
        const data = await fetchAQI(location.lat, location.lon);
        setAqi(data.aqi);
      } catch (err) {
        console.error("AQI fetch failed:", err);
      }
    };

    loadAQI();
  }, [location]);

  /* -------- SEARCH -------- */
  const handleLocationSelect = (loc) => {
    setLocation(loc);
    setCenter([loc.lat, loc.lon]);
    setZoom(11);
    setIsPanelOpen(true);
    if (onLocationSelect) onLocationSelect(loc);
  };

  /* -------- ZOOM PRESETS -------- */
  const handleZoomPreset = (type) => {
    if (type === "country") {
      setCenter(INDIA_CENTER);
      setZoom(5);
      return;
    }
    if (!location) return;
    const locCenter = [location.lat, location.lon];
    if (type === "city") {
      setCenter(locCenter);
      setZoom(10);
    }
    if (type === "region") {
      setCenter(locCenter);
      setZoom(7);
    }
  };

  /* -------- DATA PREP -------- */
  const heatmapPoints = stations.map((s) => ({
    lat: s.lat,
    lng: s.lon,
    value: Math.min(s.aqi, 500),
  }));

  const pollutants = location ? [
    { name: "PM2.5", value: "76", unit: "µg/m³", icon: Droplets, color: "text-emerald-400" },
    { name: "PM10", value: "85", unit: "µg/m³", icon: Wind, color: "text-yellow-400" },
    { name: "NO2", value: "40", unit: "ppb", icon: CloudRain, color: "text-blue-400" },
    { name: "O3", value: "12", unit: "ppb", icon: Wind, color: "text-cyan-400" },
  ] : [];

  return (
    <div className="relative w-full h-[850px] bg-[#020617] rounded-[3rem] border border-white/5 shadow-2xl overflow-hidden group/map-section ring-1 ring-white/10">

      {/* ================= MAP Container ================= */}
      <MapContainer
        center={center}
        zoom={zoom}
        zoomControl={false}
        style={{ height: "100%", width: "100%" }}
        className="z-0"
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; CARTO'
        />

        <MapController center={center} zoom={zoom} />

        {/* ================= SELECTION GRADIENT EFFECT ================= */}
        {location && (
          <>
            <Circle
              center={[location.lat, location.lon]}
              radius={20000}
              pathOptions={{
                fillColor: getAQIColor(aqi || 100),
                fillOpacity: 0.05,
                stroke: false
              }}
            />
            <Circle
              center={[location.lat, location.lon]}
              radius={10000}
              pathOptions={{
                fillColor: getAQIColor(aqi || 100),
                fillOpacity: 0.1,
                stroke: false
              }}
            />
            <Circle
              center={[location.lat, location.lon]}
              radius={3000}
              pathOptions={{
                fillColor: getAQIColor(aqi || 100),
                fillOpacity: 0.2,
                color: getAQIColor(aqi || 100),
                weight: 2,
                dashArray: "5, 10"
              }}
            />
          </>
        )}

        {/* HEATMAP LAYER (Intensified) */}
        {heatmapPoints.length > 0 && (
          <HeatmapLayer
            points={heatmapPoints}
            options={{
              radius: 110,
              blur: 60,
              max: 250,
              minOpacity: 0.2,
              gradient: {
                0.1: '#0ea5e9', // Deep Sky Blue (Low)
                0.2: '#14b8a6', // Teal
                0.4: '#facc15', // Yellow
                0.6: '#f97316', // Orange
                0.8: '#ef4444', // Red
                1.0: '#7f1d1d'  // Dark Red
              }
            }}
          />
        )}

        {/* FAMOUS PLACE HUBS */}
        {hubData.map((hub) => (
          <CircleMarker
            key={`hub-${hub.name}`}
            center={[hub.lat, hub.lon]}
            radius={zoom > 6 ? 12 : 8}
            pathOptions={{
              fillColor: getAQIColor(hub.aqi),
              fillOpacity: 0.9,
              color: "#fff",
              weight: 2,
              className: "hub-marker-pulse"
            }}
            eventHandlers={{
              click: () => handleLocationSelect({ name: hub.name, lat: hub.lat, lon: hub.lon })
            }}
          >
            <Tooltip permanent={zoom > 6} direction="top" offset={[0, -10]} className="hub-tooltip">
              <div className="flex flex-col items-center bg-slate-950/80 p-2 rounded-lg border border-white/10 backdrop-blur-md">
                <span className="text-[12px] font-black" style={{ color: getAQIColor(hub.aqi) }}>{hub.aqi}</span>
              </div>
            </Tooltip>
          </CircleMarker>
        ))}

        {/* STATION MARKERS (Secondary) */}
        {stations.length > 0 && stations.filter(s => !FAMOUS_PLACES.some(p => p.name === s.station)).map((s) => (
          <CircleMarker
            key={s.uid || `${s.lat}-${s.lon}`}
            center={[s.lat, s.lon]}
            radius={zoom > 7 ? 6 : 3}
            pathOptions={{
              fillColor: getAQIColor(s.aqi),
              fillOpacity: 0.8,
              color: "#fff",
              weight: 1,
            }}
            eventHandlers={{
              click: () => handleLocationSelect({ name: s.station, lat: s.lat, lon: s.lon })
            }}
          >
            <Tooltip sticky className="marker-tooltip">
              <div className="p-2 text-xs font-bold text-white bg-slate-950/90 border border-white/10 rounded-lg backdrop-blur-md">
                {s.station}: <span style={{ color: getAQIColor(s.aqi) }}>{s.aqi}</span>
              </div>
            </Tooltip>
          </CircleMarker>
        ))}
      </MapContainer>

      {/* ================= FLOATING OVERLAYS ================= */}

      {/* 1. TOP-LEFT: SEARCH OVERLAY */}
      <div className="absolute top-8 left-8 z-[1000] w-[340px] animate-slide-right">
        <div className="glass-panel p-1 rounded-2xl border border-white/10 shadow-2xl transition-all duration-300 focus-within:border-teal-500/50 hover:border-white/20">
          <LocationSearch onSelect={handleLocationSelect} />
        </div>
      </div>

      {/* 2. CENTER-LEFT: DATA PANEL */}
      {location && (
        <div className={`absolute top-24 left-8 z-[900] transition-all duration-500 ease-in-out ${isPanelOpen ? 'translate-x-0 opacity-100' : '-translate-x-[110%] opacity-0'}`}>
          <div className="w-[360px] glass-panel rounded-[2.5rem] border border-white/10 shadow-2xl overflow-hidden backdrop-blur-3xl bg-slate-950/60 p-8 space-y-8">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <p className="text-[10px] font-black uppercase text-slate-500 tracking-widest flex items-center gap-2">
                  <MapPin size={10} className="text-teal-400" /> Current Station
                </p>
                <h3 className="text-2xl font-black text-white leading-tight">{location.name}</h3>
                <p className="text-slate-400 text-xs font-medium">Regional Air Intelligence</p>
              </div>
              <button
                onClick={() => setIsPanelOpen(false)}
                className="p-2 rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
                title="Close Panel"
              >
                <X size={16} className="text-slate-500" />
              </button>
            </div>

            <div className="flex items-center justify-between gap-6 py-6 border-y border-white/5">
              <div className="space-y-1">
                <span className="text-7xl font-black text-white leading-none tracking-tighter">
                  {aqi ?? '--'}
                </span>
                <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">AQI Index</p>
              </div>
              <div className="flex flex-col gap-2 flex-1">
                <div
                  className="px-4 py-2 rounded-xl text-[10px] font-black uppercase text-center shadow-lg transition-colors border tracking-wider"
                  style={{
                    backgroundColor: `${getAQIColor(aqi ?? 0)}20`,
                    borderColor: `${getAQIColor(aqi ?? 0)}40`,
                    color: getAQIColor(aqi ?? 0)
                  }}
                >
                  {getAQILabel(aqi ?? 0)}
                </div>
                <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="h-full transition-all duration-1000"
                    style={{
                      width: `${Math.min(100, (aqi / 300) * 100)}%`,
                      backgroundColor: getAQIColor(aqi ?? 0),
                      boxShadow: `0 0 10px ${getAQIColor(aqi ?? 0)}`
                    }}
                  />
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <p className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Key Pollutants</p>
              <div className="grid grid-cols-2 gap-3">
                {pollutants.map((p) => (
                  <div key={p.name} className="p-4 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-all group/p">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-[10px] uppercase text-slate-500 font-bold">{p.name}</p>
                      <p.icon size={12} className="text-slate-600 group-hover/p:text-teal-400" />
                    </div>
                    <div className="flex items-baseline gap-1">
                      <span className="text-lg font-black text-white">{p.value}</span>
                      <span className="text-[10px] text-slate-500 font-bold">{p.unit}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-5 rounded-3xl bg-gradient-to-br from-teal-500/10 via-emerald-500/5 to-transparent border border-teal-500/20">
              <div className="flex items-center gap-2 mb-2">
                <Activity size={12} className="text-teal-400 animate-pulse" />
                <span className="text-[10px] font-black uppercase text-teal-400 tracking-widest">AI Health Pulse</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed italic mb-4">
                "Safe for most outdoor activities in your area today."
              </p>

              <button
                onClick={() => navigate('/dashboard', { state: { selectedLocation: location } })}
                className="w-full py-3 bg-teal-500/10 hover:bg-teal-500/20 border border-teal-500/30 rounded-2xl text-teal-400 text-[10px] font-black uppercase tracking-[0.2em] transition-all flex items-center justify-center gap-2"
              >
                Get Detailed Analysis
                <ChevronRight size={12} />
              </button>
            </div>
          </div>
        </div>
      )}

      {location && !isPanelOpen && (
        <button
          onClick={() => setIsPanelOpen(true)}
          className="absolute top-24 left-8 z-[1000] p-4 bg-slate-950/80 backdrop-blur-xl border border-white/10 rounded-2xl text-teal-400 hover:scale-110 transition-all animate-slide-right shadow-2xl hover:border-teal-500/50"
        >
          <ChevronRight size={20} />
        </button>
      )}

      {/* 3. BOTTOM-LEFT: STATUS */}
      <div className="absolute bottom-8 left-8 z-[400]">
        <div className="flex items-center gap-3 px-5 py-2.5 rounded-full bg-slate-900/90 backdrop-blur-xl border border-white/10 shadow-2xl group/status hover:border-teal-500/30 transition-all">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.5)]" />
          <span className="text-[10px] font-bold text-white uppercase tracking-[0.2em]">AeroGrid Live</span>
          <div className="w-[1px] h-3 bg-white/10 mx-1" />
          <span className="text-[10px] font-bold text-slate-500 uppercase group-hover:text-teal-400 transition-colors">
            Last Sync: {lastSync.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </div>

      {/* 4. BOTTOM-RIGHT: CONTROLS */}
      <div className="absolute bottom-8 right-8 z-[400] flex flex-col items-end gap-6">
        <div className="flex bg-slate-900/60 backdrop-blur-2xl p-1.5 rounded-2xl border border-white/10 shadow-2xl group/presets ring-1 ring-white/5">
          {[
            { id: 'city', icon: Maximize, label: 'City' },
            { id: 'region', icon: ZoomIn, label: 'Region' },
            { id: 'country', icon: Globe, label: 'Nation' }
          ].map((btn) => (
            <button
              key={btn.id}
              onClick={() => handleZoomPreset(btn.id)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-all active:scale-95"
            >
              <btn.icon size={16} />
              <span className="text-[10px] font-bold uppercase tracking-widest">{btn.label}</span>
            </button>
          ))}
        </div>

        <div className="glass-panel p-6 rounded-[2rem] border border-white/10 backdrop-blur-3xl shadow-2xl w-64 space-y-4 ring-1 ring-white/5">
          <div className="flex justify-between items-center">
            <p className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Air Spectrum</p>
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          </div>
          <div className="flex h-1.5 w-full rounded-full overflow-hidden bg-white/5 ring-1 ring-white/10">
            {['#14b8a6', '#facc15', '#f97316', '#ef4444', '#7f1d1d'].map((c, i) => (
              <div key={i} className="flex-1 h-full" style={{ backgroundColor: c }} />
            ))}
          </div>
          <div className="flex justify-between text-[9px] text-slate-500 font-bold uppercase tracking-[0.15em]">
            <span>Good</span>
            <span>Poor</span>
            <span>Severe</span>
          </div>
        </div>
      </div>

      {loadingStations && (
        <div className="absolute inset-0 z-[2000] bg-slate-950/60 backdrop-blur-xl flex items-center justify-center">
          <div className="flex flex-col items-center gap-8 animate-in fade-in zoom-in duration-500">
            <div className="relative">
              <div className="w-24 h-24 border-2 border-teal-500/10 border-t-teal-500 rounded-full animate-spin" />
              <div className="absolute inset-0 flex items-center justify-center">
                <Globe className="text-teal-500 w-8 h-8 animate-pulse" />
              </div>
            </div>
            <div className="text-center space-y-2">
              <span className="text-white text-lg font-black tracking-[0.4em] uppercase block">AeroGrid Sync</span>
              <div className="flex items-center gap-2 justify-center">
                <span className="w-1.5 h-1.5 bg-teal-500 rounded-full animate-pulse" />
                <span className="text-teal-400 text-[10px] font-black uppercase tracking-widest">Global Station Scan active</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
