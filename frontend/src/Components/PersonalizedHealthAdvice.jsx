export default function PersonalizedHealthAdvice() {
  const personas = [
    {
      icon: "👶",
      name: "Children",
      age: "Aged 5–14",
      color: "border-green-500/40 bg-green-500/10",
      advice:
        "Limit prolonged outdoor play. Keep children indoors as much as possible, especially during peak pollution hours.",
    },
    {
      icon: "🧑",
      name: "General Adult",
      age: "Aged 18–60",
      color: "border-green-500/40 bg-green-500/10",
      advice:
        "Reduce prolonged or heavy exertion outdoors. Take more breaks and avoid high-traffic areas when possible.",
    },
    {
      icon: "🏃",
      name: "Athletes",
      age: "Active Individuals",
      color: "border-orange-500/40 bg-orange-500/10",
      advice:
        "Reduce workout intensity outdoors. Prefer indoor training or schedule workouts during early morning hours.",
    },
    {
      icon: "👴",
      name: "Elderly",
      age: "Aged 60+",
      color: "border-orange-500/40 bg-orange-500/10",
      advice:
        "Stay indoors as much as possible. Use air purifiers and avoid exposure during high pollution periods.",
    },
  ];

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-6">
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-white pl-7">
          Personalized Health Advice
        </h3>
        <span className="text-xl"></span>
      </div>

      {/* CARDS */}
      <div className="space-y-5">
        {personas.map((persona, idx) => (
          <div
            key={idx}
            className={`rounded-xl border ${persona.color} p-5 transition-all duration-300 hover:border-opacity-80`}
          >
            <div className="flex items-start gap-4">
              <div className="text-3xl">{persona.icon}</div>

              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <p className="text-white font-semibold text-base">
                    {persona.name}
                  </p>
                  <span className="text-xs text-slate-400">
                    {persona.age}
                  </span>
                </div>

                <p className="text-xs uppercase tracking-widest text-slate-500">
                  Health Advisory
                </p>

                <p className="text-sm text-slate-300 leading-relaxed mt-2">
                  {persona.advice}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
