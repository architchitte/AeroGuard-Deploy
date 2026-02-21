import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Shield, AlertTriangle, Heart, Activity, Users, TrendingUp, Info, MapPin, ArrowLeft, Clock } from 'lucide-react';
import healthRiskService, { getHealthRisk } from '../api/healthRiskService';
import { useForecast6h } from '../hooks/forcast6h.js';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export default function HealthRisk() {
  const location = useLocation();
  const navigate = useNavigate();

  // Get location from navigation state or default to null
  const dashboardLocation = location.state?.location || null;
  const dashboardAqi = location.state?.aqi || null;

  const [selectedPersona, setSelectedPersona] = useState('General Public');
  const [healthData, setHealthData] = useState(null);
  const [aqiData, setAqiData] = useState(dashboardAqi ? { aqi: dashboardAqi, category: location.state?.category } : null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [searchInput, setSearchInput] = useState('');
  const [activeLocation, setActiveLocation] = useState(dashboardLocation);

  const { forecast6h, summary, loading: forecastLoading } = useForecast6h(activeLocation ? { name: activeLocation } : null);

  const personas = [
    { id: 'General Public', label: 'General Public', icon: Users, color: 'cyan' },
    { id: 'Children', label: 'Children', icon: Heart, color: 'pink' },
    { id: 'Elderly', label: 'Elderly', icon: Shield, color: 'purple' },
    { id: 'Athletes', label: 'Athletes', icon: Activity, color: 'emerald' }
  ];

  useEffect(() => {
    if (activeLocation && !dashboardAqi) {
      fetchRealtimeAQI(activeLocation);
    } else if (dashboardAqi) {
      fetchHealthRisk();
    }
  }, [activeLocation, dashboardAqi]);

  useEffect(() => {
    if (aqiData) {
      fetchHealthRisk();
    }
  }, [aqiData, selectedPersona]);

  const fetchRealtimeAQI = async (locationName) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/v1/realtime-aqi/city/${locationName}`
      );

      if (response.data.status === 'success') {
        setAqiData(response.data.data);
      } else {
        setError('Failed to fetch AQI data');
      }
    } catch (err) {
      console.error('Failed to fetch AQI:', err);
      setError('Unable to fetch real-time AQI data. Please return to Dashboard and select a location.');
    } finally {
      setLoading(false);
    }
  };

  const fetchHealthRisk = async () => {
    if (!aqiData?.aqi) return;

    setLoading(true);
    setError(null);
    try {
      const locationName = activeLocation || 'Unknown';
      const data = await getHealthRisk(aqiData.aqi, locationName, 'PM2.5', selectedPersona);

      if (data && (data.health_assessment || data.recommendations || data.persona_advice)) {
        setHealthData(data);
      } else {
        // This should theoretically not happen as getHealthRisk has its own fallback
        setError('Failed to fetch health risk assessment');
      }
    } catch (err) {
      console.error('Failed to fetch health risk:', err);
      setError('Unable to complete health risk assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low': return 'from-green-500 to-emerald-600';
      case 'moderate': return 'from-yellow-500 to-orange-500';
      case 'high': return 'from-orange-500 to-red-500';
      case 'hazardous': return 'from-red-600 to-red-800';
      default: return 'from-slate-500 to-slate-600';
    }
  };

  const getRiskIcon = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low': return <Shield className="w-6 h-6" />;
      case 'moderate': return <Info className="w-6 h-6" />;
      case 'high':
      case 'hazardous': return <AlertTriangle className="w-6 h-6" />;
      default: return <Info className="w-6 h-6" />;
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      setActiveLocation(searchInput.trim());
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      <div className="max-w-7xl mx-auto space-y-6">

        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 transition-colors"
              title="Back to Dashboard"
            >
              <ArrowLeft className="w-5 h-5 text-slate-400" />
            </button>
            <h1 className="text-4xl md:text-5xl font-black text-white">
              Health Risk Assessment
            </h1>
          </div>
          <p className="text-slate-400 text-lg">
            AI-powered personalized health guidance based on air quality
          </p>
          {activeLocation && (
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 border border-emerald-500/20">
              <MapPin className="w-4 h-4 text-emerald-400" />
              <span className="text-sm font-semibold text-emerald-300">{activeLocation}</span>
            </div>
          )}
        </div>

        {/* Location Selector (Always show if no location active, or as an option) */}
        {!activeLocation && (
          <div className="glass-panel rounded-2xl p-8 max-w-2xl mx-auto">
            <div className="text-center mb-6">
              <MapPin className="w-12 h-12 text-cyan-500 mx-auto mb-3" />
              <h2 className="text-xl font-bold text-white">Enter Your Location</h2>
              <p className="text-slate-400 text-sm mt-1">
                Get personalized health advice for your area
              </p>
            </div>

            <form onSubmit={handleSearch} className="flex gap-2">
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="e.g. Delhi, Mumbai, Bangalore..."
                className="flex-1 px-4 py-3 rounded-xl bg-slate-800/50 border border-slate-700 text-white focus:outline-none focus:border-cyan-500 transition-colors"
              />
              <button
                type="submit"
                disabled={!searchInput.trim()}
                className="px-6 py-3 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold rounded-xl transition-all shadow-lg shadow-cyan-900/20"
              >
                Analyze
              </button>
            </form>

            <div className="mt-6 pt-6 border-t border-slate-800">
              <p className="text-xs text-slate-500 text-center uppercase tracking-widest mb-4">Popular Cities</p>
              <div className="flex flex-wrap justify-center gap-2">
                {['Delhi', 'Mumbai', 'Bangalore', 'Chennai'].map(city => (
                  <button
                    key={city}
                    onClick={() => setActiveLocation(city)}
                    className="px-3 py-1 rounded-full bg-slate-800 hover:bg-slate-700 text-xs text-slate-400 transition-colors"
                  >
                    {city}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Controls - Only show if we have location */}
        {activeLocation && (
          <div className="glass-panel rounded-2xl p-6 space-y-6">
            {/* Real-time AQI Display */}
            {aqiData && (
              <div className="p-4 rounded-xl bg-gradient-to-r from-cyan-500/10 to-emerald-500/10 border border-cyan-500/20">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">Real-time AQI</p>
                    <p className="text-4xl font-black text-white">{aqiData.aqi}</p>
                    <p className="text-sm text-slate-300 mt-1">{aqiData.category || 'Loading...'}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-slate-400 mb-1">Location</p>
                    <p className="text-sm text-white font-semibold">{activeLocation}</p>
                    <p className="text-xs text-slate-500 mt-1">
                      Updated: {new Date().toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Persona Selection */}
            <div className="space-y-3">
              <label className="text-sm font-semibold text-slate-300">
                Select Persona
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {personas.map((persona) => {
                  const Icon = persona.icon;
                  const isSelected = selectedPersona === persona.id;
                  return (
                    <button
                      key={persona.id}
                      onClick={() => setSelectedPersona(persona.id)}
                      className={`p-4 rounded-xl border-2 transition-all duration-300 ${isSelected
                        ? `border-${persona.color}-500 bg-${persona.color}-500/10`
                        : 'border-slate-700 bg-slate-800/30 hover:border-slate-600'
                        }`}
                    >
                      <Icon className={`w-6 h-6 mx-auto mb-2 ${isSelected ? `text-${persona.color}-400` : 'text-slate-400'
                        }`} />
                      <p className={`text-sm font-semibold ${isSelected ? 'text-white' : 'text-slate-400'
                        }`}>
                        {persona.label}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="glass-panel rounded-2xl p-6 border-red-500/20 bg-red-500/5 text-center">
            <AlertTriangle className="w-8 h-8 text-red-500 mx-auto mb-2" />
            <p className="text-red-400 font-medium">{error}</p>
            <button
              onClick={() => fetchHealthRisk()}
              className="mt-4 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm transition-colors"
            >
              Retry Assessment
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="glass-panel rounded-2xl p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto mb-4"></div>
            <p className="text-slate-400">Analyzing health risk...</p>
          </div>
        )}

        {/* Health Risk Results - Only show if we have location and data */}
        {activeLocation && !loading && healthData && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

            {/* Risk Overview Card */}
            <div className="lg:col-span-1">
              <div className={`glass-panel rounded-2xl p-6 bg-gradient-to-br ${getRiskColor(healthData.aqi?.risk_level)} bg-opacity-10`}>
                <div className="text-center space-y-4">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/10 backdrop-blur-sm">
                    {getRiskIcon(healthData.aqi?.risk_level)}
                  </div>

                  <div>
                    <h3 className="text-3xl font-bold text-white mb-1">
                      {healthData.aqi?.category}
                    </h3>
                    <p className="text-sm text-slate-300 uppercase tracking-wider">
                      {healthData.aqi?.risk_level} Risk Level
                    </p>
                  </div>

                  <div className="pt-4 border-t border-white/10">
                    <p className="text-xs text-slate-400 mb-2">AQI Value</p>
                    <p className="text-4xl font-black text-white">
                      {healthData.aqi?.value}
                    </p>
                  </div>

                  <div className="pt-4 space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-400">Primary Pollutant</span>
                      <span className="text-white font-semibold">
                        {healthData.aqi?.primary_pollutant}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-400">Model Source</span>
                      <span className="text-white font-semibold capitalize">
                        {healthData.model_source}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Health Assessment & Recommendations */}
            <div className="lg:col-span-2 space-y-6">

              {/* Health Assessment */}
              <div className="glass-panel rounded-2xl p-6 space-y-4">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <Heart className="w-5 h-5 text-red-400" />
                  Health Assessment
                </h3>

                <p className="text-slate-300 leading-relaxed">
                  {healthData.health_assessment?.description}
                </p>

                {healthData.health_assessment?.cautionary_statement && (
                  <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                    <p className="text-sm text-yellow-200">
                      <strong>Caution:</strong> {healthData.health_assessment.cautionary_statement}
                    </p>
                  </div>
                )}

                {healthData.health_assessment?.health_implications?.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-semibold text-slate-400">Health Implications:</p>
                    <ul className="space-y-1">
                      {healthData.health_assessment.health_implications.map((implication, idx) => (
                        <li key={idx} className="text-sm text-slate-300 flex items-start gap-2">
                          <span className="text-cyan-400 mt-1">•</span>
                          <span>{implication}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {healthData.health_assessment?.at_risk_groups?.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-semibold text-slate-400">At-Risk Groups:</p>
                    <div className="flex flex-wrap gap-2">
                      {healthData.health_assessment.at_risk_groups.map((group, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 rounded-full bg-red-500/10 border border-red-500/30 text-xs text-red-300"
                        >
                          {group}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Recommendations */}
              <div className="glass-panel rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-emerald-400" />
                    Recommendations
                  </h3>
                  <span className="px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-[10px] font-bold text-cyan-400 uppercase">
                    For {selectedPersona}
                  </span>
                </div>

                {/* Persona-Specific Advice (if available) */}
                {healthData.persona_advice && (
                  <div className="p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/30">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="w-4 h-4 text-indigo-400" />
                      <p className="text-xs font-bold text-indigo-300 uppercase">Personalized Insight</p>
                    </div>
                    <p className="text-sm text-slate-200 leading-relaxed font-medium">
                      {healthData.persona_advice.advice || healthData.persona_advice}
                    </p>
                  </div>
                )}

                <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30">
                  <p className="text-sm text-emerald-200">
                    {healthData.recommendations?.general_advice || "Follow general air quality precautions."}
                  </p>
                </div>

                {healthData.recommendations?.precautions?.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-semibold text-slate-400">Targeted Precautions:</p>
                    <ul className="space-y-2">
                      {healthData.recommendations.precautions.map((precaution, idx) => (
                        <li key={idx} className="text-sm text-slate-300 flex items-start gap-2 p-3 rounded-lg bg-slate-800/50">
                          <Shield className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />
                          <span>{precaution}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {healthData.recommendations?.activity_recommendations && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {Object.entries(healthData.recommendations.activity_recommendations).map(([key, value]) => (
                      <div key={key} className="p-3 rounded-lg bg-slate-800/50 border border-slate-700">
                        <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">
                          {key.replace('_', ' ')}
                        </p>
                        <p className="text-sm text-slate-200">
                          {typeof value === 'object' ? JSON.stringify(value) : value}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* 6-Hour Forecast Trend */}
              <div className="glass-panel rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    <Clock className="w-5 h-5 text-cyan-400" />
                    6-Hour Health Trend
                  </h3>
                  {forecast6h.length > 0 && (
                    <div className={`px-2 py-1 rounded text-[10px] font-bold uppercase ${forecast6h[forecast6h.length - 1].aqi > forecast6h[0].aqi ? 'text-red-400 bg-red-400/10' : 'text-emerald-400 bg-emerald-400/10'
                      }`}>
                      {forecast6h[forecast6h.length - 1].aqi > forecast6h[0].aqi ? 'Worsening' : 'Improving'}
                    </div>
                  )}
                </div>

                <div className="h-64 mt-4">
                  {forecastLoading ? (
                    <div className="flex items-center justify-center h-full">
                      <Activity className="w-8 h-8 text-cyan-500 animate-spin" />
                    </div>
                  ) : forecast6h.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
                      <AreaChart data={forecast6h}>
                        <defs>
                          <linearGradient id="healthTrendGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#22d3ee" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <XAxis dataKey="hour" stroke="#475569" fontSize={10} />
                        <YAxis stroke="#475569" fontSize={10} />
                        <Tooltip
                          contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }}
                          labelStyle={{ color: '#94a3b8' }}
                        />
                        <Area
                          type="monotone"
                          dataKey="aqi"
                          stroke="#22d3ee"
                          fill="url(#healthTrendGradient)"
                          strokeWidth={2}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className="text-center text-slate-500 text-sm py-12">Trend data temporarily unavailable</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Model Info Footer */}
        {healthData && (
          <div className="glass-panel rounded-xl p-4 text-center">
            <p className="text-xs text-slate-400">
              Powered by ML-based health risk assessment model •
              Confidence: <span className="text-cyan-400 font-semibold capitalize">{healthData.model_confidence}</span> •
              Updated: {new Date(healthData.timestamp).toLocaleString()}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

