import { useState, useMemo, useEffect } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import {
    Wind, Map as MapIcon, Layers, Filter, Maximize, ZoomIn, Globe, Download, RefreshCw, Info
} from "lucide-react";

// --- MOCK DATA: 15 Indian Cities ---
const CITIES_DATA = [
    { id: 'delhi', name: 'Delhi', lat: 28.7041, lon: 77.1025, aqi: 342, pollutant: 'PM2.5' },
    { id: 'mumbai', name: 'Mumbai', lat: 19.0760, lon: 72.8777, aqi: 156, pollutant: 'PM10' },
    { id: 'bangalore', name: 'Bangalore', lat: 12.9716, lon: 77.5946, aqi: 42, pollutant: 'O3' },
    { id: 'chennai', name: 'Chennai', lat: 13.0827, lon: 80.2707, aqi: 89, pollutant: 'PM2.5' },
    { id: 'kolkata', name: 'Kolkata', lat: 22.5726, lon: 88.3639, aqi: 189, pollutant: 'NO2' },
    { id: 'hyderabad', name: 'Hyderabad', lat: 17.3850, lon: 78.4867, aqi: 110, pollutant: 'PM2.5' },
    { id: 'pune', name: 'Pune', lat: 18.5204, lon: 73.8567, aqi: 95, pollutant: 'O3' },
    { id: 'ahmedabad', name: 'Ahmedabad', lat: 23.0225, lon: 72.5714, aqi: 165, pollutant: 'SO2' },
    { id: 'jaipur', name: 'Jaipur', lat: 26.9124, lon: 75.7873, aqi: 130, pollutant: 'PM10' },
    { id: 'lucknow', name: 'Lucknow', lat: 26.8467, lon: 80.9462, aqi: 210, pollutant: 'PM2.5' },
    { id: 'chandigarh', name: 'Chandigarh', lat: 30.7333, lon: 76.7794, aqi: 85, pollutant: 'NO2' },
    { id: 'bhopal', name: 'Bhopal', lat: 23.2599, lon: 77.4126, aqi: 115, pollutant: 'CO' },
    { id: 'patna', name: 'Patna', lat: 25.5941, lon: 85.1376, aqi: 245, pollutant: 'PM2.5' },
    { id: 'nagpur', name: 'Nagpur', lat: 21.1458, lon: 79.0882, aqi: 105, pollutant: 'O3' },
    { id: 'kochi', name: 'Kochi', lat: 9.9312, lon: 76.2673, aqi: 45, pollutant: 'PM10' },
];

// --- UTILITIES ---
const getAQIColor = (aqi) => {
    if (aqi <= 50) return { hex: "#14b8a6", tailwind: "text-neon-teal" }; // Good
    if (aqi <= 100) return { hex: "#facc15", tailwind: "text-yellow-400" }; // Moderate
    if (aqi <= 150) return { hex: "#f97316", tailwind: "text-orange-500" }; // Unhealthy
    if (aqi <= 200) return { hex: "#ef4444", tailwind: "text-red-500" }; // Unhealthy
    if (aqi <= 300) return { hex: "#7f1d1d", tailwind: "text-red-800" }; // Very Unhealthy
    return { hex: "#450a0a", tailwind: "text-rose-950" }; // Hazardous
};

// Component to handle programmatic zoom/pan
function MapController({ center, zoom }) {
    const map = useMap();
    useEffect(() => {
        map.setView(center, zoom, { animate: true, duration: 1.5 });
    }, [center, zoom, map]);
    return null;
}

