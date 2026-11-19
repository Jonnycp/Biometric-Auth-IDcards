import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 9.5,
    "mathtext.fontset": "cm"
})

fig, ax = plt.subplots(figsize=(15.5, 11.8), dpi=300)
ax.set_xlim(0, 16.5)
ax.set_ylim(0, 12.8)
ax.axis('off')

# ==============================================================================
# 1. DEFINIZIONE PARTECIPANTI E LINEE DI VITA (LIFELINES)
# ==============================================================================
actors = [
    {"x": 1.4,  "name": "Utente",                       "w": 1.8},
    {"x": 4.4,  "name": "Client PWA",                   "w": 2.0},
    {"x": 7.8,  "name": "Backend\n(/login + FSM)",  "w": 2.3},
    {"x": 11.4, "name": "Moduli Core", "w": 2.5},
    {"x": 14.9, "name": "Database Vettoriale",                "w": 2.2}
]

y_top = 12.1
y_bot = 0.55
box_h = 0.75

for act in actors:
    x, w = act["x"], act["w"]
    top_box = patches.Rectangle((x - w/2, y_top - box_h/2), w, box_h,
                                facecolor="white", edgecolor="#333333", linewidth=1.2, zorder=4)
    ax.add_patch(top_box)
    ax.text(x, y_top, act["name"], ha='center', va='center', fontsize=9.0, fontweight='bold', color='#111111', zorder=5)
    
    bot_box = patches.Rectangle((x - w/2, y_bot - box_h/2), w, box_h,
                                facecolor="white", edgecolor="#333333", linewidth=1.2, zorder=4)
    ax.add_patch(bot_box)
    ax.text(x, y_bot, act["name"], ha='center', va='center', fontsize=9.0, fontweight='bold', color='#111111', zorder=5)
    
    ax.plot([x, x], [y_top - box_h/2, y_bot + box_h/2], color="#555555", linestyle="--", linewidth=1.1, zorder=1)

# ==============================================================================
# 2. BANNER DI FASE
# ==============================================================================
def draw_phase_banner(y, text):
    banner = patches.Rectangle((0.6, y - 0.16), 15.3, 0.32,
                               facecolor="#fef9c3", edgecolor="#eab308", linewidth=0.9, zorder=2)
    ax.add_patch(banner)
    ax.text(8.25, y, text, ha='center', va='center', fontsize=8.8, fontweight='bold', color='#422006', zorder=3)

draw_phase_banner(11.35, "FASE DI AUTENTICAZIONE LIVE SU WEBSOCKET (WSS /login)")

# ==============================================================================
# 3. BARRE DI ATTIVAZIONE
# ==============================================================================
def draw_activation(x, y_start, y_end, color="#f8fafc"):
    w = 0.22
    bar = patches.Rectangle((x - w/2, y_end), w, y_start - y_end,
                            facecolor=color, edgecolor="#333333", linewidth=1.0, zorder=3)
    ax.add_patch(bar)

draw_activation(1.4,  10.8, 10.2)   # Utente
draw_activation(4.4,  10.7, 1.25)   # Client PWA
draw_activation(7.8,  10.1, 1.35)   # FastAPI
draw_activation(11.4, 8.75, 7.60)   # MiniFASNet & InsightFace (Loop Liveness)
draw_activation(11.4, 4.15, 3.45)   # InsightFace (Estrazione e_live)
draw_activation(14.9, 3.15, 2.55)   # MongoDB Atlas (Query 1:N)

# ==============================================================================
# 4. FUNZIONE FRECCE MESSAGGI UML
# ==============================================================================
def draw_msg(x1, x2, y, label, dashed=False, self_call=False):
    if self_call:
        loop_w = 0.65
        loop_h = 0.30
        ax.plot([x1 + 0.11, x1 + loop_w, x1 + loop_w], [y, y, y - loop_h], color="#222222", lw=1.1, zorder=4)
        ax.annotate('', xy=(x1 + 0.11, y - loop_h), xytext=(x1 + loop_w, y - loop_h),
                    arrowprops=dict(arrowstyle='-|>', lw=1.1, color='#222222', mutation_scale=11), zorder=4)
        ax.text(x1 + loop_w + 0.12, y - loop_h/2, label, ha='left', va='center', fontsize=8.3, color='#111111',
                bbox=dict(boxstyle='square,pad=0.08', facecolor='white', edgecolor='none', alpha=0.88), zorder=5)
    else:
        offset = 0.12 if x2 > x1 else -0.12
        ls = '--' if dashed else '-'
        ax.annotate('', xy=(x2 - offset, y), xytext=(x1 + offset, y),
                    arrowprops=dict(arrowstyle='-|>', lw=1.15, ls=ls, color='#222222', mutation_scale=12), zorder=4)
        mx = (x1 + x2) / 2.0
        ax.text(mx, y + 0.08, label, ha='center', va='bottom', fontsize=8.3, color='#111111',
                bbox=dict(boxstyle='square,pad=0.06', facecolor='white', edgecolor='none', alpha=0.88), zorder=5)

def draw_pentagon_tag(ax, x, y, w, h, tag_text):
    pent = patches.Polygon([[x, y], [x + w, y], [x + w, y - h*0.62],
                            [x + w*0.80, y - h], [x, y - h]],
                           closed=True, facecolor="#f1f5f9", edgecolor="#444444", linewidth=1.1, zorder=4)
    ax.add_patch(pent)
    ax.text(x + w*0.45, y - h*0.5, tag_text, ha='center', va='center', fontsize=8.6, fontweight='bold', color='#111111', zorder=5)

