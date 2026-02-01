import { useState, useEffect, use } from "react";
import {
  MapContainer,
  TileLayer,
  Circle,
  CircleMarker,
  Tooltip,
  useMap,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import {
  Maximize,
  ZoomIn,
  Globe,
} from "lucide-react";

import LocationSearch from "../components/LocationSelector";
import { fetchAQI, fetchMapData } from "../api/aqi";

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

/* ================= MAIN ================= */

export default function PollutionHeatmap() {
  const INDIA_CENTER = [22.3511, 78.6677];

  const [location, setLocation] = useState(null);
  const [center, setCenter] = useState(INDIA_CENTER);
  const [zoom, setZoom] = useState(5);

  // mock AQI (API later)
  const [aqi, setAqi] = useState(null);
  const [stations, setStations] = useState([]);
  const [loadingStations, setLoadingStations] = useState(false);
  const color = getAQIColor(aqi ?? 0);

  // 1. Fetch Nationwide Data
  useEffect(() => {
    const loadMapData = async () => {
      try {
        setLoadingStations(true);
        const data = await fetchMapData(); // Fetches all stations
        setStations(data);
      } catch (err) {
        console.error("Failed to fetch nationwide AQI points:", err);
      } finally {
        setLoadingStations(false);
      }
    };
    loadMapData();
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
      setZoom(12);
    }

    if (type === "region") {
      setCenter(locCenter); // 🔥 THIS WAS MISSING
      setZoom(7);
    }
  };

  return (
    <div className="relative w-full h-[820px] rounded-3xl overflow-hidden bg-[#020617] border border-white/10">

      {/* ================= MAP ================= */}
      <MapContainer
        center={center}
        zoom={zoom}
        zoomControl={false}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        <MapController center={center} zoom={zoom} />

        {location && aqi !== null && (
          <>
            {/* OUTER */}
            <Circle
              center={center}
              radius={30000}
              pathOptions={{ fillColor: color, fillOpacity: 0.08, stroke: false }}
            />

            {/* MID (hover info) */}
            <Circle
              center={center}
              radius={15000}
              pathOptions={{ fillColor: color, fillOpacity: 0.18, stroke: false }}
            >
              <Tooltip sticky opacity={1} className="aqi-tooltip">
                <div className="min-w-[180px]">
                  <p className="text-xs uppercase text-slate-500">Air Quality</p>
                  {/* <p className="text-sm font-bold text-slate-900">
                    {location.name}
                  </p> */}
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-2xl font-bold" style={{ color }}>
                      {aqi !== null ? aqi : "loading..."}
                    </span>
                    <span className="text-xs bg-slate-200 px-2 py-0.5 rounded">
                      AQI
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 mt-1">
                    {getAQILabel(aqi)}
                  </p>
                  <p className="text-[10px] text-slate-400 mt-2">
                    Coverage ~15 km
                  </p>
                </div>
              </Tooltip>
            </Circle>

            {/* CORE */}
            <Circle
              center={center}
              radius={5000}
              pathOptions={{
                fillColor: color,
                fillOpacity: 0.4,
                color,
                weight: 1,
              }}
            />
          </>
        )}

        {/* NATIONWIDE STATIONS */}
        {stations.map((s) => (
          <CircleMarker
            key={s.uid || `${s.lat}-${s.lon}`}
            center={[s.lat, s.lon]}
            radius={zoom > 7 ? 12 : 8}
            pathOptions={{
              fillColor: getAQIColor(s.aqi),
              fillOpacity: 0.8,
              color: "#fff",
              weight: 1,
            }}
          >
            <Tooltip permanent={zoom > 8} direction="center" className="marker-tooltip-num" opacity={1}>
              <span className="text-[9px] font-bold text-slate-900">{s.aqi}</span>
            </Tooltip>

            <Tooltip sticky className="aqi-details-tooltip">
              <div className="p-2 min-w-[120px]">
                <p className="text-[10px] uppercase text-slate-500 font-bold mb-1">Monitoring Station</p>
                <p className="text-xs font-bold text-slate-900 mb-2 truncate max-w-[150px]">{s.station}</p>
                <div className="flex items-center gap-2">
                  <span className="text-xl font-bold" style={{ color: getAQIColor(s.aqi) }}>{s.aqi}</span>
                  <span className="text-[10px] bg-slate-100 px-1.5 py-0.5 rounded font-bold uppercase">AQI</span>
                </div>
                <p className="text-[10px] mt-1 font-medium">{getAQILabel(s.aqi)}</p>
              </div>
            </Tooltip>
          </CircleMarker>
        ))}
      </MapContainer>

      {/* LOADING OVERLAY */}
      {loadingStations && (
        <div className="absolute inset-0 z-[2000] bg-slate-900/40 backdrop-blur-[2px] flex items-center justify-center rounded-3xl">
          <div className="flex flex-col items-center gap-3">
            <div className="w-10 h-10 border-4 border-teal-500/20 border-t-teal-500 rounded-full animate-spin" />
            <span className="text-white text-sm font-bold tracking-widest uppercase">Syncing National Grid</span>
          </div>
        </div>
      )}

      {/* LEGEND */}
      <div className="absolute bottom-6 left-6 z-[1000] bg-slate-900/90 backdrop-blur-xl border border-white/10 p-4 rounded-2xl shadow-2xl">
        {/* <h4 className="text-[10px] uppercase font-bold text-slate-500 mb-3 tracking-wider">AQI Scale</h4>
        <div className="space-y-2">
          {[
            { label: 'Good', range: '0 - 50', color: '#10b981' },
            { label: 'Moderate', range: '51 - 100', color: '#f59e0b' },
            { label: 'Unhealthy', range: '101 - 200', color: '#f97316' },
            { label: 'Hazardous', range: '201+', color: '#ef4444' }
          ].map(item => (
            <div key={item.label} className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
              <div>
                <p className="text-[10px] text-white font-bold leading-none">{item.label}</p>
                <p className="text-[8px] text-slate-500">{item.range}</p>
              </div>
            </div>
          ))}
        </div> */}
      </div>

      {/* ================= SEARCH PANEL ================= */}
      <div className="absolute top-6 left-6 z-[1000] w-[380px] h-[200px]">
        <div className="
          rounded-3xl p-6
          bg-gradient-to-br from-slate-900/95 to-slate-800/90
          backdrop-blur-xl
          border border-teal-400/20
          shadow-[0_0_50px_-12px_rgba(20,184,166,0.45)]
        ">
          <h3 className="text-xl font-bold text-white mb-1">
            Search Location
          </h3>
          <p className="text-xs text-slate-400 mb-4">
            India only
          </p>

          <LocationSearch onSelect={handleLocationSelect} />

          {location && aqi !== null && (
            <div className="mt-4">
              <p className="text-sm text-white font-semibold">
                {location.name}
              </p>
              <div className="mt-2 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-teal-500/10 border border-teal-400/30">
                <span className="text-xs text-teal-300">AQI</span>
                <span className="text-lg font-bold text-teal-400">
                  {aqi}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ================= ZOOM ================= */}
      <div className="absolute right-6 top-1/2 -translate-y-1/2 z-[1000] flex flex-col gap-2">
        <button onClick={() => handleZoomPreset("city")} className="zoom-btn">
          <Maximize size={18} />
        </button>
        <button onClick={() => handleZoomPreset("region")} className="zoom-btn">
          <ZoomIn size={18} />
        </button>
        <button onClick={() => handleZoomPreset("country")} className="zoom-btn">
          <Globe size={18} />
        </button>
      </div>
    </div>
  );
}
