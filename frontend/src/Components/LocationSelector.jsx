import { useState } from "react";
import { MapPin, Search } from "lucide-react";

export default function LocationSearch({ onSelect }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const searchLocation = async (text) => {
    setQuery(text);

    // If input too small → reset
    if (text.length < 3) {
      setResults([]);
      return;
    }

    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

    setLoading(true);
    try {
      const res = await fetch(
        `${API_BASE_URL}/api/v1/realtime-aqi/search?q=${encodeURIComponent(text)}`
      );
      const data = await res.json();

      setResults(
        data.map((item) => ({
          displayName: item.display_name,
          name: item.display_name.split(',')[0], // Extract city name
          lat: parseFloat(item.lat),
          lon: parseFloat(item.lon),
        }))
      );
    } catch (err) {
      console.error("Location search failed", err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-2xl p-5 border border-slate-700">
      <div className="flex items-center gap-2 mb-3">
        <MapPin className="text-teal-400" size={18} />
        <h3 className="text-white font-semibold">Search Location</h3>
      </div>

      {/* INPUT */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 w-4 h-4" />
        <input
          value={query}
          onChange={(e) => searchLocation(e.target.value)}
          placeholder="Search city, area, place..."
          className="w-full pl-9 pr-3 py-2 bg-black/30 border border-white/10 rounded-lg text-sm text-white focus:outline-none focus:border-teal-400"
        />
      </div>

      {/* LOADING */}
      {loading && (
        <p className="text-xs text-slate-400 mt-2">Searching…</p>
      )}

      {/* RESULTS */}
      {!loading && results.length > 0 && (
        <div className="mt-3 space-y-2 max-h-48 overflow-y-auto">
          {results.map((loc, i) => (
            <button
              key={i}
              onClick={() => {
                onSelect(loc);
                setQuery("");     // ✅ allows fresh search
                setResults([]);   // ✅ hide dropdown
              }}
              className="w-full text-left px-3 py-2 rounded-lg bg-black/30 hover:bg-white/5 text-slate-300 text-xs transition"
            >
              {loc.displayName}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
