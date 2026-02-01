
export default function ForecastCard({ forecasts, loading }) {
  const getColor = (aqi) => {
    if (aqi >= 150) return "bg-red-500";
    if (aqi >= 100) return "bg-orange-500";
    if (aqi >= 50) return "bg-yellow-500";
    return "bg-green-500";
  };

  const getBgColor = (aqi) => {
    if (aqi >= 150) return "bg-red-500/20 border-red-500/50";
    if (aqi >= 100) return "bg-orange-500/20 border-orange-500/50";
    if (aqi >= 50) return "bg-yellow-500/20 border-yellow-500/50";
    return "bg-green-500/20 border-green-500/50";
  };

  const getTrendIcon = (trend) => {
    if (trend === "up") return "📈";
    if (trend === "down") return "📉";
    return "➖";
  };

  return (
    <div className=".bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl p-6 shadow-2xl border border-slate-700">
      <div className="flex items-center gap-2 mb-6">
        <h3 className="text-lg font-bold text-white">
          Next 6 Hours Forecast
        </h3>
        <span className="text-xl">📊</span>
      </div>

      {loading ? (
        <p className="text-xs text-slate-400 text-center">
          Generating forecast…
        </p>
      ) : forecasts.length === 0 ? (
        <p className="text-xs text-slate-500 text-center">
          Forecast unavailable
        </p>
      ) : (
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
          {forecasts.map((item, idx) => (
            <div
              key={idx}
              className={`${getBgColor(item.aqi)} border rounded-lg p-3 text-center transition-all hover:scale-105`}
            >
              <p className="text-slate-300 text-xs font-semibold mb-2">
                {item.time}
              </p>

              <div
                className={`${getColor(item.aqi)} w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-2 shadow-lg`}
              >
                <span className="text-white font-bold text-sm">
                  {item.aqi}
                </span>
              </div>

              <p className="text-slate-400 text-xs">
                {getTrendIcon(item.trend)}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}