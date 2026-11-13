import React, { useState, useRef, useEffect, useCallback } from "react";
import { Modal, Button, Input, Spinner } from "@heroui/react";
import { Icon } from "@iconify/react";
import { registerUserApi } from "../services/api";
import type { RegisterResponse } from "../types/auth";

interface RegisterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (res: RegisterResponse) => void;
}

export function RegisterModal({ isOpen, onClose, onSuccess }: RegisterModalProps) {
  const [fullName, setFullName] = useState("");
  const [capturedBlob, setCapturedBlob] = useState<Blob | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isCameraActive, setIsCameraActive] = useState(true);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successData, setSuccessData] = useState<RegisterResponse | null>(null);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const isRequestingCameraRef = useRef<boolean>(false);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.srcObject = null;
    }
    isRequestingCameraRef.current = false;
  }, []);

  const startCamera = useCallback(async () => {
    if (isRequestingCameraRef.current) return;
    isRequestingCameraRef.current = true;

    stopCamera();
    try {
      let stream: MediaStream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: { ideal: "environment" },
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
    } catch (err) {
      console.warn("Fotocamera documento non disponibile, passaggio a upload file:", err);
      setIsCameraActive(false);
    } finally {
      isRequestingCameraRef.current = false;
    }
  }, [stopCamera]);

  useEffect(() => {
    if (isOpen && isCameraActive && !capturedBlob) {
      startCamera();
    } else {
      stopCamera();
    }
    return () => {
      stopCamera();
    };
  }, [isOpen, isCameraActive, capturedBlob, startCamera, stopCamera]);

  const handleClose = () => {
    stopCamera();
    setFullName("");
    setCapturedBlob(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setErrorMsg(null);
    setSuccessData(null);
    setIsLoading(false);
    setIsCameraActive(true);
    onClose();
  };

  const handleSnap = () => {
    const video = videoRef.current;
    if (!video || video.videoWidth === 0 || video.videoHeight === 0) return;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(
      (blob) => {
        if (blob) {
          setCapturedBlob(blob);
          setPreviewUrl(URL.createObjectURL(blob));
          stopCamera();
        }
      },
      "image/jpeg",
      0.92
    );
  };

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setErrorMsg(null);
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setErrorMsg("Formato non supportato. Carica un'immagine JPEG, PNG o WEBP.");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setErrorMsg("File troppo grande (max 5 MB).");
      return;
    }

    setCapturedBlob(file);
    setPreviewUrl(URL.createObjectURL(file));
    stopCamera();
  };

  const handleRetake = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setCapturedBlob(null);
    setErrorMsg(null);
    setIsCameraActive(true);
    startCamera();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    if (!fullName.trim()) {
      setErrorMsg("Inserisci nome e cognome.");
      return;
    }
    if (!capturedBlob) {
      setErrorMsg("Acquisisci o seleziona il fronte della carta d'identità.");
      return;
    }

    setIsLoading(true);
    try {
      const res = await registerUserApi(fullName, capturedBlob);
      setSuccessData(res);
      onSuccess?.(res);
      setTimeout(() => {
        handleClose();
      }, 1500);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Errore durante la registrazione.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onOpenChange={(open) => !open && handleClose()}>
      <Modal.Trigger className="hidden" />

      <Modal.Backdrop className="bg-black/80 backdrop-blur-sm fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4">
        {/*
          Container neutro senza bordi o padding invasivi
        */}
        <Modal.Container className="!p-0 !m-0 !w-full !max-w-xl bg-transparent !border-0 !shadow-none flex items-center justify-center pointer-events-auto">
          {/*
            UNICA CARD: Dialog con bordi squadrati (rounded-lg) e nessun padding esterno superfluo
          */}
          <Modal.Dialog className="!p-0 !m-0 w-full bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden shadow-2xl flex flex-col outline-none">
            
            {/* Header compatto */}
            <div className="flex items-center justify-between px-5 py-3 border-b border-zinc-800/80 bg-zinc-900">
              <Modal.Heading className="text-base font-bold text-zinc-100 flex items-center gap-2">
                <Icon icon="solar:user-id-bold" className="w-5 h-5 text-sky-400" />
                Registrazione Nuovo Utente
              </Modal.Heading>
              <button
                type="button"
                onClick={handleClose}
                aria-label="Chiudi"
                className="w-7 h-7 rounded-md flex items-center justify-center text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors cursor-pointer"
              >
                <Icon icon="solar:close-circle-linear" className="w-5 h-5" />
              </button>
            </div>

            {successData ? (
              <div className="py-10 px-5 flex flex-col items-center text-center gap-3">
                <div className="w-14 h-14 rounded-md bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                  <Icon icon="solar:check-circle-bold" className="w-8 h-8" />
                </div>
                <div>
                  <p className="text-lg font-bold text-zinc-100">
                    {successData.user?.fullName} registrato!
                  </p>
                  <p className="text-xs text-zinc-400 mt-1">
                    Embedding biometrico estratto con successo.
                  </p>
                </div>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="flex flex-col">
                
                {/* 
                  AREA FOTOCAMERA / DOCUMENTO: EDGE-TO-EDGE
                  A filo completo dei bordi laterali, senza margini interni o esterni!
                */}
                <div className="relative w-full aspect-[16/10] max-h-[250px] bg-black border-b border-zinc-800 flex items-center justify-center overflow-hidden">
                  {previewUrl ? (
                    <div className="relative w-full h-full">
                      <img
                        src={previewUrl}
                        alt="Fronte Carta d'Identità"
                        className="w-full h-full object-cover"
                      />
                      <button
                        type="button"
                        onClick={handleRetake}
                        aria-label="Rifai foto"
                        className="absolute top-3 right-3 px-3 py-1.5 rounded-md bg-black/80 hover:bg-black text-zinc-100 border border-white/20 text-xs flex items-center gap-1.5 backdrop-blur-md cursor-pointer shadow-xl font-medium"
                      >
                        <Icon icon="solar:restart-bold" className="w-4 h-4" />
                        Rifai Foto
                      </button>
                    </div>
                  ) : isCameraActive ? (
                    <div className="relative w-full h-full flex items-center justify-center">
                      <video
                        ref={videoRef}
                        className="w-full h-full object-cover"
                        playsInline
                        muted
                        autoPlay
                      />

                      {/* Mirino CIE proporzionato */}
                      <div className="absolute inset-4 border-2 border-dashed border-sky-400/90 rounded-md pointer-events-none flex items-center justify-center shadow-[0_0_20px_rgba(56,189,248,0.25)]">
                        <span className="text-[11px] font-semibold bg-black/75 text-sky-200 px-3 py-1 rounded-md backdrop-blur-md border border-white/10">
                          Inquadra il FRONTE del documento
                        </span>
                      </div>

                      {/* Controlli scatto sopra al video con bordi squadrati */}
                      <div className="absolute bottom-3 inset-x-0 flex justify-center items-center gap-3">
                        <Button
                          type="button"
                          variant="primary"
                          size="sm"
                          onPress={handleSnap}
                          className="flex items-center gap-1.5 rounded-md shadow-xl shadow-sky-500/30 cursor-pointer font-semibold"
                        >
                          <Icon icon="solar:camera-bold" className="w-4 h-4" />
                          <span>Scatta Foto</span>
                        </Button>
                        <button
                          type="button"
                          onClick={() => {
                            stopCamera();
                            setIsCameraActive(false);
                          }}
                          className="text-xs text-zinc-300 hover:text-white px-3 py-1 bg-black/75 hover:bg-black/90 rounded-md backdrop-blur-md border border-white/10 cursor-pointer transition-colors"
                        >
                          Carica File
                        </button>
                      </div>
                    </div>
                  ) : (
                    /* Modalità Caricamento File */
                    <div
                      onClick={() => fileInputRef.current?.click()}
                      className="w-full h-full flex flex-col items-center justify-center p-6 text-center cursor-pointer hover:bg-zinc-900/50 transition-colors"
                    >
                      <Icon icon="solar:upload-track-2-linear" className="w-10 h-10 text-sky-400 mb-2" />
                      <p className="text-sm font-semibold text-zinc-200">
                        Carica immagine fronte CIE
                      </p>
                      <p className="text-xs text-zinc-400 mt-0.5">
                        JPEG, PNG o WEBP (max 5MB)
                      </p>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setIsCameraActive(true);
                          startCamera();
                        }}
                        className="mt-3 text-xs text-sky-400 hover:underline cursor-pointer"
                      >
                        Usa la Fotocamera
                      </button>
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/jpeg,image/png,image/webp"
                        onChange={handleFile}
                        className="hidden"
                      />
                    </div>
                  )}
                </div>

                {/* Sezione Campi Form & Spiegazione GDPR */}
                <div className="p-5 flex flex-col gap-3.5">
                  {/* Input Nome e Cognome */}
                  <div className="flex flex-col gap-1">
                    <Input
                      type="text"
                      placeholder="Nome e Cognome dell'utente"
                      aria-label="Nome e Cognome"
                      value={fullName}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                        setFullName(e.target.value)
                      }
                      required
                      className="bg-zinc-800/80 border border-zinc-700/80 text-zinc-100 text-sm rounded-md px-3.5 py-2.5 focus:border-sky-500 focus:outline-none"
                    />
                  </div>

                  {/* Box Giallo Informativo CIE + GDPR */}
                  <div className="p-3 rounded-md bg-amber-950/30 border border-amber-800/50 text-amber-200/90 text-xs flex items-start gap-2.5 leading-relaxed">
                    <Icon icon="solar:shield-warning-bold" className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-semibold text-amber-300 block mb-0.5">
                        Fronte Documento & Tutela Privacy (GDPR)
                      </span>
                      È richiesto esclusivamente il <strong>FRONTE</strong> della carta di identità come immagine (no PDF). L'immagine viene usata solo in memoria volatile per calcolare l'embedding ed <strong className="underline">eliminata immediatamente</strong> in conformità al GDPR (Regolamento UE 2016/679).
                    </div>
                  </div>

                  {errorMsg && (
                    <p className="text-xs text-red-400 bg-red-950/60 border border-red-800/60 p-2.5 rounded-md flex items-center gap-2">
                      <Icon icon="solar:danger-circle-bold" className="w-4 h-4 shrink-0" />
                      <span>{errorMsg}</span>
                    </p>
                  )}

                  {/* Pulsanti Azione: con pulsante SALVA ben visibile e squadrato */}
                  <div className="flex items-center justify-end gap-2.5 pt-1 border-t border-zinc-800/80">
                    <Button
                      type="button"
                      variant="secondary"
                      size="sm"
                      onPress={handleClose}
                      isDisabled={isLoading}
                      className="rounded-md"
                    >
                      Annulla
                    </Button>
                    <Button
                      type="submit"
                      variant="primary"
                      size="sm"
                      isDisabled={isLoading || !capturedBlob || !fullName.trim()}
                      className="flex items-center gap-1.5 font-bold tracking-wide rounded-md px-5 shadow-lg shadow-sky-500/20"
                    >
                      {isLoading ? (
                        <>
                          <Spinner size="sm" />
                          <span>Salvataggio...</span>
                        </>
                      ) : (
                        <>
                          <Icon icon="solar:diskette-bold" className="w-4 h-4" />
                          <span>SALVA</span>
                        </>
                      )}
                    </Button>
                  </div>
                </div>

              </form>
            )}

          </Modal.Dialog>
        </Modal.Container>
      </Modal.Backdrop>
    </Modal>
  );
}
