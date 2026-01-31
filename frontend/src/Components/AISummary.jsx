export default function AISummary() {
  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl p-6 shadow-2xl border border-slate-700">
      <div className="flex items-center gap-2 mb-4">
        <h3 className="text-lg font-bold text-white">AI Summary</h3>
        <span className="text-xl">🤖</span>
      </div>

      <div className="bg-slate-700/50 border border-teal-500/30 rounded-lg p-4 space-y-3">
        <p className="text-slate-200 text-sm leading-relaxed">
          Current air quality conditions are primarily driven by traffic emissions during peak hours, combined with meteorological conditions that facilitate pollutant dispersion. Expect improvements after 9 PM as traffic decreases.
        </p>
        
        <div className="grid grid-cols-3 gap-4 pt-3 border-t border-slate-600">
          <div className="text-center">
            <p className="text-xs text-slate-400 mb-1">Peak Time</p>
            <p className="text-sm font-bold text-teal-400">5-9 PM</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-400 mb-1">Forecast</p>
            <p className="text-sm font-bold text-teal-400">↓ Improving</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-400 mb-1">Confidence</p>
            <p className="text-sm font-bold text-teal-400">95%</p>
          </div>
        </div>
      </div>
    </div>
  );
}
