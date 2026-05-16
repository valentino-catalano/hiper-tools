import os
import shutil
import glob
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

# --- FUNZIONI DI PULIZIA ---

def is_process_running(process_name):
    """Verifica se un browser è aperto per evitare errori di file bloccati."""
    try:
        output = subprocess.check_output(f'tasklist /FI "IMAGENAME eq {process_name}"', shell=True, text=True)
        return process_name.lower() in output.lower()
    except Exception:
        return False

def clean_windows_temp():
    """Pulisce i file temporanei e i log dell'utente loggato (Non richiede Admin)."""
    # Cartella Temp dell'utente (es. C:\Users\Nome\AppData\Local\Temp)
    user_temp = os.environ.get('TEMP')
    count_deleted = 0
    count_errors = 0

    if user_temp and os.path.exists(user_temp):
        # Utilizziamo glob per trovare tutti i file e cartelle
        for item in glob.glob(os.path.join(user_temp, '*')):
            try:
                if os.path.isfile(item) or os.path.islink(item):
                    os.unlink(item)
                elif os.path.isdir(item):
                    shutil.rmtree(item)
                count_deleted += 1
            except Exception:
                # Alcuni file saranno in uso dal sistema operativo stesso, è normale saltarli
                count_errors += 1
                continue

        messagebox.showinfo("Successo", f"Pulizia Temp completata!\nFile eliminati/svuotati: {count_deleted}\nFile occupati dal sistema (saltati): {count_errors}")
    else:
        messagebox.showerror("Errore", "Impossibile accedere alla cartella temporanea di Windows.")

def clean_chrome_cache():
    """Cancella la cache di Chrome senza toccare Login data (Password) e moduli."""
    if is_process_running("chrome.exe"):
        messagebox.showwarning("Attenzione", "Google Chrome è attualmente aperto. Chiudilo prima di procedere alla pulizia.")
        return

    local_appdata = os.environ.get('LOCALAPPDATA')
    # Percorsi tipici della cache di Chrome
    chrome_cache_paths = [
        os.path.join(local_appdata, r"Google\Chrome\User Data\Default\Cache"),
        os.path.join(local_appdata, r"Google\Chrome\User Data\Default\Code Cache"),
        os.path.join(local_appdata, r"Google\Chrome\User Data\Default\GPUCache")
    ]

    deleted_any = False
    for path in chrome_cache_paths:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                os.makedirs(path) # Ricrea la cartella vuota
                deleted_any = True
            except Exception as e:
                print(f"Errore Chrome: {e}")

    if deleted_any:
        messagebox.showinfo("Chrome", "Cache di Google Chrome ripulita con successo!\n(Password e Moduli salvati)")
    else:
        messagebox.showinfo("Chrome", "Nessun file di cache residuo trovato per Chrome.")

def clean_edge_cache():
    """Cancella la cache di Microsoft Edge senza toccare Login data (Password) e moduli."""
    if is_process_running("msedge.exe"):
        messagebox.showwarning("Attenzione", "Microsoft Edge è attualmente aperto. Chiudilo prima di procedere alla pulizia.")
        return

    local_appdata = os.environ.get('LOCALAPPDATA')
    # Percorsi tipici della cache di Edge
    edge_cache_paths = [
        os.path.join(local_appdata, r"Microsoft\Edge\User Data\Default\Cache"),
        os.path.join(local_appdata, r"Microsoft\Edge\User Data\Default\Code Cache"),
        os.path.join(local_appdata, r"Microsoft\Edge\User Data\Default\GPUCache")
    ]

    deleted_any = False
    for path in edge_cache_paths:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                os.makedirs(path) # Ricrea la cartella vuota
                deleted_any = True
            except Exception as e:
                print(f"Errore Edge: {e}")

    if deleted_any:
        messagebox.showinfo("Edge", "Cache di Microsoft Edge ripulita con successo!\n(Password e Moduli salvati)")
    else:
        messagebox.showinfo("Edge", "Nessun file di cache residuo trovato per Edge.")


# --- INTERFACCIA GRAFICA (GUI) ---

def create_gui():
    root = tk.Tk()
    root.title("Clear Cache & Temp Catalyst")
    root.geometry("400x280")
    root.resizable(False, False)

    # Stile
    style = ttk.Style()
    style.configure("TLabel", font=("Segoe UI", 10))
    style.configure("Title.TLabel", font=("Segoe UI", 12, "bold"))
    style.configure("Action.TButton", font=("Segoe UI", 10), padding=6)

    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Titolo dell'App
    ttk.Label(main_frame, text="Cache & Temp Catalyst", style="Title.TLabel").pack(pady=(0, 5))
    ttk.Label(main_frame, text="Utility di pulizia rapida (No privilegi Admin)", font=("Segoe UI", 9, "italic"), foreground="gray").pack(pady=(0, 20))

    # Pulsante Temp Windows
    btn_win = ttk.Button(main_frame, text="Pulisci File Temporanei Windows", style="Action.TButton", command=clean_windows_temp)
    btn_win.pack(fill=tk.X, pady=5)

    # Pulsante Chrome
    btn_chrome = ttk.Button(main_frame, text="Svuota Cache Google Chrome", style="Action.TButton", command=clean_chrome_cache)
    btn_chrome.pack(fill=tk.X, pady=5)

    # Pulsante Edge
    btn_edge = ttk.Button(main_frame, text="Svuota Cache Microsoft Edge", style="Action.TButton", command=clean_edge_cache)
    btn_edge.pack(fill=tk.X, pady=5)

    # Separatore visivo e info di chiusura
    ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=15)
    ttk.Label(main_frame, text="Nota: Chiudi i browser prima di avviare la pulizia.", font=("Segoe UI", 8), foreground="red").pack()

    root.mainloop()

if __name__ == "__main__":
    create_gui()
