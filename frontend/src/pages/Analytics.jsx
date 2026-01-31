export default function Analytics() {
  return (
    <div className="w-full .bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 min-h-screen">
      <div className="absolute inset-0 .bg-[radial-gradient(circle_at_top,_rgba(34,197,94,0.08),_transparent_55%)] pointer-events-none" />
      <div className="relative w-full px-4 sm:px-6 md:px-8 py-6 md:py-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl font-bold text-white mb-2">Analytics</h1>
          <p className="text-slate-400 mb-8">Historical trends and statistical analysis</p>
          <div className=".bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl p-12 shadow-2xl border border-slate-700 text-center">
            <p className="text-2xl text-slate-300 mb-2">📈</p>
            <p className="text-white font-semibold mb-2">Analytics Dashboard</p>
            <p className="text-slate-400 text-sm">Coming soon: Charts, graphs, and statistical analysis of air quality trends</p>
          </div>
        </div>
      </div>
    </div>
  );
}
