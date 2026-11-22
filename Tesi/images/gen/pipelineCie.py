import sys
from pathlib import Path

import cv2
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from backend.core.id_card import findCardContour, fixProspective, orderPoints, enhanceContrast  # noqa: E402

OUT_DIR = Path(__file__).resolve().parents[1]
TARGET_SIZE = (856, 540)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 9.5,
})


def toRgb(bgr):
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def drawPanel(ax, img, title):
    ax.imshow(img, cmap="gray" if img.ndim == 2 else None)
    ax.set_title(title, fontsize=10)
    ax.axis("off")


def main(path):
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        sys.exit(f"Impossibile leggere l'immagine: {path}")

    edged, contour = findCardContour(image)

    # Pannello 3: contorno e vertici ordinati
    overlay = image.copy()
    thickness = max(2, image.shape[1] // 300)
    if contour is not None:
        rect = orderPoints(contour)
        cv2.polylines(overlay, [rect.astype(np.int32).reshape(-1, 1, 2)], True, (0, 200, 0), thickness)
        radius = thickness * 3
        for label, (x, y) in zip(["TL", "TR", "BR", "BL"], rect):
            cv2.circle(overlay, (int(x), int(y)), radius, (0, 0, 255), -1)
            cv2.putText(overlay, label, (int(x) + radius, int(y) - radius),
                        cv2.FONT_HERSHEY_SIMPLEX, thickness * 0.5, (0, 0, 255), thickness)
        titolo3 = "(c) Vertici ordinati (TL, TR, BR, BL)"
    else:
        titolo3 = "(c) Nessun quadrilatero valido: nessuna rettifica"

    # Pannello 4: sistema reale (rettifica + CLAHE)
    rectified, found = fixProspective(image, TARGET_SIZE)
    enhanced = enhanceContrast(rectified)

    fig, axes = plt.subplots(2, 2, figsize=(9, 6.4), dpi=300)
    drawPanel(axes[0, 0], toRgb(image), "(a) Immagine acquisita")
    drawPanel(axes[0, 1], edged, "(b) Bordi (Canny 75–200)")
    drawPanel(axes[1, 0], toRgb(overlay), titolo3)
    drawPanel(axes[1, 1], toRgb(enhanced),
              f"(d) Rettifica {TARGET_SIZE[0]}$\\times${TARGET_SIZE[1]} e CLAHE" if found
              else "(d) Solo CLAHE (immagine originale)")
    fig.tight_layout()
    OUT_DIR.mkdir(exist_ok=True)
    fig.savefig(OUT_DIR / "pipeline-cie.png", bbox_inches="tight")
    plt.close(fig)

    # Istogrammi del canale L prima e dopo CLAHE (sull'immagine rettificata)
    lBefore = cv2.split(cv2.cvtColor(rectified, cv2.COLOR_BGR2LAB))[0]
    lAfter = cv2.split(cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB))[0]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.0), dpi=300, sharey=True)
    for ax, data, title in [(axes[0], lBefore, "(a) Prima di CLAHE"),
                            (axes[1], lAfter, "(b) Dopo CLAHE")]:
        ax.hist(data.ravel(), bins=64, range=(0, 255), color="#4a6fa5", edgecolor="none")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Luminanza $L$ (8 bit)")
        ax.set_xlim(0, 255)
        ax.grid(alpha=0.25)
        ax.text(0.97, 0.93, f"$\\sigma_L$ = {data.std():.1f}", transform=ax.transAxes,
                ha="right", va="top", fontsize=9)
    axes[0].set_ylabel("Numero di pixel")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "istogrammi-clahe.png", bbox_inches="tight")
    plt.close(fig)

    print(f"Rettifica riuscita: {found}")
    print(f"sigma_L prima={lBefore.std():.1f}, dopo={lAfter.std():.1f}")
    print(f"Figure salvate in {OUT_DIR}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: python Tesi/images/gen/pipelineCIE.py <immagine>")
    main(sys.argv[1])