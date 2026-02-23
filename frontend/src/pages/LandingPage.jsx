import { useState, useEffect, useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import {
    ArrowRight, Shield, Clock, BrainCircuit, MapPin,
    Sparkles, BarChart2, Zap, Globe, ChevronDown,
    Activity, Users, CheckCircle, Eye, Wind,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import PollutionHeatmap from "../Components/PollutionHeatmap";

/* ── FEATURES ── */
const FEATURES = [
    { emoji: "⏱️", label: "6-Hour AQI Forecast", desc: "AI-predicted atmospheric trajectory for the next 6 hours. Know if the air is getting better or worse before it happens.", color: "#B51A2B", tag: "HERO FEATURE" },
    { emoji: "🧠", label: "Explainable AI (XAI)", desc: "Feature importance rankings show exactly which pollutant is driving the model's forecast — no black-box guessing.", color: "#FFA586", tag: "AI POWERED" },
    { emoji: "🛡️", label: "Personalized Health Guard", desc: "Persona-aware health advice for General Public, Children & Elderly — tailored risk levels with actionable guidance.", color: "#B51A2B", tag: "HEALTH AI" },
    { emoji: "🗺️", label: "Live Pollution Heatmap", desc: "Nationwide real-time AQI heatmap across 250+ Indian cities on a dark interactive map. Updated every 5 minutes.", color: "#FFA586", tag: "LIVE DATA" },
    { emoji: "📊", label: "Historical Analytics", desc: "7-30 day atmospheric trend charts for PM2.5, PM10, NO₂, O₃ — switch pollutants and time ranges on the fly.", color: "#384358", tag: "ANALYTICS" },
    { emoji: "📡", label: "Real-Time Sync", desc: "Live data from the World Air Quality Index (WAQI) API — no stale cache, no polling delays, always current.", color: "#B51A2B", tag: "LIVE" },
    { emoji: "🎯", label: "City Search & Detection", desc: "Search any city, region, or coordinates globally. Instant geocoding with fuzzy matching and station auto-selection.", color: "#FFA586", tag: "GLOBAL" },
    { emoji: "⚡", label: "Sub-second Performance", desc: "FastAPI async backend serves predictions and full analytics in under 500 ms — no spinner, only instant results.", color: "#384358", tag: "FAST" },
];

/* ── STATS ── */
const STATS = [
    { value: "250+", label: "Indian Cities Covered", emoji: "🏙️" },
    { value: "<500ms", label: "Response Time", emoji: "⚡" },
    { value: "6 hr", label: "AI Forecast Window", emoji: "🔮" },
    { value: "3", label: "Health Personas", emoji: "🛡️" },
];

/* ── Scroll progress bar ── */
function ScrollBar() {
    const { scrollYProgress } = useScroll();
    const width = useTransform(scrollYProgress, [0, 1], ["0%", "100%"]);
    return (
        <div className="fixed top-0 left-0 right-0 h-[2px] z-[999] bg-[#242F49]">
            <motion.div className="h-full bg-gradient-to-r from-[#B51A2B] via-[#FFA586] to-[#541A2B]" style={{ width }} />
        </div>
    );
}

/* ── Section reveal ── */
const Reveal = ({ children, delay = 0, className = "" }) => (
    <motion.div
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 0.7, delay, ease: [0.22, 1, 0.36, 1] }}
        className={className}
    >
        {children}
    </motion.div>
);

/* ══ AURORA BACKGROUND ══
   Animated conic-gradient orbs + SVG mesh lines + scanline shimmer */
