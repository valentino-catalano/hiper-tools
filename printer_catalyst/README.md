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
