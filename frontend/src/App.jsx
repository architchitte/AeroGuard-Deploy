
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import Navbar from "./Components/Navbar";
import { motion } from "framer-motion";

import PollutionHeatmap from "./Components/PollutionHeatmap";

import AdvancedAnalytics from "./Components/AdvancedAnalytics";

export default function App() {
  return (
    <div className="bg-void min-h-screen text-slate-300 overflow-x-hidden">
      <Navbar />

      <section id="hero">
        <LandingPage />
      </section>

      <section id="dashboard" className="py-10">
        <Dashboard />
      </section>

      <section id="heatmap" className="py-10 container mx-auto px-4 min-h-[50vh]">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="glass-panel p-8 rounded-3xl border border-white/10 relative overflow-hidden shadow-2xl"
        >
          <h2 className="text-4xl font-display font-bold text-white mb-8 border-l-4 border-neon-teal pl-4">Heatmap</h2>
          <div className="h-[700px]">
            <PollutionHeatmap />
          </div>
        </motion.div>
      </section>

      <section id="analytics" className="py-10 container mx-auto px-4 min-h-[50vh]">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="glass-panel p-8 rounded-3xl border border-white/10"
        >
          <h2 className="text-4xl font-display font-bold text-white mb-8 border-l-4 border-indigo-500 pl-4">Advanced Analytics</h2>
          <AdvancedAnalytics />
        </motion.div>
      </section>

      <footer className="py-10 text-center text-xs text-slate-600 border-t border-white/5">
        <p>© 2026 AeroGuard AI Systems. All rights reserved.</p>
      </footer>
    </div>
  );
}
