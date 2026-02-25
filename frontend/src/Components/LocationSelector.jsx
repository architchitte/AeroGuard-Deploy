import { Search, MapPin, Loader2, X } from "lucide-react";
import { API_BASE_URL } from "../api/apiConfig";
import { useState, useRef, useEffect } from "react";

export default function LocationSearch({ onSelect }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [focused, setFocused] = useState(false);
  const ref = useRef(null);

  const searchLocation = async (text) => {
    setQuery(text);
    if (text.length < 3) { setResults([]); return; }
    const API_BASE = API_BASE_URL;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/realtime-aqi/search?q=${encodeURIComponent(text)}`);
      const data = await res.json();
      setResults(data.map((it) => ({
        displayName: it.display_name,
        name: it.display_name.split(",")[0],
        lat: parseFloat(it.lat),
        lon: parseFloat(it.lon),
      })));
    } catch { setResults([]); }
    finally { setLoading(false); }
  };

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setFocused(false); };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div ref={ref} className="relative w-full">
      {/* Input */}
      <div className={`flex items-center gap-2.5 px-4 py-2.5 rounded-xl border transition-all duration-200
        ${focused ? "bg-[#242F49] border-[#384358]/60 shadow-[0_0_20px_rgba(181,26,43,0.08)]"
          : "bg-[#242F49]/70 border-[#384358]/25 hover:border-[#384358]/50"}`}>
        {loading
          ? <Loader2 size={14} className="text-[#B51A2B] animate-spin shrink-0" />
          : <Search size={14} className={`${focused ? "text-[#B51A2B]" : "text-[#9BA3AF]"} shrink-0 transition-colors`} />}
        <input
          value={query}
          onFocus={() => setFocused(true)}
          onChange={(e) => searchLocation(e.target.value)}
          placeholder="Search any city or region…"
          className="bg-transparent border-none outline-none w-full text-xs font-bold text-[#FFA586] placeholder:text-[#9BA3AF]/60 placeholder:font-medium"
        />
      </div>

      {/* Dropdown */}
      {focused && results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 p-2 glass-card rounded-2xl border-[#384358]/30 shadow-2xl z-[200]">
          <div className="px-2 py-1.5 border-b border-[#384358]/15 mb-1">
            <span className="text-[9px] font-black uppercase tracking-widest text-[#9BA3AF]">Search Results</span>
          </div>
          <div className="space-y-0.5 max-h-52 overflow-y-auto">
            {results.map((loc, i) => (
              <button key={i}
                onClick={() => { onSelect(loc); setQuery(""); setResults([]); setFocused(false); }}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-[#242F49] transition-all group">
                <div className="p-1.5 rounded-lg bg-[#101525]/60 group-hover:bg-[#B51A2B]/10 transition-colors">
                  <MapPin size={12} className="text-[#9BA3AF] group-hover:text-[#B51A2B]" />
                </div>
                <div className="flex flex-col items-start overflow-hidden text-left">
                  <span className="text-xs font-bold text-[#FFA586] group-hover:text-[#B51A2B] transition-colors truncate w-full">
                    {loc.name}
                  </span>
                  <span className="text-[10px] text-[#9BA3AF] truncate w-full">{loc.displayName}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
