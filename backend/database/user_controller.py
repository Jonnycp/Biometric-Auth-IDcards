from backend.database.models.user import User, UserResult
from backend.database.connection import getUsersCollection
from backend.core.face_recognizer import verifyIdentity

import numpy as np

def createUser(user: User):
    users = getUsersCollection()

    result = users.insert_one(user.model_dump())
    return result

def searchUser_byEmbedding(query_embedding: np.ndarray, threshold: float = 0.35):
    users = getUsersCollection()
    query_embedding_list = query_embedding.tolist()

    pipeline = [
        {
                "$vectorSearch": {
                    "index": "vector_index",      # Nome dell'indice su Atlas
                    "path": "embedding",          # Campo dove risiede il vettore
                    "queryVector": query_embedding_list,
                    "numCandidates": 100,
                    "limit": 1
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "fullName": 1,
                    "createdAt": 1,
                    "vector_score": {"$meta": "vectorSearchScore"},
                    "embedding": 1
                }
            }
    ]

    results = list(users.aggregate(pipeline))
    if not results:
        return UserResult(isMatch=False, similarity=0.0)

    best_match = results[0]
    db_embedding = np.array(best_match["embedding"])

    identityResult = verifyIdentity(db_embedding, query_embedding, threshold)
    
    return UserResult(
        isMatch=identityResult["isMatch"], 
        user=best_match, 
        similarity=identityResult["similarity"], 
        vectorScore=best_match["vector_score"]
        )

def deleteUser(user_id):
    collection = getUsersCollection()
    try:
        result = collection.delete_one({"_id": user_id})
        if result.deleted_count == 1:
            return True
        else:
            return False
    except Exception as e:
        return False