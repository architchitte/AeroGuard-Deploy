export default function PollutantDetails({ pollutants }) {
  if (!pollutants) return null;

  const getStatusMeta = (value, limit) => {
    if (value >= limit * 2) return { label: "Critical", color: "text-red-400", bg: "bg-red-500/10" };
    if (value >= limit) return { label: "Caution", color: "text-orange-400", bg: "bg-orange-500/10" };
    return { label: "Good", color: "text-green-400", bg: "bg-green-500/10" };
  };

  const CONFIG = [
    { key: "pm25", backend: "pm25", name: "PM2.5", unit: "μg/m³", limit: 60 },
    { key: "pm10", backend: "pm10", name: "PM10", unit: "μg/m³", limit: 100 },
    { key: "o3", backend: "o3", name: "O₃", unit: "ppb", limit: 70 },
    { key: "no2", backend: "no2", name: "NO₂", unit: "ppb", limit: 40 },
  ];

  return (
    <div className=".bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl p-6 shadow-2xl border border-slate-700">
      <h3 className="text-lg font-bold text-white mb-6">Pollutant Details 💨</h3>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {CONFIG.map(cfg => {
          const value = Number(pollutants?.[cfg.backend] ?? 0);
          const meta = getStatusMeta(value, cfg.limit);

          return (
            <div key={cfg.key} className={`border border-slate-600 rounded-lg p-4 ${meta.bg}`}>
              <p className="text-slate-300 text-sm font-semibold">{cfg.name}</p>
              <p className={`text-2xl font-bold ${meta.color}`}>{value}</p>
              <p className="text-xs text-slate-400">{cfg.unit}</p>
              <p className={`text-xs font-semibold mt-2 ${meta.color}`}>{meta.label}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
