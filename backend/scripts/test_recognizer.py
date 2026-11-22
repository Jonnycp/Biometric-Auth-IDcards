import cv2
import numpy as np
from insightface.app import FaceAnalysis

def cosine_similarity(emb1, emb2):
    """Calcola la similarità coseno tra due vettori di 512 numeri."""
    dot = np.dot(emb1, emb2)
    norm1 = np.linalg.norm(emb1)
    norm2 = np.linalg.norm(emb2)
    return dot / (norm1 * norm2)

print("1. Inizializzazione InsightFace...")
app = FaceAnalysis(name="buffalo_sc", root="~/.insightface")
app.prepare(ctx_id=-1, det_size=(480, 480))

cap = cv2.VideoCapture(3)
if not cap.isOpened():
    print("❌ Impossibile aprire la webcam.")
    exit()

reference_embedding = None
THRESHOLD = 0.50  # Soglia di riconoscimento (tipicamente tra 0.45 e 0.60)

print("\n" + "="*50)
print("👉 Inquadrati e premi [BARRA SPAZIATRICE] per registrare il tuo volto.")
print("👉 Premi [q] o [ESC] per uscire.")
print("="*50 + "\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    faces = app.get(frame)

    # Istruzioni a schermo
    if reference_embedding is None:
        cv2.putText(frame, "Premi [SPAZIO] per registrare il volto", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 2)
    else:
        cv2.putText(frame, "Volto registrato! [R] per azzerare", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 2)

    for face in faces:
        x1, y1, x2, y2 = face.bbox.astype(int)
        current_embedding = face.embedding

        # Se abbiamo già registrato un volto di riferimento, facciamo il confronto!
        if reference_embedding is not None:
            similarity = cosine_similarity(reference_embedding, current_embedding)

            if similarity >= THRESHOLD:
                color = (0, 255, 0) # Verde: riconosciuto!
                text = f"ACCESSO CONSENTITO ({similarity:.2f})"
            else:
                color = (0, 0, 255) # Rosso: non corrisponde!
                text = f"ACCESSO NEGATO ({similarity:.2f})"

            # Disegna il box e il risultato
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 2)
        else:
            # Finché non registri, mostra solo il box neutro
            cv2.rectangle(frame, (x1, y1), (x2, y2), (200, 200, 200), 2)

    cv2.imshow("Test Riconoscimento Facciale", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord(' ') and len(faces) > 0:
        # Prendi il volto più grande e salva il suo embedding come riferimento
        main_face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
        reference_embedding = main_face.embedding.copy()
        print("✅ Volto registrato come riferimento!")
    elif key == ord('r'):
        # Azzera per riprovare
        reference_embedding = None
        print("🔄 Riferimento azzerato.")
    elif key == ord('q') or key == 27:
        break

cap.release()
cv2.destroyAllWindows()