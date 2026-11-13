import React from "react";
import { Button } from "@heroui/react";
import { Icon } from "@iconify/react";

interface HeaderProps {
  onOpenRegister: () => void;
}

export function Header({ onOpenRegister }: HeaderProps) {
  return (
    <header className="w-full border-b border-zinc-800/80 bg-zinc-950/90 backdrop-blur-md px-6 py-3.5">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        {/* Logo + Brand */}
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-md bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-sky-400">
            <Icon icon="solar:face-scan-square-bold" className="w-5 h-5" />
          </div>
          <span className="text-base font-semibold tracking-tight text-zinc-100">
            AuthCIE
          </span>
        </div>

        {/* Pulsante NUOVO UTENTE squadrato con icona + */}
        <Button
          variant="primary"
          size="sm"
          onPress={onOpenRegister}
          className="flex items-center gap-1.5 rounded-md font-semibold tracking-wide shadow-md shadow-sky-500/15"
        >
          <Icon icon="solar:add-circle-linear" className="w-4 h-4" />
          <span>NUOVO UTENTE</span>
        </Button>
      </div>
    </header>
  );
}
