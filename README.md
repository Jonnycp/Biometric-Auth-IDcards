# Autenticazione Biometrica via Face Recognition e Liveness Detection su Documenti d'Identità

## Abstract
Questa tesi presenta la progettazione e la validazione sperimentale di un sistema client-server per l'*autenticazione biometrica*}* in tempo reale, che confronta il volto ripreso dalla fotocamera con la fototessera della _Carta d'Identità Elettronica_, rettificata e normalizzata.
La presenza fisica dell'utente è verificata da una *liveness detection* passiva su un buffer di fotogrammi e da un controllo di staticità, mentre gli embedding facciali sono confrontati tramite *similarità coseno* in un database vettoriale, senza conservare immagini.
Su registrazioni reali, il sistema raggiunge un EER del 4,8\% con circa 14~ms di elaborazione per fotogramma.

## Parole chiave
- Face Recognition
- Biometric Auth
- ID cards