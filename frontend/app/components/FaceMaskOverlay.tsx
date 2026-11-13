import React from "react";

interface FaceMaskOverlayProps {
  isScanning: boolean;
  statusText?: string;
  isCompleted?: boolean;
  isError?: boolean;
}

export function FaceMaskOverlay({
  isScanning,
  statusText,
  isCompleted,
  isError,
}: FaceMaskOverlayProps) {
  const borderColor = isError
    ? "border-red-500"
    : isCompleted
    ? "border-emerald-500"
    : isScanning
    ? "border-sky-400"
    : "border-zinc-600";

  return (
    <div className="absolute inset-0 pointer-events-none flex flex-col items-center justify-center p-4">
      {/* Ovale biometrico pulito */}
      <div className="relative w-48 h-64 sm:w-56 sm:h-72 max-h-[75%] max-w-[75%]">
        <div
          className={`w-full h-full rounded-[48%] border-2 ${
            isScanning ? "border-dashed animate-pulse" : "border-solid"
          } ${borderColor} transition-colors duration-200 bg-black/5`}
        />
        {/* Angoli minimali */}
        <div className={`absolute -top-1.5 -left-1.5 w-4 h-4 border-t-2 border-l-2 ${borderColor}`} />
        <div className={`absolute -top-1.5 -right-1.5 w-4 h-4 border-t-2 border-r-2 ${borderColor}`} />
        <div className={`absolute -bottom-1.5 -left-1.5 w-4 h-4 border-b-2 border-l-2 ${borderColor}`} />
        <div className={`absolute -bottom-1.5 -right-1.5 w-4 h-4 border-b-2 border-r-2 ${borderColor}`} />
      </div>

      {statusText && (
        <span className="mt-3 px-3 py-1 rounded-full bg-black/80 backdrop-blur-md text-[11px] font-medium text-white border border-white/10 shadow-md">
          {statusText}
        </span>
      )}
    </div>
  );
}
