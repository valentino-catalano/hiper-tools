import os
import re
import sys
import time
import zipfile
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# =====================================================================
# CONFIGURAZIONE AZIENDALE (Facilmente personalizzabile)
# =====================================================================

# 1. PATH DI SALVATAGGIO LOG CENTRALIZZATO (Adattato per Linux)
# Se impostato su un percorso valido (es. un mount di rete o cartella condivisa),
# l'app salverà un report CSV. Es: "/mnt/server_aziendale/logs"
LOG_EXPORT_PATH = ""

# 2. WHITELIST / EXCLUSIONS (Specifiche per Linux)
# Cartelle da saltare per preservare CPU ed evitare file di sistema/virtuali
DIR_EXCLUSIONS = {
    "usr", "var", "proc", "sys", "dev", "run", "boot", "lib", "lib64",
    "snap", "flatpak", "node_modules", ".git", ".vscode", "vendor", "cache"
}

# 3. ESTENSIONI COMPATIBILI
TEXT_EXTENSIONS = {".txt", ".csv", ".md", ".json", ".xml", ".ini", ".log"}
OFFICE_EXTENSIONS = {".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp"}
ALL_EXTENSIONS = TEXT_EXTENSIONS.union(OFFICE_EXTENSIONS)

# 4. THROTTLING (GENTLE CPU/IO MODE)
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
    try:
        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path) as z:
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
# CORE ENGINE: LINUX DIRECTORY SCANNER
# =====================================================================

def get_scan_targets():
    """Definisce i punti di partenza logici per la scansione su Linux Fedora."""
    targets = []
    # 1. La home dell'utente corrente (dove risiede il 99% dei file personali)
    targets.append(os.path.expanduser('~'))
    # 2. La cartella dei file temporanei globali
    if os.path.exists("/tmp"):
        targets.append("/tmp")
    # 3. Cartelle di supporti rimovibili o dischi secondari montati dal sistema
    if os.path.exists(f"/run/media/{os.getlogin()}"):
        targets.append(f"/run/media/{os.getlogin()}")
    return targets

def start_pii_scan_fedora():
    detected_files = []
    targets = get_scan_targets()

    for target in targets:
        for root, dirs, files in os.walk(target, topdown=True):
            # Whitelist per Linux: esclude le cartelle nascoste e quelle nella DIR_EXCLUSIONS
            dirs[:] = [d for d in dirs if d.lower() not in DIR_EXCLUSIONS and not d.startswith('.')]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in ALL_EXTENSIONS:
                    file_path = os.path.join(root, file)

                    if THROTTLING_DELAY > 0:
                        time.sleep(THROTTLING_DELAY)

                    is_positive = False
                    pii_found = None

                    if ext in TEXT_EXTENSIONS:
                        is_positive, pii_found = scan_text_file(file_path)
                    elif ext in OFFICE_EXTENSIONS:
                        is_positive, pii_found = scan_office_file(file_path)

                    if is_positive:
                        detected_files.append((file, root, pii_found, file_path))

    return detected_files

def export_silent_log_linux(results):
    if LOG_EXPORT_PATH and os.path.exists(LOG_EXPORT_PATH):
        try:
            username = os.getlogin()
            computername = os.uname().nodename
            log_filename = f"PII_Report_{computername}_{username}.csv"
            full_log_path = os.path.join(LOG_EXPORT_PATH, log_filename)

            with open(full_log_path, "w", encoding="utf-8") as f:
                f.write("DataScansione;Computer;Utente;NomeFile;Cartella;TipoDato\n")
                for file, folder, pii_type, _ in results:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')};{computername};{username};{file};{folder};{pii_type}\n")
        except Exception:
            pass

# =====================================================================
# INTERFACCIA GRAFICA (GUI RISULTATI - Linux Native)
# =====================================================================

class PIIResultLinuxApp:
    def __init__(self, results):
        self.results = results
        self.root = tk.Tk()
        self.root.title("Privacy Audit - Controllo PII Fedora")
        self.root.geometry("750x400")

        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)

        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Rilevamento File Sensibili (Privacy by Design)", font=("Helvetica", 11, "bold"), foreground="red").pack(anchor="w", pady=(0,5))
        ttk.Label(main_frame, text="I seguenti file locali contengono dati sensibili. Fai doppio clic su una riga per aprire la cartella del file.", font=("Helvetica", 9, "italic")).pack(anchor="w", pady=(0,15))

        cols = ("File", "Tipo di Dato Rilevato", "Percorso Cartella")
        self.tree = ttk.Treeview(main_frame, columns=cols, show="headings")

        self.tree.heading("File", text="Nome File")
        self.tree.heading("Tipo di Dato Rilevato", text="Tipo di Dato Rilevato")
        self.tree.heading("Percorso Cartella", text="Percorso Cartella")

        self.tree.column("File", width=180, anchor="w")
        self.tree.column("Tipo di Dato Rilevato", width=150, anchor="center")
        self.tree.column("Percorso Cartella", width=380, anchor="w")

        scroll = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        for file, folder, pii_type, full_path in self.results:
            self.tree.insert("", tk.END, values=(file, pii_type, folder), tags=(folder,))

        self.tree.bind("<Double-1>", self.on_double_click)
        self.root.mainloop()

    def on_double_click(self, event):
        """Apre il file manager predefinito di Fedora (Nautilus/Dolphin) puntando alla cartella."""
        item = self.tree.selection()[0]
        folder_path = self.tree.item(item, "tags")[0]
        # In Linux, xdg-open lancia l'applicazione predefinita per gestire i percorsi di cartella
        os.system(f'xdg-open "{folder_path}" &')

# =====================================================================
# EXECUTION ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    results_found = start_pii_scan_fedora()

    if results_found:
        export_silent_log_linux(results_found)
        PIIResultLinuxApp(results_found)
    else:
        sys.exit(0)
