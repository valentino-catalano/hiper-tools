import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

def run_bash_cmd(cmd_list):
    """Esegue un comando Bash in sicurezza e restituisce il risultato."""
    try:
        result = subprocess.run(
            cmd_list,
            capture_output=True, text=True, check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

# --- FUNZIONI DEI TASTI ---

def reset_user_spooler_linux():
    """Tasto 1: Cancella tutti i lavori di stampa dell'utente corrente (Flush)."""
    # Il comando 'lprm -' rimuove tutti i job dell'utente che ha lanciato il comando
    success, _ = run_bash_cmd(["lprm", "-"])

    if success:
        messagebox.showinfo("Reset Spooler", "Svuotamento della tua coda di stampa completato!\nTutti i tuoi documenti bloccati sono stati rimossi da CUPS.")
    else:
        # Se lprm fallisce perché la coda è già vuota, diamo comunque un feedback positivo
        messagebox.showinfo("Reset Spooler", "Coda già vuota o pulizia completata.")

def restart_and_resume_prints_linux():
    """Tasto 2: Tenta di sbloccare e reinviare le stampe trattenute o in errore."""
    # 1. Troviamo gli ID dei lavori dell'utente corrente
    success, output = run_bash_cmd(["lpstat", "-o"])

    if success and output.strip():
        current_user = os.getlogin()
        jobs_resumed = 0

        # Scorriamo le linee per trovare i job dell'utente
        for line in output.splitlines():
            if current_user in line:
                # L'ID del job è solitamente la prima parte (es. "HP-LaserJet-123")
                job_id = line.split()[0]
                # Diamo il comando di release/resume sul singolo job
                run_bash_cmd(["lp", "-i", job_id, "-H", "resume"])
                jobs_resumed += 1

        messagebox.showinfo("Ripristino Stampe", f"Inviato segnale di ripresa (Resume) per {jobs_resumed} tuoi documenti in coda.")
    else:
        messagebox.showinfo("Ripristino Stampe", "Nessun documento attivo trovato nella coda da sbloccare.")

def generate_error_report_linux():
    """Tasto 3: Genera un report sullo stato delle stampanti e della coda sul Desktop."""
    home_path = os.path.expanduser('~')
    desktop_path = os.path.join(home_path, 'Scrivania')

    # Gestione cartella Desktop se in inglese (Desktop vs Scrivania)
    if not os.path.exists(desktop_path):
        desktop_path = os.path.join(home_path, 'Desktop')

    report_file = os.path.join(desktop_path, 'Report_Errori_Stampa.txt')

    # Raccogliamo informazioni diagnostiche per l'assistenza
    _, status_stampanti = run_bash_cmd(["lpc", "status"])
    _, coda_attuale = run_bash_cmd(["lpstat", "-t"])

    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=== REPORT DIAGNOSTICA STAMPA LINUX (CUPS) ===\n\n")
            f.write(f"Utente Corrente: {os.getlogin()}\n")
            f.write("-----------------------------------------\n")
            f.write("STATUS PERIFERICHE:\n")
            f.write(status_stampanti if status_stampanti else "Nessuna info.\n")
            f.write("-----------------------------------------\n")
            f.write("CODA GLOBALE E STATO SERVIZIO:\n")
            f.write(coda_attuale if coda_attuale else "Nessun job presente.\n")

        messagebox.showinfo("Report Generato", f"Report salvato sul Desktop:\n{report_file}\n\nOra verrà aperto automaticamente.")
        # Apre il file di testo con l'editor predefinito di Fedora (Gedit, Gnome Text Editor, ecc.)
        subprocess.run(["xdg-open", report_file])
    except Exception as e:
        messagebox.showerror("Errore", f"Impossibile salvare il report: {e}")

# --- INTERFACCIA GRAFICA (GUI) ---

def create_gui():
    root = tk.Tk()
    root.title("Printer Catalyst (Fedora)")
    root.geometry("420x260")
    root.resizable(False, False)

    style = ttk.Style()
    style.configure("TLabel", font=("Helvetica", 10))
    style.configure("Title.TLabel", font=("Helvetica", 12, "bold"))
    style.configure("Action.TButton", font=("Helvetica", 10), padding=8)

    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Titolo
    ttk.Label(main_frame, text="Printer & Spooler Catalyst - Linux", style="Title.TLabel").pack(pady=(0, 5))
    ttk.Label(main_frame, text="Risoluzione problemi di stampa CUPS (No Root)", font=("Helvetica", 9, "italic"), foreground="gray").pack(pady=(0, 15))

    # Pulsanti
    ttk.Button(main_frame, text="1. Svuota la mia Coda di Stampa (Flush)", style="Action.TButton", command=reset_user_spooler_linux).pack(fill=tk.X, pady=5)
    ttk.Button(main_frame, text="2. Sblocca e Riavvia mie stampe in corso", style="Action.TButton", command=restart_and_resume_prints_linux).pack(fill=tk.X, pady=5)
    ttk.Button(main_frame, text="3. Genera report stampanti per Assistenza", style="Action.TButton", command=generate_error_report_linux).pack(fill=tk.X, pady=5)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
