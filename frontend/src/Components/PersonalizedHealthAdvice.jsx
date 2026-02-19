import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, AlertTriangle, Info, ArrowRight } from 'lucide-react';
import { getMultiPersonaAdvice } from '../api/healthRiskService';

export default function PersonalizedHealthAdvice({ aqi = 100, location = 'Your Area' }) {
  const navigate = useNavigate();
  const [healthAdvice, setHealthAdvice] = useState(null);
  const [loading, setLoading] = useState(true);

  const personaConfig = {
    'General Public': {
      icon: "🧑",
      age: "Aged 18–60",
      defaultAdvice: "Reduce prolonged or heavy exertion outdoors. Take more breaks and avoid high-traffic areas when possible."
    },
    'Children': {
      icon: "👶",
      age: "Aged 5–14",
      defaultAdvice: "Limit prolonged outdoor play. Keep children indoors as much as possible, especially during peak pollution hours."
    },
    'Elderly': {
      icon: "👴",
      age: "Aged 60+",
      defaultAdvice: "Stay indoors as much as possible. Use air purifiers and avoid exposure during high pollution periods."
    },
    'Athletes': {
      icon: "🏃",
      age: "Active Individuals",
      defaultAdvice: "Reduce workout intensity outdoors. Prefer indoor training or schedule workouts during early morning hours."
    }
  };

  useEffect(() => {
    const fetchHealthAdvice = async () => {
      setLoading(true);
      try {
        const personas = Object.keys(personaConfig);
        const advice = await getMultiPersonaAdvice(aqi, location, personas);
        setHealthAdvice(advice);
      } catch (error) {
        console.error('Failed to fetch health advice:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHealthAdvice();
  }, [aqi, location]);

  const getColorClass = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low':
        return 'border-green-500/40 bg-green-500/10';
      case 'moderate':
        return 'border-yellow-500/40 bg-yellow-500/10';
      case 'high':
        return 'border-orange-500/40 bg-orange-500/10';
      case 'hazardous':
        return 'border-red-500/40 bg-red-500/10';
      default:
        return 'border-slate-500/40 bg-slate-500/10';
    }
  };

  const getRiskIcon = (riskLevel) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low':
        return <Shield className="w-4 h-4 text-green-400" />;
      case 'moderate':
        return <Info className="w-4 h-4 text-yellow-400" />;
      case 'high':
      case 'hazardous':
        return <AlertTriangle className="w-4 h-4 text-red-400" />;
      default:
        return <Info className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-6">
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-white pl-7">
          Personalized Health Advice
        </h3>
        <div className="flex items-center gap-3">
          {healthAdvice && (
            <span className="text-xs text-slate-400">
              AQI: {aqi}
            </span>
          )}
          <button
            onClick={() => navigate('/health-risk', { state: { location, aqi } })}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 transition-colors group"
          >
            <span className="text-xs font-semibold text-cyan-400">View Details</span>
            <ArrowRight className="w-3 h-3 text-cyan-400 group-hover:translate-x-0.5 transition-transform" />
          </button>
        </div>
      </div>

      {/* LOADING STATE */}
      {loading && (
        <div className="space-y-5">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="rounded-xl border border-slate-700/40 bg-slate-800/20 p-5 animate-pulse">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-slate-700/40 rounded-lg"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-slate-700/40 rounded w-1/3"></div>
                  <div className="h-3 bg-slate-700/40 rounded w-1/4"></div>
                  <div className="h-3 bg-slate-700/40 rounded w-full"></div>
                  <div className="h-3 bg-slate-700/40 rounded w-5/6"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* CARDS */}
      {!loading && healthAdvice && (
        <div className="space-y-5">
          {Object.entries(personaConfig).map(([personaName, config]) => {
            const advice = healthAdvice[personaName];
            const riskLevel = advice?.aqi?.risk_level || 'Moderate';
            const colorClass = getColorClass(riskLevel);
            const recommendations = advice?.recommendations || {};
            const generalAdvice = recommendations.general_advice || config.defaultAdvice;
            const precautions = recommendations.precautions || [];

            return (
              <div
                key={personaName}
                className={`rounded-xl border ${colorClass} p-5 transition-all duration-300 hover:border-opacity-80 hover:scale-[1.02]`}
              >
                <div className="flex items-start gap-4">
                  <div className="text-3xl">{config.icon}</div>

                  <div className="flex-1 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <p className="text-white font-semibold text-base">
                          {personaName}
                        </p>
                        <span className="text-xs text-slate-400">
                          {config.age}
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        {getRiskIcon(riskLevel)}
                        <span className="text-xs text-slate-400 capitalize">
                          {riskLevel} Risk
                        </span>
                      </div>
                    </div>

                    <p className="text-xs uppercase tracking-widest text-slate-500">
                      Health Advisory
                    </p>

                    <p className="text-sm text-slate-300 leading-relaxed">
                      {generalAdvice}
                    </p>

                    {precautions.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-slate-700/40">
                        <p className="text-xs text-slate-400 mb-2">Precautions:</p>
                        <ul className="space-y-1">
                          {precautions.slice(0, 2).map((precaution, idx) => (
                            <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                              <span className="text-emerald-400 mt-0.5">•</span>
                              <span>{precaution}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ERROR STATE */}
      {!loading && !healthAdvice && (
        <div className="text-center py-8">
          <p className="text-slate-400 text-sm">
            Unable to load health advice. Please try again.
          </p>
        </div>
      )}
    </div>
  );
}
