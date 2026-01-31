import React from "react";
import PropTypes from "prop-types";

export default function AQIGauge({ value, size = "lg", updatedAt }) {
  const getStatus = (aqi) => {
    if (aqi <= 50) return { text: "Good", color: "text-green-400", bg: "bg-green-500/20", ring: "border-green-500", glow: "bg-green-500/20" };
    if (aqi <= 100) return { text: "Moderate", color: "text-yellow-400", bg: "bg-yellow-500/20", ring: "border-yellow-500", glow: "bg-yellow-500/20" };
    if (aqi <= 150) return { text: "Unhealthy for Sensitive", color: "text-orange-400", bg: "bg-orange-500/20", ring: "border-orange-500", glow: "bg-orange-500/20" };
    return { text: "Unhealthy", color: "text-red-400", bg: "bg-red-500/20", ring: "border-red-500", glow: "bg-red-500/20" };
  };

  const status = getStatus(value);
  const sizeClasses = size === "lg" ? "w-48 h-48 text-6xl" : "w-32 h-32 text-4xl";

  return (
    <div className="w-full">
      <p className="text-xs text-slate-400 uppercase tracking-widest font-semibold mb-4">
        Current Status
      </p>

      <h3 className="text-2xl font-bold text-white mb-6">
        Air Quality Index
      </h3>

      {/* AQI Gauge */}
      <div className="relative flex items-center justify-center py-6">
        <div className={`absolute inset-0 ${status.glow} blur-3xl rounded-full`} />

        <div
          className={`relative ${sizeClasses} rounded-full .bg-gradient-to-br from-slate-900 to-slate-800 border-4 ${status.ring} flex items-center justify-center shadow-2xl`}
        >
          <div className="text-center">
            <p className={`font-bold ${status.color}`}>{value}</p>
            <p className="text-lg text-slate-400 mt-2">AQI</p>
          </div>
        </div>
      </div>

      {/* Status */}
      <div className="text-center space-y-3 mt-6">
        <div className={`inline-block px-4 py-2 ${status.bg} border rounded-full`}>
          <p className={`${status.color} font-bold text-sm`}>
            ⚠️ {status.text}
          </p>
        </div>

        <p className="text-slate-400 text-sm leading-relaxed">
          Air quality health impact based on current exposure levels.
        </p>
      </div>

      {/* Timestamp */}
      <div className="border-t border-slate-700 pt-4 mt-6">
        <p className="text-xs text-slate-500 text-center">
          ⏱️ Last updated:{" "}
          {updatedAt
            ? new Date(updatedAt).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })
            : "Just now"}
        </p>
      </div>
    </div>
  );
}

AQIGauge.propTypes = {
  value: PropTypes.number.isRequired,
  size: PropTypes.oneOf(["lg", "sm"]),
  updatedAt: PropTypes.string,
};
