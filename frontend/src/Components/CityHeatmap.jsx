import { useEffect } from 'react';
import { MapContainer, TileLayer, Circle, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

// Component to handle map center updates
function MapUpdater({ center }) {
    const map = useMap();
    useEffect(() => {
        map.flyTo(center, 10, { duration: 1.5 });
    }, [center, map]);
    return null;
}

export default function CityHeatmap({ lat, lon, aqi }) {
    const center = [lat, lon];

    // Determine color based on AQI
    const getColor = (val) => {
        if (val <= 50) return '#14b8a6'; // Neon Teal
        if (val <= 100) return '#facc15'; // Yellow
        if (val <= 200) return '#f97316'; // Orange
        if (val <= 300) return '#ef4444'; // Red
        return '#7f1d1d'; // Dark Red
    };

    const color = getColor(aqi);

    return (
        <div className="h-full w-full rounded-2xl overflow-hidden relative z-0">
            <MapContainer
                center={center}
                zoom={10}
                style={{ height: '100%', width: '100%', background: '#020617' }}
                zoomControl={false}
                scrollWheelZoom={false}
                dragging={false} // Static view as per "heatmap" request, or allow if user wants interaction
                doubleClickZoom={false}
            >
                {/* Dark Mode Map Tiles */}
                <TileLayer
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                />

                <MapUpdater center={center} />

                {/* Outer Halo (30km) - Faint */}
                <Circle
                    center={center}
                    radius={30000}
                    pathOptions={{
                        fillColor: color,
                        fillOpacity: 0.1,
                        stroke: false
                    }}
                />

                {/* Mid Halo (15km) - Moderate */}
                <Circle
                    center={center}
                    radius={15000}
                    pathOptions={{
                        fillColor: color,
                        fillOpacity: 0.2,
                        stroke: false
                    }}
                />

                {/* Inner Core (5km) - Intense */}
                <Circle
                    center={center}
                    radius={5000}
                    pathOptions={{
                        fillColor: color,
                        fillOpacity: 0.4,
                        color: color,
                        weight: 1,
                        opacity: 0.6
                    }}
                />
            </MapContainer>

            {/* Overlay Text */}
            <div className="absolute top-4 right-4 z-[400] bg-black/60 backdrop-blur-md px-3 py-1 rounded-full border border-white/10">
                <span className="text-[10px] font-bold text-white uppercase tracking-wider flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: color }}></span>
                    Coverage: 30km
                </span>
            </div>
        </div>
    );
}
