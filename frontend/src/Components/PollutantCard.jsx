export default function PollutantCard({ name, value, unit, limit, description }) {
  const getStatus = () => {
    if (value > limit * 2) return { color: 'text-red-400', bg: 'bg-red-500/10' };
    if (value > limit) return { color: 'text-orange-400', bg: 'bg-orange-500/10' };
    return { color: 'text-green-400', bg: 'bg-green-500/10' };
  };

  const status = getStatus();

  return (
    <div className={`${status.bg} border border-slate-700 rounded-lg p-4 space-y-2`}>
      <p className="text-slate-300 text-sm font-semibold">{name}</p>
      <p className={`text-2xl font-bold ${status.color}`}>{value}</p>
      <p className="text-xs text-slate-400">{unit}</p>
      <div className="pt-2 border-t border-slate-600">
        <p className="text-xs text-slate-400">{description}</p>
        <p className={`text-xs font-semibold ${status.color} mt-1`}>
          Limit: {limit} {unit}
        </p>
      </div>
    </div>
  );
}
