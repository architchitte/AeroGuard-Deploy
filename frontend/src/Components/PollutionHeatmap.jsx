import { useState, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Circle,
  CircleMarker,
  Tooltip,
  useMap
} from "react-leaflet";
import { useNavigate } from "react-router-dom";
import "leaflet/dist/leaflet.css";
import {
  Maximize,
  ZoomIn,
  Globe,
  Wind,
  Droplets,
  CloudRain,
  Activity,
  ChevronRight,
  ChevronLeft,
  X,
  MapPin,
  TrendingUp
} from "lucide-react";

import LocationSearch from "../Components/LocationSelector";
import { fetchAQI, fetchMapData } from "../api/aqi";
import HeatmapLayer from "./HeatmapLayer";  // Custom heatmap component


/* ================= MAP CONTROLLER ================= */

function MapController({ center, zoom }) {
  const map = useMap();

  useEffect(() => {
    if (!center) return;
    map.flyTo(center, zoom, { animate: true, duration: 1.5 });
  }, [center, zoom, map]);

  return null;
}

/* ================= AQI HELPERS ================= */

const getAQIColor = (aqi) => {
  if (aqi <= 50) return "#14b8a6";
  if (aqi <= 100) return "#facc15";
  if (aqi <= 150) return "#f97316";
  if (aqi <= 200) return "#ef4444";
  if (aqi <= 300) return "#7f1d1d";
  return "#450a0a";
};

const getAQILabel = (aqi) => {
  if (aqi <= 50) return "Good";
  if (aqi <= 100) return "Moderate";
  if (aqi <= 150) return "Unhealthy for Sensitive Groups";
  if (aqi <= 200) return "Unhealthy";
  if (aqi <= 300) return "Very Unhealthy";
  return "Hazardous";
}
const getHealthAdvice = (aqi) => {
  if (aqi <= 50) return "Air quality is ideal for outdoor activities.";
  if (aqi <= 100) return "Air quality is acceptable; however, sensitive individuals should monitor their symptoms.";
  if (aqi <= 150) return "Members of sensitive groups may experience health effects. The general public is less likely to be affected.";
  if (aqi <= 200) return "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects.";
  if (aqi <= 300) return "Health warnings of emergency conditions. The entire population is more likely to be affected.";
  return "Health alert: everyone may experience more serious health effects.";
};

/* ================= CONSTANTS ================= */