function AuroraBackground() {
    return (
        <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
            {/* Aurora orb 1 — top-left accent */}
            <motion.div
                className="absolute rounded-full"
                style={{
                    width: 900, height: 900,
                    top: "-25%", left: "-20%",
                    background: "conic-gradient(from 0deg at 40% 40%, #B51A2B22, #242F49 40%, #541A2B18, #101525 70%, #B51A2B22)",
                    filter: "blur(90px)",
                }}
                animate={{ rotate: [0, 360] }}
                transition={{ duration: 28, repeat: Infinity, ease: "linear" }}
            />
            {/* Aurora orb 2 — bottom-right blue */}
            <motion.div
                className="absolute rounded-full"
                style={{
                    width: 800, height: 800,
                    bottom: "-25%", right: "-15%",
                    background: "conic-gradient(from 180deg at 60% 60%, #FFA58615, #242F49 30%, #541A2B20, #101525 65%, #FFA58615)",
                    filter: "blur(100px)",
                }}
                animate={{ rotate: [360, 0] }}
                transition={{ duration: 22, repeat: Infinity, ease: "linear" }}
            />
            {/* Mid pulse blob */}
            <motion.div
                className="absolute rounded-full"
                style={{
                    width: 500, height: 500,
                    top: "30%", left: "50%",
                    background: "radial-gradient(circle, #B51A2B12 0%, transparent 70%)",
                    filter: "blur(60px)",
                    translateX: "-50%",
                }}
                animate={{ scale: [1, 1.3, 1], opacity: [0.6, 1, 0.6] }}
                transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
            />

            {/* Dot grid */}
            <div className="absolute inset-0 opacity-[0.35]"
                style={{
                    backgroundImage: "radial-gradient(circle, #FFA58630 1px, transparent 1px)",
                    backgroundSize: "36px 36px",
                    maskImage: "radial-gradient(ellipse 80% 70% at 50% 50%, black, transparent)",
                    WebkitMaskImage: "radial-gradient(ellipse 80% 70% at 50% 50%, black, transparent)",
                }} />

            {/* Scanning horizontal shimmer line */}
            <motion.div
                className="absolute left-0 right-0 h-px pointer-events-none"
                style={{ background: "linear-gradient(to right, transparent, #B51A2B50, #FFA58640, transparent)" }}
                animate={{ top: ["0%", "100%"] }}
                transition={{ duration: 8, repeat: Infinity, ease: "linear", repeatDelay: 2 }}
            />

            {/* Floating particles */}
            {[...Array(22)].map((_, i) => (
                <motion.div key={i}
                    className="absolute rounded-full"
                    style={{
                        width: `${1.5 + (i % 3) * 1.5}px`,
                        height: `${1.5 + (i % 3) * 1.5}px`,
                        left: `${(i * 4.4 + 3) % 96}%`,
                        top: `${(i * 6.7 + 5) % 90}%`,
                        background: i % 4 === 0 ? "#B51A2B" : i % 4 === 1 ? "#FFA586" : i % 4 === 2 ? "#541A2B" : "#384358",
                        boxShadow: `0 0 ${4 + i % 4}px currentColor`,
                    }}
                    animate={{ y: [-10, 10, -10], opacity: [0.2, 0.9, 0.2] }}
                    transition={{ duration: 3 + (i % 5), repeat: Infinity, delay: i * 0.22, ease: "easeInOut" }}
                />
            ))}
        </div>
    );
}

