import { useState } from "react";

export default function Navbar({ variant = "dashboard" }) {
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    /* ================= NAV ITEMS ================= */

    const landingNavItems = [
        { path: '#hero', icon: '✨', label: 'Overview' },
        { path: '#heatmap', icon: '🗺️', label: 'Heatmap' },
        { path: '/dashboard', icon: '🚀', label: 'Explore' },
    ];

    const dashboardNavItems = [
        { path: '#dashboard', icon: '📊', label: 'Dashboard' },
        { path: '#Analytics', icon: '🗺️', label: 'Analytics' },
        { path: '/', icon: '🚀', label: 'Landing' },
    ];

    const navItems = variant === "landing" ? landingNavItems : dashboardNavItems;

    /* ================= SCROLL / NAV ================= */

    const scrollToSection = (path) => {
        setIsMobileMenuOpen(false);

        // Route navigation for Explore button
        if (path.startsWith("/")) {
            window.location.href = path;
            return;
        }

        const element = document.querySelector(path);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    };

    return (
        <header className="fixed top-0 left-0 w-full bg-void/80 backdrop-blur-md p-4 flex items-center justify-between border-b border-white/10 relative z-50">

            {/* LOGO */}
            <div
                className="flex items-center gap-3 cursor-pointer"
                onClick={() => scrollToSection(variant === "landing" ? '#hero' : '#dashboard')}
            >
                <span className="text-3xl">🌍</span>
                <div>
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-transparent">
                        AeroGuard
                    </h1>
                    <p className="text-xs text-slate-400 hidden sm:block">
                        AI-Powered Air Quality
                    </p>
                </div>
            </div>

            {/* DESKTOP NAV */}
            <nav className="hidden md:flex items-center gap-1 bg-white/5 rounded-full px-2 py-1 backdrop-blur-md border border-white/10">
                {navItems.map((item) => (
                    <button
                        key={item.label}
                        onClick={() => scrollToSection(item.path)}
                        className="flex items-center gap-2 px-4 py-2 rounded-full transition-all duration-300 transform hover:scale-105 text-slate-300 hover:text-white hover:bg-white/5"
                    >
                        <span>{item.icon}</span>
                        <span className="text-sm font-medium">{item.label}</span>
                    </button>
                ))}
            </nav>

            {/* MOBILE MENU BUTTON */}
            <div className="md:hidden z-50">
                <button
                    onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                    className="text-slate-300 hover:text-white focus:outline-none"
                >
                    {isMobileMenuOpen ? (
                        <span className="text-2xl">✕</span>
                    ) : (
                        <span className="text-2xl">☰</span>
                    )}
                </button>
            </div>

            {/* RIGHT SIDE */}
            <div className="hidden md:flex items-center gap-4">
                <div className="bg-teal-500/10 border border-teal-500/20 rounded-lg px-3 py-1 text-center">
                    <p className="text-xs text-teal-300 font-semibold">Stay Protected</p>
                </div>
            </div>

            {/* MOBILE NAV OVERLAY */}
            {isMobileMenuOpen && (
                <div className="fixed inset-0 bg-slate-950/95 backdrop-blur-lg z-40 flex flex-col items-center justify-center space-y-6 md:hidden">
                    {navItems.map((item) => (
                        <button
                            key={item.label}
                            onClick={() => scrollToSection(item.path)}
                            className="flex items-center gap-3 px-6 py-3 rounded-full text-lg transition-all duration-300 text-slate-300 hover:text-white"
                        >
                            <span>{item.icon}</span>
                            <span className="font-medium">{item.label}</span>
                        </button>
                    ))}
                </div>
            )}
        </header>
    );
}
