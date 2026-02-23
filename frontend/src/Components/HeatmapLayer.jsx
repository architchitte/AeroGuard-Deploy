import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';

/**
 * Custom Heatmap Layer Component
 * 
 * Replaces react-leaflet-heatmap-layer-v3 with direct leaflet.heat integration
 * Compatible with React 18 and react-leaflet 4.x
 */
function HeatmapLayer({ points, options = {} }) {
  const map = useMap();

  useEffect(() => {
    if (!points || points.length === 0) return;

    // Verify L.heatLayer exists (plugin loading check)
    if (typeof L.heatLayer !== 'function') {
      console.warn('L.heatLayer is not available. Ensure leaflet.heat is loaded.');
      return;
    }

    // Convert points to leaflet.heat format: [lat, lng, intensity]
    const heatPoints = points.map(point => {
      const lat = typeof options.latitudeExtractor === 'function'
        ? options.latitudeExtractor(point)
        : point.lat;
      const lng = typeof options.longitudeExtractor === 'function'
        ? options.longitudeExtractor(point)
        : point.lng || point.lon;
      const intensity = typeof options.intensityExtractor === 'function'
        ? options.intensityExtractor(point)
        : point.value || point.intensity || 1;

      return [lat, lng, intensity];
    });

    // Create heatmap layer with options
    const heatLayer = L.heatLayer(heatPoints, {
      radius: options.radius || 25,
      blur: options.blur || 15,
      maxZoom: options.maxZoom || 17,
      max: options.max || 1.0,
      minOpacity: options.minOpacity || 0.05,
      gradient: options.gradient || {
        0.0: 'blue',
        0.5: 'lime',
        0.7: 'yellow',
        0.9: 'orange',
        1.0: 'red'
      }
    }).addTo(map);

    // Patch for the willReadFrequently warning if possible
    // Note: leaflet.heat creates a private canvas, so direct patching is difficult.
    // However, we can hint to the browser by creating a dummy canvas if needed, 
    // but the best fix is in the library itself. We'll stick to the safety check.

    // Cleanup on unmount or when points change
    return () => {
      if (map && heatLayer) {
        map.removeLayer(heatLayer);
      }
    };
  }, [map, points, options]);

  return null;
}

export default HeatmapLayer;
