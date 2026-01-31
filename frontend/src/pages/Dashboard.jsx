import { useState } from "react";
import AQIGauge from "../components/AQIGauge";
import ForecastCard from "../components/HourlyForecast";
import HealthAdviceCard from "../components/HealthAdviceCard";
import ExplainabilityPanel from "../components/ExplainabilityPanel";
import LocationSelector from "../components/LocationSelector";
import PollutantCard from "../components/PollutantCard";
import { Button } from "../components/ui/button";
import { RefreshCw, Bell } from "lucide-react";

const mockLocation = {
  id: "1",
  name: "Connaught Place",
  area: "Central Delhi",
  lat: 28.6315,
  lng: 77.2167,
};

const mockForecasts = [
  { hour: "Now", aqi: 142, trend: "up" },
  { hour: "+1h", aqi: 156, trend: "up" },
  { hour: "+2h", aqi: 168, trend: "up" },
  { hour: "+3h", aqi: 152, trend: "down" },
  { hour: "+4h", aqi: 138, trend: "down" },
  { hour: "+5h", aqi: 125, trend: "down" },
];

const mockPollutants = [
  { name: "PM2.5", value: 85, unit: "µg/m³", limit: 25, description: "Fine particulate matter" },
  { name: "PM10", value: 142, unit: "µg/m³", limit: 50, description: "Coarse particulate matter" },
  { name: "O₃", value: 45, unit: "ppb", limit: 60, description: "Ground-level ozone" },
  { name: "NO₂", value: 38, unit: "ppb", limit: 40, description: "Nitrogen dioxide" },
];

export default function Dashboard() {
  const [selectedLocation, setSelectedLocation] = useState(mockLocation);
  const [selectedPersona, setSelectedPersona] = useState("adult");
  const currentAQI = 142;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 pb-8 sm:pb-10 lg:pb-12">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(16,185,129,0.12),_transparent_50%)] pointer-events-none" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_20%,_rgba(34,211,238,0.08),_transparent_40%)] pointer-events-none" />
      
      <div className="relative w-full max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-4 sm:py-6 md:py-8 lg:py-10">
        {/* Header */}
        <header className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 sm:mb-8 md:mb-10 gap-3 sm:gap-4">
          <div className="space-y-1 sm:space-y-1.5 w-full sm:w-auto">
            <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold text-white tracking-tight leading-tight">Air Quality Dashboard</h1>
            <p className="text-slate-400 text-xs sm:text-sm md:text-base font-medium">Real-time predictions with explainable AI</p>
          </div>
          <div className="flex items-center gap-2 sm:gap-2.5 flex-shrink-0">
            <Button 
              variant="outline" 
              size="icon"
              className="border-slate-700 bg-slate-800/50 hover:bg-slate-800 hover:border-slate-600 text-slate-300 hover:text-white transition-all duration-200 backdrop-blur-sm w-9 h-9 sm:w-10 sm:h-10"
            >
              <Bell className="w-4 h-4 sm:w-5 sm:h-5" />
            </Button>
            <Button 
              variant="outline" 
              className="gap-1.5 sm:gap-2 border-slate-700 bg-slate-800/50 hover:bg-slate-800 hover:border-slate-600 text-slate-300 hover:text-white transition-all duration-200 backdrop-blur-sm px-2.5 sm:px-4 py-1.5 sm:py-2 text-xs sm:text-sm"
            >
              <RefreshCw className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              <span className="hidden sm:inline font-medium">Refresh</span>
            </Button>
          </div>
        </header>

        {/* Main Grid - Responsive 1 column on mobile, 3 on desktop */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 lg:gap-6">
          {/* Left Column - Main AQI Display */}
          <div className="lg:col-span-1 space-y-4 sm:space-y-5 lg:space-y-6">
            {/* Location Selector */}
            <div className="transform transition-all duration-300 hover:scale-[1.01]">
              <LocationSelector
                selected={selectedLocation}
                onSelect={setSelectedLocation}
              />
            </div>

            {/* AQI Gauge */}
            <div className="bg-gradient-to-br from-slate-800/90 via-slate-800/80 to-slate-900/90 rounded-xl sm:rounded-2xl lg:rounded-3xl p-4 sm:p-6 lg:p-8 shadow-2xl border border-slate-700/50 backdrop-blur-xl transform transition-all duration-300 hover:shadow-emerald-500/10 hover:border-slate-600/50">
              <AQIGauge value={currentAQI} size="lg" />
            </div>

            {/* Pollutants Grid - 2 columns on all sizes */}
            <div className="grid grid-cols-2 gap-2 sm:gap-3 lg:gap-4">
              {mockPollutants.map((pollutant, index) => (
                <div 
                  key={pollutant.name}
                  className="transform transition-all duration-300 hover:scale-[1.02]"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <PollutantCard {...pollutant} />
                </div>
              ))}
            </div>
          </div>

          {/* Right Column - Forecasts & Insights */}
          <div className="md:col-span-1 lg:col-span-2 space-y-4 sm:space-y-5 lg:space-y-6">
            {/* 6-Hour Forecast */}
            <div className="transform transition-all duration-300 hover:shadow-lg hover:shadow-emerald-500/5">
              <ForecastCard forecasts={mockForecasts} />
            </div>

            {/* Health Advice Section */}
            <div className="space-y-3 sm:space-y-4 lg:space-y-5">
              <h3 className="text-base sm:text-lg lg:text-xl font-semibold text-white tracking-tight px-1">
                Personalized Health Advice
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-2.5 sm:gap-3 lg:gap-4">
                {["child", "adult", "athlete", "elderly"].map((persona, index) => (
                  <div 
                    key={persona}
                    className="transform transition-all duration-300"
                    style={{ animationDelay: `${index * 75}ms` }}
                  >
                    <HealthAdviceCard
                      persona={persona}
                      aqi={currentAQI}
                      isSelected={selectedPersona === persona}
                      onClick={() => setSelectedPersona(persona)}
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Explainability Panel */}
            <div className="transform transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/5">
              <ExplainabilityPanel aqi={currentAQI} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}