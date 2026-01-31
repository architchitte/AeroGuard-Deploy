import { motion } from "framer-motion";
import { ArrowRight, Clock, Shield, MapPin } from "lucide-react";
import { useNavigate } from "react-router-dom";
import PollutionHeatmap from "../Components/PollutionHeatmap";

export default function LandingPage() {
  const navigate = useNavigate();

  const handleLaunch = () => {
    navigate("/dashboard");
  };

  return (
    <>
      {/* ================= HERO SECTION ================= */}
      <motion.div
        id="hero"   // ✅ REQUIRED FOR OVERVIEW SCROLL
        className="relative w-full min-h-screen overflow-hidden flex flex-col items-center justify-center text-center p-6 bg-void"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        {/* Background */}
        <div className="absolute inset-0 z-0 pointer-events-none">
          <div className="absolute top-[-20%] left-[-10%] w-[60vw] h-[60vw] rounded-full bg-neon-teal/5 blur-[120px]" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[50vw] h-[50vw] rounded-full bg-indigo-900/10 blur-[100px]" />
          <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_at_center,black,transparent_80%)]" />
        </div>

        <div className="relative z-10 max-w-5xl mx-auto space-y-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="space-y-4"
          >
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold tracking-tighter leading-tight">
              Invisible Threats,<br />
              <span className="text-gradient">Visible Solutions.</span>
            </h1>

            <p className="text-xl text-slate-400 max-w-2xl mx-auto font-light">
              Hyper-local air quality intelligence customized for your health.
              Powered by next-gen predictive AI.
            </p>
          </motion.div>

          {/* CTA */}
          <motion.button
            whileHover={{ scale: 1.05, boxShadow: "0 0 30px -5px rgba(20, 184, 166, 0.4)" }}
            whileTap={{ scale: 0.95 }}
            onClick={handleLaunch}
            className="group relative inline-flex items-center gap-3 px-8 py-4 bg-white/5 border border-white/10 rounded-full backdrop-blur-md text-white font-medium overflow-hidden transition-colors hover:bg-white/10"
          >
            <span className="absolute inset-0 bg-gradient-to-r from-neon-teal/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <span className="relative z-10">View Detailed Insights</span>
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
              <div
                key={idx}
                className="flex flex-col items-center gap-3 p-4 rounded-2xl glass-panel hover:bg-white/5 transition-colors group"
              >
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

      {/* ================= HEATMAP SECTION ================= */}
      <section
        id="heatmap"   // ✅ REQUIRED FOR HEATMAP SCROLL
        className="py-16 container mx-auto px-4"
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="glass-panel p-8 rounded-3xl border border-white/10 shadow-2xl"
        >
          <h2 className="text-4xl font-display font-bold text-white mb-8 border-l-4 border-neon-teal pl-4">
            City Pollution Heatmap
          </h2>

          <div className="relative w-full h-[600px] rounded-2xl overflow-hidden">
            <PollutionHeatmap />
          </div>
        </motion.div>
      </section>

      {/* ================= FOOTER ================= */}
      <footer className="py-10 text-center text-xs text-slate-600 border-t border-white/5">
        © 2026 AeroGuard AI Systems. All rights reserved.
      </footer>
    </>
  );
}
