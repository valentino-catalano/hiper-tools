# =====================================================================
# CONFIGURAZIONE STRUMENTO (Modificabile dall'amministratore IT)
# =====================================================================

# Ogni quanti giorni deve girare lo script (es: 1 = ogni giorno, 7 = ogni settimana)
$OgniQuantiGiorni = 7

# Path dell'eseguibile Windows (Default impostato come richiesto)
$PathEseguibile = "C:\utils\pii_scanner_windows.exe"

# Nome identificativo dell'attività dentro l'Utilità di Pianificazione
$TaskName = "Azienda_PII_Privacy_Scanner"


# =====================================================================
# MOTORE DI INSTALLAZIONE AUTOMATICA TASK SCHEDULER
# =====================================================================

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "   Privacy Audit - Configurazione Automazione Windows" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan

# 1. Controllo di sicurezza: verifica se il file eseguibile esiste davvero
if (-not (Test-Path -Path $PathEseguibile)) {
    Write-Host "⚠️  ATTENZIONE: L'eseguibile non è stato trovato in: $PathEseguibile" -ForegroundColor Yellow
    Write-Host "Assicurati di aver inserito il percorso corretto e ricomincia." -ForegroundColor Yellow
    Exit
}

# 2. Controllo privilegi amministrativi dello script corrente
$CurrentUser = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $CurrentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "❌ ERRORE: Questo script deve essere eseguito come AMMINISTRATORE." -ForegroundColor Red
    Write-Host "Apri PowerShell come Admin e riprova." -ForegroundColor Red
    Exit
}

# 3. Definizione dell'Azione (Cosa lanciare)
$Action = New-ScheduledTaskAction -Execute $PathEseguibile

# 4. Definizione del Trigger (Quando lanciarlo)
# Definiamo l'avvio al Logon di qualunque utente (AtLogon) e impostiamo la ripetizione a giorni
$Trigger = New-ScheduledTaskTrigger -AtLogon

# 5. Definizione dei settings avanzati e dei Principi di Sicurezza
# "Interactive" permette all'eseguibile di interagire con la sessione grafica dell'utente (mostrare la GUI)
# "Limited" avvia l'app con i privilegi standard dell'utente loggato, senza chiedere UAC, rispettando la Privacy by Design.
$Principal = New-ScheduledTaskPrincipal -GroupId "BUILTIN\Users" -Role Limited

$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 6. Registrazione/Sovrascrittura del Task nel sistema
try {
    # Se esiste già un task con lo stesso nome, viene sovrascritto automaticamente per aggiornare le impostazioni
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force | Out-Null

    # Applichiamo l'intervallo di giorni calcolato modificando i dettagli del trigger post-registrazione
    $RegisteredTask = Get-ScheduledTask -TaskName $TaskName
    $RegisteredTask.Triggers[0].Repetition.Interval = "P$($OgniQuantiGiorni)D" # Formato ISO 8601 (es: P7D = Periodo 7 Giorni)
    $RegisteredTask | Set-ScheduledTask -User "Interactive" | Out-Null

    Write-Host "✅ Successo! L'attività pianificata '$TaskName' è stata installata." -ForegroundColor Green
    Write-Host "-----------------------------------------------------"
    Write-Host "Dettagli Pianificazione:"
    Write-Host "• Target: $PathEseguibile"
    Write-Host "• Frequenza di Trigger: Esecuzione programmata ogni $OgniQuantiGiorni giorni."
    Write-Host "• Modalità visiva: Attiva al Login dell'utente (Zero-Click)."
    Write-Host "=====================================================" -ForegroundColor Cyan
}
catch {
    Write-Host "❌ Errore critico durante la creazione dell'attività pianificata: $_" -ForegroundColor Red
    Exit
}
