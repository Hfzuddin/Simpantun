// Base URL for the Flask backend.
//
// Empty by default, so local dev keeps requesting same-origin paths and Vite's
// dev proxy (see vite.config.js) forwards them to 127.0.0.1:5500. The Docker
// image also leaves this empty: there Flask serves dist/ itself, so frontend
// and API share one origin.
//
// On Vercel the frontend is served from a different origin than the API, so
// VITE_API_BASE is set at build time to the Hugging Face Space URL.
const API_BASE = (import.meta.env.VITE_API_BASE || "").replace(/\/+$/, "");

export function apiUrl(path) {
  return `${API_BASE}${path}`;
}

export default API_BASE;
