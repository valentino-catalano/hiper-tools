# API Health Monitor - Lightweight Endpoint Auditor 📊🌐

Un'applicazione di monitoraggio asincrona, ultra-leggera e cross-platform (Windows & Linux Fedora), progettata per supervisionare lo stato di operatività (*health status*) di URL aziendali, servizi Cloud ed endpoint API critici.

L'obiettivo dell'applicazione è garantire la **Business Continuity** attraverso un monitoraggio costante e immediato, orchestrato in background tramite thread isolati e configurabile in totale autonomia dal Service Desk tramite un semplice file di testo.

---

## 💼 Impatto Aziendale e ROI (Per Budget Owner & Decision Maker)

Il downtime di un servizio Cloud o di un'applicazione interna si traduce istantaneamente in perdite economiche, calo della produttività e danno d'immagine. Spesso le aziende si affidano a suite di monitoraggio enterprise che richiedono mesi di configurazione, server dedicati e costose licenze ricorrenti.

*   **Efficacia Funzionale:** Identifica istantaneamente la non disponibilità di un servizio (Response Code diverso da 200 o anomalie di rete) prima che l'interruzione impatti l'operatività degli utenti finali o dei clienti.
*   **Impatto Temporale:** Abbattimento dei tempi di reazione (*Mean Time to Resolution - MTTR*). L'applicazione aggiorna lo stato visivo in frazioni di secondo, permettendo al personale tecnico di intervenire in modo mirato e tempestivo.
*   **Valore Commerciale:** Soluzione chirurgica a **costo infrastrutturale zero**. Non richiede server centralizzati, database o setup complessi. È un'utility stand-alone agile che massimizza l'efficienza dei team senza pesare sulle linee di budget IT.

---

## 🛠️ Trasparenza Tecnica e Architettura (Per Stakeholder Tecnici & Sistemisti)

L'applicazione è sviluppata seguendo logiche di programmazione asincrona avanzata per garantire la massima accuratezza dei dati senza compromettere le performance dell'endpoint su cui è eseguita.

 ``` mermaid
graph TD
    Start([Avvio App]) --> ReadCSV[Lettura dinamica list.csv]
    ReadCSV --> ThreadSpawn[Generazione Thread Dedicati per ogni URL]
    
    subgraph Thread Pool Asincrono
        Thread1[Thread API 1 - Loop ogni X min]
        Thread2[Thread API 2 - Loop ogni Y min]
    end
    
    ThreadSpawn --> Thread1 & Thread2
    Thread1 & Thread2 --> HTTPReq[Richiesta HTTP GET con Timeout 10s]
    
    HTTPReq -- Status 200 --> UI_OK[Segnale Thread-Safe: ONLINE]
    HTTPReq -- Status != 200 / Timeout / DNS Err --> UI_ERR[Segnale Thread-Safe: OFFLINE]
    
    UI_OK --> GUI[Interfaccia Grafica Tkinter - Refresh 500ms]
    UI_ERR --> GUI
 ``` 

*   **Architettura Multi-Threading Isolata:** Ogni URL specificato nel file di configurazione viene assegnato a un thread worker indipendente in background. Questo approccio previene i colli di bottiglia: se un'API aziendale è estremamente lenta o in timeout, il monitoraggio degli altri servizi e la reattività della GUI continuano senza alcun ritardo.
*   **Algoritmo Frozen Path Resolution:** Per ovviare ai limiti di scompattamento temporaneo di PyInstaller (`/tmp` su Linux e `AppData\Local\Temp` su Windows), l'applicazione implementa un controllo dinamico sull'eseguibile. Questo garantisce che il file `list.csv` venga cercato e letto sempre nella cartella di lavoro corrente dell'utente.
*   **UI Engine Reattivo e Cross-Platform:** Sviluppata in Tkinter con un layout scuro moderno ad alto contrasto. L'effetto lampeggiante degli alert rossi è gestito tramite la pianificazione dei cicli nativi `.after()` della GUI (ogni 500ms), eliminando il sovraccarico della CPU ed evitando l'uso di librerie grafiche terze non standard.

---

## 📋 Coordinamento Operativo e Service Desk (Per Project Manager & Responsabili IT)

Lo strumento è pensato per integrarsi perfettamente nei flussi di lavoro giornalieri del **Service Desk (SD)** e dei team di monitoraggio, semplificando la governance delle infrastrutture IT delicate.

*   **Autonomia Operativa del Service Desk:** Non è necessaria alcuna competenza di programmazione per aggiornare la lista dei servizi. Se viene distribuita una nuova API o se cambiano i parametri di un servizio cloud, l'operatore dell'SD deve semplicemente modificare il file `list.csv` con Excel, LibreOffice o un blocco note.
*   **Flessibilità di Monitoraggio:** Grazie al supporto per i minuti frazionari (es. `0.2` per 12 secondi), il team può configurare controlli ultra-rapidi per applicativi core e critici, mantenendo intervalli più rilassati (es. `10` o `30` minuti) per servizi secondari.
*   **Immediatezza Visiva per Controllo Costante:** Pensata per essere lasciata aperta su un secondo monitor o su una dashboard di reparto. La distinzione visiva netta (Spunta Verde fissa vs Simbolo Rosso Lampeggiante con l'indicazione esatta dell'errore es. `404`, `500`, `ERR`) elimina la fatica cognitiva e permette un controllo visivo istantaneo a colpo d'occhio.

---

## 📂 Struttura del File di Configurazione (`list.csv`)

Il file deve essere posizionato nella stessa cartella dell'eseguibile e strutturato con codifica **UTF-8** e separatore **punto e virgola (`;`)**:

```csv
nome;urlbase;parametri;minuti
Google Search;[https://www.google.com](https://www.google.com);;1
GitHub API;[https://api.github.com](https://api.github.com);;0.5
CRM Aziendale;[https://crm.azienda.internal](https://crm.azienda.internal);/v1/status;2
Gateway Errato Test;[https://httpbin.org](https://httpbin.org);/status/500;0.5
```
---
*Garantire la visibilità dello stato di rete significa anticipare il problema e proteggere la produttività aziendale.*
---
