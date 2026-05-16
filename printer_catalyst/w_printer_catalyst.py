import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

def run_powershell_cmd(cmd):
    """Esegue un comando PowerShell in modalità nascosta e restituisce il risultato."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True, text=True, check=True, creationflags=0x08000000  # Nasconde la finestra nera
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

# --- FUNZIONI DEI TASTI ---

def reset_user_spooler():
    """Tasto 1: Effettua il flush completo della coda di stampa dell'utente corrente."""
    # Comando PS che seleziona tutte le stampe dell'utente loggato e le cancella forzatamente
    ps_cmd = "Get-PrintJob -PrinterName * | Where-Object {$_.UserName -eq $env:USERNAME} | Remove-PrintJob"

    success, _ = run_powershell_cmd(ps_cmd)

    if success:
        messagebox.showinfo("Reset Spooler", "Svuotamento forzato della tua coda di stampa inviato con successo!\nLe tue stampe bloccate sono state rimosse.")
    else:
        messagebox.showerror("Errore", "Si è verificato un errore durante il flush della coda.")

def restart_and_resume_prints():
    """Tasto 2: Killa i processi di stampa rimasti appesi e riavvia le stampe in errore/pausa."""
    # 1. Chiude il bridge di stampa di Windows che spesso si blocca
    try:
        subprocess.run(["taskkill", "/F", "/IM", "splwow64.exe", "/T"], creationflags=0x08000000, capture_output=True)
    except Exception:
        pass

    # 2. Riprende (Resume) tutti i lavori di stampa dell'utente che sono in stato di blocco
    ps_cmd = "Get-PrintJob -PrinterName * | Where-Object {$_.UserName -eq $env:USERNAME -and ($_.JobState -like '*Error*' -or $_.JobState -like '*Paused*')} | Resume-PrintJob"

    success, _ = run_powershell_cmd(ps_cmd)

    if success:
        messagebox.showinfo("Ripristino Stampe", "Processi di stampa isolati riavviati.\nInviato segnale di 'Riprendi' (Resume) per i tuoi documenti in coda.")
    else:
        messagebox.showerror("Errore", "Impossibile riavviare i documenti in coda.")

def generate_error_report():
    """Tasto 3: Estrae gli errori di stampa dal registro eventi e crea un file sul Desktop."""
    desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    report_file = os.path.join(desktop_path, 'Report_Errori_Stampa.txt')

    # Query PowerShell per estrarre gli ultimi 15 eventi di errore dal PrintService di Windows
    ps_cmd = (
        "Get-WinEvent -LogName 'Microsoft-Windows-PrintService/Admin' -ErrorAction SilentlyContinue | "
        "Where-Object {$_.LevelDisplayName -eq 'Errore' -or $_.LevelDisplayName -eq 'Error'} | "
        "Select-Object -First 15 | "
        "Format-List TimeCreated, Message | Out-String"
    )

    success, output = run_powershell_cmd(ps_cmd)

    if success and output.strip():
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=== REPORT DIAGNOSTICA STAMPA AZIENDALE ===\n\n")
            f.write(output)

        messagebox.showinfo("Report Generato", f"Report salvato sul Desktop:\n{report_file}\n\nOra verrà aperto automaticamente.")
        # Apre il file di testo con il Blocco Note
        os.system(f'start notepad.exe "{report_file}"')
    else:
        # Se non ci sono errori registrati di recente
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=== REPORT DIAGNOSTICA STAMPA AZIENDALE ===\n\nNessun errore recente rilevato nel registro eventi di stampa.")
        os.system(f'start notepad.exe "{report_file}"')

# --- INTERFACCIA GRAFICA (GUI) ---

def create_gui():
    root = tk.Tk()
    root.title("Printer & Spooler Resetter")
    root.geometry("420x260")
    root.resizable(False, False)

    style = ttk.Style()
    style.configure("TLabel", font=("Segoe UI", 10))
    style.configure("Title.TLabel", font=("Segoe UI", 12, "bold"))
    style.configure("Action.TButton", font=("Segoe UI", 10), padding=8)

    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Titolo
    ttk.Label(main_frame, text="Printer & Spooler Catalyst", style="Title.TLabel").pack(pady=(0, 5))
    ttk.Label(main_frame, text="Risoluzione problemi di stampa (No Admin)", font=("Segoe UI", 9, "italic"), foreground="gray").pack(pady=(0, 15))

    # Pulsanti principali
    btn_reset = ttk.Button(main_frame, text="1. Svuota la mia Coda di Stampa (Flush)", style="Action.TButton", command=reset_user_spooler)
    btn_reset.pack(fill=tk.X, pady=5)

    btn_resume = ttk.Button(main_frame, text="2. Sblocca e Riavvia stampe in corso", style="Action.TButton", command=restart_and_resume_prints)
    btn_resume.pack(fill=tk.X, pady=5)

    btn_report = ttk.Button(main_frame, text="3. Genera report errori per Assistenza", style="Action.TButton", command=generate_error_report)
    btn_report.pack(fill=tk.X, pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
