// API base for the deployed frontend.
// "" = same origin (local dev and Render, where backend serves this UI).
// On Vercel (static hosting) points to the Render backend.
window.__API_BASE__ = /(\.|^)vercel\.app$/.test(location.hostname)
  ? "https://customer-support-agent-65it.onrender.com"
  : "";
