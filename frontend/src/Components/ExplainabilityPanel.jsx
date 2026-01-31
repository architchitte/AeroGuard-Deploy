export default function ExplainabilityPanel({ aqi }) {
  const factors = [
    { icon: '🚗', name: 'Traffic Emissions', status: 'High Impact', color: 'border-red-500/50 bg-red-500/10' },
    { icon: '💨', name: 'Low-Wind Speed', status: 'High Impact', color: 'border-red-500/50 bg-red-500/10' },
    { icon: '🏭', name: 'Industrial Activity', status: 'Moderate Impact', color: 'border-yellow-500/50 bg-yellow-500/10' },
    { icon: '🌡️', name: 'Temperature Inversion', status: 'Moderate Impact', color: 'border-yellow-500/50 bg-yellow-500/10' },
  ];

  return (
    <div className=".bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl p-6 shadow-2xl border border-slate-700">
      <div className="flex items-center gap-2 mb-6">
        <h3 className="text-lg font-bold text-white">Why is AQI elevated?</h3>
        <span className="text-xl">🔍</span>
      </div>

      <div className="space-y-3">
        {factors.map((factor, idx) => (
          <div
            key={idx}
            className={`${factor.color} border rounded-lg p-4 flex items-center gap-4 transition-all hover:scale-102`}
          >
            <span className="text-2xl">{factor.icon}</span>
            <div className="flex-1">
              <p className="text-white font-semibold text-sm">{factor.name}</p>
              <p className={`text-xs ${
                factor.status === 'High Impact' ? 'text-red-400' : 'text-yellow-400'
              }`}>
                {factor.status}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 pt-6 border-t border-slate-600">
        <div className="bg-slate-700/50 border border-teal-500/30 rounded-lg p-4 space-y-3">
          <p className="text-teal-300 text-sm leading-relaxed">
            Current air quality conditions are primarily driven by traffic emissions during peak hours, combined with meteorological conditions that facilitate pollutant dispersion.
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
    </div>
  );
}
