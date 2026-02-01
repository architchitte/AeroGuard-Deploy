
import React from "react";

const fetchAQI = async (lat, lon) => {
  const res = await fetch(
    `http://localhost:5000/api/v1/realtime-aqi/coordinates?latitude=${lat}&longitude=${lon}`
  );

  const json = await res.json();

  if (json.status !== "success") {
    throw new Error(json.message || "Failed to fetch AQI");
  }

  return json.data; // ← this contains AQI
};
const fetchMapData = async () => {
  const res = await fetch(
    "http://localhost:5000/api/v1/realtime-aqi/popular-cities"
  );

  if (!res.ok) {
    throw new Error("Failed to fetch nationwide AQI");
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