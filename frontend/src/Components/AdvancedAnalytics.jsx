import React, { useState, useEffect } from "react";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { analyticsService } from "../api/analyticsService";

const AQI_BANDS = [
  { max: 50, emoji: "🟢", color: "#B51A2B" },
  { max: 100, emoji: "🟡", color: "#f59e0b" },
  { max: 200, emoji: "🟠", color: "#f97316" },
  { max: 300, emoji: "🔴", color: "#ef4444" },
  { max: 9999, emoji: "☠️", color: "#a855f7" },
];
const getBand = (aqi) => AQI_BANDS.find(b => aqi <= b.max) || AQI_BANDS[0];

const AreaTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const b = getBand(payload[0].value);
  return (
    <div className="bg-[#101525] border border-[#384358]/40 rounded-xl px-3 py-2 text-[10px] shadow-xl backdrop-blur-xl">
      <div className="flex items-center gap-1.5">
        <span className="text-sm">{b.emoji}</span>
        <span className="font-black" style={{ color: b.color }}>{payload[0].value?.toFixed ? payload[0].value.toFixed(1) : payload[0].value}</span>
      </div>
      <p className="text-[#9BA3AF]">{payload[0].payload?.date || payload[0].payload?.feature}</p>
    </div>
  );
};

const BarTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#101525] border border-[#384358]/40 rounded-xl px-3 py-2 text-[10px] shadow-xl backdrop-blur-xl">
      <p className="text-[#9BA3AF] font-black uppercase">{payload[0].payload?.feature}</p>
      <p className="font-black text-[#FFA586]">{payload[0].value?.toFixed(1)}%</p>
    </div>
  );
};

