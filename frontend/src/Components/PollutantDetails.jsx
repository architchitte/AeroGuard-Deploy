export default function PollutantDetails({ pollutants }) {
  if (!pollutants) return null;

  /* ---------------- STATUS LOGIC ---------------- */

  const getStatusMeta = (value, limit) => {
    if (value >= limit * 2) {
      return { label: "Critical", color: "text-red-400", bg: "bg-red-500/10" };
    }
    if (value >= limit) {
      return { label: "Caution", color: "text-orange-400", bg: "bg-orange-500/10" };
    }
    return { label: "Good", color: "text-green-400", bg: "bg-green-500/10" };
  };

  /* ---------------- BACKEND → FRONTEND KEY MAP ---------------- */
  // Backend sends: "PM2.5", "PM10", "NO2", "O3"
  // UI expects: pm25, pm10, no2, o3

  const BACKEND_KEY_MAP = {
    pm25: "PM2.5",
    pm10: "PM10",
    no2: "NO2",
    o3: "O3",
  };

  const CONFIG = [
    { key: "pm25", name: "PM2.5", unit: "μg/m³", limit: 60 },
    { key: "pm10", name: "PM10", unit: "μg/m³", limit: 100 },
    { key: "o3", name: "O₃", unit: "ppb", limit: 70 },
    { key: "no2", name: "NO₂", unit: "ppb", limit: 40 },
  ];

  /* ---------------- UI ---------------- */

  return (
    <div className=".bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl p-6 shadow-2xl border border-slate-700">
      <div className="flex items-center gap-2 mb-6">
        <h3 className="text-lg font-bold text-white">Pollutant Details</h3>
        <span className="text-xl">💨</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {CONFIG.map((cfg) => {
          const backendKey = BACKEND_KEY_MAP[cfg.key];
          const value = Number(pollutants?.[backendKey] ?? 0);

          const meta = getStatusMeta(value, cfg.limit);

          return (
            <div
              key={cfg.key}
              className={`border border-slate-600 rounded-lg p-4 space-y-2 ${meta.bg}`}
            >
              <p className="text-slate-300 text-sm font-semibold">
                {cfg.name}
              </p>

              <p className={`text-2xl font-bold ${meta.color}`}>
                {value}
              </p>

              <p className="text-xs text-slate-400">{cfg.unit}</p>

              <div className="pt-2 border-t border-slate-600">
                <p className={`text-xs font-semibold ${meta.color}`}>
                  {meta.label}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
