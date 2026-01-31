export default function AQIGauge({ value = 142, size = 'lg' }) {
  const getStatus = (aqi) => {
    if (aqi <= 50) return { text: 'Good', color: 'text-green-400', bg: 'bg-green-500/20' };
    if (aqi <= 100) return { text: 'Moderate', color: 'text-yellow-400', bg: 'bg-yellow-500/20' };
    if (aqi <= 150) return { text: 'Unhealthy for Sensitive', color: 'text-orange-400', bg: 'bg-orange-500/20' };
    return { text: 'Unhealthy', color: 'text-red-400', bg: 'bg-red-500/20' };
  };

  const status = getStatus(value);
  const sizeClasses = size === 'lg' ? 'w-48 h-48 text-6xl' : 'w-32 h-32 text-4xl';

  return (
    <div className="w-full">
      <p className="text-xs text-slate-400 uppercase tracking-widest font-semibold mb-4">Current Status</p>
      <h3 className="text-2xl font-bold text-white mb-6">Air Quality Index</h3>
      
      {/* AQI Circle with glow effect */}
      <div className="relative flex items-center justify-center py-6">
        <div className="absolute inset-0 bg-orange-500/20 blur-3xl rounded-full"></div>
        <div className={`relative ${sizeClasses} rounded-full bg-gradient-to-br from-orange-500/30 to-red-500/30 border-4 border-orange-500 flex items-center justify-center shadow-2xl shadow-orange-500/50`}>
          <div className="text-center">
            <p className="font-bold text-orange-400">{value}</p>
            <p className="text-lg text-orange-300/80 mt-2">AQI</p>
          </div>
        </div>
      </div>

      {/* Status Badge */}
      <div className="text-center space-y-3 mt-6">
        <div className={`inline-block px-4 py-2 ${status.bg} border border-orange-500/50 rounded-full`}>
          <p className={`${status.color} font-bold text-sm`}>⚠️ {status.text}</p>
        </div>
        <p className="text-slate-400 text-sm leading-relaxed">
          Sensitive groups may experience health effects. General public less likely to be affected.
        </p>
      </div>

      {/* Footer timestamp */}
      <div className="border-t border-slate-600 pt-4 mt-6">
        <p className="text-xs text-slate-500 text-center">
          ⏱️ Last updated: Just now
        </p>
      </div>
    </div>
  );
}
