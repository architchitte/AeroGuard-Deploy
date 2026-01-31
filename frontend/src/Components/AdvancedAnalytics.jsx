import React, { useState, useMemo, useEffect } from "react";
import {
    LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area
} from "recharts";
import {
    BrainCircuit, TrendingUp, AlertTriangle, Activity, Database, CheckCircle, Calendar, Clock, BarChart3, Wind, Server, Wifi, WifiOff
} from "lucide-react";
import { analyticsService } from "../api/analyticsService";
import AeroIntelligenceBriefing from "./AeroIntelligenceBriefing";

// --- MOCK DATA ---

// 1. Historical Trends (Generated for flexibility)
const generateHistoryData = (days) => {
    const data = [];
    const now = new Date();
    for (let i = days; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        data.push({
            date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
            pm25: Math.floor(Math.random() * 150) + 50,
            pm10: Math.floor(Math.random() * 200) + 80,
            no2: Math.floor(Math.random() * 80) + 20,
            o3: Math.floor(Math.random() * 60) + 10,
        });
    }
    return data;
};

// 2. Feature Importance
const FEATURE_IMPORTANCE = [
    { feature: "Previous AQI (t-1)", score: 0.85 },
    { feature: "Wind Speed", score: 0.62 },
    { feature: "Traffic Density", score: 0.58 },
    { feature: "Humidity", score: 0.45 },
    { feature: "Hour of Day", score: 0.38 },
];

// 3. Model Comparison Metrics
const MODEL_METRICS = {
    6: {
        sarima: { prediction: 145, mae: 12.4, rmse: 15.2, r2: 0.82, uncertainty: 15 },
        xgboost: { prediction: 142, mae: 8.5, rmse: 10.1, r2: 0.89, uncertainty: 8 },
        hybrid: { prediction: 143, mae: 5.2, rmse: 6.8, r2: 0.94, uncertainty: 5 },
    },
    12: {
        sarima: { prediction: 160, mae: 18.1, rmse: 22.5, r2: 0.75, uncertainty: 25 },
        xgboost: { prediction: 155, mae: 14.2, rmse: 18.3, r2: 0.81, uncertainty: 15 },
        hybrid: { prediction: 158, mae: 9.8, rmse: 12.4, r2: 0.88, uncertainty: 10 },
    },
    24: {
        sarima: { prediction: 185, mae: 25.4, rmse: 30.1, r2: 0.65, uncertainty: 40 },
        xgboost: { prediction: 175, mae: 20.5, rmse: 24.8, r2: 0.72, uncertainty: 25 },
        hybrid: { prediction: 180, mae: 15.2, rmse: 18.5, r2: 0.81, uncertainty: 18 },
    }
};

// 4. Pollutant Composition
const POLLUTANT_COMPOSITION = [
    { name: 'PM2.5', value: 45, color: '#f43f5e' },
    { name: 'PM10', value: 30, color: '#f97316' },
    { name: 'NO2', value: 15, color: '#eab308' },
    { name: 'O3', value: 10, color: '#14b8a6' },
];

// 5. Heatmap Data (Day x Hour)
const HEATMAP_DATA = Array.from({ length: 7 }, (_, day) =>
    Array.from({ length: 4 }, (_, slot) => Math.floor(Math.random() * 4)) // 0: Low, 1: Mod, 2: High, 3: Haz
);
const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const TIME_SLOTS = ['Morning', 'Afternoon', 'Evening', 'Night'];
const HEATMAP_COLORS = ['bg-teal-500/20', 'bg-yellow-500/20', 'bg-orange-500/40', 'bg-red-500/60'];