# ==============================================================================
# 5. APERTURA CONNESSIONE E INIZIALIZZAZIONE FSM
# ==============================================================================
draw_msg(1.4, 4.4, 10.65, "1. Avvia verifica biometrica live")
draw_msg(4.4, 7.8, 10.05, "2. Handshake WebSocket Secure (WSS /login)")
draw_msg(7.8, 7.8, 9.65,  r"3. Init FSM in stato $s_0$: WAITING_FACE", self_call=True)

# ==============================================================================
# 6. BLOCCO LOOP (BUFFER LIVENESS)
# ==============================================================================
loop_x, loop_w = 3.6, 9.3
loop_top, loop_bot = 9.05, 6.75

loop_rect = patches.Rectangle((loop_x, loop_bot), loop_w, loop_top - loop_bot,
                              facecolor="none", edgecolor="#0284c7", linewidth=1.2, zorder=3)
ax.add_patch(loop_rect)
draw_pentagon_tag(ax, loop_x, loop_top, 0.90, 0.34, "loop")
ax.text(loop_x + 1.05, loop_top - 0.17, r"[Buffer $N \in [30, 60]$ frame (~1–2 s) in stato $s_1$: WAITING_LIVENESS]",
        ha='left', va='center', fontsize=8.5, fontweight='bold', color='#0369a1', zorder=5)

draw_msg(4.4, 7.8,  8.45, r"4. Invia binary frame $f_t$ (bytes)")
draw_msg(7.8, 11.4, 7.95, r"5. 5 KPS ($\sigma_{\mathrm{kps}}^2$), score $l_t$, aggiorna $f_{\mathrm{best}}$")
draw_msg(11.4, 7.8, 7.50, r"Restituisce $(l_t, \mathrm{KPS}_t, q_{\mathrm{face}, t})$", dashed=True)
draw_msg(7.8, 4.4,  7.05, r'6. JSON: {"status": "WAITING_LIVENESS","progress":%, ...}', dashed=True)

# ==============================================================================
# 7. BLOCCO COMBINATO ALT / ELSE (VALUTAZIONE LIVENESS E MATCHING)
# ==============================================================================
alt_x, alt_w = 3.5, 12.4
alt_top, alt_bot = 6.35, 1.10
alt_mid = 4.80

alt_rect = patches.Rectangle((alt_x, alt_bot), alt_w, alt_top - alt_bot,
                             facecolor="none", edgecolor="#444444", linewidth=1.2, zorder=3)
ax.add_patch(alt_rect)
draw_pentagon_tag(ax, alt_x, alt_top, 0.85, 0.34, "alt")

# Guardia alt [Spoof rilevato]
ax.text(alt_x + 1.00, alt_top - 0.18, r"[$\bar{L} < \tau_{\mathrm{liveness}}$ OR $\sigma_{\mathrm{kps}}^2 < \sigma_{\min}^2$ (Spoof / Staticità)]",
        ha='left', va='center', fontsize=8.5, fontweight='bold', color='#991b1b', zorder=5)

draw_msg(7.8, 7.8, 5.75, r"7a. Transizione in $s_2$: SPOOF_ATTACK + reset buffer RAM", self_call=True)
draw_msg(7.8, 4.4, 5.20, r'8a. JSON: {"status": "SPOOF_ATTACK"} + chiusura WSS', dashed=True)
draw_msg(4.4, 1.4, 4.95, "Allarme spoofing", dashed=True)

# Linea tratteggiata else
ax.plot([alt_x, alt_x + alt_w], [alt_mid, alt_mid], color="#444444", linestyle="--", linewidth=1.1, zorder=3)
ax.text(alt_x + 0.22, alt_mid - 0.20, "else", ha='left', va='center', fontsize=8.6, fontweight='bold', color='#111111', zorder=5)
ax.text(alt_x + 1.00, alt_mid - 0.20, r"[Vitalità confermata: $\bar{L} \geq \tau_{\mathrm{liveness}}$ AND $\sigma_{\mathrm{kps}}^2 \in [\sigma_{\min}^2, \sigma_{\max}^2]$]",
        ha='left', va='center', fontsize=8.5, fontweight='bold', color='#166534', zorder=5)

# Messaggi dentro else
draw_msg(7.8, 11.4, 4.05, r"7b. Estrae embedding $e_{\mathrm{live}} \in \mathbb{R}^{512}$ solo su $f_{\mathrm{best}}$")
draw_msg(11.4, 7.8, 3.55, r"Restituisce $e_{\mathrm{live}}$", dashed=True)
draw_msg(7.8, 14.9, 3.10, r"8b. Singola query $vectorSearch $1:N$ + verifica BioHash")
draw_msg(14.9, 7.8, 2.60, r"9. Candidato migliore e score $S_c(e_{\mathrm{live}}, e_{\mathrm{ID}})$", dashed=True)
draw_msg(7.8, 7.8,  2.25, r"10. Stato $s_3$: MATCH / NO_MATCH ($S_c \geq \tau$) + pulizia RAM", self_call=True)
draw_msg(7.8, 4.4,  1.60, "11. Verdetto finale JSON + chiusura WSS", dashed=True)
draw_msg(4.4, 1.4,  1.30, "Esito autenticazione", dashed=True)

plt.tight_layout()
plt.savefig('../diagrammaSequenza-Login.png', format='png', dpi=300, bbox_inches='tight')
plt.show()
