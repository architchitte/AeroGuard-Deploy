// useAQIData.js
import { useState, useEffect } from "react";
import { dashboardService } from "../api/dashboardService";

export const useAQIData = (city, persona, lat = null, lon = null) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!city && !(lat && lon)) return;

    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        const result = await dashboardService.getOverview(city, persona, lat, lon);

        /* ✅ Normalize 6-hour forecast */
        const forecast6h = (result.forecast_6h || []).map((item) => ({
          time: item.time
            ?? new Date(item.timestamp).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            }),
          aqi: Number(item.aqi),
        }));

        setData({
          ...result,
          forecast_6h: forecast6h, // 👈 guaranteed format
        });
      } catch (err) {
        setError(err.message || "Failed to fetch AQI data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [city, persona, lat, lon]);

  return { data, loading, error };
};
