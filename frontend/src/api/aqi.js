
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
const fetchMapData = async (sw_lat, sw_lng, ne_lat, ne_lng) => {
  let url = `http://localhost:5000/api/v1/realtime-aqi/map-data`;
  if (sw_lat && sw_lng && ne_lat && ne_lng) {
    url += `?sw_lat=${sw_lat}&sw_lng=${sw_lng}&ne_lat=${ne_lat}&ne_lng=${ne_lng}`;
  }

  const res = await fetch(url);
  const json = await res.json();

  if (json.status !== "success") {
    throw new Error(json.message || "Failed to fetch map data");
  }

  return json.data;
};

export { fetchAQI, fetchMapData };