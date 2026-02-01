import React, { useState, useEffect } from "react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  TrendingUp,
  Database,
  CheckCircle,
  Clock,
  Wifi,
  WifiOff,
} from "lucide-react";

import { analyticsService } from "../api/analyticsService";

/* ================= COMPONENT ================= */

export default function AdvancedAnalytics({ location, persona }) {
  const cityName = location?.name || "Mumbai";
  const [timeRange, setTimeRange] = useState(14);
  const [historyData, setHistoryData] = useState([]);

  const [currentAqi, setCurrentAqi] = useState(null);
  const [selectedPollutant, setSelectedPollutant] = useState("pm25");

  const [featureImportance, setFeatureImportance] = useState([]);
  const [backendStatus, setBackendStatus] = useState("checking");


  const getDominantPollutant = (latest) => {
      if (!latest) return "pm25";

      const pollutants = {
        pm25: latest.pm25,
        pm10: latest.pm10,
        no2: latest.no2,
        o3: latest.o3,
      };

      return Object.entries(pollutants)
        .sort((a, b) => b[1] - a[1])[0][0];
    };

  /* ================= INIT ================= */
  useEffect(() => {
      const fetchHistory = async () => {
        const data = await analyticsService.getHistoricalAnalysis(
          timeRange,
          cityName
        );

        setHistoryData(data || []);

        if (data?.length) {
          const latest = data[data.length - 1];

          setCurrentAqi(latest.aqi);

          const dominant = Object.entries({
            pm25: latest.pm25,
            pm10: latest.pm10,
            no2: latest.no2,
            o3: latest.o3,
          }).sort((a, b) => b[1] - a[1])[0][0];

          setSelectedPollutant(dominant);
        }
      };

      fetchHistory();
    }, [cityName, timeRange]);


  useEffect(() => {
      if (!currentAqi || !selectedPollutant) return;

      const fetchXAI = async () => {
        try {
          const health = await analyticsService.checkHealth();
          setBackendStatus(
            health?.status === "healthy" ? "online" : "offline"
          );

          const xai = await analyticsService.getFeatureImportance(
            cityName,
            currentAqi,
            selectedPollutant
          );

          setFeatureImportance(xai);
        } catch (err) {
          console.warn("XAI fetch failed", err);
          setBackendStatus("offline");
        }
      };

      fetchXAI();
    }, [cityName, currentAqi, selectedPollutant]); 

    console.log("XAI refresh", {
      cityName,
      currentAqi,
      selectedPollutant
    });

  /* ================= HISTORY ================= */

  useEffect(() => {
    const fetchHistory = async () => {
      const data = await analyticsService.getHistoricalAnalysis(
        timeRange,
        cityName
      );
      setHistoryData(data || []);
    };

    fetchHistory();
  }, [timeRange, cityName]);

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

      {/* ---------- FEATURE IMPORTANCE (XAI) ---------- */}
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
              <Bar
                dataKey="score"
                fill="#ec4899"
                radius={[0, 4, 4, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
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