export default function PollutionHeatmap() {
    // --- STATE ---
    const [pollutantType, setPollutantType] = useState("PM2.5");
    const [viewType, setViewType] = useState("AQI Heatmap");
    const [timeRange, setTimeRange] = useState("Real-time");

    // Viewport State (Default: India Center)
    const [viewState, setViewState] = useState({ center: [22.3511, 78.6677], zoom: 5 });

    // --- HANDLERS ---
    const handleZoom = (level) => {
        const newViewState =
            level === 'city' ? { center: [28.7041, 77.1025], zoom: 11 } : // Focus Delhi
                level === 'region' ? { center: [28.7041, 77.1025], zoom: 7 } : // North India
                    { center: [22.3511, 78.6677], zoom: 5 }; // Country
        setViewState(newViewState);
    };

    return (
        <div className="w-full h-[800px] relative rounded-3xl overflow-hidden border border-white/10 shadow-2xl bg-slate-900 group">

            {/* 1. MAP CONTAINER */}
            <MapContainer
                center={viewState.center}
                zoom={viewState.zoom}
                style={{ height: "100%", width: "100%", background: "#0f172a" }}
                zoomControl={false}
            >
                <MapController center={viewState.center} zoom={viewState.zoom} />

                {/* Dark Matter Tiles */}
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />

                {/* Spatial Interpolation (Simulated Heatmap Layer - Large blurred circles behind) */}
                {CITIES_DATA.map((city) => (
                    <CircleMarker
                        key={`heat-${city.id}`}
                        center={[city.lat, city.lon]}
                        radius={60} // Large radius for overlap
                        pathOptions={{
                            color: 'transparent',
                            fillColor: getAQIColor(city.aqi).hex,
                            fillOpacity: 0.15 // Very transparent for blending
                        }}
                    />
                ))}

                {/* City Markers (Sharp Points) */}
                {CITIES_DATA.map((city) => {
                    const color = getAQIColor(city.aqi);
                    return (
                        <CircleMarker
                            key={city.id}
                            center={[city.lat, city.lon]}
                            radius={8}
                            pathOptions={{
                                color: '#fff',
                                weight: 1,
                                fillColor: color.hex,
                                fillOpacity: 0.9
                            }}
                        >
                            <Popup className="glass-popup">
                                <div className="p-2 min-w-[150px]">
                                    <h3 className="font-bold text-slate-800 text-lg">{city.name}</h3>
                                    <div className="flex items-center gap-2 mt-1">
                                        <span className="text-2xl font-bold" style={{ color: color.hex }}>{city.aqi}</span>
                                        <span className="text-xs text-slate-500 font-medium bg-slate-100 px-1 py-0.5 rounded">AQI</span>
                                    </div>
                                    <p className="text-xs text-slate-500 mt-2">Primary: {city.pollutant}</p>
                                </div>
                            </Popup>
                        </CircleMarker>
                    );
                })}
            </MapContainer>

            {/* 2. FLOATING CONTROLS (Top Left) */}
            <div className="absolute top-6 left-6 z-[1000] flex flex-col gap-4">
                {/* Main Filter Panel */}
                <div className="glass-panel p-4 rounded-xl border border-white/10 backdrop-blur-md shadow-lg w-64">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                        <Filter size={12} /> Data Layers
                    </h3>

                    <div className="space-y-3">
                        <div className="space-y-1">
                            <label className="text-[10px] text-slate-500">Pollutant</label>
                            <select
                                value={pollutantType}
                                onChange={(e) => setPollutantType(e.target.value)}
                                className="w-full bg-black/40 border border-white/10 text-slate-300 text-xs rounded-md px-2 py-1.5 focus:outline-none focus:border-neon-teal"
                            >
                                {['PM2.5', 'PM10', 'NO2', 'O3', 'SO2', 'CO'].map(p => <option key={p} value={p}>{p}</option>)}
                            </select>
                        </div>

                        <div className="space-y-1">
                            <label className="text-[10px] text-slate-500">View Mode</label>
                            <select
                                value={viewType}
                                onChange={(e) => setViewType(e.target.value)}
                                className="w-full bg-black/40 border border-white/10 text-slate-300 text-xs rounded-md px-2 py-1.5 focus:outline-none focus:border-neon-teal"
                            >
                                <option>AQI Heatmap</option>
                                <option>Risk Level</option>
                                <option>Specific Pollutant</option>
                            </select>
                        </div>

                        <div className="space-y-1">
                            <label className="text-[10px] text-slate-500">Time Range</label>
                            <select
                                value={timeRange}
                                onChange={(e) => setTimeRange(e.target.value)}
                                className="w-full bg-black/40 border border-white/10 text-slate-300 text-xs rounded-md px-2 py-1.5 focus:outline-none focus:border-neon-teal"
                            >
                                <option>Real-time</option>
                                <option>Last 6 Hours</option>
                                <option>Last 24 Hours</option>
                                <option>Last 7 Days</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            {/* 3. ZOOM CONTROLS (Right Side) */}
            <div className="absolute top-1/2 -translate-y-1/2 right-6 z-[1000] flex flex-col gap-2">
                {[['city', Maximize, 'City Focus'], ['region', ZoomIn, 'Region View'], ['country', Globe, 'Country View']].map(([lvl, Icon, label]) => (
                    <button
                        key={lvl}
                        onClick={() => handleZoom(lvl)}
                        className="p-3 bg-slate-900/90 border border-white/20 text-slate-300 rounded-lg hover:bg-neon-teal hover:text-white hover:border-neon-teal transition-all shadow-lg group/btn relative"
                    >
                        <Icon size={20} />
                        <span className="absolute right-full mr-3 top-1/2 -translate-y-1/2 px-2 py-1 bg-black/80 text-xs text-white rounded opacity-0 group-hover/btn:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                            {label}
                        </span>
                    </button>
                ))}
            </div>

            {/* 4. OVERLAYS & LEGEND (Bottom) */}
            <div className="absolute bottom-6 left-6 right-6 z-[1000] flex flex-col md:flex-row items-end justify-between gap-4 pointer-events-none">

                {/* Footer Info */}
                <div className="bg-slate-900/90 md:bg-black/60 backdrop-blur-md border border-white/10 rounded-full px-4 py-2 flex items-center gap-4 pointer-events-auto">
                    <div className="flex items-center gap-2 text-[10px] text-slate-400">
                        <Info size={12} />
                        <span className="hidden sm:inline">Source: </span>
                        <span className="text-neon-teal font-mono">WAQI API</span>
                    </div>
                    <div className="w-px h-3 bg-white/10" />
                    <div className="flex items-center gap-2 text-[10px] text-slate-400">
                        <RefreshCw size={12} />
                        <span>Updated: 10:45 AM</span>
                    </div>
                    <div className="w-px h-3 bg-white/10" />
                    <button className="flex items-center gap-1.5 text-[10px] font-bold text-white hover:text-neon-teal transition-colors">
                        <Download size={12} /> Export
                    </button>
                </div>

                {/* Legend & Wind Scale */}
                <div className="flex flex-col gap-3 items-end pointer-events-auto">

                    {/* Wind Direction (Mock Animated) */}
                    <div className="bg-black/60 backdrop-blur-md p-2 rounded-lg border border-white/10 flex items-center gap-3">
                        <span className="text-[10px] text-slate-400 font-mono uppercase">Wind Flow</span>
                        <div className="flex gap-1">
                            {[...Array(3)].map((_, i) => (
                                <Wind key={i} size={16} className="text-slate-500 animate-pulse" style={{ animationDelay: `${i * 0.5}s` }} />
                            ))}
                        </div>
                        <span className="text-xs font-bold text-white">NW 12km/h</span>
                    </div>

                    {/* AQI Color Scale */}
                    <div className="bg-white/95 backdrop-blur-xl p-3 rounded-lg border border-white/20 shadow-xl w-64">
                        <div className="flex justify-between text-[10px] font-bold text-slate-600 mb-1">
                            <span>0</span>
                            <span>50</span>
                            <span>100</span>
                            <span>200</span>
                            <span>300+</span>
                        </div>
                        <div className="h-2 w-full rounded-full bg-gradient-to-r from-teal-400 via-yellow-400 to-red-800" />
                        <div className="flex justify-between mt-1">
                            <span className="text-[8px] font-bold text-teal-600">GOOD</span>
                            <span className="text-[8px] font-bold text-red-800">HAZARDOUS</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
