# Printer & Spooler Catalyst 🖨️⚡

Un'utility aziendale cross-platform (Windows & Linux) leggera e autonoma, progettata per risolvere istantaneamente i blocchi della coda di stampa **senza richiedere privilegi di amministratore (No Admin/Root)**. 

Disponibile sia come script sorgente Python (`w_printer_catalyst.py`, `f_printer_catalyst_linux.py`) sia come eseguibili binari precompilati pronti all'uso, (portable) senza necessità di installare dipendenze sui PC degli utenti.

---

## 💼 Business Case & ROI (Per Budget Owner & Decision Maker)

Il blocco dello spooler di stampa è storicamente una delle cause principali di ticket a bassa priorità ma ad alto impatto sui tempi di fermo macchina.

*   **Efficacia Funzionale:** L'applicazione decentralizza la risoluzione del problema. L'utente finale è in grado di sbloccare la propria postazione in modalità "one-click" in totale autonomia.
*   **Impatto Temporale:** Abbattimento del tempo medio di risoluzione (MTTR) da ~15 minuti (tempo di attesa e intervento del supporto) a **meno di 10 secondi**.
*   **Ritorno Commerciale (ROI):** Riduzione del carico di ticket di Livello 1 per il reparto IT. Meno interruzioni per il Service Desk significano più tempo da dedicare a progetti ad alto valore tecnologico, ottimizzando i costi operativi aziendali.

---

## 🛠️ Architettura e Sicurezza (Per Stakeholder Tecnici)

L'applicazione è concepita secondo il principio del *privilegio minimo* ed evita l'approccio distruttivo dei vecchi script Batch/Bash.

                [ Avvio Utente Standard ]
                           │
        ┌──────────────────┴──────────────────┐
        ▼                                     ▼
 [ OS: Windows ]                       [ OS: Linux ]
        │                                     │
(PowerShell Core)                        (Bash/CUPS)
        │                                     │
Flush Coda Personale                  Flush Coda Personale
Kill Processo splwow64                Resume Job ID Utente

---

*   **Sicurezza Compliance:** L'applicazione **non richiede elevazione di privilegi (UAC/Sudo)**. Opera esclusivamente all'interno del contesto di sicurezza dell'utente loggato, azzerando i rischi di vulnerabilità locali.
*   **Isolamento dell'Utente:** Invece di riavviare il servizio globale (operazione che richiederebbe permessi Admin e interromperebbe le stampe di altri utenti sullo stesso PC), l'app effettua un *Targeted Flush* (pulizia mirata) isolando e cancellando solo i pacchetti corrotti dell'utente corrente.
*   **Zero Dipendenze:** Gli eseguibili inclusi includono l'interprete runtime. Possono essere distribuiti tramite share di rete aziendali o System Center (SCCM/Intune) senza installare Python sulle macchine target.

---

## 🖥️ Funzionalità e Troubleshooting (Per Service Desk & Gestionali)

L'interfaccia si presenta con un layout minimale a 3 pulsanti, pensato per guidare l'utente o il tecnico durante il primo contatto telefonico.

### 1. Svuota la mia Coda di Stampa (Flush)
Invia un comando forzato al sistema di stampa per ripulire i documenti in coda inviati dall'utente corrente. Risolve i casi in cui un file di grandi dimensioni o corrotto (es. PDF non formattato) blocca l'invio dei successivi lavori.

### 2. Sblocca e Riavvia stampe in corso
*   **Su Windows:** Interrompe forzatamente il processo orfano `splwow64.exe` (spesso responsabile del congelamento dell'interfaccia di stampa) e invia un comando di `Resume` sui job in stato di errore.
*   **Su Linux:** Interroga l'ID dei job utente tramite CUPS e forza lo stato in `resume`, sbloccando le stampanti condivise rimaste in attesa.

### 3. Genera report errori per Assistenza
Se il problema persiste, questo tasto automatizza la raccolta log liberando il Service Desk da lunghe procedure di diagnostica:
*   Estrae i codici errore nativi (da *Event Viewer PrintService* su Windows e da *CUPS/lpc* su Linux).
*   Genera un file pulito direttamente sul Desktop dell'utente (`Report_Errori_Stampa.txt`) e lo apre a schermo.
*   L'utente deve solo allegare il file al ticket o leggerlo all'operatore, riducendo i tempi di diagnosi del problema del 90%.

---

## 📂 Struttura del Repository

*   `/w_printer_catalyst.py` - Codice sorgente Python (ottimizzato per Windows / PowerShell).
*   `/w_printer_catalyst.exe` - Eseguibile autonomo Windows (compilato a 64-bit).
*   `/f_printer_catalyst_linux.py` - Codice sorgente Python (ottimizzato per Fedora / Bash / CUPS).
*   `/f_printer_catalyst_linux` - Eseguibile nativo binario per Linux Fedora.

---
*Sviluppato con focus sull'efficienza operativa e la sicurezza degli endpoint aziendali.*

---
