import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 9.5,
    "mathtext.fontset": "cm"
})

fig, ax = plt.subplots(figsize=(15.5, 11.2), dpi=300)
ax.set_xlim(0, 16.5)
ax.set_ylim(0, 12.2)
ax.axis('off')

# ==============================================================================
# 1. DEFINIZIONE PARTECIPANTI E LINEE DI VITA (LIFELINES)
# ==============================================================================
actors = [
    {"x": 1.4,  "name": "Utente",                 "w": 1.8},
    {"x": 4.4,  "name": "Client PWA",             "w": 2.0},
    {"x": 7.8,  "name": "Backend\n(/register)",   "w": 2.1},
    {"x": 11.4, "name": "Moduli Core", "w": 2.3},
    {"x": 14.9, "name": "Database Vettoriale",          "w": 2.2}
]

y_top = 11.5
y_bot = 0.55
box_h = 0.72

for act in actors:
    x, w = act["x"], act["w"]
    # Box superiore
    top_box = patches.Rectangle((x - w/2, y_top - box_h/2), w, box_h,
                                facecolor="white", edgecolor="#333333", linewidth=1.2, zorder=4)
    ax.add_patch(top_box)
    ax.text(x, y_top, act["name"], ha='center', va='center', fontsize=9.2, fontweight='bold', color='#111111', zorder=5)
    
    # Box inferiore
    bot_box = patches.Rectangle((x - w/2, y_bot - box_h/2), w, box_h,
                                facecolor="white", edgecolor="#333333", linewidth=1.2, zorder=4)
    ax.add_patch(bot_box)
    ax.text(x, y_bot, act["name"], ha='center', va='center', fontsize=9.2, fontweight='bold', color='#111111', zorder=5)
    
    # Linea di vita tratteggiata
    ax.plot([x, x], [y_top - box_h/2, y_bot + box_h/2], color="#555555", linestyle="--", linewidth=1.1, zorder=1)

# ==============================================================================
# 2. BANNER DI FASE (Stile giallo tenue come nell'immagine)
# ==============================================================================
def draw_phase_banner(y, text):
    banner = patches.Rectangle((0.6, y - 0.16), 15.3, 0.32,
                               facecolor="#fef9c3", edgecolor="#eab308", linewidth=0.9, zorder=2)
    ax.add_patch(banner)
    ax.text(8.25, y, text, ha='center', va='center', fontsize=8.8, fontweight='bold', color='#422006', zorder=3)

draw_phase_banner(10.75, "FASE DI ENROLLMENT BIOMETRICO (POST /register)")

# ==============================================================================
# 3. BARRE DI ATTIVAZIONE (EXECUTION SPECIFICATIONS)
# ==============================================================================
def draw_activation(x, y_start, y_end, color="#f8fafc"):
    w = 0.22
    bar = patches.Rectangle((x - w/2, y_end), w, y_start - y_end,
                            facecolor=color, edgecolor="#333333", linewidth=1.0, zorder=3)
    ax.add_patch(bar)

draw_activation(1.4,  10.2, 9.7)   # Utente
draw_activation(4.4,  10.1, 1.3)   # Client PWA
draw_activation(7.8,  9.5,  1.4)   # FastAPI
draw_activation(11.4, 9.2,  7.4)   # Moduli CV (Estrazione)
draw_activation(14.9, 6.9,  6.2)   # MongoDB (Vector Search)
draw_activation(11.4, 3.8,  3.1)   # Moduli CV (BioHashing)
draw_activation(14.9, 2.8,  2.2)   # MongoDB (Insert)

# ==============================================================================
# 4. FUNZIONE FRECCE MESSAGGI UML
# ==============================================================================
def draw_msg(x1, x2, y, label, dashed=False, self_call=False):
    if self_call:
        # Auto-chiamata a destra della lifeline
        loop_w = 0.65
        loop_h = 0.32
        ax.plot([x1 + 0.11, x1 + loop_w, x1 + loop_w], [y, y, y - loop_h], color="#222222", lw=1.1, zorder=4)
        ax.annotate('', xy=(x1 + 0.11, y - loop_h), xytext=(x1 + loop_w, y - loop_h),
                    arrowprops=dict(arrowstyle='-|>', lw=1.1, color='#222222', mutation_scale=11), zorder=4)
        ax.text(x1 + loop_w + 0.12, y - loop_h/2, label, ha='left', va='center', fontsize=8.4, color='#111111',
                bbox=dict(boxstyle='square,pad=0.1', facecolor='white', edgecolor='none', alpha=0.85), zorder=5)
    else:
        offset = 0.12 if x2 > x1 else -0.12
        ls = '--' if dashed else '-'
        ax.annotate('', xy=(x2 - offset, y), xytext=(x1 + offset, y),
                    arrowprops=dict(arrowstyle='-|>', lw=1.15, ls=ls, color='#222222', mutation_scale=12), zorder=4)
        mx = (x1 + x2) / 2.0
        ax.text(mx, y + 0.08, label, ha='center', va='bottom', fontsize=8.4, color='#111111',
                bbox=dict(boxstyle='square,pad=0.08', facecolor='white', edgecolor='none', alpha=0.85), zorder=5)

