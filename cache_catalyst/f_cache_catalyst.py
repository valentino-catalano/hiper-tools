import os
import shutil
import glob
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

# --- FUNZIONI DI PULIZIA ---

def is_process_running(process_name):
    """Verifica se un browser è aperto su Linux usando il comando 'pgrep'."""
    try:
        # pgrep restituisce 0 se il processo esiste
        subprocess.check_output(["pgrep", "-x", process_name])
        return True
    except subprocess.CalledProcessError:
        return False

def clean_linux_temp():
    """Svuota i file temporanei della sessione utente in /tmp."""
    # Nota: Non cancelliamo l'intera /tmp per evitare instabilità,
    # ma solo i file creati dall'utente corrente.
    current_user = os.getlogin()
    count_deleted = 0
    count_errors = 0

    # Cerchiamo file in /tmp appartenenti all'utente o generici sacrificabili
    for item in glob.glob('/tmp/*'):
        try:
            # Verifichiamo se il file è di proprietà dell'utente corrente
            if os.stat(item).st_uid == os.getuid():
                if os.path.isfile(item) or os.path.islink(item):
                    os.unlink(item)
                elif os.path.isdir(item):
                    shutil.rmtree(item)
                count_deleted += 1
        except Exception:
            count_errors += 1
            continue

    messagebox.showinfo("Successo", f"Pulizia /tmp completata!\nFile rimossi: {count_deleted}\nFile protetti/in uso: {count_errors}")

def clean_chrome_cache():
    """Cancella la cache di Google Chrome su Linux (Flatpak o nativo)."""
    if is_process_running("chrome") or is_process_running("google-chrome"):
        messagebox.showwarning("Attenzione", "Google Chrome è aperto. Chiudilo per procedere.")
        return

    home = os.path.expanduser("~")
    # Percorsi tipici su Linux (Nativo RPM e versione Flatpak)
    chrome_paths = [
        os.path.join(home, ".cache/google-chrome/Default/Cache"),
        os.path.join(home, ".var/app/com.google.Chrome/cache/google-chrome/Default/Cache")
    ]

    deleted_any = False
    for path in chrome_paths:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                os.makedirs(path)
                deleted_any = True
            except Exception as e:
                print(f"Errore Chrome: {e}")

    if deleted_any:
        messagebox.showinfo("Chrome", "Cache di Google Chrome svuotata!")
    else:
        messagebox.showinfo("Chrome", "Nessuna cache di Chrome trovata.")

def clean_firefox_cache():
    """Cancella la cache di Firefox su Fedora (Nativo o Flatpak) senza toccare le password."""
    if is_process_running("firefox"):
        messagebox.showwarning("Attenzione", "Firefox è attualmente aperto. Chiudilo per procedere.")
        return

    home = os.path.expanduser("~")
    # I profili di Firefox hanno nomi casuali, quindi usiamo il glob (*) per trovarli
    firefox_paths = [
        os.path.join(home, ".cache/mozilla/firefox/*"),
        os.path.join(home, ".var/app/org.mozilla.firefox/.cache/mozilla/firefox/*")
    ]

    deleted_any = False
    for path_pattern in firefox_paths:
        for path in glob.glob(path_pattern):
            # Evitiamo di cancellare la cartella dei profili stessa, entriamo dentro le cache
            cache_folder = os.path.join(path, "cache2")
            if os.path.exists(cache_folder):
                try:
                    shutil.rmtree(cache_folder)
                    os.makedirs(cache_folder)
                    deleted_any = True
                except Exception as e:
                    print(f"Errore Firefox: {e}")

    if deleted_any:
        messagebox.showinfo("Firefox", "Cache di Firefox svuotata con successo!")
    else:
        messagebox.showinfo("Firefox", "Nessuna cache di Firefox trovata.")


# --- INTERFACCIA GRAFICA (GUI) ---

def create_gui():
    root = tk.Tk()
    root.title("Cache & Temp Catalyst (Linux)")
    root.geometry("400x280")
    root.resizable(False, False)

    style = ttk.Style()
    style.configure("TLabel", font=("Helvetica", 10))
    style.configure("Title.TLabel", font=("Helvetica", 12, "bold"))
    style.configure("Action.TButton", font=("Helvetica", 10), padding=6)

    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="Cache & Temp Catalyst - Fedora", style="Title.TLabel").pack(pady=(0, 5))
    ttk.Label(main_frame, text="Utility di pulizia rapida utente", font=("Helvetica", 9, "italic"), foreground="gray").pack(pady=(0, 20))

    # Pulsanti
    ttk.Button(main_frame, text="Svuota File Temporanei (/tmp utente)", style="Action.TButton", command=clean_linux_temp).pack(fill=tk.X, pady=5)
    ttk.Button(main_frame, text="Svuota Cache Google Chrome", style="Action.TButton", command=clean_chrome_cache).pack(fill=tk.X, pady=5)
    ttk.Button(main_frame, text="Svuota Cache Mozilla Firefox", style="Action.TButton", command=clean_firefox_cache).pack(fill=tk.X, pady=5)

    ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=15)
    ttk.Label(main_frame, text="Nota: Chiudi i browser prima di avviare la pulizia.", font=("Helvetica", 8), foreground="red").pack()

    root.mainloop()

if __name__ == "__main__":
    create_gui()
