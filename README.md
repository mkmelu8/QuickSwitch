# QuickSwitch
The LMU Fast streering wheels load preset
Gestore Setup Volanti - Le Mans Ultimate (LMU) Un'applicazione standalone con interfaccia grafica pensata per i sim racer che necessitano di scambiare rapidamente i profili delle periferiche (basi Direct Drive, volanti, pedaliere) su Le Mans Ultimate.

Il programma automatizza la gestione, l'archiviazione e la sostituzione del file direct input.json, permettendo di cambiare setup hardware in pochi secondi senza dover riavviare il simulatore.

🚀 Funzionalità Principali Interfaccia Visiva a Griglia: Tutti i preset salvati sono mostrati in comode "schede" visive per una selezione rapida.

Smart Hardware Detection: Durante l'importazione di un nuovo setup, il programma legge internamente il file .json, individua il dispositivo che utilizza il Force Feedback (ignorando ad esempio le pedaliere) ed estrae in automatico il nome esatto dell'hardware (es. Ascher Racing Artura ULTIMATE).

Associazione Immagini Intelligente: È possibile associare una foto a ogni volante. L'immagine viene legata al nome dell'hardware rilevato: ogni futuro preset che utilizzerà la stessa base caricherà automaticamente la foto corretta. Include un'icona di default per i dispositivi non ancora personalizzati.

Hot-Swap del Setup: Sostituisce e rinomina il preset in direct input.json con un solo clic.

Plug & Play: Compilato in un unico file .exe. Non richiede l'installazione di Python o librerie esterne.

📥 Installazione Scarica l'ultima release contenente il file Selettore_LMU.exe e l'immagine iconavolantetstandard.jpg.

(Opzionale ma consigliato per setup automatico): Posiziona entrambi i file direttamente nella cartella del tuo profilo di LMU: ...\Le Mans Ultimate\UserData\player\

Avvia l'eseguibile. Il programma creerà automaticamente la sua directory di lavoro e sarà pronto all'uso.

🏎️ Come usarlo in gioco (Senza riavviare LMU) Il motore grafico di LMU non supporta l'hot-reload automatico mentre si è alla guida. Per cambiare volante a sessione in corso:

Rientra ai box ed esci dall'abitacolo (schermata dei tempi).

Apri questa applicazione (tramite ALT+TAB o su un monitor secondario) e clicca su ATTIVA PRESET SELEZIONATO.

Torna su LMU, entra in Settings -> Controls.

L'ingresso nel menu forzerà il gioco a rileggere il file direct input.json aggiornato dal disco. (In caso di mancata ricezione degli input, cliccare su Calibrate per forzare il refresh).

Torna al garage e scendi in pista.

🛠️ Stack Tecnico Linguaggio: Python 3

GUI: Tkinter

Image Processing: Pillow (PIL)

Build: PyInstaller
