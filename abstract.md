# Autenticazione Biometrica via Face Recognition e Liveness Detection su Documenti d'Identità

## Abstract
Progettazione e implementazione di una pipeline edge-computing per l’autenticazione biometrica basata su face verification e liveness detection in tempo reale.
Il sistema acquisisce un breve stream video dalla fotocamera per validare la presenza fisica dell’utente (anti-spoofing) ed effettua l’estrazione e il confronto di feature map facciali profonde (deep face embeddings) mediante reti neurali.
La verifica dell’identità opera tramite cosine-similarity confrontando il volto live con le immagini di riferimento estratte da carte d’identità, affrontando problematiche ingegneristiche di low-resolution, rumore da scansione e age-gap, con un focus prioritario su minimizzazione della latenza, footprint computazionale ridotto e alta accuratezza di classificazione. 

## Parole chiave
- Face Recognition
- Biometric Auth
- ID cards