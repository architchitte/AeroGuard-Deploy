const personaConfig = {
  child: {
    emoji: '👶',
    title: 'Children',
    age: 'Ages 0-12',
    advice: 'Limit prolonged outdoor play. Keep indoors as much as possible',
    borderColor: 'border-green-500/50 bg-green-500/10',
  },
  adult: {
    emoji: '👨',
    title: 'General Adult',
    age: 'Ages 13-59',
    advice: 'Reduce prolonged or heavy exertion outdoors. Take more breaks during outdoor activities',
    borderColor: 'border-green-500/50 bg-green-500/10',
  },
  athlete: {
    emoji: '🏃',
    title: 'Athletes',
    age: 'Outdoor workers',
    advice: 'Reduce intensity of outdoor workouts. Consider indoor training alternatives',
    borderColor: 'border-orange-500/50 bg-orange-500/10',
  },
  elderly: {
    emoji: '👴',
    title: 'Elderly',
    age: 'Ages 60+',
    advice: 'Stay indoors as much as possible. Use air purifier indoors',
    borderColor: 'border-orange-500/50 bg-orange-500/10',
  },
};

export default function HealthAdviceCard({ persona, aqi, isSelected, onClick }) {
  const config = personaConfig[persona];

  return (
    <div
      onClick={onClick}
      className={`${config.borderColor} border rounded-lg p-4 transition-all hover:scale-105 cursor-pointer ${
        isSelected ? 'ring-2 ring-teal-500' : ''
      }`}
    >
      <div className="flex items-start gap-3 mb-3">
        <span className="text-2xl">{config.emoji}</span>
        <div className="flex-1">
          <p className="text-white font-semibold">{config.title}</p>
          <p className="text-xs text-slate-400">{config.age}</p>
        </div>
      </div>
      <p className="text-xs text-slate-300 mb-2 font-semibold">Health Advisory</p>
      <p className="text-sm text-slate-300">{config.advice}</p>
    </div>
  );
}
