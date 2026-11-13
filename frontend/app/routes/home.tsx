import React, { useState, useCallback } from "react";
import { useLocation, useNavigate } from "react-router";
import { Header } from "../components/Header";
import { CameraScanner } from "../components/CameraScanner";
import { ResultCards } from "../components/ResultCards";
import { RegisterModal } from "../components/RegisterModal";
import type { LoginWSMessage, RegisterResponse } from "../types/auth";
import { Icon } from "@iconify/react";

export function meta() {
  return [
    { title: "AuthCIE - Riconoscimento Facciale Biometrico" },
    {
      name: "description",
      content: "Autenticazione da carta d'identità con verifica liveness attiva.",
    },
  ];
}

export default function Home() {
  const location = useLocation();
  const navigate = useNavigate();

  const isRegisterOpen = location.pathname === "/register";
  const [loginResult, setLoginResult] = useState<LoginWSMessage | null>(null);
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  const handleOpenRegister = useCallback(() => {
    navigate("/register");
  }, [navigate]);

  const handleCloseRegister = useCallback(() => {
    navigate("/");
  }, [navigate]);

  const handleRegisterSuccess = useCallback((res: RegisterResponse) => {
    setToastMsg(`Utente "${res.user?.fullName}" registrato con successo!`);
    setTimeout(() => {
      setToastMsg(null);
    }, 5000);
  }, []);

  const handleResult = useCallback((res: LoginWSMessage | null) => {
    setLoginResult(res);
  }, []);

  const handleScanChange = useCallback((scanning: boolean) => {
    setIsScanning(scanning);
  }, []);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans selection:bg-sky-500/20">
      {/* Header compatto */}
      <Header onOpenRegister={handleOpenRegister} />

      {/* Toast Notifica Registrazione */}
      {toastMsg && (
        <div className="fixed top-20 right-6 z-50 animate-in fade-in slide-in-from-top-2 duration-300">
          <div className="bg-zinc-900 border border-emerald-500/50 text-emerald-300 px-4 py-2.5 rounded-md shadow-2xl text-xs flex items-center gap-2.5 backdrop-blur-md">
            <Icon icon="solar:check-circle-bold" className="w-5 h-5 text-emerald-400 shrink-0" />
            <span className="font-medium">{toastMsg}</span>
          </div>
        </div>
      )}

      {/* Area Principale: due colonne affiancate su desktop, una sotto l'altra su mobile */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col justify-center">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          
          {/* Zona 1: Fotocamera con pulsante integrato */}
          <section className="lg:col-span-7 flex flex-col justify-center">
            <CameraScanner
              onResult={handleResult}
              onScanStateChange={handleScanChange}
            />
          </section>

          {/* Zona 2: Card Risultati, Statistiche e Liveness */}
          <section className="lg:col-span-5 flex flex-col justify-center">
            <ResultCards
              result={loginResult}
              isScanning={isScanning}
              onOpenRegister={handleOpenRegister}
            />
          </section>

        </div>
      </main>

      {/* Modale Registrazione (edge-to-edge, zero margini laterali, pulsante SALVA) */}
      <RegisterModal
        isOpen={isRegisterOpen}
        onClose={handleCloseRegister}
        onSuccess={handleRegisterSuccess}
      />
    </div>
  );
}
