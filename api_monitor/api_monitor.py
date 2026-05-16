import os
import sys
import csv
import time
import requests
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# =====================================================================
# CONFIGURAZIONE E COSTANTI
# =====================================================================
CSV_FILENAME = "list.csv"

# Colori per la UI
COLOR_BG = "#1e1e2e"       # Tema scuro moderno
COLOR_CARD = "#252538"
COLOR_TEXT = "#cdd6f4"
COLOR_GREEN = "#a6e3a1"    # Spunta verde
COLOR_RED = "#f38ba8"      # Alert rosso

def get_base_path():
    """Rileva correttamente la cartella dell'eseguibile o dello script sorgente."""
    if getattr(sys, 'frozen', False):
        # Se l'app è compilata con PyInstaller, sys.executable dà il percorso del binario
        return os.path.dirname(sys.executable)
    else:
        # Se l'app è lanciata come script .py normale
        return os.path.dirname(os.path.abspath(__file__))

class APIMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("API Health Monitor")
        self.root.geometry("650x450")
        self.root.configure(bg=COLOR_BG)

        # Dizionario per tracciare lo stato visivo di ogni riga per il lampeggio
        self.tracked_services = {}

        # Inizializzazione Interfaccia
        self.setup_ui()

        # Caricamento dati e avvio loop di monitoraggio
        self.load_and_start_monitors()

        # Avvio del ciclo di lampeggio per i servizi offline
        self.blink_loop()

        # Gestione chiusura pulita
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """Configura l'interfaccia grafica con uno stile moderno e cross-platform."""
        # Header
        header_frame = tk.Frame(self.root, bg=COLOR_BG, padx=20, pady=15)
        header_frame.pack(fill=tk.X)

        lbl_title = tk.Label(header_frame, text="📊 API & Cloud Service Monitor", font=("Segoe UI", 14, "bold"), fg=COLOR_TEXT, bg=COLOR_BG)
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(header_frame, text="Monitoraggio asincrono basato su intervalli personalizzati (list.csv)", font=("Segoe UI", 9, "italic"), fg="#a6adc8", bg=COLOR_BG)
        lbl_sub.pack(anchor="w")

        # Container Principale con Scrollbar
        canvas_container = tk.Frame(self.root, bg=COLOR_BG, padx=20, pady=5)
        canvas_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_container, bg=COLOR_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)

        self.scrollable_frame = tk.Frame(canvas, bg=COLOR_BG)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_and_start_monitors(self):
        """Legge il file CSV e lancia un thread di monitoraggio isolato per ogni URL."""
        csv_path = os.path.join(get_base_path(), CSV_FILENAME)

        if not os.path.exists(csv_path):
            self.create_default_csv(csv_path)
            messagebox.showinfo("Configurazione", f"il file \"{CSV_FILENAME}\" non presente nella cartella dell'app, è stato creato un file di esempio, modificalo e riavvia l'applicazione")
            self.on_closing() # Chiude l'app per permettere la modifica

        try:
            with open(csv_path, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f, delimiter=";")

                for idx, row in enumerate(reader):
                    nome = row.get("nome", "").strip()
                    url_base = row.get("urlbase", "").strip()
                    parametri = row.get("parametri", "").strip()

                    try:
                        minuti = float(row.get("minuti", "5").strip())
                    except ValueError:
                        minuti = 5.0

                    if not url_base:
                        continue

                    full_url = url_base + parametri
                    display_name = nome if nome else full_url

                    self.create_service_row(idx, display_name, full_url)

                    # Avvia il thread dedicato
                    t = threading.Thread(target=self.worker_monitor, args=(idx, url_base, parametri, minuti), daemon=True)
                    t.start()

        except Exception as e:
            messagebox.showerror("Errore di Lettura", f"Impossibile leggere il file {CSV_FILENAME}: {str(e)}")

    def create_service_row(self, service_id, display_name, full_url):
        """Genera i widget grafici per la riga del servizio."""
        row_frame = tk.Frame(self.scrollable_frame, bg=COLOR_CARD, padx=15, pady=10, highlightbackground="#313244", highlightthickness=1)
        row_frame.pack(fill=tk.X, expand=True, pady=5, ipadx=10)

        text_frame = tk.Frame(row_frame, bg=COLOR_CARD)
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        lbl_name = tk.Label(text_frame, text=display_name, font=("Segoe UI", 11, "bold"), fg=COLOR_TEXT, bg=COLOR_CARD, anchor="w")
        lbl_name.pack(fill=tk.X)

        lbl_url = tk.Label(text_frame, text=full_url, font=("Segoe UI", 8), fg="#7f849c", bg=COLOR_CARD, anchor="w")
        lbl_url.pack(fill=tk.X)

        lbl_badge = tk.Label(row_frame, text="⏳ CHECKING", font=("Segoe UI", 10, "bold"), fg="#f9e2af", bg=COLOR_CARD, width=12, anchor="center")
        lbl_badge.pack(side=tk.RIGHT, padx=10)

        self.tracked_services[service_id] = {
            "status": "CHECKING",
            "badge_widget": lbl_badge,
            "code": ""
        }

    def worker_monitor(self, service_id, url_base, parametri, minuti):
        """Ciclo di monitoraggio eseguito in background dal thread proprietario."""
        full_url = url_base + parametri
        if not full_url.startswith(("http://", "https://")):
            full_url = "http://" + full_url

        headers = {"User-Agent": "API Health Monitor Aziendale"}
        interval_seconds = max(1, int(minuti * 60))

        while True:
            try:
                response = requests.get(full_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    self.update_gui_status(service_id, "ONLINE", "200")
                else:
                    self.update_gui_status(service_id, "OFFLINE", str(response.status_code))
            except requests.RequestException:
                self.update_gui_status(service_id, "OFFLINE", "ERR")

            time.sleep(interval_seconds)

    def update_gui_status(self, service_id, status, code):
        """Aggiorna in modo sicuro lo stato del servizio."""
        if service_id in self.tracked_services:
            self.tracked_services[service_id]["status"] = status
            self.tracked_services[service_id]["code"] = code

    def blink_loop(self):
        """Gestisce la reattività grafica e il lampeggio asincrono."""
        blink_visible = int(time.time() * 2) % 2 == 0

        for service_id, info in self.tracked_services.items():
            badge = info["badge_widget"]
            status = info["status"]
            code = info["code"]

            if status == "ONLINE":
                badge.config(text="✓ ONLINE", fg=COLOR_GREEN)
            elif status == "OFFLINE":
                if blink_visible:
                    badge.config(text=f"❌ ({code})", fg=COLOR_RED)
                else:
                    badge.config(text="", fg=COLOR_RED)
            elif status == "CHECKING":
                badge.config(text="⏳ CHECKING", fg="#f9e2af")

        self.root.after(500, self.blink_loop)

    def create_default_csv(self, path):
        """Genera un file di configurazione iniziale valido nella cartella reale."""
        with open(path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["nome", "urlbase", "parametri", "minuti"])
            writer.writerow(["Google Web", "https://www.google.com", "", "1"])
            writer.writerow(["API Errata Test", "https://httpbin.org", "/status/404", "0.5"])

    def on_closing(self):
        """Chiusura pulita dell'applicazione."""
        self.root.destroy()
        os._exit(0)

if __name__ == "__main__":
    main_root = tk.Tk()
    app = APIMonitorApp(main_root)
    main_root.mainloop()

