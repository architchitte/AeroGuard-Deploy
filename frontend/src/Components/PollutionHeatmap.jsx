import {
  MapContainer,
  TileLayer,
  Circle,
  CircleMarker,
  Tooltip,
  useMap,
  Polyline,
  Marker,
  Popup,
  ZoomControl,
  useMapEvents
} from "react-leaflet";
import { API_BASE_URL } from "../api/apiConfig";

// Custom grid lines component to match user's reference image
function GridLines() {
  const lines = [];
  // Latitudes
  for (let lat = -90; lat <= 90; lat += 10) {
    lines.push([[lat, -180], [lat, 180]]);
  }
  // Longitudes
  for (let lon = -180; lon <= 180; lon += 10) {
    lines.push([[-90, lon], [90, lon]]);
  }

  return (
    <>
      {lines.map((pos, i) => (
        <Polyline
          key={i}
          positions={pos}
          pathOptions={{
            color: 'rgba(255, 255, 255, 0.1)',
            weight: 1,
            interactive: false
          }}
        />
      ))}
    </>
  );
}
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
import DISTRICTS from "../constants/districts";
import HeatmapLayer from "./HeatmapLayer";

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
}
const getHealthAdvice = (aqi) => {
  if (aqi <= 50) return "Air quality is ideal for outdoor activities.";
  if (aqi <= 100) return "Air quality is acceptable; however, sensitive individuals should monitor their symptoms.";
  if (aqi <= 150) return "Members of sensitive groups may experience health effects. The general public is less likely to be affected.";
  if (aqi <= 200) return "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects.";
  if (aqi <= 300) return "Health warnings of emergency conditions. The entire population is more likely to be affected.";
  return "Health alert: everyone may experience more serious health effects.";
};

/* ================= MAIN ================= */

