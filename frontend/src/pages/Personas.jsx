export default function Personas() {
  return (
    <div className="w-full .bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 min-h-screen">
      <div className="absolute inset-0 .bg-[radial-gradient(circle_at_top,_rgba(34,197,94,0.08),_transparent_55%)] pointer-events-none" />
      <div className="relative w-full px-4 sm:px-6 md:px-8 py-6 md:py-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl font-bold text-white mb-2">Personas</h1>
          <p className="text-slate-400 mb-8">Personalized insights for different user groups</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {['👶 Children', '👨 Adults', '🏃 Athletes', '👴 Elderly'].map((persona, idx) => (
              <div key={idx} className=".bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl p-8 shadow-2xl border border-slate-700">
                <p className="text-3xl mb-3">{persona.split(' ')[0]}</p>
                <p className="text-white font-semibold text-lg mb-2">{persona.split(' ')[1]}</p>
                <p className="text-slate-400 text-sm">Customized health recommendations based on your profile</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
