import argparse
import re
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NOMI = {"normale": "Luce normale", "fisso": "Immobile", "rotazione": "Rotazione", "pocaluce": "Poca luce",
        "controluce": "Controluce", "distanza": "Distanza", "senzaocchiali": "Senza occhiali",
        "ballo": "Movimenti ampi", "linguaccia": "Espressione"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cartella", required=True)
    ap.add_argument("--out", default="../condizioniAcquisizione.png")
    ap.add_argument("--istante", type=float, default=None)
    ap.add_argument("--colonne", type=int, default=4)
    a = ap.parse_args()
    video = sorted(p for p in Path(a.cartella).expanduser().iterdir()
                   if p.suffix.lower() in {".mov", ".mp4", ".m4v"})
    immagini = []
    for v in video:
        cap = cv2.VideoCapture(str(v))
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps = cap.get(cv2.CAP_PROP_FPS) or 30
        k = int(a.istante * fps) if a.istante is not None else n // 2
        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, min(k, n - 1)))
        ok, fr = cap.read(); cap.release()
        if not ok:
            continue
        m = re.match(r"^(\d+)-(.+)$", v.stem)
        cod, nome = (f"V{m.group(1)}", m.group(2)) if m else ("", v.stem)
        immagini.append((f"{cod} {NOMI.get(nome.lower(), nome)}".strip(), cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)))
    c = a.colonne; r = (len(immagini) + c - 1) // c
    fig, axs = plt.subplots(r, c, figsize=(2.6 * c, 1.75 * r))
    for ax in axs.flat:
        ax.axis("off")
    for ax, (tit, im) in zip(axs.flat, immagini):
        ax.imshow(im); ax.set_title(tit, fontsize=9, family="serif")
    fig.tight_layout()
    fig.savefig(a.out, dpi=300, bbox_inches="tight")
    print("Salvata", a.out, "con", len(immagini), "miniature")


if __name__ == "__main__":
    main()
