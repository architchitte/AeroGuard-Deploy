import { motion } from "framer-motion";
import { ArrowRight, Clock, Shield, MapPin, Sparkles, Wind, Activity } from "lucide-react";
import { useNavigate } from "react-router-dom";
import PollutionHeatmap from "../Components/PollutionHeatmap";

export default function LandingPage() {
  const navigate = useNavigate();

  const handleLaunch = () => {
    navigate("/dashboard");
  };

  return (
    <div className="bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 min-h-screen">
      {/* ================= HERO SECTION ================= */}
      <motion.div
        id="hero"
        className="relative w-full min-h-screen overflow-hidden flex flex-col items-center justify-center text-center px-6 py-20"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        {/* Enhanced Background Effects */}
        <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
          {/* Radial Gradients */}
          <div className="absolute top-[-20%] left-[-10%] w-[60vw] h-[60vw] rounded-full bg-emerald-500/10 blur-[140px] animate-pulse" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[50vw] h-[50vw] rounded-full bg-cyan-500/10 blur-[120px] animate-pulse" style={{ animationDelay: '1s' }} />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[40vw] h-[40vw] rounded-full bg-blue-500/5 blur-[100px]" />

          {/* Grid Pattern */}
          <div className="absolute inset-0 bg-[linear-gradient(rgba(16,185,129,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(16,185,129,0.03)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_at_center,black,transparent_85%)]" />

          {/* Floating Particles */}
          {[...Array(20)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-cyan-400/40 rounded-full"
              initial={{
                x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1000),
                y: Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 1000),
                opacity: 0.3,
              }}
              animate={{
                y: [null, Math.random() * -100, Math.random() * 100],
                x: [null, Math.random() * -50, Math.random() * 50],
                opacity: [0.3, 0.6, 0.3],
              }}
              transition={{
                duration: 10 + Math.random() * 10,
                repeat: Infinity,
                ease: "linear",
                delay: Math.random() * 5,
              }}
            />
          ))}
        </div>

        <div className="relative z-10 max-w-6xl mx-auto space-y-12">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 border border-emerald-500/20 backdrop-blur-xl"
          >
            <Sparkles className="w-4 h-4 text-emerald-400 animate-pulse" />
            <span className="text-sm font-bold text-emerald-300 tracking-wide">AI-Powered Air Quality Intelligence</span>
          </motion.div>

          {/* Headline */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
            className="space-y-6"
          >
            <h1 className="text-6xl md:text-7xl lg:text-8xl xl:text-9xl font-black tracking-tighter leading-[0.95]">
              <span className="text-white block mb-2">Invisible Threats,</span>
              <span className="bg-gradient-to-r from-cyan-400 via-emerald-400 to-cyan-500 bg-clip-text text-transparent block animate-gradient-x">
                Visible Solutions.
              </span>
            </h1>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="text-xl md:text-2xl text-slate-400 max-w-3xl mx-auto font-medium leading-relaxed"
            >
              Hyper-local air quality intelligence customized for your health.
              Powered by next-generation predictive AI.
            </motion.p>
          </motion.div>

          {/* CTA Button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7, duration: 0.6 }}
          >
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleLaunch}
              className="group relative inline-flex items-center gap-3 px-10 py-5 bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 border border-emerald-500/30 rounded-full backdrop-blur-xl text-white font-bold text-lg overflow-hidden transition-all duration-300 hover:border-emerald-500/50 hover:shadow-2xl hover:shadow-emerald-500/20"
            >
              {/* Animated Background */}
              <span className="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

              {/* Shine Effect */}
              <span className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/10 to-transparent" />

              <span className="relative z-10">View Detailed Insights</span>
              <ArrowRight className="w-5 h-5 text-emerald-400 relative z-10 group-hover:translate-x-2 transition-transform duration-300" />
            </motion.button>
          </motion.div>

          {/* Feature Cards */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9, duration: 0.8 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-16 max-w-5xl mx-auto"
          >
            {[
              {
                icon: Clock,
                label: "Real-time Forecasting",
                desc: "Live sensor data integration with predictive analytics",
                color: "emerald"
              },
              {
                icon: Shield,
                label: "Persona Protection",
                desc: "Customized health advice for every individual profile",
                color: "cyan"
              },
              {
                icon: MapPin,
                label: "Hyper-Local Maps",
                desc: "Spatial pollution tracking at street-level granularity",
                color: "blue"
              },
            ].map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1 + idx * 0.1, duration: 0.6 }}
                whileHover={{ y: -8, scale: 1.02 }}
                className="group relative flex flex-col items-center gap-4 p-8 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-white/10 hover:border-emerald-500/30 transition-all duration-300 hover:shadow-2xl hover:shadow-emerald-500/10"
              >
                {/* Glow Effect on Hover */}
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-2xl" />

                {/* Icon Container */}
                <div className="relative p-4 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/10 border border-emerald-500/30 group-hover:scale-110 transition-transform duration-300">
                  <item.icon className="w-8 h-8 text-emerald-400" />
                </div>

                {/* Content */}
                <div className="text-center space-y-2 relative z-10">
                  <h3 className="text-lg font-black text-white group-hover:text-emerald-400 transition-colors">
                    {item.label}
                  </h3>
                  <p className="text-sm text-slate-400 leading-relaxed">
                    {item.desc}
                  </p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>

        {/* Scroll Indicator */}
        {/* <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1, y: [0, 10, 0] }}
          transition={{ 
            opacity: { delay: 1.5, duration: 0.6 },
            y: { repeat: Infinity, duration: 2, ease: "easeInOut" }
          }}
          className="absolute bottom-12 left-1/2 -translate-x-1/2"
        >
          <div className="flex flex-col items-center gap-2">
            <span className="text-xs text-slate-500 uppercase tracking-widest font-bold">Scroll to Explore</span>
            <div className="w-6 h-10 rounded-full border-2 border-emerald-500/30 flex items-start justify-center p-2">
              <div className="w-1 h-2 bg-emerald-400 rounded-full" />
            </div>
          </div>
        </motion.div> */}
      </motion.div>

      {/* ================= HEATMAP SECTION ================= */}
      <section
        id="heatmap"
        className="py-24 container mx-auto px-4 sm:px-6 lg:px-8 relative"
      >
        {/* Background Accent */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-emerald-500/5 to-transparent pointer-events-none" />

        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8 }}
          className="relative glass-panel p-8 lg:p-12 rounded-3xl border border-white/10 shadow-2xl hover:border-emerald-500/20 transition-all duration-500"
        >
          {/* Section Header */}
          <div className="flex items-center gap-4 mb-10">
            <div className="p-3 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 border border-emerald-500/30">
              <MapPin className="w-6 h-6 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-4xl md:text-5xl font-black text-white">
                City Pollution Heatmap
              </h2>
              <p className="text-sm text-slate-400 mt-1">
                Real-time air quality visualization across your region
              </p>
            </div>
          </div>

          {/* Heatmap Container - FIXED: Badge now properly inside */}
          <div className="relative w-full h-[500px] md:h-[600px] lg:h-[700px] rounded-2xl border border-white/10 bg-slate-900/50 overflow-hidden">
            {/* Map with padding */}
            <div className="absolute inset-4">
              <PollutionHeatmap />
            </div>

            {/* Live Data Badge - Now properly positioned inside border */}
            <div className="absolute top-6 right-6 px-4 py-2 rounded-full bg-slate-900/90 backdrop-blur-xl border border-emerald-500/30 z-50">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Live Data</span>
              </div>
            </div>
          </div>

          {/* Feature Pills */}
          <div className="flex flex-wrap gap-3 mt-8 justify-center">
            {["Predictive AI", "Real-time Updates", "30km Coverage", "Street-Level Detail"].map((feature, idx) => (
              <div
                key={idx}
                className="px-4 py-2 rounded-full bg-white/5 border border-white/10 text-xs font-semibold text-slate-400 hover:bg-white/10 hover:text-emerald-400 hover:border-emerald-500/30 transition-all duration-300 cursor-pointer"
              >
                {feature}
              </div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* ================= FOOTER ================= */}
      <footer className="relative py-12 text-center border-t border-white/10 backdrop-blur-sm">
        <div className="container mx-auto px-4">
          <div className="flex flex-col items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center">
                <Wind className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-black text-white">AeroGuard</span>
            </div>
            <p className="text-xs text-slate-500 font-medium">
              © 2026 AeroGuard AI Systems. All rights reserved.
            </p>
            <div className="flex items-center gap-2 text-xs text-slate-600">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Protecting your health, one breath at a time
            </div>
          </div>
        </div>
      </footer>

      {/* Animation Styles */}
      <style>{`
        @keyframes gradient-x {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        .animate-gradient-x {
          background-size: 200% 200%;
          animation: gradient-x 3s ease infinite;
        }
      `}</style>
    </div>
  );
}