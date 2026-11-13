import {
  isRouteErrorResponse,
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
} from "react-router";

import type { Route } from "./+types/root";
import "./app.css";

export const links: Route.LinksFunction = () => [
  { rel: "preconnect", href: "https://fonts.googleapis.com" },
  {
    rel: "preconnect",
    href: "https://fonts.gstatic.com",
    crossOrigin: "anonymous",
  },
  {
    rel: "stylesheet",
    href: "https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300..800;1,300..800&display=swap",
  },
];

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it" className="dark">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
        <title>AuthCIE - Riconoscimento Facciale</title>
        <Meta />
        <Links />
      </head>
      <body className="bg-zinc-950 text-zinc-100 min-h-screen">
        {children}
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export function HydrateFallback() {
  return <div className="min-h-screen bg-zinc-950" />;
}

export default function App() {
  return <Outlet />;
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  let message = "Si è verificato un errore";
  let details = "Riprova più tardi.";

  if (isRouteErrorResponse(error)) {
    message = error.status === 404 ? "404 Pagina non trovata" : "Errore";
    details = error.statusText || details;
  }

  return (
    <main className="p-8 text-center flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-xl font-bold text-red-400 mb-2">{message}</h1>
      <p className="text-sm text-zinc-400">{details}</p>
    </main>
  );
}
