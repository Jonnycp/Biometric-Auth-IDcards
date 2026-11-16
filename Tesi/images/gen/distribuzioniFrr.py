import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "mathtext.fontset": "cm"
})

x = np.linspace(-1.0, 1.0, 1000)

mu_imp, sigma_imp = 0.15, 0.16
mu_gen, sigma_gen = 0.72, 0.12
tau = 0.50

y_imp = norm.pdf(x, mu_imp, sigma_imp)
y_gen = norm.pdf(x, mu_gen, sigma_gen)

fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)

# Curve principali senza p(Sc | H0) e p(Sc | H1)
ax.plot(x, y_imp, color='#d62728', lw=2, label='Confronti Impostori (persone diverse)')
ax.plot(x, y_gen, color='#1f77b4', lw=2, label='Confronti Genuini (stessa persona)')

# Campitura aree di errore (FAR e FRR)
ax.fill_between(x, 0, y_imp, where=(x >= tau), color='#d62728', alpha=0.35)
ax.fill_between(x, 0, y_gen, where=(x <= tau), color='#1f77b4', alpha=0.35)

# Linea verticale soglia tau
ax.axvline(tau, color='black', linestyle='--', lw=1.5)
ax.text(tau, max(y_gen)*1.03, r'Soglia $\tau = 0{,}50$', ha='center', va='bottom', fontweight='bold')

# Annotazioni FAR e FRR
ax.annotate('FRR', xy=(0.45, 0.25), xytext=(0.30, 1.05),
            arrowprops=dict(arrowstyle='->', color='#1f77b4', lw=1.2),
            color='#1f77b4', fontweight='bold', ha='center')

ax.annotate('FAR', xy=(0.55, 0.20), xytext=(0.70, 1.05),
            arrowprops=dict(arrowstyle='->', color='#d62728', lw=1.2),
            color='#d62728', fontweight='bold', ha='center')

# Punto di intersezione EER con etichetta diretta vicino al punto (niente freccia lunga)
idx_eer = np.argmin(np.abs(y_imp[400:750] - y_gen[400:750])) + 400
x_eer, y_eer = x[idx_eer], y_imp[idx_eer]

ax.plot(x_eer, y_eer, 'ko', markersize=5.5, zorder=5)
ax.text(x_eer - 0.03, y_eer + 0.12, 'EER', fontsize=10, fontweight='bold', ha='right', va='bottom')

# Formattazione assi
ax.set_xlim(-1.0, 1.0)
ax.set_ylim(0, max(y_gen)*1.15)
ax.set_xlabel(r'Cosine Similarity $S_c$')
ax.set_ylabel('Densità di distribuzione')
ax.set_yticks([])

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.legend(frameon=False, loc='upper left')
plt.tight_layout()
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "mathtext.fontset": "cm"
})

# Stessi parametri delle distribuzioni della Figura precedente per coerenza
mu_imp, sigma_imp = 0.15, 0.16
mu_gen, sigma_gen = 0.72, 0.12

# Calcolo di FAR e TAR al variare della soglia tau tra -1 e 1
taus = np.linspace(-1.0, 1.0, 2000)
far = 1 - norm.cdf(taus, mu_imp, sigma_imp)  # Coda destra impostori
frr = norm.cdf(taus, mu_gen, sigma_gen)      # Coda sinistra genuini
tar = 1 - frr                                # True Acceptance Rate (1 - FRR)

# Calcolo del punto EER (dove FAR == FRR, quindi TAR == 1 - FAR)
idx_eer = np.argmin(np.abs(far - frr))
far_eer = far[idx_eer]
tar_eer = tar[idx_eer]

fig, ax = plt.subplots(figsize=(6.5, 5.5), dpi=300)

# Curva ROC principale
ax.plot(far, tar, color='#1f77b4', lw=2.2, label='Curva ROC del sistema')

# Diagonale del classificatore casuale (random guess)
ax.plot([0, 1], [0, 1], color='gray', linestyle='--', lw=1.2, label='Classificatore casuale')

# Diagonale secondaria per evidenziare l'incrocio EER (TAR = 1 - FAR)
ax.plot([0, 1], [1, 0], color='#d62728', linestyle=':', lw=1.1, alpha=0.7)

# Punto EER direttamente sul grafico
ax.plot(far_eer, tar_eer, 'ko', markersize=6, zorder=5)
ax.text(far_eer + 0.04, tar_eer - 0.04, f'EER ({far_eer*100:.1f}%)', 
        fontsize=10, fontweight='bold', ha='left', va='top')

# Formattazione assi e griglia leggera
ax.set_xlim(-0.02, 1.02)
ax.set_ylim(-0.02, 1.04)
ax.set_xlabel('False Acceptance Rate (FAR)')
ax.set_ylabel('True Acceptance Rate (TAR = 1 - FRR)')
ax.grid(True, linestyle='--', alpha=0.35)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax.legend(frameon=False, loc='lower right')
plt.tight_layout()

plt.savefig('curva_roc.png', format='png', dpi=300, bbox_inches='tight')
plt.show()

plt.savefig('distribuzioni_far_frr.png', format='png', dpi=300, bbox_inches='tight')
plt.show()
