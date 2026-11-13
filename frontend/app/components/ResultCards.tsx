import React from "react";
import { Card, Chip, ProgressBar } from "@heroui/react";
import { Icon } from "@iconify/react";
import type { LoginWSMessage, LoginMatchResponse, LoginSpoofResponse } from "../types/auth";

interface ResultCardsProps {
  result: LoginWSMessage | null;
  isScanning: boolean;
  onOpenRegister?: () => void;
}

export function ResultCards({ result, isScanning, onOpenRegister }: ResultCardsProps) {
  // Stato iniziale: in attesa o durante la scansione
  if (!result || result.status === "WAITING_FACE" || result.status === "ERROR" || result.status === "WAITING_LIVENESS") {
    return (
      <Card
        variant="default"
        className="w-full bg-zinc-900/60 border border-zinc-800/80 rounded-2xl p-6 shadow-xl backdrop-blur-sm"
      >
        <div className="flex flex-col items-center justify-center text-center py-8 gap-3">
          <div className="w-14 h-14 rounded-2xl bg-zinc-800/60 border border-zinc-700/60 flex items-center justify-center text-zinc-400">
            <Icon
              icon={isScanning ? "solar:face-scan-circle-bold" : "solar:shield-user-linear"}
              className={`w-7 h-7 ${isScanning ? "animate-pulse text-sky-400" : "text-zinc-500"}`}
            />
          </div>
          <div className="flex flex-col gap-1">
            <h3 className="text-base font-semibold text-zinc-200">
              {isScanning ? "Elaborazione fotogrammi..." : "In attesa di scansione"}
            </h3>
            <p className="text-xs text-zinc-400 max-w-xs leading-relaxed">
              {isScanning
                ? "Il sistema sta analizzando i frame per calcolare la vitalità e comparare l'embedding con il database."
                : "Avvia il riconoscimento facciale per visualizzare l'identità e tutti i parametri biometrici."}
            </p>
          </div>
        </div>
      </Card>
    );
  }

  // SPOOF ATTACK
  if (result.status === "SPOOF_ATTACK") {
    const spoof = result as LoginSpoofResponse;
    const realProb = Math.round((spoof.liveness_probabilities?.real || 0) * 100);
    const printProb = Math.round((spoof.liveness_probabilities?.print || 0) * 100);
    const screenProb = Math.round((spoof.liveness_probabilities?.screen || 0) * 100);

    return (
      <Card
        variant="default"
        className="w-full bg-zinc-900/70 border border-red-500/40 rounded-2xl p-6 shadow-2xl animate-in fade-in duration-300"
      >
        <div className="flex items-center justify-between pb-4 border-b border-zinc-800">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-md bg-red-500/20 text-red-400 border border-red-500/30 flex items-center justify-center">
              <Icon icon="solar:shield-cross-bold" className="w-6 h-6" />
            </div>
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-red-400 block">
                Attacco Spoofing Rilevato
              </span>
              <h3 className="text-lg font-bold text-zinc-100">
                {spoof.attack_type === "PRINT"
                  ? "Foto Stampata (Print)"
                  : spoof.attack_type === "SCREEN"
                  ? "Display / Schermo (Screen)"
                  : spoof.attack_type}
              </h3>
            </div>
          </div>
          <Chip color="danger" variant="primary" size="sm">
            <Chip.Label>Non Autentico</Chip.Label>
          </Chip>
        </div>

        <div className="flex flex-col gap-3.5 pt-4 text-xs">
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <span className="text-zinc-400 font-medium">Liveness Score</span>
              <span className="font-mono font-bold text-red-400">
                {Math.round(spoof.liveness_score * 100)}%{" "}
                <span className="text-zinc-500 font-normal">
                  (min {Math.round(spoof.liveness_threshold * 100)}%)
                </span>
              </span>
            </div>
            <ProgressBar
              value={Math.round(spoof.liveness_score * 100)}
              color="danger"
              size="sm"
              aria-label="Liveness score"
            >
              <ProgressBar.Track className="bg-zinc-800 h-2 rounded-full">
                <ProgressBar.Fill className="rounded-full bg-red-500" />
              </ProgressBar.Track>
            </ProgressBar>
          </div>

          <div className="grid grid-cols-3 gap-2 pt-1 text-center">
            <div className="py-2 px-1 rounded-md bg-zinc-800/40 border border-zinc-700/40">
              <span className="text-[10px] text-zinc-400 block">Reale</span>
              <span className="font-mono font-semibold text-zinc-300">{realProb}%</span>
            </div>
            <div className="py-2 px-1 rounded-md bg-zinc-800/40 border border-zinc-700/40">
              <span className="text-[10px] text-zinc-400 block">Stampa</span>
              <span className="font-mono font-semibold text-red-400">{printProb}%</span>
            </div>
            <div className="py-2 px-1 rounded-md bg-zinc-800/40 border border-zinc-700/40">
              <span className="text-[10px] text-zinc-400 block">Schermo</span>
              <span className="font-mono font-semibold text-amber-400">{screenProb}%</span>
            </div>
          </div>
        </div>
      </Card>
    );
  }

  // Risultato con confronto MATCH o NO_MATCH
  const match = result as LoginMatchResponse;
  const isMatch = match.status === "MATCH";
  const user = match.user;

  const simPercent = Math.round(match.similarity * 100);
  const simThresholdPercent = Math.round(match.similarity_threshold * 100);
  const livePercent = Math.round(match.liveness_score * 100);
  const liveThresholdPercent = Math.round(match.liveness_threshold * 100);

  // Probabilità reali percentuali con decimali se molto piccole
  const realProb = (match.liveness_probabilities?.real * 100).toFixed(1);
  const printProb = (match.liveness_probabilities?.print * 100).toFixed(2);
  const screenProb = (match.liveness_probabilities?.screen * 100).toFixed(2);

  return (
    <Card
      variant="default"
      className={`w-full bg-zinc-900/70 border ${
        isMatch ? "border-emerald-500/50" : "border-amber-500/50"
      } rounded-2xl p-6 shadow-2xl animate-in fade-in duration-300 flex flex-col gap-4`}
    >
      {/* 1. Esito Principale & Nome Utente (SEMPRE VISIBILE SE PRESENTE NEL DB!) */}
      <div className="flex items-center justify-between pb-4 border-b border-zinc-800">
        <div className="flex items-center gap-3">
          <div
            className={`w-12 h-12 rounded-md flex items-center justify-center ${
              isMatch
                ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
            }`}
          >
            <Icon
              icon={isMatch ? "solar:user-check-bold" : "solar:user-id-bold"}
              className="w-7 h-7"
            />
          </div>
          <div>
            <span
              className={`text-[11px] font-bold uppercase tracking-wider block ${
                isMatch ? "text-emerald-400" : "text-amber-400"
              }`}
            >
              {isMatch
                ? "Accesso Autorizzato"
                : user
                ? "Utente Incerto"
                : "Utente Non Riconosciuto"}
            </span>
            <h3 className="text-xl font-bold text-zinc-100">
              {user?.fullName || "Profilo Sconosciuto"}
            </h3>
          </div>
        </div>

        <Chip color={isMatch ? "success" : "warning"} variant="primary" size="sm">
          <Chip.Label>{isMatch ? "Autorizzato" : "Soglia Non Raggiunta"}</Chip.Label>
        </Chip>
      </div>

      {/* Nota esplicativa se l'utente è individuato ma similarity < threshold */}
      {!isMatch && user && (
        <div className="p-3 rounded-md bg-amber-950/30 border border-amber-800/40 text-amber-200/90 text-xs flex items-center gap-2">
          <Icon icon="solar:info-circle-bold" className="w-4 h-4 text-amber-400 shrink-0" />
          <span>
            Corrispondenza con <strong>{user.fullName}</strong> trovato ({simPercent}%), ma inferiore alla soglia richiesta ({simThresholdPercent}%).
          </span>
        </div>
      )}

      {/* 2. Tutte le Statistiche Complete e Dettagliate */}
      <div className="flex flex-col gap-4 text-xs">
        
        {/* Barra Somiglianza Volto (InsightFace) */}
        <div>
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-zinc-400 font-medium">Somiglianza Facciale (Cosine)</span>
            <span
              className={`font-mono font-bold ${
                isMatch ? "text-sky-400" : "text-amber-400"
              }`}
            >
              {simPercent}%{" "}
              <span className="text-zinc-500 font-normal">
                (Soglia minima: {simThresholdPercent}%)
              </span>
            </span>
          </div>
          <ProgressBar
            value={simPercent}
            color={isMatch ? "accent" : "warning"}
            size="sm"
            aria-label="Somiglianza volto"
          >
            <ProgressBar.Track className="bg-zinc-800 h-2 rounded-full">
              <ProgressBar.Fill
                className={`rounded-full ${
                  isMatch ? "bg-sky-500" : "bg-amber-500"
                }`}
              />
            </ProgressBar.Track>
          </ProgressBar>
        </div>

        {/* Barra Liveness Score (MiniFASNet v2) */}
        <div>
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-zinc-400 font-medium">Punteggio Vitalità (Liveness)</span>
            <span className="font-mono font-bold text-emerald-400">
              {livePercent}%{" "}
              <span className="text-zinc-500 font-normal">
                (Soglia minima: {liveThresholdPercent}%)
              </span>
            </span>
          </div>
          <ProgressBar
            value={livePercent}
            color="success"
            size="sm"
            aria-label="Liveness score"
          >
            <ProgressBar.Track className="bg-zinc-800 h-2 rounded-full">
              <ProgressBar.Fill className="rounded-full bg-emerald-500" />
            </ProgressBar.Track>
          </ProgressBar>
        </div>

        {/* Distribuzione Probabilità Anti-Spoofing (MiniFASNet) */}
        <div className="grid grid-cols-3 gap-2 pt-1 text-center">
          <div className="py-2 px-1.5 rounded-md bg-zinc-800/40 border border-zinc-700/40">
            <span className="text-[10px] text-zinc-400 block font-medium">Persona Reale</span>
            <span className="font-mono font-bold text-emerald-400 text-xs">{realProb}%</span>
          </div>
          <div className="py-2 px-1.5 rounded-md bg-zinc-800/40 border border-zinc-700/40">
            <span className="text-[10px] text-zinc-400 block font-medium">Foto Cartacea</span>
            <span className="font-mono font-semibold text-zinc-400 text-xs">{printProb}%</span>
          </div>
          <div className="py-2 px-1.5 rounded-md bg-zinc-800/40 border border-zinc-700/40">
            <span className="text-[10px] text-zinc-400 block font-medium">Schermo Digitale</span>
            <span className="font-mono font-semibold text-zinc-400 text-xs">{screenProb}%</span>
          </div>
        </div>

        {/* Griglia Metriche Tecniche: Vector Score, Embedding Score, Score CIE */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 pt-2 border-t border-zinc-800 text-[11px]">
          <div className="p-2 rounded-md bg-zinc-800/30 border border-zinc-800 flex flex-col">
            <span className="text-zinc-400 text-[10px]">Atlas Vector Score</span>
            <span className="font-mono font-bold text-zinc-100">
              {match.vector_score.toFixed(3)}
            </span>
          </div>

          <div className="p-2 rounded-md bg-zinc-800/30 border border-zinc-800 flex flex-col">
            <span className="text-zinc-400 text-[10px]">Embedding Live Score</span>
            <span className="font-mono font-bold text-zinc-100">
              {match.embedding_score.toFixed(3)}
            </span>
          </div>

          {user?.score !== undefined && (
            <div className="p-2 rounded-md bg-zinc-800/30 border border-zinc-800 flex flex-col col-span-2 sm:col-span-1">
              <span className="text-zinc-400 text-[10px]">Qualità Foto CIE</span>
              <span className="font-mono font-bold text-zinc-100">
                {(user.score * 100).toFixed(1)}%
              </span>
            </div>
          )}
        </div>

        {/* Informazioni aggiuntive (data registrazione) */}
        {user?.createdAt && (
          <div className="flex justify-between items-center pt-2 text-[11px] text-zinc-400">
            <span>Utente registrato nel sistema il:</span>
            <span className="font-medium text-zinc-300">
              {new Date(user.createdAt).toLocaleDateString("it-IT", {
                day: "2-digit",
                month: "long",
                year: "numeric",
              })}
            </span>
          </div>
        )}

      </div>
    </Card>
  );
}