export default function AdvancedAnalytics({ location, persona }) {
  const cityName = location?.name || "Mumbai";
  const [timeRange, setTimeRange] = useState(14);
  const [historyData, setHistoryData] = useState([]);
  const [currentAqi, setCurrentAqi] = useState(null);
  const [selectedPollutant, setSelectedPollutant] = useState("pm25");
  const [featureImportance, setFeatureImportance] = useState([]);
  const [backendStatus, setBackendStatus] = useState("checking");
  const [activeChart, setActiveChart] = useState("trend");

  useEffect(() => {
    (async () => {
      const data = await analyticsService.getHistoricalAnalysis(timeRange, cityName);
      setHistoryData(data || []);
      if (data?.length) {
        const latest = data[data.length - 1];
        setCurrentAqi(latest.aqi);
        const dominant = Object.entries({ pm25: latest.pm25 ?? 0, pm10: latest.pm10 ?? 0, no2: latest.no2 ?? 0, o3: latest.o3 ?? 0 })
          .sort((a, b) => b[1] - a[1])[0]?.[0] || "pm25";
        setSelectedPollutant(dominant);
      }
    })();
  }, [cityName, timeRange]);

  useEffect(() => {
    if (!currentAqi || !selectedPollutant) return;
    (async () => {
      try {
        const h = await analyticsService.checkHealth();
        setBackendStatus(h?.status === "healthy" ? "online" : "offline");
        const xai = await analyticsService.getFeatureImportance(cityName, currentAqi, selectedPollutant);
        setFeatureImportance(xai);
      } catch { setBackendStatus("offline"); }
    })();
  }, [cityName, currentAqi, selectedPollutant]);

  const pollutantOptions = ["pm25", "pm10", "no2", "o3"];
  const pollutantEmojis = { pm25: "💨", pm10: "🌫️", no2: "🟡", o3: "🌀" };

  return (
    <div className="w-full space-y-5">

      {/* ── Controls ── */}
      <div className="flex flex-wrap items-center justify-between gap-3 sm:flex-nowrap">
        {/* Chart Toggle */}
        <div className="flex p-0.5 bg-[#101525]/70 rounded-xl border border-[#384358]/20">
          {[{ k: "trend", label: "📈 Trend" }, { k: "xai", label: "🧠 XAI" }].map(opt => (
            <button key={opt.k} onClick={() => setActiveChart(opt.k)}
              className={`px-3 py-1.5 rounded-lg text-xs font-black uppercase tracking-wide transition-all
                ${activeChart === opt.k
                  ? "bg-[#B51A2B] text-[#101525] shadow-md"
                  : "text-[#9BA3AF] hover:text-[#FFA586]"}`}>
              {opt.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          {/* Pollutant selector */}
          {activeChart === "trend" && (
            <div className="flex gap-1">
              {pollutantOptions.map(p => (
                <button key={p} onClick={() => setSelectedPollutant(p)}
                  className={`px-2 py-1 rounded-lg text-[10px] font-black transition-all border
                    ${selectedPollutant === p
                      ? "bg-[#B51A2B]/20 border-[#384358]/50 text-[#B51A2B]"
                      : "border-transparent text-[#9BA3AF] hover:text-[#FFA586]"}`}>
                  {pollutantEmojis[p]} {p.toUpperCase()}
                </button>
              ))}
            </div>
          )}
          {/* Time range */}
          <select value={timeRange} onChange={e => setTimeRange(Number(e.target.value))}
            className="bg-[#101525] border border-[#384358]/25 rounded-lg px-2 py-1 text-[9px] font-bold text-[#FFA586] outline-none">
            <option value={7}>7D</option>
            <option value={14}>14D</option>
            <option value={30}>30D</option>
          </select>
        </div>
      </div>

      {/* ── Chart ── */}
      <div className="h-44 w-full">
        <ResponsiveContainer width="100%" height="100%">
          {activeChart === "trend" ? (
            <AreaChart data={historyData} margin={{ top: 5, right: 5, left: -28, bottom: 0 }}>
              <defs>
                <linearGradient id="aGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#B51A2B" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#B51A2B" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(56,67,88,0.1)" />
              <XAxis dataKey="date" tick={{ fill: "#9BA3AF", fontSize: 8, fontWeight: 800 }}
                axisLine={false} tickLine={false} interval="preserveStartEnd" />
              <YAxis tick={{ fill: "#9BA3AF", fontSize: 8 }} axisLine={false} tickLine={false} />
              <Tooltip content={<AreaTooltip />} />
              <Area type="monotone" dataKey={selectedPollutant} stroke="#B51A2B" strokeWidth={2}
                fill="url(#aGrad)" dot={false} activeDot={{ r: 4, fill: "#B51A2B", stroke: "#FFA586", strokeWidth: 2 }} />
            </AreaChart>
          ) : (
            <BarChart layout="vertical" data={featureImportance.map(f => ({ ...f, vis: f.score * 100 }))}
              margin={{ top: 0, right: 20, left: 0, bottom: 0 }}>
              <XAxis type="number" hide />
              <YAxis dataKey="feature" type="category" width={68} axisLine={false} tickLine={false}
                tick={{ fill: "#9BA3AF", fontSize: 9, fontWeight: 800 }} />
              <Tooltip content={<BarTooltip />} cursor={{ fill: "rgba(181,26,43,0.04)" }} />
              <Bar dataKey="vis" radius={[0, 4, 4, 0]} fill="#B51A2B" barSize={10}
                label={{ position: "right", fill: "#9BA3AF", fontSize: 8, formatter: (v) => `${v?.toFixed(1)}%` }} />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>

      {/* ── Status bar ── */}
      <div className="flex justify-between items-center pt-3 border-t border-[#384358]/15">
        <div className="flex items-center gap-2 text-[9px] font-black uppercase">
          <div className={`w-1.5 h-1.5 rounded-full ${backendStatus === "online" ? "bg-[#B51A2B]" : "bg-red-400"}`} />
          <span className={backendStatus === "online" ? "text-[#B51A2B]" : "text-red-400"}>
            {backendStatus === "online" ? "✅ Analytics Active" : "⚠️ Degraded Mode"}
          </span>
        </div>
        <div className="text-[8px] font-black text-[#9BA3AF] uppercase tracking-widest">
          📡 WAQI · ⚡ 1s refresh · 🧠 XAI powered
        </div>
      </div>
    </div>
  );
}
