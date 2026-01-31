export default function ContributingFactors() {
  const factors = [
    { icon: '🚗', name: 'Traffic Emissions', status: 'High Impact', color: 'border-red-500/50 bg-red-500/10' },
    { icon: '💨', name: 'Low-Wind Speed', status: 'High Impact', color: 'border-red-500/50 bg-red-500/10' },
    { icon: '🏭', name: 'Industrial Activity', status: 'Moderate Impact', color: 'border-yellow-500/50 bg-yellow-500/10' },
    { icon: '🌡️', name: 'Temperature Inversion', status: 'Moderate Impact', color: 'border-yellow-500/50 bg-yellow-500/10' },
  ];

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl p-6 shadow-2xl border border-slate-700">
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
    </div>
  );
}
