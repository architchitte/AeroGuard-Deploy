import React, { useState, useEffect } from "react";
import { analyticsService } from "../api/analyticsService";

const SEV_CONFIG = {
  alert: { emoji: "🚨", color: "text-red-500", bg: "bg-red-500/10", border: "border-red-500/20", label: "Alert" },
  warning: { emoji: "⚠️", color: "text-orange-400", bg: "bg-orange-500/10", border: "border-orange-500/20", label: "Warning" },
  info: { emoji: "✅", color: "text-[#B51A2B]", bg: "bg-[#B51A2B]/10", border: "border-[#384358]/30", label: "Clear" },
};

export default function AeroIntelligenceBriefing({ city = "Mumbai", persona = "general" }) {
  const [loading, setLoading] = useState(true);
  const [briefing, setBriefing] = useState(null);

  const personaMap = { general: "general_public", vulnerable: "elderly", outdoor: "athletes" };

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const res = await analyticsService.getAIBriefing(city, personaMap[persona] || "general_public");
        const norm = res?.data?.explanation ? res.data : res?.explanation ? res : null;
        setBriefing(norm);
      } catch { setBriefing(null); }
      finally { setLoading(false); }
    })();
  }, [city, persona]);

  if (loading) return (
    <div className="space-y-3 animate-pulse">
      <div className="h-3 w-3/4 bg-[#242F49] rounded-full" />
      <div className="h-3 w-full bg-[#242F49] rounded-full" />
      <div className="h-3 w-2/3 bg-[#242F49] rounded-full" />
      <div className="h-3 w-1/2 bg-[#242F49] rounded-full opacity-50" />
    </div>
  );

  if (!briefing) return (
    <div className="py-6 text-center border border-dashed border-[#384358]/20 rounded-2xl">
      <p className="text-xl mb-2">🛰️</p>
      <span className="text-[10px] font-bold text-[#9BA3AF] italic">Syncing with AI intelligence layer…</span>
    </div>
  );

  const explanation = briefing.explanation || "Atmospheric conditions are stable. All monitoring parameters within normal operational bounds.";
  const sev = briefing.health_advisory?.severity || "info";
  const actions = briefing.health_advisory?.recommended_actions || [];
  const cfg = SEV_CONFIG[sev] || SEV_CONFIG.info;

  return (
    <div className="flex flex-col gap-4 h-full">
      {/* Severity badge */}
      <div className={`flex items-center gap-2 self-start px-3 py-1.5 rounded-full border text-xs font-black uppercase ${cfg.border} ${cfg.bg} ${cfg.color}`}>
        <span>{cfg.emoji}</span>
        <span>{cfg.label} <span className="cursive-accent normal-case tracking-normal text-sm ml-0.5">Advisory</span></span>
      </div>

      {/* Main explanation */}
      <p className="text-xs font-bold text-[#FFA586] leading-relaxed flex-1 italic">{explanation}</p>

      {/* Recommended actions */}
      {actions.length > 0 && (
        <div className="space-y-2">
          {actions.slice(0, 3).map((a, i) => (
            <div key={i} className="flex items-start gap-2 p-2.5 rounded-xl bg-[#101525]/60 border border-[#384358]/15">
              <span className="text-sm mt-0.5">
                {i === 0 ? "🎯" : i === 1 ? "💡" : "🔔"}
              </span>
              <p className="text-xs font-bold text-[#FFA586] leading-relaxed">{a}</p>
            </div>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between pt-3 border-t border-[#384358]/15 mt-auto">
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-[#B51A2B] animate-pulse" />
          <span className="text-[9px] font-black uppercase text-[#9BA3AF] tracking-widest">🧠 <span className="cursive-accent normal-case tracking-normal opacity-70">AERO-LVT4</span> Model</span>
        </div>
        <span className="text-[8px] font-black text-[#9BA3AF] opacity-40">© AeroGuard AI</span>
      </div>
    </div>
  );
}
