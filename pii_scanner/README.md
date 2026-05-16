# PII Scanner - Privacy Endpoint Auditor 🛡️🔍

Un'applicazione DLP (Data Loss Prevention) aziendale, ultra-leggera e cross-platform (Windows & Linux Fedora), progettata per automatizzare la ricerca di dati sensibili non strutturati (*Personally Identifiable Information*). 

L'obiettivo dell'applicazione è far rispettare il principio della **Privacy by Design & by Default** a livello di endpoint, scansionando in background i dischi locali alla ricerca di pattern critici (Codici Fiscali, IBAN, Carte di Credito) all'interno di file di testo e documenti Office, attivando una maschera interattiva solo in caso di non conformità.

---

## 💼 Impatto Aziendale e ROI (Per Budget Owner & Decision Maker)

La frammentazione dei dati sensibili sui computer dei dipendenti (es. report scaricati e dimenticati nella cartella "Download", file Excel temporanei con elenchi clienti) rappresenta il rischio invisibile più elevato per la sicurezza aziendale e l'esposizione a sanzioni.

*   **Efficacia Funzionale:** Consente di implementare un monitoraggio costante e preventivo della flotta aziendale. L'applicazione rileva le anomalie prima che si trasformino in una violazione (Data Breach).
*   **Impatto Temporale:** Abbattimento totale dei tempi di gestione. L'operazione è automatizzata al 100%: lo script viene orchestrato dai sistemi operativi a "zero-click", senza richiedere l'intervento dell'utente o del team IT, se non in caso di effettivo riscontro positivo.
*   **Valore Commerciale:** Protezione del brand e azzeramento dei costi derivanti da sanzioni. Rispetto ai software DLP di livello enterprise — spesso invasivi, costosi, pesanti sulla CPU e complessi da licenziare — questa utility offre una soluzione chirurgica, mirata, a costo infrastrutturale zero e immediata da distribuire.

---

## ⚖️ Sicurezza e Compliance (Per DPO & Addetti alla Compliance / Risorse Umane)

L'utility si configura come lo strumento perfetto per supportare sia l'organizzazione che il dipendente, promuovendo una cultura aziendale basata sulla responsabilità condivisa (*Accountability*).

*   **Supporto al Dipendente:** L'interfaccia interattiva non ha intenti punitivi o di controllo occulto delle attività. Al contrario, funge da assistente proattivo alla privacy: avvisa il dipendente della presenza di dati sensibili dimenticati, permettendogli di rimediare all'istante ed evitando sanzioni disciplinari legate alla cattiva gestione dei dati.
*   **Garanzia per l'Azienda (DPO):** Fornisce la prova tangibile alle autorità di controllo (es. Garante Privacy) che l'azienda adotta misure tecniche idonee ed efficaci per proteggere i dati e minimizzare i rischi di memorizzazione incontrollata, come esplicitamente richiesto dall'Articolo 32 del GDPR.
*   **Monitoraggio Attivo Centralizzato:** Attraverso la funzione di logging silente (configurabile su share protette di rete), l'IT Security e il DPO possono disporre di una telemetria chiara dello stato di conformità complessivo della flotta aziendale, tracciando i progressi di bonifica nel tempo.

---

## 🛠️ Trasparenza Tecnica e Sicurezza (Per Stakeholder Tecnici)

L'applicazione è progettata seguendo rigidi criteri ingegneristici per garantire la massima trasparenza, la stabilità dell'endpoint e la totale assenza di dipendenze esterne pesanti.

 ``` mermaid
graph TD
    Start([Avvio headless da Task/Cron]) --> Scan[Scansione Dischi Locali]
    Scan --> Filter{Filtro Whitelist Cartelle}
    Filter -- Sì --> Skip[Salto Cartella di Sistema/Log]
    Filter -- No --> Engine{Motore di Analisi Estensioni}
    
    Engine -- .txt/.csv/.json/.md --> RegexT[Regex Engine Nativo]
    Engine -- .docx/.xlsx/.pptx/.ods --> ZipE[Estrazione XML da ZIP Office]
    
    RegexT & ZipE --> Match{Pattern Rilevato?}
    Match -- No --> Exit([Chiusura Silente - Processo Terminato])
    Match -- Sì --> Action[Esporta Log Centralizzato se attivo]
    Action --> GUI[Apertura GUI Interattiva Tkinter]
 ``` 

*   **Analisi dei file Office Zero-Dependency:** Per evitare l'installazione di librerie terze massicce (come openpyxl o python-docx), lo scanner sfrutta l'architettura nativa dei file OpenXML di Office (`.docx`, `.xlsx`, ecc.), che internamente non sono altro che archivi compressi ZIP. Lo script estrae i file XML strutturali e analizza il testo al volo tramite espressioni regolari (Regex) ottimizzate, mantenendo il binario leggero e privo di dipendenze esterne.
*   **Throttling di Sicurezza (CPU/IO Gentle Mode):** Durante la scansione profonda dei file, lo script applica un ritardo calcolato in millisecondi dopo ogni operazione. Questo previene picchi di utilizzo della CPU o saturazioni dell'I/O del disco, permettendo all'utente di lavorare senza percepire rallentamenti sul sistema operativo.
*   **Principio del Privilegio Minimo:** L'eseguibile non richiede i diritti di amministratore (No UAC su Windows, No Sudo su Linux) e opera esclusivamente nel contesto di sicurezza dell'utente loggato. Di conseguenza, scansiona e ha accesso alle sole risorse a cui il dipendente è effettivamente autorizzato ad accedere, azzerando i rischi di escalation dei privilegi.
*   **Integrazione Nativa con il File Manager:** Nel caso in cui vengano rilevate violazioni, la tabella dei risultati permette un troubleshooting immediato. Al doppio clic sulla riga della tabella, l'applicazione invoca le API native del sistema operativo (`explorer.exe /select` su Windows, `xdg-open` su Fedora) per aprire la cartella corretta ed evidenziare in modo mirato il file, facilitandone la rimozione o la cifratura.

---

## 📂 Architettura dei file di installazione

Il repository è strutturato per consentire un provisioning immediato sui due ambienti aziendali supportati:

*   `pii_scanner_windows.py` - Codice sorgente Python ottimizzato per Windows.
*   `Setup_Task_PII.ps1` - Script di configurazione PowerShell per l'Utilità di Pianificazione di Windows.
*   `w_istruzioni.md` - Guida di distribuzione e compilazione dettagliata per ambienti Microsoft.
*   `f_pii_scanner.py` - Codice sorgente Python ottimizzato per Linux Fedora.
*   `setup_cron_pii.sh` - Script Bash per l'installazione automatica nel Crontab locale.
*   `f_istruzioni.md` - Guida di distribuzione e compilazione dettagliata per ambienti Linux Fedora.

---
*Fornire strumenti per proteggere i dati significa proteggere l'azienda e responsabilizzare le persone.*
