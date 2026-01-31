export default function PersonalizedHealthAdvice() {
  const personas = [
    { icon: '👶', name: 'Children', status: 'Health Advisory', color: 'border-green-500/50 bg-green-500/10', advice: 'Limit prolonged outdoor play. Keep indoors as much as possible' },
    { icon: '👨', name: 'General Adult', status: 'Health Advisory', color: 'border-green-500/50 bg-green-500/10', advice: 'Reduce prolonged or heavy exertion outdoors. Take more breaks during outdoor activities' },
    { icon: '🏃', name: 'Athletes', status: 'Health Advisory', color: 'border-orange-500/50 bg-orange-500/10', advice: 'Reduce intensity of outdoor workouts. Consider indoor training alternatives' },
    { icon: '👴', name: 'Elderly', status: 'Health Advisory', color: 'border-orange-500/50 bg-orange-500/10', advice: 'Stay indoors as much as possible. Use air purifier indoors' },
  ];

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl p-6 shadow-2xl border border-slate-700">
      <div className="flex items-center gap-2 mb-6">
        <h3 className="text-lg font-bold text-white">Personalized Health Advice</h3>
        <span className="text-xl">💚</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {personas.map((persona, idx) => (
          <div
            key={idx}
            className={`${persona.color} border rounded-lg p-4 transition-all hover:scale-105`}
          >
            <div className="flex items-start gap-3 mb-3">
              <span className="text-2xl">{persona.icon}</span>
              <div className="flex-1">
                <p className="text-white font-semibold">{persona.name}</p>
                <p className="text-xs text-slate-400">Aged 5-14</p>
              </div>
            </div>
            <p className="text-xs text-slate-300">{persona.status}</p>
            <p className="text-sm text-slate-300 mt-2">{persona.advice}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
