import { API_BASE_URL } from './apiConfig';

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
    `${API_BASE_URL}/api/v1/realtime-aqi/nationwide`
  );

  if (!res.ok) {
    throw new Error(`Failed to fetch nationwide AQI: ${res.status}`);
  }

  const json = await res.json();

  if (json.status !== "success") {
    throw new Error(json.message || "Invalid AQI data");
  }

  return json.data.map((v) => ({
    station: v.station,
    lat: v.lat,
    lon: v.lon,
    aqi: v.aqi,
  }));
};

const fetchToken = async () => {
  const res = await fetch(`${API_BASE_URL}/api/v1/realtime-aqi/token`);
  if (!res.ok) throw new Error("Failed to fetch token");
  const json = await res.json();
  return json.token;
};

export { fetchAQI, fetchMapData, fetchToken };
