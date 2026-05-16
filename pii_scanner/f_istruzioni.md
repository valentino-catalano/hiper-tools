# ⚙️ Guida di Configurazione e Distribuzione Fedora: PII Scanner

Questo documento fornisce le istruzioni tecniche per personalizzare lo script Python, compilarlo in un binario nativo ed eseguirne la distribuzione automatizzata sui sistemi operativi Linux Fedora tramite script Bash e sottosistema Cron.

---

## 1. Personalizzazione dei Parametri Aziendali (Python)

Le politiche di scansione e i comportamenti di logging possono essere configurati modificando le variabili presenti nel blocco iniziale del file sorgente `f_pii_scanner.py`:

### 📂 Percorso per Log Centralizzato
Per raccogliere i report di conformità in modo centralizzato, valorizza la variabile `LOG_EXPORT_PATH` con il punto di mount locale o di rete condiviso stabilito per l'infrastruttura Linux:
 ``` python
# Sostituire con il percorso desiderato (es. una share di rete montata)
LOG_EXPORT_PATH = "/mnt/server_aziendale/logs"
 ``` 
*Se la variabile viene lasciata vuota (`""`), la funzione di export silente rimarrà disattivata.*

### 🛡️ Whitelist delle Cartelle (Esclusioni)
Per preservare le prestazioni della CPU ed evitare il controllo di file di sistema, runtime o virtuali che genererebbero falsi positivi, compila l'array delle esclusioni inserendo i nomi delle directory strutturali rigorosamente in **minuscolo**:
 ``` python
DIR_EXCLUSIONS = {
    "usr", "var", "proc", "sys", "dev", "run", "boot", "lib", "lib64", 
    "snap", "flatpak", "node_modules", ".git", ".vscode", "vendor", "cache"
}
 ``` 

### ⏱️ Throttling (Frenatura I/O)
La variabile `THROTTLING_DELAY` introduce una micro-pausa (espressa in frazioni di secondo) dopo l'analisi di ogni singolo file. Questo evita il sovraccarico del disco durante la ricerca dei pattern.
* **Valore consigliato:** `0.01` (10 millisecondi di ritardo per file).

---

## 2. Compilazione in Binario Nativo (Linux)

Per distribuire l'applicazione sugli endpoint Fedora senza dover installare l'interprete Python o le relative dipendenze grafiche su ogni macchina, lo script deve essere convertito in un file eseguibile ELF standalone.

1. Installa il modulo di compilazione tramite terminale Fedora:
 ``` bash
pip install pyinstaller
 ``` 
2. Genera il file eseguibile utilizzando il flag `--noconsole`. Questo parametro è fondamentale poiché impedisce l'allocazione di una finestra di terminale fissa all'avvio, garantendo l'esecuzione fluida in background:
 ``` bash
pyinstaller --onefile --noconsole f_pii_scanner.py
 ``` 
3. Preleva il file binario `f_pii_scanner` generato all'interno della directory `dist/` e centralizzalo nel percorso locale di destinazione stabilito per la distribuzione aziendale (es. `/opt/utils/`).

---

## 3. Automazione del Task tramite Bash e Cron

L'automazione dello scanner su Fedora viene gestita inserendo una riga di pianificazione permanente all'interno del Crontab locale dell'utente standard, sfruttando lo script di automazione fornito.

### Procedura di installazione:

1. Apri il terminale di Fedora.
2. Assicurati che lo script di installazione `setup_cron_pii.sh` disponga dei corretti permessi di esecuzione:
 ``` bash
chmod +x setup_cron_pii.sh
 ``` 
3. Esegui lo script direttamente dal tuo utente standard (non richiede l'uso di `sudo` o privilegi di root, poiché ogni utente Linux ha diritto a gestire il proprio crontab isolato):
 ``` bash
./setup_cron_pii.sh
 ``` 

### Specifiche tecniche dell'automazione installata:
* **Privilegio Minimo:** Lo scanner agisce esclusivamente nel contesto dell'utente non privilegiato che ha avviato il setup. Analizza esclusivamente le partizioni locali, i supporti rimovibili e le directory home a cui l'utente possiede nativamente i permessi di lettura, impedendo qualsiasi violazione di sicurezza o accesso a file protetti di root.
* **Frequenza Temporale:** Modificando la variabile `OGNI_QUANTI_GIORNI` all'interno dello script di setup (es. `7`), il sistema calcolerà la sintassi Cron standard `0 9 */7 * *`. Questa istruisce il demone `crond` a svegliare il processo ogni 7 days alle ore 09:00 del mattino.
* **Interattività Grafica Linux:** Quando viene lanciato da Cron, il binario `f_pii_scanner` si appoggia alla chiamata di sistema `xdg-open` per gestire il doppio clic interattivo sulla tabella dei risultati, integrandosi nativamente con il file manager predefinito dell'ambiente desktop in uso su Fedora (Nautilus per GNOME o Dolphin per KDE).
