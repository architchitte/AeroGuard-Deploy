import { useEffect, useState } from "react";
import axios from "axios";
import api from "../lib/axios";

export const useForecast6h = (location) => {
  const [forecast6h, setForecast6h] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!location?.name) return;

    const fetchForecast = async () => {
      setLoading(true);
      try {
        const res = await api.get(
          `/api/v1/forecast/${location.name}/6h`
        );

        setForecast6h(res.data?.forecast || []);
      } catch (err) {
        console.error("6H Forecast fetch failed", err);
        setForecast6h([]);
      } finally {
        setLoading(false);
      }
    };

    fetchForecast();
  }, [location?.name]);   // 🔥 ONLY city change

  return { forecast6h, loading };
};