import numpy as np

# Estrae embeddings faccia
def extractEmbeddings(face):
   if face is None or not hasattr(face, 'embedding'):
       return (None, 0.0)
   return face.embedding.copy(), float(face.det_score)

# Formula cos similarity tra due vettori embedding
def cosineSimilarity(embedding1: np.ndarray, embedding2: np.ndarray):
    # 1.0 -> vettori identici
    # 0.0 -> vettori ortogonali -> nessuna correlazione
    # -1.0 -> vettori opposti
    if embedding1 is None or embedding2 is None:
        return 0.0
    
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)

    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

# Verifica similarity da threshold
def verifyIdentity(embedding1: np.ndarray, embedding2: np.ndarray, threshold=0.45):
    similarity = cosineSimilarity(embedding1, embedding2)
    return {
        "similarity": float(similarity),
        "isMatch": similarity >= threshold,
        "threshold": float(threshold)
    }
