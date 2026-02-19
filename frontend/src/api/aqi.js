const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const fetchAQI = async (lat, lon) => {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/realtime-aqi/coordinates?latitude=${lat}&longitude=${lon}`
  );

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  }

  const json = await res.json();

  if (json.status !== "success") {
    throw new Error(json.message || "Failed to fetch AQI");
  }

  return json.data;
};

const fetchMapData = async () => {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/realtime-aqi/popular-cities`
  );

  if (!res.ok) {
    throw new Error(`Failed to fetch nationwide AQI: ${res.status}`);
  }

  const json = await res.json();

  if (json.status !== "success") {
    throw new Error(json.message || "Invalid AQI data");
  }

  return Object.entries(json.data)
    .filter(([_, v]) => v && v.lat && v.lon && v.aqi)
    .map(([city, v]) => ({
      station: city,
      lat: v.lat,
      lon: v.lon,
      aqi: v.aqi,
    }));
};

export { fetchAQI, fetchMapData };