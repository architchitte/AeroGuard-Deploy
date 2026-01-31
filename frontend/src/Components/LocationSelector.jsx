import { MapPin } from 'lucide-react';

const mockLocations = [
  { id: '1', name: 'Connaught Place', area: 'Central Delhi', lat: 28.6315, lng: 77.2167 },
  { id: '2', name: 'Delhi Center', area: 'Central Delhi', lat: 28.63, lng: 77.22 },
  { id: '3', name: 'Noida City Center', area: 'Noida', lat: 28.5921, lng: 77.3707 },
  { id: '4', name: 'Gurgaon', area: 'Haryana', lat: 28.4595, lng: 77.0266 },
  { id: '5', name: 'Greater Noida', area: 'Noida', lat: 28.4744, lng: 77.5040 },
];

export default function LocationSelector({ selected, onSelect }) {
  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl p-6 shadow-2xl border border-slate-700">
      <div className="flex items-center gap-3 mb-4">
        <MapPin className="w-5 h-5 text-teal-400" />
        <h3 className="text-lg font-bold text-white">Location</h3>
      </div>
      
      <select
        value={selected?.id || '1'}
        onChange={(e) => {
          const loc = mockLocations.find(l => l.id === e.target.value);
          onSelect(loc);
        }}
        className="w-full bg-slate-700/50 border border-slate-600 rounded-lg px-4 py-3 text-white text-sm hover:border-teal-500 transition-colors cursor-pointer"
      >
        {mockLocations.map(loc => (
          <option key={loc.id} value={loc.id}>
            {loc.name} - {loc.area}
          </option>
        ))}
      </select>
      
      <div className="mt-4 pt-4 border-t border-slate-600">
        <p className="text-slate-300 font-semibold">{selected?.name}</p>
        <p className="text-slate-400 text-sm">{selected?.area}</p>
        <p className="text-xs text-slate-500 mt-2">📍 {selected?.lat?.toFixed(4)}, {selected?.lng?.toFixed(4)}</p>
      </div>
    </div>
  );
}
