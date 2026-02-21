import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

export const useForecast6h = (location) => {
  const [forecast6h, setForecast6h] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!location?.name) return;

    const fetchForecast = async () => {
      setLoading(true);
      try {
        const res = await axios.get(
          `${API_BASE_URL}/api/v1/forecast/${location.name}/6h`
        );

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
  }, [location?.name]);

  return { forecast6h, summary, loading };
};
