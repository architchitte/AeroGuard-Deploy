/**
 * API Configuration
 * 
 * Centralized settings for API connectivity.
 * Automatically switches between local development and production.
 */

// Priority:
// 1. Environment Variable VITE_API_BASE_URL (set in .env or CI/CD)
// 2. Localhost detection (use :5000)
// 3. Fallback to production URL
export const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL ||
    (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:5000'
        : 'https://aeroguard-deploy.onrender.com');

export const DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
};

console.log(`[API Config] Base URL set to: ${API_BASE_URL}`);
