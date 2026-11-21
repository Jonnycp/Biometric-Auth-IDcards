export function getApiBaseUrl(): string {
  if (typeof window !== "undefined") {
    if (
      window.location.hostname.includes("ngrok") ||
      window.location.protocol === "https:" ||
      (window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1")
    ) {
      return "";
    }
  }

  if (import.meta.env.VITE_BACKEND_URL) {
    return import.meta.env.VITE_BACKEND_URL;
  }

  if (typeof window !== "undefined") {
    return `http://${window.location.hostname}:3000`;
  }
  return "http://localhost:3000";
}

export function getWsLoginUrl(): string {
  if (typeof window !== "undefined") {
    if (
      window.location.hostname.includes("ngrok") ||
      window.location.protocol === "https:" ||
      (window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1")
    ) {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      return `${protocol}//${window.location.host}/api/login`;
    }
  }

  if (import.meta.env.VITE_WS_URL) {
    return import.meta.env.VITE_WS_URL;
  }

  if (typeof window !== "undefined") {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.hostname}:3000/api/login`;
  }
  return "ws://localhost:3000/api/login";
}

export const API_BASE_URL = getApiBaseUrl();
export const WS_LOGIN_URL = getWsLoginUrl();
// Intervallo minimo tra due fotogrammi (40 ms = massimo 25 fps).
// Il ritmo reale è limitato dal controllo di flusso: un nuovo frame parte solo
// dopo la risposta del server al precedente.
export const FRAME_INTERVAL_MS = 40;
