export default function ForecastCard() {
  const forecast = [
    { day: 'Today', aqi: 142, trend: '↑', status: 'Unhealthy' },
    { day: 'Tomorrow', aqi: 128, trend: '↓', status: 'Moderate' },
    { day: 'Wed', aqi: 95, trend: '↓', status: 'Moderate' },
    { day: 'Thu', aqi: 78, trend: '↓', status: 'Moderate' },
  ];

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl p-8 shadow-2xl border border-slate-700">
      <div className="flex items-center gap-2 mb-6">
        <h3 className="text-xl font-bold text-white">5-Day Forecast</h3>
        <span className="text-2xl">📈</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {forecast.map((item, idx) => (
          <div
            key={idx}
            className="bg-slate-700/50 rounded-lg p-4 border border-slate-600 hover:border-blue-500 transition-colors duration-200"
          >
            <p className="text-slate-300 text-sm font-semibold mb-3">{item.day}</p>
            <p className="text-3xl font-bold text-blue-400 mb-2">{item.aqi}</p>
            <div className="flex items-center justify-between">
              <span className="text-xl font-bold text-yellow-400">{item.trend}</span>
              <span className="text-xs text-slate-400">{item.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
