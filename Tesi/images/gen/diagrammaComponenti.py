import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 11
})

fig, ax = plt.subplots(figsize=(15.5, 7.2), dpi=300)
ax.set_xlim(0, 17.5)
ax.set_ylim(0, 8.2)
ax.axis('off')

# Funzione per disegnare le colonne principali (Tiers)
def draw_tier(x, y, w, h, title, subtitle, bg_color, header_color):
    shadow = patches.FancyBboxPatch((x + 0.08, y - 0.08), w, h,
                                    boxstyle="round,pad=0.05,rounding_size=0.35",
                                    facecolor="#e2e8f0", edgecolor="none", zorder=0)
    ax.add_patch(shadow)
    
    rect = patches.FancyBboxPatch((x, y), w, h,
                                  boxstyle="round,pad=0.05,rounding_size=0.35",
                                  facecolor=bg_color, edgecolor=header_color,
                                  linewidth=2.0, zorder=1)
    ax.add_patch(rect)
    
    header = patches.FancyBboxPatch((x + 0.15, y + h - 1.05), w - 0.30, 0.88,
                                    boxstyle="round,pad=0.04,rounding_size=0.25",
                                    facecolor=header_color, edgecolor="none", zorder=2)
    ax.add_patch(header)
    
    ax.text(x + w/2, y + h - 0.45, title, ha='center', va='center',
            fontsize=12.5, fontweight='bold', color='white', zorder=3)
    ax.text(x + w/2, y + h - 0.80, subtitle, ha='center', va='center',
            fontsize=9.8, color='#f8fafc', zorder=3)

# Funzione per i box interni essenziali
def draw_pill_box(x, y, w, h, title, fc="white", ec="#6366f1", text_color="#1e293b"):
    sh = patches.FancyBboxPatch((x - w/2 + 0.05, y - h/2 - 0.05), w, h,
                                boxstyle="round,pad=0.04,rounding_size=0.22",
                                facecolor="#cbd5e1", alpha=0.45, edgecolor="none", zorder=2)
    ax.add_patch(sh)
    
    rect = patches.FancyBboxPatch((x - w/2, y - h/2), w, h,
                                  boxstyle="round,pad=0.04,rounding_size=0.22",
                                  facecolor=fc, edgecolor=ec, linewidth=1.8, zorder=3)
    ax.add_patch(rect)
    ax.text(x, y, title, ha='center', va='center',
            fontsize=10.8, fontweight='bold', color=text_color, linespacing=1.25, zorder=4)

# ==============================================================================
# 1. COLONNA SINISTRA: PRESENTATION TIER
# ==============================================================================
draw_tier(0.3, 0.4, 4.0, 7.4,
          "Presentation Tier", "Client PWA",
          bg_color="#eef2ff", header_color="#4f46e5")

draw_pill_box(2.3, 5.75, 3.2, 0.90, "Acquisizione Ottica\n(Webcam / CIE)", ec="#4f46e5", text_color="#1e1b4b")

ax.annotate('', xy=(2.3, 4.55), xytext=(2.3, 5.20),
            arrowprops=dict(arrowstyle='->,head_width=0.35,head_length=0.35', lw=2.0, color='#4f46e5'), zorder=4)

draw_pill_box(2.3, 3.95, 3.2, 0.90, "Pre-compressione\nFotogrammi", ec="#4f46e5", text_color="#1e1b4b")

ax.annotate('', xy=(2.3, 2.75), xytext=(2.3, 3.40),
            arrowprops=dict(arrowstyle='<->,head_width=0.35,head_length=0.35', lw=2.0, color='#4f46e5'), zorder=4)

draw_pill_box(2.3, 2.15, 3.2, 0.90, "Interfaccia & Feedback\nReal-Time", ec="#4f46e5", text_color="#1e1b4b")

# ==============================================================================
# 2. COLONNA CENTRALE: APPLICATION & BIOMETRIC TIER
# ==============================================================================
draw_tier(6.1, 0.4, 5.4, 7.4,
          "Application & Biometric Tier", "Backend FastAPI",
          bg_color="#ecfeff", header_color="#0284c7")

mod_w, mod_h = 4.5, 0.78
x_mod = 8.8

modules = [
    {"y": 5.95, "title": "Rettifica Documentale (CIE)"},
    {"y": 4.82, "title": "Rilevamento & Allineamento"},
    {"y": 3.69, "title": "Liveness Detection (MiniFASNet)"},
    {"y": 2.56, "title": "Estrazione & Confronto (ArcFace)"},
    {"y": 1.43, "title": "Protezione BioHashing"}
]

for i, m in enumerate(modules):
    draw_pill_box(x_mod, m["y"], mod_w, mod_h, m["title"], ec="#0284c7", text_color="#0c4a6e")
    if i < len(modules) - 1:
        ax.annotate('', xy=(x_mod, modules[i+1]["y"] + mod_h/2 + 0.05),
                    xytext=(x_mod, m["y"] - mod_h/2 - 0.05),
                    arrowprops=dict(arrowstyle='->,head_width=0.3,head_length=0.3', lw=1.8, color='#0284c7'), zorder=4)

# ==============================================================================
# 3. COLONNA DESTRA: DATA TIER
# ==============================================================================
draw_tier(13.3, 0.4, 3.9, 7.4,
          "Data Tier", "MongoDB Atlas",
          bg_color="#ecfdf5", header_color="#059669")

draw_pill_box(15.25, 5.15, 3.1, 1.15, "Archivio Vettoriale\n(Template BioHash 512D)", ec="#059669", text_color="#064e3b")

ax.annotate('', xy=(15.25, 3.55), xytext=(15.25, 4.45),
            arrowprops=dict(arrowstyle='<->,head_width=0.35,head_length=0.35', lw=2.0, color='#059669'), zorder=4)

draw_pill_box(15.25, 2.80, 3.1, 1.15, "Atlas Vector Search\n(Query 1:N)", ec="#059669", text_color="#064e3b")

# ==============================================================================
# 4. CANALI DI COMUNICAZIONE TRA I LIVELLI (SENZA RETTANGOLI INTORNO)
# ==============================================================================
# Client -> Backend (HTTPS REST)
ax.annotate('', xy=(6.02, 5.20), xytext=(4.38, 5.20),
            arrowprops=dict(arrowstyle='->,head_width=0.35,head_length=0.35', lw=2.2, color='#4f46e5'), zorder=5)
ax.text(5.20, 5.32, "HTTPS\nREST", ha='center', va='bottom',
        fontsize=10.2, fontweight='bold', color='#3730a3')

# Client <-> Backend (WSS WebSocket)
ax.annotate('', xy=(6.02, 3.00), xytext=(4.38, 3.00),
            arrowprops=dict(arrowstyle='<->,head_width=0.35,head_length=0.35', lw=2.2, color='#0284c7'), zorder=5)
ax.text(5.20, 3.12, "WSS\nWebSocket", ha='center', va='bottom',
        fontsize=10.2, fontweight='bold', color='#0369a1')

# Backend <-> Cloud DB (TLS)
ax.annotate('', xy=(13.22, 4.00), xytext=(11.58, 4.00),
            arrowprops=dict(arrowstyle='<->,head_width=0.35,head_length=0.35', lw=2.2, color='#059669'), zorder=5)
ax.text(12.40, 4.12, "TLS\nDriver", ha='center', va='bottom',
        fontsize=10.2, fontweight='bold', color='#065f46')

plt.tight_layout()
plt.savefig('../diagramma-componenti.png', format='png', dpi=300, bbox_inches='tight')
plt.show()