export default function AdvancedAnalytics() {
    const [timeRange, setTimeRange] = useState(14);
    const [forecastHorizon, setForecastHorizon] = useState(6);
    const [selectedPollutant, setSelectedPollutant] = useState('pm25');

    // Backend Integration State
    const [backendStatus, setBackendStatus] = useState('checking');
    const [availableModels, setAvailableModels] = useState([]);

    // Data State
    const [historyData, setHistoryData] = useState([]);
    const [metrics, setMetrics] = useState({
        sarima: { prediction: 0, mae: 0, rmse: 0, r2: 0, uncertainty: 0 },
        xgboost: { prediction: 0, mae: 0, rmse: 0, r2: 0, uncertainty: 0 },
        hybrid: { prediction: 0, mae: 0, rmse: 0, r2: 0, uncertainty: 0 }
    });
    const [featureImportance, setFeatureImportance] = useState([]);
    const [pollutantComposition, setPollutantComposition] = useState([]);

    // 1. Initial System Check
    useEffect(() => {
        const init = async () => {
            const health = await analyticsService.checkHealth();
            setBackendStatus(health.status === 'healthy' ? 'online' : 'offline');

            const models = await analyticsService.getAvailableModels();
            setAvailableModels(models);

            const composition = await analyticsService.getPollutantComposition();
            setPollutantComposition(composition);

            const features = await analyticsService.getFeatureImportance();
            setFeatureImportance(features);
        };
        init();
    }, []);

    // 2. Fetch History when timeRange changes
    useEffect(() => {
        const fetchHistory = async () => {
            const data = await analyticsService.getHistoricalAnalysis(timeRange);
            setHistoryData(data);
        };
        fetchHistory();
    }, [timeRange]);

    // 3. Fetch Metrics when horizon changes
    useEffect(() => {
        const fetchMetrics = async () => {
            const data = await analyticsService.getModelMetrics(forecastHorizon);
            setMetrics(data);
        };
        fetchMetrics();
    }, [forecastHorizon]);

    return (
        <div className="w-full space-y-8 text-slate-300">

            {/* Backend Status Indicator */}
            <div className="flex justify-end items-center gap-2 text-xs mb-4">
                <span className="text-slate-500">Analytics Engine:</span>
                {backendStatus === 'online' ? (
                    <span className="flex items-center gap-1.5 text-green-400 font-bold bg-green-500/10 px-2.5 py-1 rounded-full border border-green-500/20">
                        <Wifi size={12} /> ONLINE
                    </span>
                ) : backendStatus === 'checking' ? (
                    <span className="flex items-center gap-1.5 text-yellow-400 font-bold bg-yellow-500/10 px-2.5 py-1 rounded-full border border-yellow-500/20 animate-pulse">
                        <Activity size={12} /> CONNECTING...
                    </span>
                ) : (
                    <span className="flex items-center gap-1.5 text-red-400 font-bold bg-red-500/10 px-2.5 py-1 rounded-full border border-red-500/20">
                        <WifiOff size={12} /> OFFLINE (Demo Mode)
                    </span>
                )}
            </div>

            {/* AI Powered Insights Briefing */}
            <AeroIntelligenceBriefing city="Mumbai" persona="outdoor_athlete" />

            {/* 1. CHART: Historical Trends */}
            <div className="glass-panel p-6 rounded-3xl border border-white/10">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
                    <div>
                        <h3 className="text-xl font-display font-bold text-white flex items-center gap-2">
                            <TrendingUp className="text-neon-teal" /> Historical Trend Analysis
                        </h3>
                        <p className="text-xs text-slate-500 mt-1">Observed pollutant levels over selected timeframe.</p>
                    </div>

                    <div className="flex flex-wrap gap-2">
                        <select
                            className="bg-black/40 border border-white/10 rounded-lg px-3 py-1 text-xs focus:ring-1 focus:ring-neon-teal outline-none"
                            value={timeRange}
                            onChange={(e) => setTimeRange(Number(e.target.value))}
                        >
                            <option value={7}>Last 7 Days</option>
                            <option value={14}>Last 14 Days</option>
                            <option value={30}>Last 30 Days</option>
                            <option value={90}>Last 3 Months</option>
                        </select>

                        <div className="flex bg-black/40 rounded-lg p-1 border border-white/10">
                            {['pm25', 'pm10', 'no2', 'o3'].map(p => (
                                <button
                                    key={p}
                                    onClick={() => setSelectedPollutant(p)}
                                    className={`px-3 py-1 rounded text-xs font-bold transition-all uppercase ${selectedPollutant === p ? 'bg-indigo-500 text-white shadow-lg' : 'text-slate-500 hover:text-white'}`}
                                >
                                    {p}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                <div style={{ width: '100%', height: 300 }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={historyData}>
                            <defs>
                                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                            <XAxis dataKey="date" stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} />
                            <YAxis stroke="#64748b" fontSize={10} tickLine={false} axisLine={false} label={{ value: 'Concentration (µg/m³)', angle: -90, position: 'insideLeft', style: { fill: '#475569', fontSize: 10 } }} />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#020617', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px' }}
                                itemStyle={{ color: '#fff' }}
                            />
                            <Area type="monotone" dataKey={selectedPollutant} stroke="#6366f1" fillOpacity={1} fill="url(#colorValue)" strokeWidth={2} />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* 2. FORECASTING MODELS COMPARISON */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Controls Header (Spans full width visually) */}
                <div className="lg:col-span-3 flex justify-between items-center">
                    <h3 className="text-xl font-display font-bold text-white flex items-center gap-2">
                        <BrainCircuit className="text-purple-400" /> Forecasting Models Leaderboard
                    </h3>
                    <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-500">Forecast Horizon:</span>
                        <select
                            className="bg-black/40 border border-white/10 rounded-lg px-3 py-1 text-xs text-white outline-none focus:border-purple-500"
                            value={forecastHorizon}
                            onChange={(e) => setForecastHorizon(Number(e.target.value))}
                        >
                            <option value={6}>Next 6 Hours</option>
                            <option value={12}>Next 12 Hours</option>
                            <option value={24}>Next 24 Hours</option>
                        </select>
                    </div>
                </div>

                {/* Model Cards */}
                {[
                    { id: 'sarima', name: 'SARIMA (Statistical)', color: 'border-cyan-500/50', text: 'text-cyan-400', bg: 'bg-cyan-950/20' },
                    { id: 'xgboost', name: 'XGBoost (ML)', color: 'border-purple-500/50', text: 'text-purple-400', bg: 'bg-purple-950/20' },
                    { id: 'hybrid', name: 'AeroGuard Hybrid', color: 'border-orange-500/50', text: 'text-orange-400', bg: 'bg-orange-950/20', isWinner: true }
                ].map(model => (
                    <div key={model.id} className={`glass-panel p-6 rounded-2xl border ${model.color} ${model.bg} relative overflow-hidden group`}>
                        {model.isWinner && (
                            <div className="absolute top-0 right-0 bg-orange-500 text-white text-[10px] font-bold px-2 py-1 rounded-bl-lg shadow-lg z-10">
                                TOP PERFORMER
                            </div>
                        )}
                        <h4 className={`text-sm font-bold ${model.text} mb-4 flex items-center gap-2`}>
                            {model.name}
                        </h4>

                        <div className="flex items-end justify-between mb-4">
                            <div>
                                <span className="text-[10px] text-slate-400 uppercase tracking-widest">Predicted AQI</span>
                                <p className="text-4xl font-display font-bold text-white mt-1">
                                    {metrics[model.id].prediction}
                                    <span className="text-xs text-slate-500 ml-2 font-normal">± {metrics[model.id].uncertainty}</span>
                                </p>
                            </div>
                            <div className="text-right">
                                <div className="radial-progress text-xs" style={{ "--value": metrics[model.id].r2 * 100, "--size": "2rem" }} role="progressbar">
                                    {(metrics[model.id].r2 * 100).toFixed(0)}%
                                </div>
                            </div>
                        </div>

                        <div className="space-y-2 pt-4 border-t border-white/5">
                            <div className="flex justify-between text-xs">
                                <span className="text-slate-400">RMSE (Error):</span>
                                <span className="text-white font-mono">{metrics[model.id].rmse}</span>
                            </div>
                            <div className="flex justify-between text-xs">
                                <span className="text-slate-400">MAE (Accuracy):</span>
                                <span className="text-white font-mono">{metrics[model.id].mae}</span>
                            </div>
                            <div className="w-full bg-black/40 rounded-full h-1 mt-2 overflow-hidden">
                                <div
                                    className={`h-full ${model.text.replace('text', 'bg')}`}
                                    style={{ width: `${metrics[model.id].r2 * 100}%` }}
                                />
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* 3. FEATURE IMPORTANCE & BREAKDOWN */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Feature Importance */}
                <div className="glass-panel p-6 rounded-3xl border border-white/10">
                    <h3 className="text-md font-bold text-white mb-6 flex items-center gap-2">
                        <Activity size={18} className="text-pink-400" /> Explainable AI (XAI)
                    </h3>
                    <div style={{ width: '100%', height: 250 }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart layout="vertical" data={featureImportance} margin={{ left: 40 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255,255,255,0.05)" />
                                <XAxis type="number" hide />
                                <YAxis dataKey="feature" type="category" width={100} tick={{ fill: '#94a3b8', fontSize: 10 }} tickLine={false} axisLine={false} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#020617', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px' }}
                                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                />
                                <Bar dataKey="score" fill="#ec4899" radius={[0, 4, 4, 0]} barSize={20} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Pollutant Breakdown & Heatmap */}
                <div className="space-y-6">

                    {/* Breakdown */}
                    <div className="glass-panel p-5 rounded-3xl border border-white/10 flex items-center gap-6">
                        <div style={{ width: 128, height: 128, flexShrink: 0 }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={pollutantComposition}
                                        innerRadius={30}
                                        outerRadius={50}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {pollutantComposition.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} stroke="rgba(0,0,0,0.5)" />
                                        ))}
                                    </Pie>
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="flex-1 space-y-2">
                            <h4 className="text-sm font-bold text-white">Pollutant Ratios</h4>
                            <div className="grid grid-cols-2 gap-2">
                                {pollutantComposition.map(p => (
                                    <div key={p.name} className="flex items-center gap-2 text-xs text-slate-400">
                                        <div className="w-2 h-2 rounded-full" style={{ background: p.color }} />
                                        <span>{p.name} ({p.value}%)</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Pattern Heatmap Matrix */}
                    <div className="glass-panel p-5 rounded-3xl border border-white/10">
                        <div className="flex justify-between items-center mb-3">
                            <h4 className="text-xs font-bold text-slate-400 uppercase">Temporal Density</h4>
                            <div className="flex gap-1">
                                {['Low', 'Mod', 'High', 'Haz'].map((l, i) => (
                                    <div key={l} className={`w-2 h-2 rounded-full ${HEATMAP_COLORS[i]}`} title={l} />
                                ))}
                            </div>
                        </div>
                        <div className="overflow-x-auto">
                            <div className="grid grid-cols-[auto_repeat(4,1fr)] gap-1 min-w-[300px]">
                                {/* Header */}
                                <div className="text-[9px] text-slate-600"></div>
                                {TIME_SLOTS.map(t => <div key={t} className="text-[9px] text-center text-slate-500 font-medium">{t.slice(0, 3)}</div>)}

                                {/* Rows */}
                                {DAYS.map((day, dIndex) => (
                                    <React.Fragment key={day}>
                                        <div className="text-[10px] text-slate-400 font-medium py-1">{day}</div>
                                        {HEATMAP_DATA[dIndex].map((intensity, hIndex) => (
                                            <div
                                                key={`${day}-${hIndex}`}
                                                className={`rounded-md h-full w-full min-h-[20px] ${HEATMAP_COLORS[intensity]} transition-all hover:brightness-125 cursor-help`}
                                                title={`${day} ${TIME_SLOTS[hIndex]}: Level ${intensity}`}
                                            />
                                        ))}
                                    </React.Fragment>
                                ))}
                            </div>
                        </div>
                    </div>

                </div>
            </div>

            {/* 4. HEALTH IMPACT & DATA QUALITY */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Persona Risk Table */}
                <div className="lg:col-span-3 glass-panel p-6 rounded-3xl border border-white/10">
                    <h3 className="text-md font-bold text-white mb-4 flex items-center gap-2">
                        <AlertTriangle size={18} className="text-orange-400" /> Exposure Risk Assessment
                    </h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="text-xs text-slate-500 border-b border-white/5">
                                    <th className="py-2 font-medium">Population Group</th>
                                    <th className="py-2 font-medium">Risk Level</th>
                                    <th className="py-2 font-medium">Max Exposure Time</th>
                                    <th className="py-2 font-medium">Primary Symptom</th>
                                </tr>
                            </thead>
                            <tbody className="text-sm">
                                <tr className="border-b border-white/5 group hover:bg-white/5">
                                    <td className="py-3 text-white font-medium">Children & Elderly</td>
                                    <td className="py-3"><span className="px-2 py-0.5 rounded bg-red-500/20 text-red-400 text-xs border border-red-500/30">High</span></td>
                                    <td className="py-3 text-slate-400">15 mins</td>
                                    <td className="py-3 text-slate-400">Respiratory Irritation</td>
                                </tr>
                                <tr className="border-b border-white/5 group hover:bg-white/5">
                                    <td className="py-3 text-white font-medium">Outdoor Athletes</td>
                                    <td className="py-3"><span className="px-2 py-0.5 rounded bg-orange-500/20 text-orange-400 text-xs border border-orange-500/30">Moderate</span></td>
                                    <td className="py-3 text-slate-400">45 mins</td>
                                    <td className="py-3 text-slate-400">Reduced Lung Function</td>
                                </tr>
                                <tr className="group hover:bg-white/5">
                                    <td className="py-3 text-white font-medium">General Public</td>
                                    <td className="py-3"><span className="px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-400 text-xs border border-yellow-500/30">Low</span></td>
                                    <td className="py-3 text-slate-400">2 Hours</td>
                                    <td className="py-3 text-slate-400">Eye Irritation</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Data Quality */}
                <div className="glass-panel p-6 rounded-3xl border border-white/10 flex flex-col justify-center items-center text-center">
                    <div className="relative w-24 h-24 flex items-center justify-center mb-4">
                        <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                            <path className="text-slate-800" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3" />
                            <path className="text-neon-teal drop-shadow-lg" strokeDasharray="92, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3" />
                        </svg>
                        <div className="absolute flex flex-col items-center">
                            <span className="text-2xl font-bold text-white">92%</span>
                            <span className="text-[8px] text-slate-500 uppercase">Confidence</span>
                        </div>
                    </div>

                    <div className="w-full space-y-3">
                        <div className="flex justify-between items-center text-xs border-b border-white/5 pb-2">
                            <span className="text-slate-500 flex items-center gap-1"><Database size={10} /> Source</span>
                            <span className="text-white font-mono">WAQI Live</span>
                        </div>
                        <div className="flex justify-between items-center text-xs pb-1">
                            <span className="text-slate-500 flex items-center gap-1"><Clock size={10} /> Latency</span>
                            <span className="text-neon-teal font-mono">1.2s</span>
                        </div>
                        <div className="text-[10px] bg-green-500/10 text-green-400 py-1 rounded border border-green-500/20 w-full flex items-center justify-center gap-1">
                            <CheckCircle size={10} /> System Operational
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