export default function LandingPage() {
    const navigate = useNavigate();
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

    useEffect(() => {
        const h = (e) => setMousePos({ x: e.clientX, y: e.clientY });
        window.addEventListener("mousemove", h);
        return () => window.removeEventListener("mousemove", h);
    }, []);

    return (
        <div className="bg-[#101525] min-h-screen text-[#FFA586] overflow-x-hidden">
            <ScrollBar />

            {/* ══ NAV ══ */}
            <nav className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[95%] max-w-6xl h-16 rounded-2xl bg-[#101525]/80 backdrop-blur-2xl border border-[#384358]/20 flex items-center justify-between px-8 shadow-2xl transition-all duration-300">
                <div className="flex items-center gap-3 group cursor-pointer" onClick={() => navigate("/")}>
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#B51A2B] to-[#FFA586] flex items-center justify-center shadow-lg shadow-[#B51A2B]/20">
                        <span className="text-sm">🌍</span>
                    </div>
                    <span className="font-black text-lg text-[#FFA586] tracking-tighter">AeroGuard<span className="text-[#B51A2B] animate-pulse">.ai</span></span>
                </div>

                <div className="hidden md:flex items-center gap-10 text-[10px] uppercase font-black tracking-widest text-[#9BA3AF]">
                    <a href="#features" className="hover:text-[#FFA586] transition-all hover:scale-110">Capabilities</a>
                    <a href="#heatmap" className="hover:text-[#FFA586] transition-all hover:scale-110">Live Map</a>
                    <a href="#about" className="hover:text-[#FFA586] transition-all hover:scale-110">Project</a>
                </div>

                <div className="flex items-center gap-3">
                    <button onClick={() => navigate("/dashboard")}
                        className="px-6 py-2.5 rounded-xl bg-[#B51A2B] text-white text-[10px] font-black uppercase tracking-widest hover:bg-[#B51A2B]/80 transition-all shadow-lg shadow-[#B51A2B]/20 flex items-center gap-2 active:scale-95">
                        <span className="hidden sm:inline">Launch Console</span>
                        <span className="sm:hidden">Console</span>
                        <ArrowRight size={12} />
                    </button>
                    {/* Simple Mobile Trigger Hint */}
                    <div className="md:hidden w-8 h-8 rounded-lg bg-[#242F49] border border-[#384358]/30 flex items-center justify-center">
                        <div className="flex flex-col gap-1">
                            <div className="w-3 h-[2px] bg-[#FFA586]" />
                            <div className="w-2 h-[2px] bg-[#B51A2B]" />
                        </div>
                    </div>
                </div>
            </nav>

            {/* ══ HERO ══ */}
            <section className="relative min-h-screen flex flex-col items-center justify-center text-center px-6 pt-20 pb-16 overflow-hidden">
                <AuroraBackground />

                {/* Mouse-follow radial highlight */}
                <div className="absolute inset-0 pointer-events-none z-[1] transition-all duration-300"
                    style={{ background: `radial-gradient(500px circle at ${mousePos.x}px ${mousePos.y}px, rgba(181,26,43,0.09), transparent 65%)` }} />

                <div className="relative z-10 max-w-5xl mx-auto space-y-8">
                    {/* Badge */}
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}
                        className="inline-flex items-center gap-2 px-5 py-2 rounded-full bg-[#242F49]/80 border border-[#384358]/50 backdrop-blur-xl">
                        <motion.span animate={{ opacity: [1, 0.4, 1] }} transition={{ duration: 1.5, repeat: Infinity }}>✨</motion.span>
                        <span className="text-[10px] font-black text-[#B51A2B] tracking-widest uppercase flex items-center gap-2">
                            <span className="cursive-accent normal-case tracking-normal text-[#FFA586] mr-1">AI-Powered</span> Atmospheric Intelligence
                        </span>
                        <motion.span animate={{ opacity: [1, 0.4, 1] }} transition={{ duration: 1.5, repeat: Infinity, delay: 0.75 }}>✨</motion.span>
                    </motion.div>

                    {/* Headline */}
                    <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.9, delay: 0.15 }}>
                        <h1 className="text-6xl md:text-7xl lg:text-8xl font-black tracking-tighter leading-[0.9] font-display">
                            <span className="text-[#FFA586] block text-glow">Invisible Threats,</span>
                            <span className="block mt-2 text-gradient py-2">
                                Visible Solutions. 💨
                            </span>
                        </h1>
                    </motion.div>

                    {/* Sub */}
                    <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5, duration: 0.8 }}
                        className="text-lg md:text-xl text-[#FFA586] max-w-2xl mx-auto font-medium leading-relaxed italic">
                        Hyper-local air quality intelligence designed for your health.
                        <br className="hidden md:block" />
                        <span className="text-[#D1A5A5] not-italic text-sm font-bold tracking-wide mt-2 block">
                            <span className="cursive-accent text-lg">Real-time</span>  · 🤖 AI Forecast · <span className="cursive-accent text-lg">Personalised</span>
                        </span>
                    </motion.p>

                    {/* CTAs */}
                    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}
                        className="flex flex-wrap items-center justify-center gap-4">
                        <motion.button onClick={() => navigate("/dashboard")}
                            whileHover={{ scale: 1.04, boxShadow: "0 20px 60px rgba(181,26,43,0.45)" }}
                            whileTap={{ scale: 0.97 }}
                            className="flex items-center gap-3 px-8 py-4 rounded-2xl bg-[#B51A2B] text-[#101525] font-black text-sm shadow-xl shadow-[#B51A2B]/30">
                            🚀 Launch Dashboard <ArrowRight size={16} />
                        </motion.button>
                        <motion.a href="#features"
                            whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}
                            className="flex items-center gap-3 px-8 py-4 rounded-2xl bg-[#242F49] border border-[#384358]/40 text-[#FFA586] font-black text-sm cursor-pointer hover:border-[#B51A2B]/50 transition-all">
                            🔍 Explore Features
                        </motion.a>
                    </motion.div>

                    {/* Pill badges */}
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1 }}
                        className="flex flex-wrap items-center justify-center gap-2">
                        {["🌏 Global Coverage", "⏱️ 6h Forecast", "🧠 Explainable AI", "📊 Live Analytics", "🛡️ Health Guards"].map(t => (
                            <span key={t} className="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider border border-[#384358]/30 bg-[#242F49]/60 text-[#D1A5A5]">{t}</span>
                        ))}
                    </motion.div>
                </div>

                {/* Scroll cue */}
                <motion.a href="#features" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.4 }}
                    className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 text-[#9BA3AF] cursor-pointer">
                    <span className="text-[9px] font-black uppercase tracking-widest">Scroll to explore</span>
                    <motion.div animate={{ y: [0, 6, 0] }} transition={{ duration: 1.4, repeat: Infinity }}>
                        <ChevronDown size={18} />
                    </motion.div>
                </motion.a>
            </section>

            {/* ══ STATS RIBBON ══ */}
            <section className="py-6 border-y border-[#384358]/15 bg-[#242F49]/30 backdrop-blur-sm">
                <div className="max-w-5xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-4 px-8">
                    {STATS.map((s, i) => (
                        <Reveal key={s.label} delay={i * 0.1}>
                            <div className="text-center space-y-1">
                                <div className="text-2xl">{s.emoji}</div>
                                <div className="text-2xl font-black text-[#FFA586]">{s.value}</div>
                                <div className="text-[10px] font-bold text-[#9BA3AF] uppercase tracking-widest">{s.label}</div>
                            </div>
                        </Reveal>
                    ))}
                </div>
            </section>

            {/* ══ FEATURES ══ */}
            <section id="features" className="py-24 px-6 sm:px-12 relative overflow-hidden">
                <div className="max-w-6xl mx-auto">
                    <Reveal className="text-center mb-16 space-y-4">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#242F49] border border-[#384358]/30">
                            <Sparkles size={12} className="text-[#B51A2B]" />
                            <span className="text-[10px] font-black uppercase tracking-widest text-[#B51A2B]">Platform Capabilities</span>
                        </div>
                        <h2 className="text-4xl md:text-5xl font-black text-[#FFA586] tracking-tight font-display text-glow">
                            Everything you need to<br />
                            <span className="text-gradient py-1">breathe with confidence</span>
                        </h2>
                        <p className="text-[#9BA3AF] max-w-lg mx-auto text-sm leading-relaxed">
                            From raw sensor data to AI-generated health advice — every feature is built to make air quality actionable.
                        </p>
                    </Reveal>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                        {FEATURES.map((f, i) => (
                            <Reveal key={f.label} delay={i * 0.06}>
                                <motion.div whileHover={{ y: -6, boxShadow: `0 20px 40px ${f.color}20` }}
                                    className="glass-card rounded-2xl p-4 hover:border-[#B51A2B]/40 hover:-translate-y-1 transition-all duration-300 group cursor-default relative overflow-hidden h-full flex flex-col gap-4">
                                    <div className="absolute top-0 left-0 right-0 h-[2px] rounded-t-3xl opacity-0 group-hover:opacity-100 transition-all duration-300"
                                        style={{ background: `linear-gradient(to right, transparent, ${f.color}, transparent)` }} />
                                    <div className="flex justify-between items-start">
                                        <span className="text-3xl">{f.emoji}</span>
                                        <span className="text-[8px] font-black px-2 py-1 rounded-full border"
                                            style={{ color: f.color, borderColor: f.color + "40", background: f.color + "12" }}>{f.tag}</span>
                                    </div>
                                    <div>
                                        <h3 className="card-title text-sm mb-2 text-interactive">{f.label}</h3>
                                        <p className="text-xs text-[#9BA3AF] leading-relaxed font-medium">{f.desc}</p>
                                    </div>
                                </motion.div>
                            </Reveal>
                        ))}
                    </div>
                </div>
            </section>

            {/* ══ LIVE HEATMAP ══ */}
            <section id="heatmap" className="py-20 px-6 sm:px-12 border-t border-[#384358]/10">
                <Reveal className="text-center mb-10 space-y-3">
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#242F49] border border-[#384358]/30">
                        <Globe size={12} className="text-[#B51A2B]" />
                        <span className="text-[10px] font-black uppercase tracking-widest text-[#B51A2B]">Live Heatmap</span>
                        <div className="w-1.5 h-1.5 rounded-full bg-[#B51A2B] animate-pulse ml-1" />
                    </div>
                    <h2 className="text-4xl font-black text-[#FFA586] font-display text-glow">Real-time pollution <span className="cursive-accent text-3xl">across India</span> 🗺️</h2>
                    <p className="text-sm text-[#9BA3AF] max-w-lg mx-auto">
                        Live AQI readings from 250+ cities, visualised spatially. Heatmap intensity reflects current pollutant concentration.
                    </p>
                </Reveal>
                <Reveal delay={0.2}>
                    {/* Height set tall enough to show full India map (lat 8°N – 37°N) */}
                    <div className="max-w-6xl mx-auto rounded-3xl overflow-hidden border border-[#384358]/30 shadow-2xl" style={{ height: 680 }}>
                        <PollutionHeatmap />
                    </div>
                </Reveal>
            </section>

            {/* ══ ABOUT ══ */}
            <section id="about" className="py-24 px-6 sm:px-12 border-t border-[#384358]/10 relative overflow-hidden">
                {/* Subtle aurora accent */}
                <motion.div className="absolute -top-40 right-0 w-[600px] h-[600px] rounded-full pointer-events-none"
                    style={{ background: "conic-gradient(from 90deg at 60% 40%, #B51A2B10, #101525 50%, #541A2B12, #101525)", filter: "blur(80px)" }}
                    animate={{ rotate: [0, 360] }} transition={{ duration: 35, repeat: Infinity, ease: "linear" }} />

                <div className="max-w-5xl mx-auto relative z-10">
                    <Reveal className="text-center mb-16 space-y-4">
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#242F49] border border-[#384358]/30">
                            <Users size={12} className="text-[#B51A2B]" />
                            <span className="text-[10px] font-black uppercase tracking-widest text-[#B51A2B]">About AeroGuard</span>
                        </div>
                        <h2 className="text-4xl md:text-5xl font-black text-[#FFA586] leading-tight font-display">
                            What is <span className="text-gradient">AeroGuard.ai</span>?
                        </h2>
                    </Reveal>

                    {/* What it is */}
                    <Reveal delay={0.05} className="mb-12 max-w-3xl mx-auto text-center">
                        <p className="text-base text-[#FFA586] leading-relaxed">
                            <strong className="text-[#FFA586]">AeroGuard</strong> is an AI-powered air quality intelligence platform that goes far beyond a simple AQI number.
                            It <strong className="text-[#B51A2B]">predicts where air quality is headed</strong>, explains <em>why</em> using transparent machine learning,
                            and translates raw pollution data into <strong className="text-[#B51A2B]">personalised health guidance</strong> for different people — from healthy adults to children and the elderly.
                        </p>
                    </Reveal>

                    {/* What it provides — 3-column cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
                        {[
                            {
                                emoji: "🔮", title: "Predictive Intelligence",
                                body: "A 6-hour AQI forecast powered by machine learning — so you can plan outdoor activities, commutes, and health precautions before conditions deteriorate.",
                            },
                            {
                                emoji: "🛡️", title: "Personalised Health Lens",
                                body: "Generic AQI numbers don't mean the same thing to a child with asthma as they do to a healthy adult. AeroGuard interprets risk for your specific health profile.",
                            },
                            {
                                emoji: "🧠", title: "Transparent AI (XAI)",
                                body: "Instead of a black-box model, our Explainable AI surface shows exactly which pollutant — PM2.5, NO₂, O₃ — is driving the prediction and by how much.",
                            },
                        ].map((c, i) => (
                            <Reveal key={c.title} delay={i * 0.1}>
                                <motion.div whileHover={{ y: -5 }}
                                    className="p-7 rounded-3xl bg-[#242F49] border border-[#384358]/20 hover:border-[#384358]/50 transition-all h-full flex flex-col gap-4">
                                    <span className="text-4xl">{c.emoji}</span>
                                    <h3 className="card-title text-base">{c.title}</h3>
                                    <p className="text-xs text-[#9BA3AF] leading-relaxed flex-1 font-medium">{c.body}</p>
                                </motion.div>
                            </Reveal>
                        ))}
                    </div>

                    {/* Unique features list */}
                    <Reveal delay={0.1} className="mb-12">
                        <h3 className="text-xl font-black text-[#FFA586] mb-6 text-center">✨ What makes AeroGuard unique</h3>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-3xl mx-auto">
                            {[
                                { icon: CheckCircle, text: "6-hour AI forecast — no other public AQI tool predicts this far ahead" },
                                { icon: CheckCircle, text: "Explainable AI layer — you see WHY the model gives its prediction" },
                                { icon: CheckCircle, text: "Persona-aware health advice — not one-size-fits-all" },
                                { icon: CheckCircle, text: "Nationwide heatmap with 250+ Indian cities on a live dark map" },
                                { icon: CheckCircle, text: "Real-time WAQI data — no cached or mocked readings" },
                                { icon: CheckCircle, text: "Sub-500 ms full-stack response via async FastAPI" },
                            ].map(({ icon: Icon, text }) => (
                                <div key={text} className="flex items-start gap-3 p-4 rounded-2xl bg-[#101525]/60 border border-[#384358]/15 hover:border-[#384358]/35 transition-all">
                                    <Icon size={14} className="text-[#B51A2B] mt-0.5 flex-shrink-0" />
                                    <span className="text-xs text-[#FFA586] font-medium leading-relaxed">{text}</span>
                                </div>
                            ))}
                        </div>
                    </Reveal>

                    {/* Origin */}
                    <Reveal delay={0.15} className="text-center space-y-4 max-w-2xl mx-auto pt-6 border-t border-[#384358]/15">
                        <p className="text-sm text-[#9BA3AF] leading-relaxed">
                            Built at the <strong className="text-[#FFA586]">AIColegion Hackathon 2026</strong> at VESIT by <strong className="text-[#B51A2B]">Team 70 — CultBoyz</strong>.
                            The core mission: make air quality data not just visible, but genuinely useful for everyday health decisions.
                        </p>
                        <motion.button onClick={() => navigate("/dashboard")}
                            whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}
                            className="inline-flex items-center gap-3 px-6 py-3 rounded-2xl bg-[#B51A2B] text-[#101525] font-black text-sm shadow-lg shadow-[#B51A2B]/25">
                            🚀 Try AeroGuard <ArrowRight size={14} />
                        </motion.button>
                    </Reveal>
                </div>
            </section>

            {/* ══ FOOTER ══ */}
            <footer className="py-8 px-8 border-t border-[#384358]/15 flex flex-wrap justify-between items-center gap-4 bg-[#101525]/80">
                <div className="flex items-center gap-2">
                    <span className="text-lg">🌍</span>
                    <span className="text-xs font-black text-[#FFA586]">AeroGuard<span className="text-[#B51A2B]">.ai</span></span>
                </div>
                <div className="flex items-center gap-6 text-[10px] font-bold text-[#9BA3AF] uppercase tracking-widest">
                    <span>🏆 AIColegion 2026</span>
                    <span>⚡ Team CultBoyz · VESIT</span>
                    <span>© 2026</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#B51A2B] animate-pulse" />
                    <span className="text-[10px] font-black text-[#B51A2B] uppercase tracking-widest">All Systems Live</span>
                </div>
            </footer>
        </div>
    );
}
