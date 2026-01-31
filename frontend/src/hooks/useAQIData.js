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
                setData(result);
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
