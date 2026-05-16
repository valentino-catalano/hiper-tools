import os
import re
import sys
import time
import zipfile
import string
import ctypes
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# =====================================================================
# CONFIGURAZIONE AZIENDALE (Facilmente personalizzabile)
# =====================================================================

# 1. PATH DI SALVATAGGIO LOG CENTRALIZZATO
# Se impostato su un percorso valido (es. una cartella di rete o locale nascosta),
# l'app salverà lì un report CSV. Se lasciata vuota o non valida, il log è disattivato.
# Esempio: r"\\ServerAziendale\LogPII$" oppure r"C:\ProgramData\AziendaLogs"
LOG_EXPORT_PATH = ""

# 2. WHITELIST / EXCLUSIONS
# Cartelle e sotto-cartelle di sistema da saltare TASSATIVAMENTE per preservare CPU e falsi positivi
DIR_EXCLUSIONS = {
    "windows", "program files", "program files (x86)", "programdata",
    "appdata", "microsoft", "system volume information", "$recycle.bin",
    "node_modules", ".git", ".vscode", "vendor", "cache", "temp"
}

# 3. ESTENSIONI COMPATIBILI
TEXT_EXTENSIONS = {".txt", ".csv", ".md", ".json", ".xml", ".ini", ".log"}
OFFICE_EXTENSIONS = {".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp"}
ALL_EXTENSIONS = TEXT_EXTENSIONS.union(OFFICE_EXTENSIONS)

# 4. THROTTLING (GENTLE CPU/IO MODE)
# Micro-pausa (in secondi) dopo l'analisi di ogni singolo file per non saturare l'I/O del disco
THROTTLING_DELAY = 0.01

# =====================================================================
# REGEX PATTERNS (Internazionali + Codice Fiscale Italiano)
# =====================================================================

REGEX_PATTERNS = {
    "Codice Fiscale Italiano": re.compile(r"\b[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]\b", re.IGNORECASE),
    "IBAN (Internazionale)": re.compile(r"\b[A-Z]{2}[0-9]{2}[A-Z0-9]{12,30}\b", re.IGNORECASE),
    "Carta di Credito (Generica)": re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|6(?:011|5[0-9][0-9])[0-9]{12}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|(?:2131|1800|35\d{3})\d{11})\b")
}

# =====================================================================
# MOTORI DI SCANSIONE TEXT RECOVERY
# =====================================================================

def scan_text_file(file_path):
    """Scansiona file di testo nativi."""
    try:
        with open(file_path, "r", errors="ignore", encoding="utf-8") as f:
            content = f.read()
            for pii_type, regex in REGEX_PATTERNS.items():
                if regex.search(content):
                    return True, pii_type
    except Exception:
        pass
    return False, None

def scan_office_file(file_path):
    """Scansiona i file di Office XML OpenDOS (docx, xlsx, pptx) estraendo il testo dai file ZIP strutturali."""
    try:
        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path) as z:
                # Leggiamo i file XML interni dove risiede il testo/dati
                for xml_file in z.namelist():
                    if "word/document.xml" in xml_file or "xl/sharedStrings.xml" in xml_file or "ppt/slides/" in xml_file or "content.xml" in xml_file:
                        content = z.read(xml_file).decode("utf-8", errors="ignore")
                        for pii_type, regex in REGEX_PATTERNS.items():
                            if regex.search(content):
                                return True, pii_type
    except Exception:
        pass
    return False, None

# =====================================================================
# CORE ENGINE: DICTIONARY SCANNER
# =====================================================================

def get_local_drives():
    """Rileva automaticamente tutte le lettere dei dischi locali disponibili e pronti su Windows."""
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drive_path = f"{letter}:\\"
            # Verifica che sia un disco fisso o rimovibile pronto (evita i lettori CD vuoti che bloccano lo script)
            if ctypes.windll.kernel32.GetDriveTypeW(drive_path) in [3, 2]:
                drives.append(drive_path)
        bitmask >>= 1
    return drives

