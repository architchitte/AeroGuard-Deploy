import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Wind } from "lucide-react";

export default function Navbar({ variant = "dashboard" }) {
    const [mobileOpen, setMobileOpen] = useState(false);
    const navigate = useNavigate();

    const landingItems = [
        { path: "#hero", label: "Overview" },
        { path: "#heatmap", label: "Heatmap" },
        { path: "/dashboard", label: "Explore" },
    ];
    const dashboardItems = [
        { path: "/dashboard", label: "Dashboard" },
        { path: "/health-risk", label: "Health" },
        { path: "/", label: "Home" },
    ];
    const navItems = variant === "landing" ? landingItems : dashboardItems;

    const go = (path) => {
        setMobileOpen(false);
        if (path.startsWith("/")) { navigate(path); return; }
        document.querySelector(path)?.scrollIntoView({ behavior: "smooth" });
    };

    return (
        <header className="fixed top-0 left-0 w-full bg-[#101525]/85 backdrop-blur-xl border-b border-[#384358]/20 z-50 px-5 sm:px-10 h-14 flex items-center justify-between">

            {/* Logo */}
            <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => go(variant === "landing" ? "#hero" : "/dashboard")}>
                <div className="w-7 h-7 rounded-lg bg-[#B51A2B]/15 border border-[#384358]/40 flex items-center justify-center">
                    <Wind size={14} className="text-[#B51A2B]" />
                </div>
                <div>
                    <h1 className="text-sm font-black text-[#FFA586] tracking-tight font-display text-interactive">AeroGuard</h1>
                    <p className="text-[9px] text-[#D1A5A5] hidden sm:block font-bold tracking-wider uppercase flex items-center gap-1">
                        <span className="cursive-accent normal-case tracking-normal text-[#B51A2B] text-sm">AI</span> Air Quality
                    </p>
                </div>
            </div>

            {/* Desktop nav */}
            <nav className="hidden md:flex items-center gap-0.5 bg-[#242F49] rounded-full px-2 py-1 border border-[#384358]/20">
                {navItems.map((item) => (
                    <button key={item.label} onClick={() => go(item.path)}
                        className="px-4 py-1.5 rounded-full text-xs font-bold text-[#FFA586] hover:text-[#B51A2B] hover:bg-[#384358]/20 transition-all text-interactive">
                        {item.label}
                    </button>
                ))}
            </nav>

            {/* Right side */}
            <div className="hidden md:flex items-center gap-3">
                <div className="bg-[#242F49] border border-[#384358]/30 rounded-lg px-3 py-1">
                    <p className="text-[9px] text-[#B51A2B] font-black uppercase tracking-wider flex items-center gap-1">
                        <span className="w-1 h-1 rounded-full bg-[#B51A2B] animate-pulse" />
                        Live <span className="cursive-accent normal-case tracking-normal text-[#FFA586] text-xs">Monitoring</span>
                    </p>
                </div>
            </div>

            {/* Mobile toggle */}
            <button className="md:hidden text-[#FFA586] hover:text-[#B51A2B] text-lg" onClick={() => setMobileOpen(!mobileOpen)}>
                {mobileOpen ? "✕" : "☰"}
            </button>

            {/* Mobile overlay */}
            {mobileOpen && (
                <div className="fixed inset-0 bg-[#101525]/97 backdrop-blur-xl z-40 flex flex-col items-center justify-center gap-4 md:hidden">
                    {navItems.map((item) => (
                        <button key={item.label} onClick={() => go(item.path)}
                            className="px-6 py-2.5 rounded-full text-base font-bold text-[#FFA586] hover:text-[#B51A2B] hover:bg-[#242F49] transition-all">
                            {item.label}
                        </button>
                    ))}
                </div>
            )}
        </header>
    );
}