const FAMOUS_PLACES = [
  // --- METROS & TIER 1 ---
  { name: "New Delhi", lat: 28.6139, lon: 77.2090 },
  { name: "Mumbai", lat: 19.0760, lon: 72.8777 },
  { name: "Bengaluru", lat: 12.9716, lon: 77.5946 },
  { name: "Hyderabad", lat: 17.3850, lon: 78.4867 },
  { name: "Chennai", lat: 13.0827, lon: 80.2707 },
  { name: "Kolkata", lat: 22.5726, lon: 88.3639 },
  { name: "Pune", lat: 18.5204, lon: 73.8567 },
  { name: "Ahmedabad", lat: 23.0225, lon: 72.5714 },
  { name: "Surat", lat: 21.1702, lon: 72.8311 },
  { name: "Visakhapatnam", lat: 17.6868, lon: 83.2185 },

  // --- NORTH INDIA ---
  { name: "Jaipur", lat: 26.9124, lon: 75.7873 },
  { name: "Lucknow", lat: 26.8467, lon: 80.9462 },
  { name: "Kanpur", lat: 26.4499, lon: 80.3319 },
  { name: "Chandigarh", lat: 30.7333, lon: 76.7794 },
  { name: "Ludhiana", lat: 30.9010, lon: 75.8573 },
  { name: "Agra", lat: 27.1767, lon: 78.0081 },
  { name: "Varanasi", lat: 25.3176, lon: 82.9739 },
  { name: "Meerut", lat: 28.9845, lon: 77.7064 },
  { name: "Faridabad", lat: 28.4089, lon: 77.3178 },
  { name: "Ghaziabad", lat: 28.6692, lon: 77.4538 },
  { name: "Noida", lat: 28.5355, lon: 77.3910 },
  { name: "Gurgaon", lat: 28.4595, lon: 77.0266 },
  { name: "Amritsar", lat: 31.6340, lon: 74.8723 },
  { name: "Jalandhar", lat: 31.3260, lon: 75.5762 },
  { name: "Shimla", lat: 31.1048, lon: 77.1734 },
  { name: "Dehradun", lat: 30.3165, lon: 78.0322 },
  { name: "Srinagar", lat: 34.0837, lon: 74.7973 },
  { name: "Jammu", lat: 32.7266, lon: 74.8570 },
  { name: "Rohtak", lat: 28.8955, lon: 76.6066 },
  { name: "Panipat", lat: 29.3909, lon: 76.9635 },
  { name: "Karnal", lat: 29.6857, lon: 76.9907 },
  { name: "Ambala", lat: 30.3782, lon: 76.7767 },
  { name: "Patiala", lat: 30.3398, lon: 76.3869 },
  { name: "Bathinda", lat: 30.2110, lon: 74.9455 },
  { name: "Bikaner", lat: 28.0229, lon: 73.3119 },
  { name: "Ajmer", lat: 26.4499, lon: 74.6399 },
  { name: "Udaipur", lat: 24.5854, lon: 73.7125 },
  { name: "Jodhpur", lat: 26.2389, lon: 73.0243 },
  { name: "Kota", lat: 25.2138, lon: 75.8648 },
  { name: "Alwar", lat: 27.5530, lon: 76.6346 },
  { name: "Bareilly", lat: 28.3670, lon: 79.4304 },
  { name: "Aligarh", lat: 27.8974, lon: 78.0880 },
  { name: "Moradabad", lat: 28.8386, lon: 78.7733 },
  { name: "Gorakhpur", lat: 26.7606, lon: 83.3731 },
  { name: "Jhansi", lat: 25.4484, lon: 78.5685 },
  { name: "Firozabad", lat: 27.1508, lon: 78.3947 },
  { name: "Mathura", lat: 27.4924, lon: 77.6737 },
  { name: "Haridwar", lat: 29.9457, lon: 78.1642 },
  { name: "Rishikesh", lat: 30.0869, lon: 78.2676 },

  // --- WEST INDIA ---
  { name: "Nagpur", lat: 21.1458, lon: 79.0882 },
  { name: "Nashik", lat: 19.9975, lon: 73.7898 },
  { name: "Aurangabad", lat: 19.8762, lon: 75.3433 },
  { name: "Solapur", lat: 17.6599, lon: 75.9064 },
  { name: "Amravati", lat: 20.9320, lon: 77.7523 },
  { name: "Navi Mumbai", lat: 19.0330, lon: 73.0297 },
  { name: "Vashi", lat: 19.0745, lon: 72.9978 },
  { name: "Nerul", lat: 19.0330, lon: 73.0297 },
  { name: "Belapur", lat: 19.0144, lon: 73.0396 },
  { name: "Kharghar", lat: 19.0473, lon: 73.0699 },
  { name: "Seawoods", lat: 19.0177, lon: 73.0186 },
  { name: "Airoli", lat: 19.1579, lon: 72.9935 },
  { name: "Ghansoli", lat: 19.1235, lon: 73.0039 },
  { name: "Kopar Khairane", lat: 19.0965, lon: 73.0104 },
  { name: "Sanpada", lat: 19.0624, lon: 73.0078 },
  { name: "Kamothe", lat: 19.0200, lon: 73.0800 },
  { name: "Kalamboli", lat: 19.0300, lon: 73.1100 },
  { name: "Uran", lat: 18.8775, lon: 72.9348 },
  { name: "Thane", lat: 19.2183, lon: 72.9781 },
  { name: "Kalyan", lat: 19.2403, lon: 73.1305 },
  { name: "Vasai-Virar", lat: 19.3919, lon: 72.8397 },
  { name: "Kolhapur", lat: 16.7050, lon: 74.2433 },
  { name: "Akola", lat: 20.7002, lon: 77.0082 },
  { name: "Jalgaon", lat: 21.0077, lon: 75.5626 },
  { name: "Nanded", lat: 19.1628, lon: 77.3176 },
  { name: "Sangli", lat: 16.8524, lon: 74.5815 },
  { name: "Rajkot", lat: 22.3039, lon: 70.8022 },
  { name: "Vadodara", lat: 22.3072, lon: 73.1812 },
  { name: "Bhavnagar", lat: 21.7645, lon: 72.1519 },
  { name: "Jamnagar", lat: 22.4707, lon: 70.0577 },
  { name: "Junagadh", lat: 21.5222, lon: 70.4579 },
  { name: "Gandhidham", lat: 23.0763, lon: 70.1270 },
  { name: "Anand", lat: 22.5645, lon: 72.9289 },
  { name: "Gandhinagar", lat: 23.2167, lon: 72.6833 },
  { name: "Gwalior", lat: 26.2183, lon: 78.1828 },
  { name: "Indore", lat: 22.7196, lon: 75.8577 },
  { name: "Bhopal", lat: 23.2599, lon: 77.4126 },
  { name: "Jabalpur", lat: 23.1815, lon: 79.9864 },
  { name: "Ujjain", lat: 23.1760, lon: 75.7885 },
  { name: "Sagar", lat: 23.8388, lon: 78.7378 },
  { name: "Ratlam", lat: 23.3315, lon: 75.0367 },

  // --- CENTRAL & EAST INDIA ---
  { name: "Raipur", lat: 21.2514, lon: 81.6296 },
  { name: "Bhilai", lat: 21.1938, lon: 81.3509 },
  { name: "Bilaspur", lat: 22.0778, lon: 82.1397 },
  { name: "Patna", lat: 25.5941, lon: 85.1376 },
  { name: "Gaya", lat: 24.7914, lon: 85.0002 },
  { name: "Bhagalpur", lat: 25.2425, lon: 86.9718 },
  { name: "Muzaffarpur", lat: 26.1209, lon: 85.3647 },
  { name: "Ranchi", lat: 23.3441, lon: 85.3094 },
  { name: "Dhanbad", lat: 23.7957, lon: 86.4304 },
  { name: "Jamshedpur", lat: 22.8046, lon: 86.2029 },
  { name: "Bokaro", lat: 23.6693, lon: 86.1511 },
  { name: "Bhubaneswar", lat: 20.2961, lon: 85.8245 },
  { name: "Cuttack", lat: 20.4625, lon: 85.8830 },
  { name: "Rourkela", lat: 22.2604, lon: 84.8536 },
  { name: "Puri", lat: 19.8135, lon: 85.8312 },
  { name: "Howrah", lat: 22.5958, lon: 88.2636 },
  { name: "Durgapur", lat: 23.4807, lon: 87.3119 },
  { name: "Asansol", lat: 23.6739, lon: 86.9524 },
  { name: "Siliguri", lat: 26.7271, lon: 88.3953 },
  { name: "Darjeeling", lat: 27.0410, lon: 88.2627 },
  { name: "Guwahati", lat: 26.1158, lon: 91.7086 },
  { name: "Agartala", lat: 23.8315, lon: 91.2723 },
  { name: "Shillong", lat: 25.5788, lon: 91.8933 },
  { name: "Imphal", lat: 24.8170, lon: 93.9368 },
  { name: "Aizawl", lat: 23.7307, lon: 92.7173 },
  { name: "Dimapur", lat: 25.9061, lon: 93.7270 },

  // --- SOUTH INDIA ---
  { name: "Coimbatore", lat: 11.0168, lon: 76.9558 },
  { name: "Madurai", lat: 9.9252, lon: 78.1198 },
  { name: "Tiruchirappalli", lat: 10.7905, lon: 78.7047 },
  { name: "Salem", lat: 11.6643, lon: 78.1460 },
  { name: "Mysore", lat: 12.2958, lon: 76.6394 },
  { name: "Hubli", lat: 15.3647, lon: 75.1240 },
  { name: "Belgaum", lat: 15.8497, lon: 74.4977 },
  { name: "Mangalore", lat: 12.9141, lon: 74.8560 },
  { name: "Kochi", lat: 9.9312, lon: 76.2673 },
  { name: "Kozhikode", lat: 11.2588, lon: 75.7804 },
  { name: "Thiruvananthapuram", lat: 8.5241, lon: 76.9366 },
  { name: "Nellore", lat: 14.4426, lon: 79.9865 },
  { name: "Vijayawada", lat: 16.5062, lon: 80.6480 },
  { name: "Guntur", lat: 16.3067, lon: 80.4365 },
  { name: "Warangal", lat: 17.9689, lon: 79.5941 },
  { name: "Nizamabad", lat: 18.6725, lon: 78.0941 },
  { name: "Pondicherry", lat: 11.9416, lon: 79.8083 },

  // --- ADDING MORE DENSITY (Smaller/Support Cities) ---
  { name: "Roorkee", lat: 29.8543, lon: 77.8880 },
  { name: "Muzaffarnagar", lat: 29.4727, lon: 77.7085 },
  { name: "Bhiwani", lat: 28.7909, lon: 76.1322 },
  { name: "Hisar", lat: 29.1492, lon: 75.7217 },
  { name: "Tirupati", lat: 13.6288, lon: 79.4192 },
  { name: "Kurnool", lat: 15.8281, lon: 78.0373 },
  { name: "Dharwad", lat: 15.4589, lon: 75.0078 },
  { name: "Udupi", lat: 13.3409, lon: 74.7421 },
  { name: "Kannur", lat: 11.8745, lon: 75.3704 },
  { name: "Kollam", lat: 8.8932, lon: 76.6141 },
  { name: "Vellore", lat: 12.9165, lon: 79.1325 },
  { name: "Hosur", lat: 12.7409, lon: 77.8253 },
  { name: "Gulbarga", lat: 17.3297, lon: 76.8343 },
  { name: "Bellary", lat: 15.1394, lon: 76.9214 },
  { name: "Satara", lat: 17.6805, lon: 73.9915 },
  { name: "Sangli", lat: 16.8524, lon: 74.5815 },
  { name: "Ratnagiri", lat: 16.9902, lon: 73.3120 },
  { name: "Bharuch", lat: 21.7119, lon: 72.9866 },
  { name: "Vapi", lat: 20.3700, lon: 72.9106 },
  { name: "Bhuj", lat: 23.2383, lon: 69.6661 },
  { name: "Palanpur", lat: 24.1722, lon: 72.4338 },
  { name: "Haldwani", lat: 29.2183, lon: 79.5130 },
  { name: "Moradabad", lat: 28.8386, lon: 78.7733 },
  { name: "Rampur", lat: 28.8123, lon: 79.0267 },
  { name: "Etawah", lat: 26.7725, lon: 79.0233 },
  { name: "Mirzapur", lat: 25.1333, lon: 82.5644 },
  { name: "Sonipat", lat: 28.9931, lon: 77.0151 },
  { name: "Rewari", lat: 28.1837, lon: 76.6114 },
  { name: "Yamunanagar", lat: 30.1290, lon: 77.2674 },
  { name: "Pathankot", lat: 32.2733, lon: 75.6522 },
  { name: "Mandi", lat: 31.7087, lon: 76.9320 },
  { name: "Kullu", lat: 31.9579, lon: 77.1095 },
  { name: "Manali", lat: 32.2432, lon: 77.1892 },
  { name: "Dibrugarh", lat: 27.4728, lon: 94.9120 },
  { name: "Silchar", lat: 24.8197, lon: 92.7782 },
  { name: "Jorhat", lat: 26.7509, lon: 94.2037 },
  { name: "Tinsukia", lat: 27.4922, lon: 95.3533 },
  { name: "Kohima", lat: 25.6751, lon: 94.1086 },
  { name: "Almora", lat: 29.5892, lon: 79.6467 },
  { name: "Nainital", lat: 29.3919, lon: 79.4542 },
  { name: "Solan", lat: 30.9045, lon: 77.0967 },
  { name: "Dharamsala", lat: 32.2190, lon: 76.3234 },
  { name: "Anantnag", lat: 33.7311, lon: 75.1487 },
  { name: "Baramulla", lat: 34.2023, lon: 74.3413 },
  { name: "Kargil", lat: 34.5539, lon: 76.1349 },
  { name: "Khammam", lat: 17.2473, lon: 80.1514 },
  { name: "Karimnagar", lat: 18.4386, lon: 79.1288 },
  { name: "Hosapete", lat: 15.2689, lon: 76.3909 },
  { name: "Raichur", lat: 16.2084, lon: 77.3592 },
  { name: "Bidar", lat: 17.9120, lon: 77.5188 },
  { name: "Tumakuru", lat: 13.3392, lon: 77.1140 },
  { name: "Hassan", lat: 13.0070, lon: 76.1020 },
  { name: "Chikmagalur", lat: 13.3153, lon: 75.7754 },
  { name: "Kasaragod", lat: 12.5101, lon: 74.9852 },
  { name: "Idukki", lat: 9.8500, lon: 76.9700 },
  { name: "Alappuzha", lat: 9.4981, lon: 76.3388 },
  { name: "Kanyakumari", lat: 8.0883, lon: 77.5385 },
  { name: "Tuticorin", lat: 8.7139, lon: 78.1348 },
  { name: "Thanjavur", lat: 10.7852, lon: 79.1391 },
  { name: "Dharmapuri", lat: 12.1273, lon: 78.1585 },
  { name: "Ratnagiri", lat: 16.9902, lon: 73.3121 },
  { name: "Panvel", lat: 18.9894, lon: 73.1175 },
  { name: "Latur", lat: 18.4088, lon: 76.5604 },
  { name: "Yavatmal", lat: 20.3900, lon: 78.1300 },
  { name: "Chandrapur", lat: 19.9500, lon: 79.3000 },
  { name: "Wardha", lat: 20.7451, lon: 78.6022 },
  { name: "Godhra", lat: 22.7753, lon: 73.6148 },
  { name: "Mehsana", lat: 23.5880, lon: 72.3693 },
  { name: "Patan", lat: 23.8500, lon: 72.1167 },
  { name: "Valsad", lat: 20.5992, lon: 72.9342 },
  { name: "Porbandar", lat: 21.6417, lon: 69.6293 },
  { name: "Daman", lat: 20.3974, lon: 72.8328 },
  { name: "Silvassa", lat: 20.2765, lon: 73.0029 },
  { name: "Rewa", lat: 24.5362, lon: 81.3037 },
  { name: "Satna", lat: 24.5764, lon: 80.8322 },
  { name: "Khandwa", lat: 21.8217, lon: 76.3481 },
  { name: "Burhanpur", lat: 21.3115, lon: 76.2230 },
  { name: "Singrauli", lat: 24.1992, lon: 82.6645 },
  { name: "Korba", lat: 22.3595, lon: 82.7501 },
  { name: "Jagdalpur", lat: 19.0700, lon: 82.0300 },
  { name: "Sambalpur", lat: 21.4669, lon: 83.9812 },
  { name: "Balasore", lat: 21.4938, lon: 86.9333 },
  { name: "Berhampur", lat: 19.3150, lon: 84.7941 },
  { name: "Rourkela", lat: 22.2604, lon: 84.8536 },
  { name: "Deoghar", lat: 24.4833, lon: 86.7000 },
  { name: "Hazaribagh", lat: 23.9925, lon: 85.3636 },
  { name: "Giridih", lat: 24.1901, lon: 86.3038 },
  { name: "Darhbanga", lat: 26.1500, lon: 85.9000 },
  { name: "Purnia", lat: 25.7771, lon: 87.4753 },
  { name: "Arrah", lat: 25.5500, lon: 84.6667 },
  { name: "Chhapra", lat: 25.7848, lon: 84.7274 }
];

