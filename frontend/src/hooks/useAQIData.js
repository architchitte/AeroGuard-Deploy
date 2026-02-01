import { useState, useEffect } from 'react';
import { dashboardService } from '../api/dashboardService';

export const useAQIData = (city, persona) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!city || !persona) return;

        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                const result = await dashboardService.getOverview(city, persona);

                /* ✅ ADDITION: normalize pollutants ONLY */
                const normalizedPollutants = result?.pollutants
                  ? {
                      pm25: { value: result.pollutants["PM2.5"] ?? 0 },
                      pm10: { value: result.pollutants["PM10"] ?? 0 },
                      no2:  { value: result.pollutants["NO2"] ?? 0 },
                      o3:   { value: result.pollutants["O3"] ?? 0 },
                      so2:  { value: result.pollutants["SO2"] ?? 0 },
                      co:   { value: result.pollutants["CO"] ?? 0 },
                    }
                  : {};

                setData({
                    ...result,
                    pollutants: normalizedPollutants, // 👈 injected here
                });
            } catch (err) {
                setError(err.message || 'Failed to fetch AQI data');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [city, persona]);

    return { data, loading, error };
};
