
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
export { fetchAQI };