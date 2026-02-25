import { useEffect, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "../api/apiConfig";

export const useForecast6h = (location) => {
  const [forecast6h, setForecast6h] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!location?.name) return;

    const fetchForecast = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (location.lat) params.append("latitude", location.lat);
        if (location.lon) params.append("longitude", location.lon);

        const res = await axios.get(
          `${API_BASE_URL}/api/v1/forecast/${location.name}/6h?${params.toString()}`);

        setForecast6h(res.data?.forecast || []);
        setSummary(res.data?.summary || null);
      } catch (err) {
        console.error("6H Forecast fetch failed", err);
        setForecast6h([]);
        setSummary(null);
      } finally {
        setLoading(false);
      }
    };

    fetchForecast();
  }, [location?.name, location?.lat, location?.lon]);

  return { forecast6h, summary, loading };
};
