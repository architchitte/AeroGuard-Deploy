import { Link, useLocation } from "react-router-dom";

export default function Sidebar() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  const navItems = [
    { path: '/', icon: '📊', label: 'Dashboard' },
    { path: '/heatmap', icon: '🗺️', label: 'Heatmap' },
    { path: '/analytics', icon: '📈', label: 'Analytics' },
    { path: '/personas', icon: '👥', label: 'Personas' },
    { path: '/alerts', icon: '🔔', label: 'Alerts' },
  ];

  return (
    <aside className="w-64 min-h-screen bg-gradient-to-b from-slate-950 to-slate-900 border-r border-slate-700 flex flex-col shadow-xl">
      {/* Logo */}
      <div className="p-6 border-b border-slate-700">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-3xl">🌍</span>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-transparent">AeroGuard</h1>
        </div>
        <p className="text-xs text-slate-400">AI-Powered Air Quality</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
              isActive(item.path)
                ? 'bg-teal-600/20 text-teal-300 border border-teal-500/50 shadow-lg shadow-teal-500/20'
                : 'text-slate-300 hover:bg-slate-700/50 hover:text-white'
            }`}
          >
            <span className="text-lg">{item.icon}</span>
            <span className="font-medium">{item.label}</span>
          </Link>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-700 bg-slate-900/50">
        <div className="bg-teal-500/10 border border-teal-500/20 rounded-lg p-3 text-center">
          <p className="text-sm text-teal-300 font-semibold">Stay Protected</p>
          <p className="text-xs text-slate-400 mt-1">Monitor air quality for your health</p>
        </div>
      </div>
    </aside>
  );
}
