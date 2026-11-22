import cv2
import time
from insightface.app import FaceAnalysis

print("1. Caricamento del modello InsightFace (buffalo_sc)...")
# buffalo_sc è compatto e velocissimo sulla CPU del tuo Mac M2
app = FaceAnalysis(name="buffalo_sc", root="~/.insightface")
app.prepare(ctx_id=-1, det_size=(480, 480))
print("2. Modello caricato con successo!")

# Apertura della webcam
cap = cv2.VideoCapture(3)

if not cap.isOpened():
    print("❌ Errore: impossibile accedere alla webcam.")
    exit()

print("3. Webcam avviata! Guarda la finestra che si apre.")
print("   👉 Premi 'q' oppure ESC sulla tastiera per chiudere la finestra.")

prev_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Errore nella lettura del frame dalla webcam.")
        break

    # L'AI analizza il fotogramma e trova tutti i volti
    faces = app.get(frame)

    # Per ogni volto trovato, disegniamo le informazioni sopra l'immagine
    for face in faces:
        print(face)
        # Coordinate del riquadro: (x1, y1) in alto a sinistra, (x2, y2) in basso a destra
        x1, y1, x2, y2 = face.bbox.astype(int)
        score = face.det_score # Confidenza del modello (es. 0.95 = 95% sicuro che sia un volto)

        # 1. Riquadro VERDE attorno al viso
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # 2. Testo con la confidenza sopra il riquadro
        label = f"Viso: {score:.2f}"
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

        # 3. Punti chiave del viso (occhi, naso, bocca) in ROSSO
        if hasattr(face, "kps") and face.kps is not None:
            for point in face.kps:
                px, py = point.astype(int)
                cv2.circle(frame, (px, py), 5, (0, 0, 255), -1)

    # Calcolo degli FPS (fotogrammi al secondo) per vedere la velocità sul tuo M2
    curr_time = time.time()
    fps = 1.0 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
    prev_time = curr_time
    cv2.putText(frame, f"FPS: {fps:.1f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    # Mostra la finestra con il video
    cv2.imshow("Test Rilevamento Volto in Tempo Reale (InsightFace)", frame)

    # Se premi 'q' o ESC chiudi il ciclo
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break

# Pulizia e rilascio della webcam
cap.release()
cv2.destroyAllWindows()