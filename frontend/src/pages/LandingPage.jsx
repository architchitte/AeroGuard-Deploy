import { motion } from "framer-motion";
import { ArrowRight, Clock, Shield, MapPin } from "lucide-react";

export default function LandingPage() {
    const handleLaunch = () => {
        const dashboard = document.getElementById("dashboard");
        if (dashboard) {
            dashboard.scrollIntoView({ behavior: "smooth" });
        }
    };

    return (
        <motion.div
            className="relative w-full min-h-screen overflow-hidden flex flex-col items-center justify-center text-center p-6 bg-void"
            exit={{ opacity: 0, scale: 1.1, filter: "blur(10px)" }}
            transition={{ duration: 0.8 }}
        >
            {/* Background Ambience */}
            <div className="absolute inset-0 z-0 pointer-events-none">
                <div className="absolute top-[-20%] left-[-10%] w-[60vw] h-[60vw] rounded-full bg-neon-teal/5 blur-[120px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[50vw] h-[50vw] rounded-full bg-indigo-900/10 blur-[100px]" />
                {/* Grid Pattern Overlay */}
                <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_at_center,black,transparent_80%)]" />
            </div>

            <div className="relative z-10 max-w-5xl mx-auto space-y-10">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="space-y-4"
                >
                    <div className="h-4"></div>

                    <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tighter leading-tight">
                        Invisible Threats,<br />
                        <span className="text-gradient">Visible Solutions.</span>
                    </h1>

                    <p className="text-xl text-slate-400 max-w-2xl mx-auto font-light">
                        Hyper-local air quality intelligence customized for your health.
                        Powered by next-gen predictive AI.
                    </p>
                </motion.div>

                <motion.button
                    whileHover={{ scale: 1.05, boxShadow: "0 0 30px -5px rgba(20, 184, 166, 0.4)" }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleLaunch}
                    className="group relative inline-flex items-center gap-3 px-8 py-4 bg-white/5 border border-white/10 rounded-full backdrop-blur-md text-white font-medium overflow-hidden transition-colors hover:bg-white/10"
                >
                    <span className="absolute inset-0 bg-gradient-to-r from-neon-teal/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                    <span className="relative z-10">Launch AeroGuard</span>
                    <ArrowRight className="w-4 h-4 text-neon-teal relative z-10 group-hover:translate-x-1 transition-transform" />
                </motion.button>

                {/* Feature Grid */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5, duration: 1 }}
                    className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12 md:px-20"
                >
                    {[
                        { icon: Clock, label: "Real-time Forecasting", desc: "Live sensor data integration" },
                        { icon: Shield, label: "Persona Protection", desc: "Customized health safeguards" },
                        { icon: MapPin, label: "Hyper-Local Maps", desc: "Spatial pollution tracking" },
                    ].map((item, idx) => (
                        <div key={idx} className="flex flex-col items-center gap-3 p-4 rounded-2xl glass-panel hover:bg-white/5 transition-colors group">
                            <div className="p-3 rounded-full bg-white/5 group-hover:bg-neon-teal/10 transition-colors">
                                <item.icon className="w-6 h-6 text-slate-300 group-hover:text-neon-teal transition-colors" />
                            </div>
                            <div>
                                <h3 className="text-sm font-semibold text-slate-200">{item.label}</h3>
                                <p className="text-xs text-slate-500">{item.desc}</p>
                            </div>
                        </div>
                    ))}
                </motion.div>
            </div>

        </motion.div>
    );
}
