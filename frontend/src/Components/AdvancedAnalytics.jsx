import React, { useState, useEffect } from "react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  BrainCircuit,
  TrendingUp,
  AlertTriangle,
  Activity,
  Database,
  CheckCircle,
  Clock,
  Wifi,
  WifiOff,
} from "lucide-react";

import { analyticsService } from "../api/analyticsService";
import AeroIntelligenceBriefing from "./AeroIntelligenceBriefing";

/* ================= CONSTANTS ================= */

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const TIME_SLOTS = ["Morning", "Afternoon", "Evening", "Night"];
const HEATMAP_COLORS = [
  "bg-teal-500/20",
  "bg-yellow-500/20",
  "bg-orange-500/40",
  "bg-red-500/60",
];

/* ================= COMPONENT ================= */

export default function AdvancedAnalytics({ location, persona }) {
  const cityName = location?.name || "Mumbai";

  /* -------- UI State -------- */
  const [timeRange, setTimeRange] = useState(14);
  const [forecastHorizon, setForecastHorizon] = useState(6);
  const [selectedPollutant, setSelectedPollutant] = useState("pm25");

  /* -------- System State -------- */
  const [backendStatus, setBackendStatus] = useState("checking");

  /* -------- Data State -------- */
  const [historyData, setHistoryData] = useState([]);
  const [metrics, setMetrics] = useState({
    sarima: {},
    xgboost: {},
    hybrid: {},
  });
  const [featureImportance, setFeatureImportance] = useState([]);
  const [pollutantComposition, setPollutantComposition] = useState([]);
  const [heatmapData, setHeatmapData] = useState([]);
  const [currentAqi, setCurrentAqi] = useState(null);

  /* ================= INIT ================= */

  useEffect(() => {
    const init = async () => {
      try {
        const health = await analyticsService.checkHealth();
        setBackendStatus(health?.status === "healthy" ? "online" : "offline");

        const features = await analyticsService.getFeatureImportance();
        setFeatureImportance(features || []);

        const composition =
          await analyticsService.getPollutantComposition(cityName);
        setPollutantComposition(composition || []);

        const heatmap =
          await analyticsService.getTemporalHeatmap(cityName);
        setHeatmapData(heatmap || []);

      } catch (err) {
        console.warn("Analytics init failed", err);
        setBackendStatus("offline");
      }
    };

    init();
  }, [cityName]);

  /* ================= HISTORY ================= */

  useEffect(() => {
    const fetchHistory = async () => {
      const data = await analyticsService.getHistoricalAnalysis(
        timeRange,
        cityName
      );
      setHistoryData(data || []);

      if (data?.length) {
        setCurrentAqi(data[data.length - 1]?.aqi ?? null);
      }
    };

    fetchHistory();
  }, [timeRange, cityName]);

  /* ================= METRICS ================= */

  useEffect(() => {
    const fetchMetrics = async () => {
      if (historyData.length >= 20) {
        const data = await analyticsService.runModelComparison(
          historyData,
          forecastHorizon
        );
        setMetrics(data || {});
      } else {
        const data = await analyticsService.getModelMetrics(forecastHorizon);
        setMetrics(data || {});
      }
    };

    fetchMetrics();
  }, [historyData, forecastHorizon]);

  /* ================= RENDER ================= */

  return (
    <div className="w-full space-y-8 text-slate-300">

      {/* ---------- Backend Status ---------- */}
      <div className="flex justify-end items-center gap-2 text-xs">
        <span className="text-slate-500">Analytics Engine:</span>
        {backendStatus === "online" ? (
          <span className="flex items-center gap-1.5 text-green-400 font-bold bg-green-500/10 px-2.5 py-1 rounded-full border border-green-500/20">
            <Wifi size={12} /> ONLINE
          </span>
        ) : (
          <span className="flex items-center gap-1.5 text-red-400 font-bold bg-red-500/10 px-2.5 py-1 rounded-full border border-red-500/20">
            <WifiOff size={12} /> OFFLINE
          </span>
        )}
      </div>

      {/* ---------- AI BRIEFING ---------- */}
      <AeroIntelligenceBriefing
        city={cityName}
        persona={persona || "general"}
      />

      {/* ---------- HISTORICAL TREND ---------- */}
      <div className="glass-panel p-6 rounded-3xl border border-white/10">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <TrendingUp className="text-neon-teal" /> Historical Trends
          </h3>

          <select
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="bg-black/40 border border-white/10 rounded-lg px-3 py-1 text-xs"
          >
            <option value={7}>7 Days</option>
            <option value={14}>14 Days</option>
            <option value={30}>30 Days</option>
            <option value={90}>90 Days</option>
          </select>
        </div>

        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={historyData}>
              <CartesianGrid stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="date" fontSize={10} />
              <YAxis fontSize={10} />
              <Tooltip />
              <Area
                type="monotone"
                dataKey={selectedPollutant}
                stroke="#6366f1"
                fill="#6366f1"
                fillOpacity={0.2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ---------- FEATURE IMPORTANCE ---------- */}
      <div className="glass-panel p-6 rounded-3xl border border-white/10">
        <h3 className="text-md font-bold text-white mb-4">
          Explainable AI (XAI)
        </h3>

        <div className="h-[250px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart layout="vertical" data={featureImportance}>
              <XAxis type="number" hide />
              <YAxis
                dataKey="feature"
                type="category"
                width={120}
                fontSize={10}
              />
              <Tooltip />
              <Bar dataKey="score" fill="#ec4899" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ---------- HEATMAP ---------- */}
      <div className="glass-panel p-6 rounded-3xl border border-white/10">
        <h3 className="text-sm font-bold text-white mb-3">
          Temporal Pollution Density
        </h3>

        <div className="grid grid-cols-[auto_repeat(4,1fr)] gap-1">
          <div />
          {TIME_SLOTS.map((t) => (
            <div key={t} className="text-xs text-center text-slate-400">
              {t}
            </div>
          ))}

          {DAYS.map((day, d) => (
            <React.Fragment key={day}>
              <div className="text-xs text-slate-400">{day}</div>
              {heatmapData?.[d]?.map((v, i) => (
                <div
                  key={i}
                  className={`h-6 rounded ${HEATMAP_COLORS[v]}`}
                />
              ))}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* ---------- DATA QUALITY ---------- */}
      <div className="glass-panel p-6 rounded-3xl border border-white/10 text-center">
        <CheckCircle className="mx-auto text-neon-teal mb-2" />
        <p className="text-sm text-white">Live data verified</p>
        <p className="text-xs text-slate-500 flex justify-center gap-1 mt-1">
          <Database size={12} /> WAQI • <Clock size={12} /> ~1s latency
        </p>
      </div>
    </div>
  );
}
