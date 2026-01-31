export default function Alerts() {
  return (
    <div className="w-full bg-linear-to-br from-slate-950 via-slate-900 to-slate-950 min-h-screen">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(34,197,94,0.08),transparent_55%)] pointer-events-none" />
      <div className="relative w-full px-4 sm:px-6 md:px-8 py-6 md:py-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl font-bold text-white mb-2">Alerts</h1>
          <p className="text-slate-400 mb-8">Real-time notifications and air quality warnings</p>
          <div className="space-y-4">
            {[
              { icon: '🔴', title: 'Unhealthy Alert', desc: 'AQI exceeds 150 in your area', time: '2 hours ago' },
              { icon: '🟠', title: 'Moderate Warning', desc: 'AQI between 100-150, sensitive groups affected', time: '4 hours ago' },
              { icon: '🟡', title: 'Information', desc: 'Air quality expected to improve by evening', time: '6 hours ago' }
            ].map((alert, idx) => (
              <div key={idx} className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl p-6 shadow-2xl border border-slate-700 flex items-start gap-4">
                <span className="text-3xl">{alert.icon}</span>
                <div className="flex-1">
                  <p className="text-white font-semibold">{alert.title}</p>
                  <p className="text-slate-400 text-sm">{alert.desc}</p>
                  <p className="text-slate-500 text-xs mt-2">{alert.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}