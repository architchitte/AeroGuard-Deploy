export default function PollutantDetails() {
  const pollutants = [
    { name: 'PM2.5', value: 85, unit: 'μg/m³', status: 'Excessive', color: 'bg-red-500', severity: 'Critical' },
    { name: 'PM10', value: 142, unit: 'μg/m³', status: 'Excessive', color: 'bg-red-500', severity: 'Critical' },
    { name: 'O₃', value: 45, unit: 'ppb', status: 'Good', color: 'bg-green-500', severity: 'OK' },
    { name: 'NO₂', value: 38, unit: 'ppb', status: 'Moderate', color: 'bg-yellow-500', severity: 'Caution' },
  ];

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl p-6 shadow-2xl border border-slate-700">
      <div className="flex items-center gap-2 mb-6">
        <h3 className="text-lg font-bold text-white">Pollutant Details</h3>
        <span className="text-xl">💨</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {pollutants.map((pollutant, idx) => (
          <div
            key={idx}
            className="bg-slate-700/50 border border-slate-600 rounded-lg p-4 space-y-2"
          >
            <p className="text-slate-300 text-sm font-semibold">{pollutant.name}</p>
            <p className="text-2xl font-bold text-white">{pollutant.value}</p>
            <p className="text-xs text-slate-400">{pollutant.unit}</p>
            <div className="pt-2 border-t border-slate-600">
              <p className={`text-xs font-semibold ${
                pollutant.color === 'bg-red-500' ? 'text-red-400' :
                pollutant.color === 'bg-orange-500' ? 'text-orange-400' :
                pollutant.color === 'bg-yellow-500' ? 'text-yellow-400' :
                'text-green-400'
              }`}>
                {pollutant.status}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