# ==============================================================================
# 5. SEQUENZA INIZIALE (ACQUISIZIONE ED ESTRAZIONE)
# ==============================================================================
draw_msg(1.4, 4.4, 10.05, "1. Inquadra fronte CIE e inserisce nominativo")
draw_msg(4.4, 7.8, 9.45,  "2. POST /register\n(multipart/form-data: fullName, idCardImage)")

draw_msg(7.8, 11.4, 8.95, "3. Decodifica in RAM + Pre-processing\n(WARP, CLAHE)")
draw_msg(11.4, 11.4, 8.40, "4. Rilevamento volto (BBox, KPS)", self_call=True)
draw_msg(11.4, 7.8, 7.50,  r"5. Estrazione Embedding $e_{\mathrm{ID}} \in \mathbb{R}^{512}$", dashed=True)

# ==============================================================================
# 6. CONTROLLO UNICITÀ 1:N SU MONGODB ATLAS
# ==============================================================================
draw_msg(7.8, 14.9, 6.85, r"6. Query $vectorSearch $1:N$ per controllo unicità (RF5)")
draw_msg(14.9, 7.8, 6.25, r"7. Risultato similarità massima $\max_j S_c(e_{\mathrm{ID}}, e_j)$", dashed=True)

# ==============================================================================
# 7. BLOCCO COMBINATO ALT / ELSE (Stile riquadro UML dell'immagine)
# ==============================================================================
alt_x, alt_w = 3.5, 12.3
alt_top, alt_bot = 5.75, 1.15
alt_mid = 4.35  # Linea separatrice tra alt ed else

# Cornice esterna alt
alt_rect = patches.Rectangle((alt_x, alt_bot), alt_w, alt_top - alt_bot,
                             facecolor="none", edgecolor="#444444", linewidth=1.2, zorder=3)
ax.add_patch(alt_rect)

# Etichetta pentagonale "alt" in alto a sinistra
pent_alt = patches.Polygon([[alt_x, alt_top], [alt_x + 0.85, alt_top], [alt_x + 0.85, alt_top - 0.22],
                            [alt_x + 0.68, alt_top - 0.36], [alt_x, alt_top - 0.36]],
                           closed=True, facecolor="#f1f5f9", edgecolor="#444444", linewidth=1.1, zorder=4)
ax.add_patch(pent_alt)
ax.text(alt_x + 0.38, alt_top - 0.18, "alt", ha='center', va='center', fontsize=8.8, fontweight='bold', color='#111111', zorder=5)

# Guardia alt [Soggetto già presente]
ax.text(alt_x + 1.05, alt_top - 0.20, r"[Soggetto già presente: $\max_j S_c(e_{\mathrm{ID}}, e_j) \geq \tau$]",
        ha='left', va='center', fontsize=8.6, fontweight='bold', color='#991b1b', zorder=5)

# Messaggi dentro blocco alt
draw_msg(7.8, 4.4, 4.95, "8a. HTTP 409 Conflict (Utente già registrato)", dashed=True)
draw_msg(4.4, 1.4, 4.60, "Notifica errore duplicazione", dashed=True)

# Linea tratteggiata separatrice else
ax.plot([alt_x, alt_x + alt_w], [alt_mid, alt_mid], color="#444444", linestyle="--", linewidth=1.1, zorder=3)
ax.text(alt_x + 0.25, alt_mid - 0.22, "else", ha='left', va='center', fontsize=8.8, fontweight='bold', color='#111111', zorder=5)
ax.text(alt_x + 1.05, alt_mid - 0.22, r"[Soggetto univoco: $\max_j S_c(e_{\mathrm{ID}}, e_j) < \tau$]",
        ha='left', va='center', fontsize=8.6, fontweight='bold', color='#166534', zorder=5)

# Messaggi dentro blocco else
draw_msg(7.8, 11.4, 3.65, r"8b. biohash.py: genera seme $K$ e template $c_{\mathrm{ID}} \in \{0,1\}^m$")
draw_msg(11.4, 7.8, 3.15, r"Restituisce $(c_{\mathrm{ID}}, K)$", dashed=True)
draw_msg(7.8, 14.9, 2.70, r"9. INSERT documento ($full\_name, c_{\mathrm{ID}}, K, timestamp$)")
draw_msg(14.9, 7.8, 2.25, "Conferma scrittura", dashed=True)
draw_msg(7.8, 7.8,  1.95, "10. Deallocazione matrici RAM (Zero-Disk Retention)", self_call=True)
draw_msg(7.8, 4.4,  1.50, "11. HTTP 201 Created (JSON DTO)", dashed=True)
draw_msg(4.4, 1.4,  1.28, "Conferma registrazione completata", dashed=True)

plt.tight_layout()
plt.savefig('../diagrammaSequenza-Registrazione.png', format='png', dpi=300, bbox_inches='tight')
plt.show()
