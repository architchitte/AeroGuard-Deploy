import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { getMultiPersonaAdvice } from "../api/healthRiskService";

const RISK_CONFIG = {
  low: { emoji: "🟢", color: "text-[#B51A2B]", bg: "bg-[#B51A2B]/10", border: "border-[#384358]/30", label: "Low Risk" },
  moderate: { emoji: "🟡", color: "text-orange-400", bg: "bg-orange-500/10", border: "border-orange-500/25", label: "Moderate" },
  high: { emoji: "🟠", color: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/25", label: "High Risk" },
  hazardous: { emoji: "🔴", color: "text-red-700", bg: "bg-red-700/10", border: "border-red-700/25", label: "Hazardous" },
  default: { emoji: "⬛", color: "text-[#9BA3AF]", bg: "bg-[#242F49]", border: "border-[#384358]/20", label: "Normal" },
};
const getRisk = (r) => RISK_CONFIG[r?.toLowerCase()] || RISK_CONFIG.default;

const PERSONAS = [
  { id: "General Public", emoji: "🧑", label: "General" },
  { id: "Children", emoji: "👦", label: "Children" },
  { id: "Elderly", emoji: "👴", label: "Elderly" },
];

export default function PersonalizedHealthAdvice({ aqi = 100, location = "Your Area", hideLink = false }) {
  const navigate = useNavigate();
  const [advice, setAdvice] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const res = await getMultiPersonaAdvice(aqi, location, PERSONAS.map(p => p.id));
        setAdvice(res);
      } catch { /* silent */ }
      finally { setLoading(false); }
    })();
  }, [aqi, location]);

  if (loading) return (
    <div className="space-y-3">
      {[1, 2, 3].map(i => <div key={i} className="h-14 bg-[#242F49] rounded-xl animate-pulse" />)}
    </div>
  );

  return (
    <div className="space-y-3">
      {PERSONAS.map(({ id, emoji, label }) => {
        const d = advice?.[id];
        const risk = d?.aqi?.risk_level;
        const cfg = getRisk(risk);
        const text = d?.recommendations?.general_advice || "Standard precautions recommended for current AQI levels.";

        return (
          <div key={id}
            className={`p-3.5 rounded-xl border transition-all hover:scale-[1.01] cursor-default relative overflow-hidden group ${cfg.border} ${cfg.bg}`}>
            <div className={`absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-r from-transparent via-white/[0.02] to-transparent`} />
            <div className="flex justify-between items-center mb-1.5 relative">
              <div className="flex items-center gap-2">
                <span className="text-base">{emoji}</span>
                <div>
                  <p className="card-title text-sm">{label}</p>
                </div>
              </div>
              <div className={`flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-black uppercase text-glow ${cfg.color}`}>
                <span>{cfg.emoji}</span>
                <span>{cfg.label}</span>
              </div>
            </div>
            <p className="text-xs text-[#FFA586] leading-relaxed line-clamp-2 relative font-medium italic">{text}</p>
          </div>
        );
      })}

      {!hideLink && (
        <button onClick={() => navigate("/health-risk", { state: { location, aqi } })}
          className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl glass-panel border border-[#384358]/20 hover:border-[#B51A2B]/40 transition-all text-xs font-black text-[#FFA586] hover:text-[#B51A2B] mt-4 text-interactive">
          🏥 Full Health <span className="cursive-accent normal-case tracking-normal ml-1">Assessment</span> <ArrowRight size={12} />
        </button>
      )}

      <p className="text-[9px] text-[#9BA3AF] leading-relaxed text-center mt-1 font-bold">
        🤖 AI-derived · <span className="cursive-accent normal-case tracking-normal text-xs text-[#B51A2B]">cross-referenced</span> with live streams
      </p>
    </div>
  );
}
