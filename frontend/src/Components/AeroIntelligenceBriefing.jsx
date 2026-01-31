import React, { useState, useEffect } from "react";
import { Sparkles, Brain, ShieldAlert, CheckCircle, Info, ArrowRight } from "lucide-react";
import { analyticsService } from "../api/analyticsService";

export default function AeroIntelligenceBriefing({ city = "Mumbai", persona = "general" }) {
    const [loading, setLoading] = useState(true);
    const [briefing, setBriefing] = useState(null);

    // Map frontend IDs to backend requirements
    const personaMap = {
        'general': 'general_public',
        'vulnerable': 'elderly',
        'outdoor': 'athletes'
    };

    const targetPersona = personaMap[persona] || persona;

    useEffect(() => {
        const fetchBriefing = async () => {
            setLoading(true);
            const response = await analyticsService.getAIBriefing(city, targetPersona);
            if (response && response.data) {
                setBriefing(response.data);
            }
            setLoading(false);
        };
        fetchBriefing();
    }, [city, persona]);

    if (loading) {
        return (
            <div className="glass-panel p-6 rounded-3xl border border-indigo-500/30 bg-indigo-500/5 animate-pulse min-h-[200px] flex flex-col justify-center items-center gap-4">
                <Brain className="text-indigo-400 animate-bounce" size={32} />
                <p className="text-indigo-300 text-sm font-medium">Aero intelligence generating briefing...</p>
            </div>
        );
    }

    if (!briefing) return null;

    const { explanation, health_advisory } = briefing;
    const severityColor =
        health_advisory.severity === 'alert' ? 'text-red-400 border-red-500/30 bg-red-500/10' :
            health_advisory.severity === 'warning' ? 'text-orange-400 border-orange-500/30 bg-orange-500/10' :
                'text-green-400 border-green-500/30 bg-green-500/10';

    const SeverityIcon =
        health_advisory.severity === 'alert' ? ShieldAlert :
            health_advisory.severity === 'warning' ? Info :
                CheckCircle;

    return (
        <div className="relative group">
            {/* Animated Glow Effect */}
            <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-3xl blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>

            <div className="relative glass-panel p-6 rounded-3xl border border-white/10 bg-black/40 overflow-hidden">
                {/* Header */}
                <div className="flex justify-between items-center mb-4">
                    <div className="flex items-center gap-2">
                        <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400">
                            <Sparkles size={20} />
                        </div>
                        <h3 className="text-lg font-display font-bold text-white tracking-tight">
                            AeroIntelligence Briefing
                        </h3>
                    </div>
                    <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full border text-[10px] font-bold uppercase tracking-wider ${severityColor}`}>
                        <SeverityIcon size={12} />
                        {health_advisory.severity}
                    </div>
                </div>

                {/* AI Explanation Text */}
                <div className="mb-6">
                    <p className="text-slate-300 text-sm leading-relaxed italic">
                        "{explanation}"
                    </p>
                </div>

                {/* Recommendations */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-white/5">
                    <div>
                        <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2 flex items-center gap-1">
                            <Brain size={10} className="text-indigo-400" /> AI Insights
                        </h4>
                        <ul className="space-y-1.5">
                            {health_advisory.recommended_actions.map((action, i) => (
                                <li key={i} className="flex items-start gap-2 text-xs text-indigo-200">
                                    <ArrowRight size={12} className="mt-0.5 flex-shrink-0" />
                                    <span>{action}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                    <div>
                        <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Affected Groups</h4>
                        <div className="flex flex-wrap gap-1.5">
                            {health_advisory.affected_groups.map((group, i) => (
                                <span key={i} className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-slate-400 text-[10px]">
                                    {group}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Background Decoration */}
                <div className="absolute top-0 right-0 -mr-8 -mt-8 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl"></div>
            </div>
        </div>
    );
}
