import { useEffect, useMemo } from "react";
import { MapContainer, TileLayer, Circle, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";

/* ================= MAP UPDATER ================= */

function MapUpdater({ lat, lon }) {
  const map = useMap();

  useEffect(() => {
    if (!lat || !lon) return;

    map.flyTo([lat, lon], 10, {
      duration: 1.5,
      animate: true,
    });
  }, [lat, lon, map]);

  return null;
}

/* ================= HEATMAP ================= */

export default function CityHeatmap({ lat, lon, aqi }) {
  // ✅ Stable center reference
  const center = useMemo(() => {
    if (!lat || !lon) return [20.5937, 78.9629]; // India fallback
    return [lat, lon];
  }, [lat, lon]);

  /* ---------- AQI COLOR ---------- */
  const getColor = (val) => {
    if (val <= 50) return "#14b8a6";
    if (val <= 100) return "#facc15";
    if (val <= 200) return "#f97316";
    if (val <= 300) return "#ef4444";
    return "#7f1d1d";
  };

  const color = getColor(aqi);

  return (
    <div className="h-full w-full rounded-2xl overflow-hidden relative">
      <MapContainer
        center={center}
        zoom={10}
        style={{ height: "100%", width: "100%", background: "#020617" }}
        zoomControl={false}
        scrollWheelZoom={false}
        dragging={false}
        doubleClickZoom={false}
      >
        {/* Dark tiles */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* 🔥 THIS is what syncs the map */}
        <MapUpdater lat={lat} lon={lon} />

        {/* Outer Halo */}
        <Circle
          center={center}
          radius={30000}
          pathOptions={{
            fillColor: color,
            fillOpacity: 0.1,
            stroke: false,
          }}
        />

        {/* Mid Halo */}
        <Circle
          center={center}
          radius={15000}
          pathOptions={{
            fillColor: color,
            fillOpacity: 0.2,
            stroke: false,
          }}
        />

        {/* Inner Core */}
        <Circle
          center={center}
          radius={5000}
          pathOptions={{
            fillColor: color,
            fillOpacity: 0.4,
            color: color,
            weight: 1,
            opacity: 0.6,
          }}
        />
      </MapContainer>

      {/* Overlay */}
      <div className="absolute top-4 right-4 z-400 bg-black/60 backdrop-blur-md px-3 py-1 rounded-full border border-white/10">
        <span className="text-[10px] font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <span
            className="w-2 h-2 rounded-full animate-pulse"
            style={{ backgroundColor: color }}
          />
          Coverage: 30km
        </span>
      </div>
    </div>
  );
}
