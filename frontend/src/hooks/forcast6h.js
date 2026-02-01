import { useEffect, useState } from "react";
import api from "../lib/axios";

export const useForecast6h = (location) => {
  const [forecast6h, setForecast6h] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!location?.name) {
      setForecast6h([]);
      return;
    }

    const fetchForecast = async () => {
      setLoading(true);
      try {
        const res = await api.get(
          `/api/v1/forecast/${location.name}/6h`
        );

        setForecast6h(res.data?.forecast ?? []);
      } catch (err) {
        console.error("6H Forecast fetch failed", err);
        setForecast6h([]);
      } finally {
        setLoading(false);
      }
    };

    fetchForecast();
  }, [location?.name]);

  return { forecast6h, loading };
};
