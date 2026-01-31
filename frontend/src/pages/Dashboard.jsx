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
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 pb-8">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(34,197,94,0.08),_transparent_55%)] pointer-events-none" />
      
      <div className="relative max-w-7xl mx-auto px-6 py-6">
        {/* Header */}
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-1">Air Quality Dashboard</h1>
            <p className="text-slate-400">Real-time predictions with explainable AI</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="icon">
              <Bell className="w-5 h-5" />
            </Button>
            <Button variant="outline" className="gap-2">
              <RefreshCw className="w-4 h-4" />
              Refresh
            </Button>
          </div>
        </header>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Main AQI Display */}
          <div className="lg:col-span-1 space-y-6">
            {/* Location Selector */}
            <LocationSelector
              selected={selectedLocation}
              onSelect={setSelectedLocation}
            />

            {/* AQI Gauge */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl p-8 shadow-2xl border border-slate-700">
              <AQIGauge value={currentAQI} size="lg" />
            </div>

            {/* Pollutants Grid */}
            <div className="grid grid-cols-2 gap-3">
              {mockPollutants.map((pollutant) => (
                <PollutantCard key={pollutant.name} {...pollutant} />
              ))}
            </div>
          </div>

          {/* Right Column - Forecasts & Insights */}
          <div className="lg:col-span-2 space-y-6">
            {/* 6-Hour Forecast */}
            <ForecastCard forecasts={mockForecasts} />

            {/* Health Advice Section */}
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">
                Personalized Health Advice
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {["child", "adult", "athlete", "elderly"].map((persona) => (
                  <HealthAdviceCard
                    key={persona}
                    persona={persona}
                    aqi={currentAQI}
                    isSelected={selectedPersona === persona}
                    onClick={() => setSelectedPersona(persona)}
                  />
                ))}
              </div>
            </div>

            {/* Explainability Panel */}
            <ExplainabilityPanel aqi={currentAQI} />
          </div>
        </div>
      </div>
    </div>
  );
}
