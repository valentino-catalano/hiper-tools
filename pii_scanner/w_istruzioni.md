# ⚙️ Guida di Configurazione e Distribuzione Windows: PII Scanner

Questo documento fornisce le istruzioni tecniche per personalizzare lo script Python, compilarlo in un binario autonomo ed eseguirne la distribuzione automatizzata sui sistemi operativi Microsoft Windows tramite PowerShell e l'Utilità di Pianificazione.

---

## 1. Personalizzazione dei Parametri Aziendali (Python)

Le politiche di scansione e i comportamenti di logging possono essere configurati modificando le variabili presenti nel blocco iniziale del file sorgente `pii_scanner_windows.py`:

### 📂 Percorso di Rete per Log Centralizzato
Per raccogliere i report di conformità in modo centralizzato, valorizza la variabile `LOG_EXPORT_PATH` con un percorso UNC valido (es. una cartella condivisa o una share di rete nascosta):
```python
# Sostituire con il percorso desiderato (es. una share di rete)
LOG_EXPORT_PATH = r"\\ServerAziendale\LogPII$"
```

Se la variabile viene lasciata vuota (""), la funzione di export silente rimarrà disattivata.

🛡️ Whitelist delle Cartelle (Esclusioni)
Per preservare le prestazioni del disco ed evitare il controllo di file protetti o log di sistema che genererebbero falsi positivi, compila l'array delle esclusioni inserendo i nomi delle directory rigorosamente in minuscolo:

```python
DIR_EXCLUSIONS = {
    "windows", "program files", "program files (x86)", "programdata",
    "appdata", "microsoft", "system volume information", "$recycle.bin",
    "node_modules", ".git", ".vscode", "vendor", "cache", "temp"
}
```

⏱️ Throttling (Frenatura I/O)
La variabile THROTTLING_DELAY introduce una micro-pausa (espressa in frazioni di secondo) dopo l'analisi di ogni singolo file. Questo evita la saturazione del disco durante la ricerca dei pattern.

Valore consigliato: 0.01 (10 millisecondi di ritardo per file).

---

## 2. Compilazione in File Eseguibile (.exe)
Per distribuire l'applicazione sugli endpoint aziendali senza dover installare l'interprete Python o le relative dipendenze, lo script deve essere convertito in un file binario standalone.

Installa il modulo di compilazione tramite prompt dei comandi:

```DOS
pip install pyinstaller
```

2. Genera l'eseguibile utilizzando il flag `--noconsole`. Questo parametro è fondamentale poiché impedisce l'allocazione e la visualizzazione della finestra nera del prompt dei comandi all'avvio, garantendo l'esecuzione in background:
   ```cmd
   pyinstaller --onefile --noconsole pii_scanner_windows.py`
   
3. Preleva il file pii_scanner_windows.exe generato all'interno della directory dist/ e centralizzalo nel percorso locale di destinazione stabilito per la rete aziendale (es. C:\utils\).

---

## 3. Automazione del Task tramite PowerShell
L'automazione dello scanner viene gestita tramite la creazione di un'attività pianificata di Windows, configurata per ripetersi ciclicamente a intervalli di giorni prestabiliti.

Procedura di installazione:

1. Apri il menu Start, digita PowerShell, fai clic destro sull'icona e seleziona Esegui come amministratore.

2. Abilita l'esecuzione degli script nella sessione corrente per consentire il provisioning del task:
```POWERSHELL
Set-ExecutionPolicy RemoteSigned -Scope Process -Force
```
3. Naviga nella directory in cui risiede lo script di automazione (es. `Setup_Task_PII.ps1`) ed eseguilo per registrare l'attività nel sistema:
   ```powershell
   .\Setup_Task_PII.ps1`

---

Specifiche tecniche del Task installato:

**Privilegio Minimo**: L'attività viene impostata con il ruolo Limited per il gruppo BUILTIN\Users. Lo scanner viene eseguito nel contesto di sicurezza dell'utente standard loggato in quel momento, senza richiedere token amministrativi (No UAC) e garantendo l'accesso alle sole risorse a cui l'utente è effettivamente autorizzato.

**Interattività Grafica**: Il task utilizza il parametro di rete Interactive. Questo permette al processo invisibile in background di agganciarsi alla sessione grafica corrente e mostrare la maschera Tkinter sullo schermo solo ed esclusivamente in caso di riscontro positivo (rilevamento PII).

**Frequenza Temporale**: L'intervallo specificato nella variabile $OgniQuantiGiorni dello script PowerShell viene tradotto in una pianificazione nativa permanente codificata in formato standard ISO 8601 (es. P7D per una ricorrenza fissa ogni 7 giorni).

---
