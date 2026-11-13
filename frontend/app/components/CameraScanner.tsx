import React, { useRef, useState, useEffect, useCallback } from "react";
import { Button, ProgressBar } from "@heroui/react";
import { Icon } from "@iconify/react";
import { getWsLoginUrl } from "../config";
import type { LoginWSMessage } from "../types/auth";
import { FaceMaskOverlay } from "./FaceMaskOverlay";

interface CameraScannerProps {
  onResult: (result: LoginWSMessage | null) => void;
  onScanStateChange?: (isScanning: boolean) => void;
}

export function CameraScanner({ onResult, onScanStateChange }: CameraScannerProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const intervalRef = useRef<number | null>(null);
  const isStartingRef = useRef<boolean>(false);
  const isSendingFrameRef = useRef<boolean>(false);
  const isScanCompletedRef = useRef<boolean>(false);

  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [livenessProgress, setLivenessProgress] = useState<number>(0);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [statusHint, setStatusHint] = useState<string>("");
  const [hasResult, setHasResult] = useState<boolean>(false);

  useEffect(() => {
    onScanStateChange?.(isScanning);
  }, [isScanning, onScanStateChange]);

  const stopScan = useCallback(() => {
    isScanCompletedRef.current = true;
    isSendingFrameRef.current = false;

    if (intervalRef.current !== null) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (wsRef.current) {
      try {
        if (wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.close(1000, "Done");
        }
      } catch {
        // Ignora
      }
      wsRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.srcObject = null;
    }

    isStartingRef.current = false;
    setIsScanning(false);
  }, []);

  useEffect(() => {
    return () => {
      stopScan();
    };
  }, [stopScan]);

  const startScan = async () => {
    if (isStartingRef.current || isScanning) {
      return;
    }
    isStartingRef.current = true;
    isScanCompletedRef.current = false;

    console.log("[CameraScanner] Avvio scansione biometrica ad alta risoluzione...");
    setCameraError(null);
    setLivenessProgress(0);
    setHasResult(false);
    onResult(null);
    setStatusHint("Avvio fotocamera HD...");

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      const err = "WebRTC non supportato o connessione non sicura (HTTPS/localhost).";
      console.error("[CameraScanner]", err);
      setCameraError(err);
      isStartingRef.current = false;
      return;
    }

    try {
      // Risoluzione 720p HD per massima fedeltà e ricchezza di dettagli per InsightFace
      let stream: MediaStream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: "user",
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
          audio: false,
        });
      } catch {
        stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });
      }

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.muted = true;
        videoRef.current.playsInline = true;
        const playPromise = videoRef.current.play();
        if (playPromise !== undefined) {
          playPromise.catch(() => {});
        }
      }

      setIsScanning(true);

      const wsUrl = getWsLoginUrl();
      console.log("[CameraScanner] Connessione a WebSocket:", wsUrl);
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("[CameraScanner] WebSocket connesso!");
        setStatusHint("Guarda la camera e muovi delicatamente la testa...");

        // Invio fotogrammi (~100ms)
        intervalRef.current = window.setInterval(() => {
          if (
            isScanCompletedRef.current ||
            !videoRef.current ||
            !canvasRef.current ||
            ws.readyState !== WebSocket.OPEN
          ) {
            return;
          }

          if (isSendingFrameRef.current) {
            return;
          }

          const video = videoRef.current;
          const canvas = canvasRef.current;
          if (video.videoWidth === 0 || video.videoHeight === 0) return;

          // Scala l'immagine a max 640px per trasmissione istantanea e fluida anche su rete mobile
          const maxDim = 640;
          let w = video.videoWidth;
          let h = video.videoHeight;
          if (w > maxDim || h > maxDim) {
            if (w > h) {
              h = Math.round((h * maxDim) / w);
              w = maxDim;
            } else {
              w = Math.round((w * maxDim) / h);
              h = maxDim;
            }
          }

          canvas.width = w;
          canvas.height = h;
          const ctx = canvas.getContext("2d");
          if (!ctx) return;

          ctx.drawImage(video, 0, 0, w, h);
          isSendingFrameRef.current = true;

          // JPEG compatto a 0.88: ideale per InsightFace e ultra-leggero su rete mobile/ngrok (~35KB)
          canvas.toBlob(
            (blob) => {
              if (
                !isScanCompletedRef.current &&
                blob &&
                ws.readyState === WebSocket.OPEN
              ) {
                blob
                  .arrayBuffer()
                  .then((buf) => {
                    if (!isScanCompletedRef.current && ws.readyState === WebSocket.OPEN) {
                      ws.send(buf);
                    }
                  })
                  .catch(() => {
                    isSendingFrameRef.current = false;
                  });
              } else {
                isSendingFrameRef.current = false;
              }
            },
            "image/jpeg",
            0.88
          );
        }, 100);
      };

      ws.onmessage = (event) => {
        try {
          const data: LoginWSMessage = JSON.parse(event.data);
          // Sblocca l'invio del fotogramma successivo solo dopo la risposta del server
          isSendingFrameRef.current = false;

          if (data.status === "WAITING_FACE") {
            setStatusHint("Posiziona il volto all'interno della sagoma");
          } else if (data.status === "WAITING_LIVENESS") {
            const prog = data.liveness_progress || 0;
            setLivenessProgress(prog);
            setStatusHint(`Verifica vitalità in corso (${prog}%)`);
          } else if (
            data.status === "MATCH" ||
            data.status === "NO_MATCH" ||
            data.status === "SPOOF_ATTACK"
          ) {
            isScanCompletedRef.current = true;
            if (intervalRef.current !== null) {
              window.clearInterval(intervalRef.current);
              intervalRef.current = null;
            }

            setHasResult(true);
            setLivenessProgress(100);
            onResult(data);
            stopScan();
          } else if (data.status === "ERROR") {
            setStatusHint(data.message || "Errore elaborazione fotogramma");
          }
        } catch (e) {
          console.error("[CameraScanner] Errore parse json:", e);
          isSendingFrameRef.current = false;
        }
      };

      ws.onerror = (e) => {
        console.error("[CameraScanner] Errore WebSocket:", e);
        if (!isScanCompletedRef.current) {
          setCameraError("Impossibile stabilire la connessione WebSocket con il server.");
        }
      };

      ws.onclose = (event) => {
        console.log("[CameraScanner] WebSocket chiuso. Codice:", event.code, "Motivo:", event.reason);
        if (
          !isScanCompletedRef.current &&
          event.code !== 1000 &&
          event.code !== 1005
        ) {
          const reasonMsg = event.reason
            ? `Errore Server (${event.code}): ${event.reason}`
            : `Chiusura anomala dal server (codice ${event.code}).`;
          setCameraError(reasonMsg);
        }
        stopScan();
      };
    } catch (err: unknown) {
      console.error("[CameraScanner] Errore fotocamera:", err);
      const msg = err instanceof Error ? err.message : "Fotocamera non accessibile.";
      setCameraError(msg);
      stopScan();
    } finally {
      isStartingRef.current = false;
    }
  };

  return (
    <div className="flex flex-col gap-3 w-full">
      {/* Box Fotocamera */}
      <div className="relative w-full aspect-[4/3] bg-zinc-950 rounded-2xl overflow-hidden border border-zinc-800 shadow-2xl flex items-center justify-center">
        {/* Elemento video reale */}
        <video
          ref={videoRef}
          className="w-full h-full object-cover transform -scale-x-100"
          playsInline
          muted
          autoPlay
        />

        <canvas ref={canvasRef} className="hidden" />

        {/* Maschera Ovale Biometrica */}
        {isScanning && (
          <FaceMaskOverlay
            isScanning={isScanning}
            statusText={statusHint}
            isCompleted={hasResult}
          />
        )}

        {/* Barra di avanzamento sincronizzata con il backend */}
        {isScanning && (
          <div className="absolute top-3 inset-x-4 flex flex-col gap-1.5 z-20">
            <div className="flex items-center justify-between text-xs font-semibold text-white px-1">
              <span className="flex items-center gap-1.5 text-sky-400">
                <span className="w-2 h-2 rounded-full bg-sky-400 animate-ping inline-block" />
                Liveness: muovi delicatamente la testa
              </span>
              <span className="font-mono text-zinc-300">{livenessProgress}%</span>
            </div>
            <ProgressBar
              value={livenessProgress}
              color="accent"
              size="sm"
              aria-label="Avanzamento liveness 45 frame"
            >
              <ProgressBar.Track className="bg-black/60 backdrop-blur-md h-2 rounded-full border border-white/10">
                <ProgressBar.Fill className="rounded-full bg-gradient-to-r from-sky-500 to-indigo-500" />
              </ProgressBar.Track>
            </ProgressBar>
          </div>
        )}

        {/* Overlay centrale quando la telecamera è in pausa o c'è un errore */}
        {!isScanning && (
          <div className="absolute inset-0 z-30 flex flex-col items-center justify-center gap-3.5 bg-zinc-950/85 backdrop-blur-xs p-6 text-center">
            <div className="w-14 h-14 rounded-md bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-300 shadow-inner">
              <Icon
                icon={hasResult ? "solar:restart-bold" : cameraError ? "solar:danger-triangle-bold" : "solar:face-scan-circle-bold"}
                className={`w-7 h-7 ${cameraError ? "text-red-400" : "text-sky-400"}`}
              />
            </div>

            <div className="flex flex-col items-center gap-1">
              <h3 className="text-base font-semibold text-zinc-100">
                {hasResult ? "Scansione Completata" : cameraError ? "Errore Rilevato" : "Riconoscimento Facciale"}
              </h3>
              <p className="text-xs text-zinc-400 max-w-xs">
                {hasResult
                  ? "Consulta l'esito a lato o avvia una nuova verifica."
                  : cameraError
                  ? "Si è verificato un problema di comunicazione con il server."
                  : "Premi il pulsante per attivare la telecamera e verificare la presenza reale."}
              </p>
            </div>

            {/* Errore in risalto se presente */}
            {cameraError && (
              <div className="text-xs text-red-300 bg-red-950/80 border border-red-800/80 px-4 py-2 rounded-md max-w-sm text-left flex items-start gap-2">
                <Icon icon="solar:danger-circle-bold" className="w-4 h-4 shrink-0 text-red-400 mt-0.5" />
                <span className="font-mono text-[11px] leading-tight break-all">{cameraError}</span>
              </div>
            )}

            {/* Pulsante squadrato */}
            <Button
              variant="primary"
              size="md"
              onPress={startScan}
              className="flex items-center gap-2 rounded-md font-bold tracking-wide shadow-xl shadow-sky-500/25 px-6 py-2.5 cursor-pointer mt-1"
            >
              <Icon
                icon={hasResult || cameraError ? "solar:refresh-circle-bold" : "solar:play-circle-bold"}
                className="w-5 h-5"
              />
              <span>{hasResult || cameraError ? "RIPROVA SCANSIONE" : "AVVIA RICONOSCIMENTO"}</span>
            </Button>
          </div>
        )}

        {/* Pulsante Pausa compatto durante la scansione */}
        {isScanning && (
          <div className="absolute bottom-3 inset-x-0 flex justify-center z-20">
            <Button
              variant="secondary"
              size="sm"
              onPress={stopScan}
              className="flex items-center gap-1.5 rounded-md shadow-lg bg-black/80 backdrop-blur-md border border-white/10 text-zinc-200"
            >
              <Icon icon="solar:pause-circle-bold" className="w-4 h-4 text-zinc-400" />
              <span>Metti in Pausa</span>
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