export default function PollutionHeatmap({ externalLocation, onLocationSelect }) {
  const INDIA_CENTER = [20.59, 78.96]; // Geographic Center of India
  const INDIA_BOUNDS = [
    [5.0, 65.0],  // Southwest (Aggressive wrap)
    [38.5, 100.0]  // Northeast (Aggressive wrap)
  ];
  const navigate = useNavigate();

  const [location, setLocation] = useState(externalLocation || null);
  const [center, setCenter] = useState(INDIA_CENTER);
  const [zoom, setZoom] = useState(5);
  const [isPanelOpen, setIsPanelOpen] = useState(true);
  const [lastSync, setLastSync] = useState(new Date());
  const [pollutantData, setPollutantData] = useState(null);
  const [aqi, setAqi] = useState(null);
  const [stations, setStations] = useState([]);
  const [loadingStations, setLoadingStations] = useState(false);

  const [waqiToken, setWaqiToken] = useState(null);

  // Sync with external location if provided
  useEffect(() => {
    if (externalLocation) {
      setLocation(externalLocation);
      setCenter([externalLocation.lat, externalLocation.lon]);
      setZoom(10);
      setIsPanelOpen(true);
    }
  }, [externalLocation]);

  const loadData = async () => {
    try {
      setLoadingStations(true);
      const mapData = await fetchMapData();
      setStations(mapData);
      setLastSync(new Date());
    } catch (err) {
      console.error("Data sync failed:", err);
    } finally {
      setLoadingStations(false);
    }
  };


  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!location) return;

    const loadAQI = async () => {
      try {
        const data = await fetchAQI(location.lat, location.lon);
        setAqi(data.aqi);
        setPollutantData({
          pm25: data.pm25,
          pm10: data.pm10,
          no2: data.no2,
          o3: data.o3
        });
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
  const isPointInIndia = (lat, lon) => {
    return lat >= 6.7 && lat <= 37.5 && lon >= 68.1 && lon <= 97.4;
  };

  const heatmapPoints = stations
    .filter(s => s.lat != null && s.lon != null && s.aqi != null)
    .filter(s => isPointInIndia(s.lat, s.lon))
    .map(s => ({
      lat: s.lat,
      lng: s.lon,
      value: Math.min(s.aqi, 500)
    }));

  const POLLUTANT_MAP = {
    pm25: { name: "PM2.5", unit: "µg/m³", icon: Droplets },
    pm10: { name: "PM10", unit: "µg/m³", icon: Wind },
    no2: { name: "NO2", unit: "ppb", icon: CloudRain },
    o3: { name: "O3", unit: "ppb", icon: Wind },
    so2: { name: "SO2", unit: "ppb", icon: Droplets },
    co: { name: "CO", unit: "ppm", icon: Activity }
  };

  const pollutants = pollutantData ? Object.entries(pollutantData)
    .filter(([key, value]) => value !== null && POLLUTANT_MAP[key])
    .map(([key, value]) => ({
      ...POLLUTANT_MAP[key],
      value: value
    })) : [];

  const healthAdvice = getHealthAdvice(aqi ?? 0);

  return (
    <div className="relative w-full h-[850px] bg-[#101525] rounded-[3rem] border border-[#384358]/20 shadow-2xl overflow-hidden group/map-section ring-1 ring-[#384358]/10">

      {/* ================= MAP Container ================= */}
      <MapContainer
        center={center}
        zoom={zoom}
        minZoom={5}
        maxBounds={INDIA_BOUNDS}
        maxBoundsViscosity={1.0}
        zoomControl={false}
        style={{ height: "100%", width: "100%" }}
        className="z-0"
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; CARTO'
        />

        <GridLines />

        {/* WAQI Official Tiles - Using Backend Proxy for security */}
        <TileLayer
          url={`${API_BASE_URL}/api/v1/realtime-aqi/tiles/{z}/{x}/{y}.png`}
          attribution='&copy; World Air Quality Index Project'
          opacity={0.8}
          zIndex={10}
        />

        <MapController center={center} zoom={zoom} />

        {/* ================= SELECTION AURA EFFECT ================= */}
        {location && (
          <>
            {/* 1. Outer Soft Coverage Glow */}
            <Circle
              center={[location.lat, location.lon]}
              radius={30000}
              pathOptions={{
                fillColor: getAQIColor(aqi || 100),
                fillOpacity: 0.1,
                stroke: true,
                color: getAQIColor(aqi || 100),
                weight: 1,
                dashArray: "5, 10",
                opacity: 0.3
              }}
            />

            {/* 2. Mid-Range Impact Zone */}
            <Circle
              center={[location.lat, location.lon]}
              radius={15000}
              pathOptions={{
                fillColor: getAQIColor(aqi || 100),
                fillOpacity: 0.1,
                stroke: false
              }}
            />

            {/* 3. Core Targeting Ring */}
            <Circle
              center={[location.lat, location.lon]}
              radius={zoom > 8 ? 5000 : 8000}
              pathOptions={{
                color: getAQIColor(aqi || 100),
                weight: 2,
                fill: true,
                fillColor: getAQIColor(aqi || 100),
                fillOpacity: 0.2,
                dashArray: "10, 10",
                opacity: 0.8
              }}
              className="selection-ring-pulse"
            />

            {/* 4. Exact Center Pinpoint */}
            <CircleMarker
              center={[location.lat, location.lon]}
              radius={zoom > 10 ? 10 : 6}
              pathOptions={{
                fillColor: getAQIColor(aqi || 100),
                fillOpacity: 1,
                color: "#fff",
                weight: 2,
              }}
            />
          </>
        )}

        {/* VIBRANT CUSTOM HEATMAP LAYER - Matching reference image */}
        {heatmapPoints.length > 0 && (
          <HeatmapLayer
            points={heatmapPoints}
            options={{
              radius: 45,      // Reduced for more pinpoint, "shabby-free" look
              blur: 35,        // Reduced for better definition
              max: 220,        // Slightly higher max to normalize intense colors
              minOpacity: 0.5, // Stronger base visibility
              gradient: {
                0.1: '#3fb5af',
                0.3: '#00e400',
                0.5: '#ffff00',
                0.7: '#ff7e00',
                0.9: '#ff0000',
                1.0: '#7e0023'
              }
            }}
          />
        )}
      </MapContainer>

      {/* ================= FLOATING OVERLAYS ================= */}

      {/* 1. TOP-LEFT: SEARCH OVERLAY */}
      <div className="absolute top-8 left-8 z-[1000] w-[340px] animate-slide-right">
        <div className="glass-panel p-1 rounded-2xl border border-[#384358]/30 shadow-2xl transition-all duration-300 focus-within:border-[#B51A2B]/50 hover:border-white/20">
          <LocationSearch onSelect={handleLocationSelect} />
        </div>
      </div>

      {/* 2. CENTER-LEFT: DATA PANEL */}
      {location && (
        <div className={`absolute top-[160px] left-8 z-[900] transition-all duration-500 ease-in-out ${isPanelOpen ? 'translate-x-0 opacity-100' : '-translate-x-[110%] opacity-0'}`}>
          <div className="w-[360px] glass-panel rounded-[2.5rem] border border-[#384358]/30 shadow-[0_0_50px_rgba(16,21,37,0.5),0_0_20px_rgba(181,26,43,0.1)] overflow-hidden backdrop-blur-3xl bg-[#101525]/95 p-8 space-y-8">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <p className="text-[10px] font-black uppercase text-[#9BA3AF] tracking-widest flex items-center gap-2">
                  <MapPin size={10} className="text-[#B51A2B]" /> Current Station
                </p>
                <h3 className="text-2xl font-black text-[#FFA586] leading-tight">{location.name}</h3>
                <p className="text-[#9BA3AF] text-xs font-medium uppercase tracking-wider">Regional Air Intelligence</p>
              </div>
              <button
                onClick={() => setIsPanelOpen(false)}
                className="p-2 rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
                title="Close Panel"
              >
                <X size={16} className="text-slate-500" />
              </button>
            </div>

            <div className="flex items-center justify-between gap-6 py-6 border-y border-[#384358]/15">
              <div className="space-y-1">
                <span className="text-7xl font-black text-[#FFA586] leading-none tracking-tighter">
                  {aqi ?? '--'}
                </span>
                <p className="text-xs font-bold text-[#9BA3AF] uppercase tracking-widest">US-EPA Index</p>
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
                <div className="w-full bg-[#101525]/80 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="h-full transition-all duration-1000"
                    style={{
                      width: `${Math.min(100, ((aqi ?? 0) / 300) * 100)}%`,
                      backgroundColor: getAQIColor(aqi ?? 0),
                      boxShadow: `0 0 10px ${getAQIColor(aqi ?? 0)}`
                    }}
                  />                </div>
              </div>
            </div>

            <div className="p-5 rounded-3xl bg-gradient-to-br from-[#B51A2B]/10 via-[#541A2B]/5 to-transparent border border-[#B51A2B]/20">
              <div className="flex items-center gap-2 mb-2">
                <Activity size={12} className="text-[#B51A2B] animate-pulse" />
                <span className="text-[10px] font-black uppercase text-[#B51A2B] tracking-widest">AI Health Pulse</span>
              </div>
              <p className="text-xs text-[#FFA586] leading-relaxed italic mb-4">
                "{healthAdvice}"
              </p>

              <button
                onClick={() => navigate('/dashboard', { state: { selectedLocation: location } })}
                className="w-full py-3 bg-[#B51A2B]/10 hover:bg-[#B51A2B]/20 border border-[#B51A2B]/30 rounded-2xl text-[#B51A2B] text-[10px] font-black uppercase tracking-[0.2em] transition-all flex items-center justify-center gap-2"
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
          className="absolute top-24 left-8 z-[1000] p-4 bg-[#101525]/90 backdrop-blur-xl border border-[#384358]/30 rounded-2xl text-[#B51A2B] hover:scale-110 transition-all animate-slide-right shadow-2xl hover:border-[#B51A2B]/50"
        >
          <ChevronRight size={20} />
        </button>
      )}

      {/* 3. BOTTOM-LEFT: STATUS */}
      <div className="absolute bottom-8 left-8 z-[400]">
        <div className="flex items-center gap-3 px-5 py-2.5 rounded-full bg-[#101525]/90 backdrop-blur-xl border border-[#384358]/20 shadow-2xl group/status hover:border-[#B51A2B]/30 transition-all">
          <div className="w-2 h-2 rounded-full bg-[#B51A2B] animate-pulse shadow-[0_0_8px_rgba(181,26,43,0.5)]" />
          <span className="text-[10px] font-bold text-[#FFA586] uppercase tracking-[0.2em]">AeroGrid Live</span>
          <div className="w-[1px] h-3 bg-[#384358]/30 mx-1" />
          <span className="text-[10px] font-bold text-[#9BA3AF] uppercase group-hover:text-[#B51A2B] transition-colors">
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
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-[#9BA3AF] hover:text-[#FFA586] hover:bg-[#B51A2B]/10 transition-all active:scale-95"
            >
              <btn.icon size={16} />
              <span className="text-[10px] font-bold uppercase tracking-widest">{btn.label}</span>
            </button>
          ))}
        </div>

        <div className="glass-panel p-6 rounded-[2rem] border border-[#384358]/20 backdrop-blur-3xl shadow-2xl w-64 space-y-4 ring-1 ring-[#384358]/10">
          <div className="flex justify-between items-center">
            <p className="text-[10px] font-black uppercase text-[#9BA3AF] tracking-widest">Air Spectrum</p>
            <div className="w-1.5 h-1.5 rounded-full bg-[#B51A2B] animate-pulse" />
          </div>
          <div className="flex h-1.5 w-full rounded-full overflow-hidden bg-[#101525]/60 ring-1 ring-[#384358]/10">
            {['#00e400', '#ffff00', '#ff7e00', '#ff0000'].map((c, i) => (
              <div key={i} className="flex-1 h-full" style={{ backgroundColor: c }} />
            ))}
          </div>
          <div className="flex justify-between text-[9px] text-[#9BA3AF] font-bold uppercase tracking-[0.15em]">
            <span>Good</span>
            <span>Poor</span>
            <span>Severe</span>
          </div>
        </div>
      </div>

      {loadingStations && (
        <div className="absolute inset-0 z-[2000] bg-[#101525]/70 backdrop-blur-xl flex items-center justify-center">
          <div className="flex flex-col items-center gap-8 animate-in fade-in zoom-in duration-500">
            <div className="relative">
              <div className="w-24 h-24 border-2 border-[#B51A2B]/10 border-t-[#B51A2B] rounded-full animate-spin" />
              <div className="absolute inset-0 flex items-center justify-center">
                <Globe className="text-[#B51A2B] w-8 h-8 animate-pulse" />
              </div>
            </div>
            <div className="text-center space-y-2">
              <span className="text-[#FFA586] text-lg font-black tracking-[0.4em] uppercase block">AeroGrid Sync</span>
              <div className="flex items-center gap-2 justify-center">
                <span className="w-1.5 h-1.5 bg-[#B51A2B] rounded-full animate-pulse" />
                <span className="text-[#B51A2B] text-[10px] font-black uppercase tracking-widest">Global Station Scan active</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