def start_pii_scan():
    """Esegue la scansione di tutti i dischi accessibili saltando la whitelist."""
    detected_files = []
    drives = get_local_drives()

    for drive in drives:
        for root, dirs, files in os.walk(drive, topdown=True):
            # Filtro Whitelist dinamico: modifica l'array 'dirs' sul posto per fare in modo che os.walk salti a pié pari le cartelle protette
            dirs[:] = [d for d in dirs if d.lower() not in DIR_EXCLUSIONS and not d.startswith('.')]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in ALL_EXTENSIONS:
                    file_path = os.path.join(root, file)

                    # Applica il Throttling richiesto per non pesare sui dischi
                    if THROTTLING_DELAY > 0:
                        time.sleep(THROTTLING_DELAY)

                    # Sceglie il motore di scansione corretto
                    is_positive = False
                    pii_found = None

                    if ext in TEXT_EXTENSIONS:
                        is_positive, pii_found = scan_text_file(file_path)
                    elif ext in OFFICE_EXTENSIONS:
                        is_positive, pii_found = scan_office_file(file_path)

                    if is_positive:
                        detected_files.append((file, root, pii_found, file_path))

    return detected_files

def export_silent_log(results):
    """Esporta un file CSV log centralizzato se la configurazione è attiva."""
    if LOG_EXPORT_PATH and os.path.exists(LOG_EXPORT_PATH):
        try:
            username = os.getlogin()
            computername = os.environ.get('COMPUTERNAME', 'Unknown')
            log_filename = f"PII_Report_{computername}_{username}.csv"
            full_log_path = os.path.join(LOG_EXPORT_PATH, log_filename)

            with open(full_log_path, "w", encoding="utf-8") as f:
                f.write("DataScansione;Computer;Utente;NomeFile;Cartella;TipoDato\n")
                for file, folder, pii_type, _ in results:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')};{computername};{username};{file};{folder};{pii_type}\n")
        except Exception:
            pass # Lavora in background in modo silente, non deve mostrare errori all'utente

# =====================================================================
# INTERFACCIA GRAFICA (GUI RISULTATI)
# =====================================================================

class PIIResultApp:
    def __init__(self, results):
        self.results = results
        self.root = tk.Tk()
        self.root.title("Privacy Audit - Controllo PII Endpoint")
        self.root.geometry("750x400")

        # Intercetta la chiusura della X della finestra per chiudere pulito il processo
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)

        # Layout
        style = ttk.Style()
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"))

        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Rilevamento File Sensibili (Privacy by Design)", style="Header.TLabel", foreground="red").pack(anchor="w", pady=(0,5))
        ttk.Label(main_frame, text="I seguenti file locali contengono pattern sensibili (CF, IBAN o Carte). Fai doppio clic su una riga per aprire la cartella ed eliminare o cifrare il file.", font=("Segoe UI", 9, "italic")).pack(anchor="w", pady=(0,15))

        # Tabella Risultati (Treeview)
        cols = ("File", "Tipo di Dato Rilevato", "Percorso Cartella")
        self.tree = ttk.Treeview(main_frame, columns=cols, show="headings")

        self.tree.heading("File", text="Nome File")
        self.tree.heading("Tipo di Dato Rilevato", text="Tipo di Dato Rilevato")
        self.tree.heading("Percorso Cartella", text="Percorso Cartella")

        self.tree.column("File", width=180, anchor="w")
        self.tree.column("Tipo di Dato Rilevato", width=150, anchor="center")
        self.tree.column("Percorso Cartella", width=380, anchor="w")

        # Scrollbar
        scroll = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Popolamento Tabella
        for file, folder, pii_type, full_path in self.results:
            self.tree.insert("", tk.END, values=(file, pii_type, folder), tags=(full_path,))

        # Binding del doppio clic
        self.tree.bind("<Double-1>", self.on_double_click)

        self.root.mainloop()

    def on_double_click(self, event):
        """Apre Explorer selezionando direttamente il file al doppio clic del mouse."""
        item = self.tree.selection()[0]
        full_path = self.tree.item(item, "tags")[0]
        # Comando explorer sicuro di Windows che evidenzia il file specifico
        os.system(f'explorer /select,"{full_path}"')

# =====================================================================
# EXECUTION ENTRY POINT (AUTOMAZIONE ZERO-CLICK)
# =====================================================================

if __name__ == "__main__":
    # 1. Esegue la scansione silente all'avvio
    results_found = start_pii_scan()

    # 2. Se configurato, esporta il log centralizzato invisibile per l'IT Security
    if results_found:
        export_silent_log(results_found)

        # 3. Sveglia l'utente mostrando i risultati solo se ci sono positivi
        PIIResultApp(results_found)
    else:
        # Se è tutto pulito, l'app si chiude istantaneamente a 0 click senza farsi notare
        sys.exit(0)
