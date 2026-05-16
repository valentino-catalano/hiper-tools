#!/bin/bash

# =====================================================================
# CONFIGURAZIONE STRUMENTO (Modificabile dall'amministratore IT)
# =====================================================================

# Ogni quanti giorni deve girare lo script (es: 1 = ogni giorno, 7 = ogni settimana)
OGNI_QUANTI_GIORNI=7

# Path dell'eseguibile Linux su Fedora (Default impostato come richiesto)
PATH_ESEGUIBILE="/opt/utils/pii_scanner_fedora"


# =====================================================================
# MOTORE DI INSTALLAZIONE AUTOMATICA CRONJOB
# =====================================================================

echo "====================================================="
echo "   Privacy Audit - Configurazione Automazione Linux  "
echo "====================================================="

# 1. Controllo di sicurezza: verifica se il file eseguibile esiste davvero
if [ ! -f "$PATH_ESEGUIBILE" ]; then
    echo "⚠️  ATTENZIONE: L'eseguibile non è stato trovato in: $PATH_ESEGUIBILE"
    echo "Assicurati di aver inserito il percorso corretto e ricomincia."
    exit 1
fi

# 2. Controllo permessi di esecuzione (+x) sul file target
if [ ! -x "$PATH_ESEGUIBILE" ]; then
    echo "🔧 Ottimizzazione: Assegnazione dei permessi di esecuzione all'utility..."
    chmod +x "$PATH_ESEGUIBILE"
fi

# 3. Generazione della stringa oraria per il Cronjob
# Nota: Su Linux, per impostare una frequenza a giorni saltati si usa la sintassi "*/X"
# Il job viene impostato per partire la mattina alle ore 09:00 dell'utente
CRON_SCHEDULING="0 9 */$OGNI_QUANTI_GIORNI * *"
NUOVO_JOB="$CRON_SCHEDULING $PATH_ESEGUIBILE"

echo "➡️  Pianificazione calcolata: Esecuzione ogni $OGNI_QUANTI_GIORNI giorni alle 09:00 AM."

# 4. Lettura del Crontab attuale ed eliminazione di vecchi job identici (Evita ridondanze)
# Esporta il crontab attuale escludendo la riga che punta al nostro eseguibile
CONTEGGI_ATTUALI=$(crontab -l 2>/dev/null | grep -v "$PATH_ESEGUIBILE")

# 5. Scrittura fisica nel sottosistema Crontab di Fedora
# Uniamo il vecchio crontab pulito alla nuova riga di pianificazione
(echo "$CONTEGGI_ATTUALI"; echo "$NUOVO_JOB") | crontab -

# 6. Verifica dell'esito dell'operazione
if [ $? -eq 0 ]; then
    echo "✅ Successo! Il Cronjob è stato installato correttamente per l'utente loggato."
    echo "-----------------------------------------------------"
    echo "Ecco la tua riga attiva nel Crontab:"
    crontab -l | grep "$PATH_ESEGUIBILE"
    echo "====================================================="
else
    echo "❌ Errore critico durante la scrittura nel Crontab di sistema."
    exit 1
fi