/* ================= MAIN ================= */

export default function PollutionHeatmap({ externalLocation, onLocationSelect }) {
  const INDIA_CENTER = [22.3511, 78.6677];
  const navigate = useNavigate();

  const [location, setLocation] = useState(externalLocation || null);
  const [center, setCenter] = useState(INDIA_CENTER);
  const [zoom, setZoom] = useState(5);
  const [isPanelOpen, setIsPanelOpen] = useState(true);
  const [lastSync, setLastSync] = useState(new Date());
  const [hubData, setHubData] = useState([]);
  const [pollutantData, setPollutantData] = useState(null);

  // Sync with external location if provided
  useEffect(() => {
    if (externalLocation) {
      setLocation(externalLocation);
      setCenter([externalLocation.lat, externalLocation.lon]);
      setZoom(10);
      setIsPanelOpen(true);
    }
  }, [externalLocation]);

  const [aqi, setAqi] = useState(null);
  const [stations, setStations] = useState([]);
  const [loadingStations, setLoadingStations] = useState(false);
  const color = getAQIColor(aqi ?? 0);

  // 1. Fetch Nationwide & Sync Hubs
  const loadData = async () => {
    try {
      setLoadingStations(true);

      // ✅ SINGLE REQUEST for all nationwide data
      const mapData = await fetchMapData();

      // Secondary logic: Derive Hub AQI from nearest station in mapData
      // This eliminates 250+ individual network requests
      const syncedHubs = FAMOUS_PLACES.map(place => {
        // Find nearest station within 15km
        let nearestStation = null;
        let minDistance = 15; // km

        mapData.forEach(s => {
          const d = Math.sqrt(
            Math.pow(s.lat - place.lat, 2) + Math.pow(s.lon - place.lon, 2)
          ) * 111; // Rough km conversion

          if (d < minDistance) {
            minDistance = d;
            nearestStation = s;
          }
        });

        return {
          ...place,
          aqi: nearestStation ? nearestStation.aqi : 100 // Fallback to 100 if no station near
        };
      });

      setStations(mapData);
      setHubData(syncedHubs);
      setLastSync(new Date());
    } catch (err) {
      console.error("Data sync failed:", err);
    } finally {
      setLoadingStations(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5 * 60 * 1000); // Poll every 5 mins
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!location) return;

    const loadAQI = async () => {
      try {
        const data = await fetchAQI(location.lat, location.lon);
        setAqi(data.aqi);
        setPollutantData({
          pm25: data.pm25,
          pm10: data.pm10,
          no2: data.no2,
          o3: data.o3
        });
      } catch (err) {
        console.error("AQI fetch failed:", err);
      }
    };

    loadAQI();
  }, [location]);

  /* -------- SEARCH -------- */
  const handleLocationSelect = (loc) => {
    setLocation(loc);
    setCenter([loc.lat, loc.lon]);
    setZoom(11);
    setIsPanelOpen(true);
    if (onLocationSelect) onLocationSelect(loc);
  };

  /* -------- ZOOM PRESETS -------- */
  const handleZoomPreset = (type) => {
    if (type === "country") {
      setCenter(INDIA_CENTER);
      setZoom(5);
      return;
    }
    if (!location) return;
    const locCenter = [location.lat, location.lon];
    if (type === "city") {
      setCenter(locCenter);
      setZoom(10);
    }
    if (type === "region") {
      setCenter(locCenter);
      setZoom(7);
    }
  };

  /* -------- DATA PREP -------- */
  // Filter for India Bounding Box: Lat [6.7, 37.5], Lon [68.1, 97.4]
  const isPointInIndia = (lat, lon) => {
    return lat >= 6.7 && lat <= 37.5 && lon >= 68.1 && lon <= 97.4;
  };

  const heatmapPoints = stations
    .filter(s => s.lat != null && s.lon != null && s.aqi != null && !isNaN(s.aqi))
    .filter(s => isPointInIndia(s.lat, s.lon))
    .map((s) => ({
      lat: s.lat,
      lng: s.lon,
      value: Math.min(s.aqi, 500),
    }));

  const POLLUTANT_MAP = {
    pm25: { name: "PM2.5", unit: "µg/m³", icon: Droplets },
    pm10: { name: "PM10", unit: "µg/m³", icon: Wind },
    no2: { name: "NO2", unit: "ppb", icon: CloudRain },
    o3: { name: "O3", unit: "ppb", icon: Wind },
    so2: { name: "SO2", unit: "ppb", icon: Droplets },
    co: { name: "CO", unit: "ppm", icon: Activity }
  };

  const pollutants = pollutantData ? Object.entries(pollutantData)
    .filter(([key, value]) => value !== null && POLLUTANT_MAP[key])
    .map(([key, value]) => ({
      ...POLLUTANT_MAP[key],
      value: value
    })) : [];

  const healthAdvice = getHealthAdvice(aqi ?? 0);

  return (
    <div className="relative w-full h-[850px] bg-[#020617] rounded-[3rem] border border-white/5 shadow-2xl overflow-hidden group/map-section ring-1 ring-white/10">

      {/* ================= MAP Container ================= */}
      <MapContainer
        center={center}
        zoom={zoom}
        zoomControl={false}
        style={{ height: "100%", width: "100%" }}
        className="z-0"
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; CARTO'
        />

        <MapController center={center} zoom={zoom} />

        {/* ================= SELECTION AURA EFFECT ================= */}
        {location && (
          <>
            {/* 1. Outer Soft Coverage Glow (The Gradient) */}
            <Circle
              center={[location.lat, location.lon]}
              radius={30000}
              pathOptions={{
                fillColor: getAQIColor(aqi || 100),
                fillOpacity: 0.1,
                stroke: true,
                color: getAQIColor(aqi || 100),
                weight: 1,
                dashArray: "5, 10",
                opacity: 0.3
              }}
            />

            {/* 2. Mid-Range Impact Zone */}
            <Circle
              center={[location.lat, location.lon]}
              radius={15000}
              pathOptions={{
                fillColor: getAQIColor(aqi || 100),
                fillOpacity: 0.1,
                stroke: false
              }}
            />

            {/* 3. Core Targeting Ring (Pulsing) */}
            <Circle
              center={[location.lat, location.lon]}
              radius={zoom > 8 ? 5000 : 8000}
              pathOptions={{
                color: getAQIColor(aqi || 100),
                weight: 2,
                fill: true,
                fillColor: getAQIColor(aqi || 100),
                fillOpacity: 0.2,
                dashArray: "10, 10",
                opacity: 0.8
              }}
              className="selection-ring-pulse"
            />

            {/* 4. Exact Center Pinpoint */}
            <CircleMarker
              center={[location.lat, location.lon]}
              radius={zoom > 10 ? 10 : 6}
              pathOptions={{
                fillColor: getAQIColor(aqi || 100),
                fillOpacity: 1,
                color: "#fff",
                weight: 2,
              }}
            />
          </>
        )}

        {/* HEATMAP LAYER (High Resolution) */}
        {heatmapPoints.length > 0 && (
          <HeatmapLayer
            points={heatmapPoints}
            options={{
              radius: 55,      // Slightly increased for better coverage with new density
              blur: 40,        // Smoother blending
              max: 400,        // Better center-weighted intensity
              minOpacity: 0.25,
              gradient: {
                0.1: '#0ea5e9', // Deep Sky Blue (Low)
                0.2: '#14b8a6', // Teal
                0.4: '#facc15', // Yellow
                0.6: '#f97316', // Orange
                0.8: '#ef4444', // Red
                1.0: '#7f1d1d'  // Dark Red
              }
            }}
          />
        )}

        {/* FAMOUS PLACE HUBS (Hidden, used for heatmap generation) */}
        {/* Hubs are now implicit in heatmapPoints via loading logic */}

        {/* STATION MARKERS (REMOVED as requested) */}
      </MapContainer>

      {/* ================= FLOATING OVERLAYS ================= */}

      {/* 1. TOP-LEFT: SEARCH OVERLAY */}
      <div className="absolute top-8 left-8 z-[1000] w-[340px] animate-slide-right">
        <div className="glass-panel p-1 rounded-2xl border border-white/10 shadow-2xl transition-all duration-300 focus-within:border-teal-500/50 hover:border-white/20">
          <LocationSearch onSelect={handleLocationSelect} />
        </div>
      </div>

      {/* 2. CENTER-LEFT: DATA PANEL */}
      {location && (
        <div className={`absolute top-[160px] left-8 z-[900] transition-all duration-500 ease-in-out ${isPanelOpen ? 'translate-x-0 opacity-100' : '-translate-x-[110%] opacity-0'}`}>
          <div className="w-[360px] glass-panel rounded-[2.5rem] border border-white/20 shadow-[0_0_50px_rgba(0,0,0,0.5),0_0_20px_rgba(20,184,166,0.1)] overflow-hidden backdrop-blur-3xl bg-slate-950/90 p-8 space-y-8">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <p className="text-[10px] font-black uppercase text-slate-500 tracking-widest flex items-center gap-2">
                  <MapPin size={10} className="text-teal-400" /> Current Station
                </p>
                <h3 className="text-2xl font-black text-white leading-tight">{location.name}</h3>
                <p className="text-slate-400 text-xs font-medium">Regional Air Intelligence</p>
              </div>
              <button
                onClick={() => setIsPanelOpen(false)}
                className="p-2 rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
                title="Close Panel"
              >
                <X size={16} className="text-slate-500" />
              </button>
            </div>

            <div className="flex items-center justify-between gap-6 py-6 border-y border-white/5">
              <div className="space-y-1">
                <span className="text-7xl font-black text-white leading-none tracking-tighter">
                  {aqi ?? '--'}
                </span>
                <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">US-EPA Index</p>
              </div>
              <div className="flex flex-col gap-2 flex-1">
                <div
                  className="px-4 py-2 rounded-xl text-[10px] font-black uppercase text-center shadow-lg transition-colors border tracking-wider"
                  style={{
                    backgroundColor: `${getAQIColor(aqi ?? 0)}20`,
                    borderColor: `${getAQIColor(aqi ?? 0)}40`,
                    color: getAQIColor(aqi ?? 0)
                  }}
                >
                  {getAQILabel(aqi ?? 0)}
                </div>
                <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="h-full transition-all duration-1000"
                    style={{
                      width: `${Math.min(100, ((aqi ?? 0) / 300) * 100)}%`,
                      backgroundColor: getAQIColor(aqi ?? 0),
                      boxShadow: `0 0 10px ${getAQIColor(aqi ?? 0)}`
                    }}
                  />                </div>
              </div>
            </div>


            <div className="p-5 rounded-3xl bg-gradient-to-br from-teal-500/10 via-emerald-500/5 to-transparent border border-teal-500/20">
              <div className="flex items-center gap-2 mb-2">
                <Activity size={12} className="text-teal-400 animate-pulse" />
                <span className="text-[10px] font-black uppercase text-teal-400 tracking-widest">AI Health Pulse</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed italic mb-4">
                "{healthAdvice}"
              </p>

              <button
                onClick={() => navigate('/dashboard', { state: { selectedLocation: location } })}
                className="w-full py-3 bg-teal-500/10 hover:bg-teal-500/20 border border-teal-500/30 rounded-2xl text-teal-400 text-[10px] font-black uppercase tracking-[0.2em] transition-all flex items-center justify-center gap-2"
              >
                Get Detailed Analysis
                <ChevronRight size={12} />
              </button>
            </div>
          </div>
        </div>
      )}

      {location && !isPanelOpen && (
        <button
          onClick={() => setIsPanelOpen(true)}
          className="absolute top-24 left-8 z-[1000] p-4 bg-slate-950/80 backdrop-blur-xl border border-white/10 rounded-2xl text-teal-400 hover:scale-110 transition-all animate-slide-right shadow-2xl hover:border-teal-500/50"
        >
          <ChevronRight size={20} />
        </button>
      )}

      {/* 3. BOTTOM-LEFT: STATUS */}
      <div className="absolute bottom-8 left-8 z-[400]">
        <div className="flex items-center gap-3 px-5 py-2.5 rounded-full bg-slate-900/90 backdrop-blur-xl border border-white/10 shadow-2xl group/status hover:border-teal-500/30 transition-all">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.5)]" />
          <span className="text-[10px] font-bold text-white uppercase tracking-[0.2em]">AeroGrid Live</span>
          <div className="w-[1px] h-3 bg-white/10 mx-1" />
          <span className="text-[10px] font-bold text-slate-500 uppercase group-hover:text-teal-400 transition-colors">
            Last Sync: {lastSync.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </div>

      {/* 4. BOTTOM-RIGHT: CONTROLS */}
      <div className="absolute bottom-8 right-8 z-[400] flex flex-col items-end gap-6">
        <div className="flex bg-slate-900/60 backdrop-blur-2xl p-1.5 rounded-2xl border border-white/10 shadow-2xl group/presets ring-1 ring-white/5">
          {[
            { id: 'city', icon: Maximize, label: 'City' },
            { id: 'region', icon: ZoomIn, label: 'Region' },
            { id: 'country', icon: Globe, label: 'Nation' }
          ].map((btn) => (
            <button
              key={btn.id}
              onClick={() => handleZoomPreset(btn.id)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition-all active:scale-95"
            >
              <btn.icon size={16} />
              <span className="text-[10px] font-bold uppercase tracking-widest">{btn.label}</span>
            </button>
          ))}
        </div>

        <div className="glass-panel p-6 rounded-[2rem] border border-white/10 backdrop-blur-3xl shadow-2xl w-64 space-y-4 ring-1 ring-white/5">
          <div className="flex justify-between items-center">
            <p className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Air Spectrum</p>
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          </div>
          <div className="flex h-1.5 w-full rounded-full overflow-hidden bg-white/5 ring-1 ring-white/10">
            {['#14b8a6', '#facc15', '#f97316', '#ef4444', '#7f1d1d'].map((c, i) => (
              <div key={i} className="flex-1 h-full" style={{ backgroundColor: c }} />
            ))}
          </div>
          <div className="flex justify-between text-[9px] text-slate-500 font-bold uppercase tracking-[0.15em]">
            <span>Good</span>
            <span>Poor</span>
            <span>Severe</span>
          </div>
        </div>
      </div>

      {loadingStations && (
        <div className="absolute inset-0 z-[2000] bg-slate-950/60 backdrop-blur-xl flex items-center justify-center">
          <div className="flex flex-col items-center gap-8 animate-in fade-in zoom-in duration-500">
            <div className="relative">
              <div className="w-24 h-24 border-2 border-teal-500/10 border-t-teal-500 rounded-full animate-spin" />
              <div className="absolute inset-0 flex items-center justify-center">
                <Globe className="text-teal-500 w-8 h-8 animate-pulse" />
              </div>
            </div>
            <div className="text-center space-y-2">
              <span className="text-white text-lg font-black tracking-[0.4em] uppercase block">AeroGrid Sync</span>
              <div className="flex items-center gap-2 justify-center">
                <span className="w-1.5 h-1.5 bg-teal-500 rounded-full animate-pulse" />
                <span className="text-teal-400 text-[10px] font-black uppercase tracking-widest">Global Station Scan active</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
