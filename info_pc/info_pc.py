import os
import socket
import getpass
import tkinter as tk
from tkinter import ttk

def get_pc_info():
    # Recupera l'username dell'utente loggato
    username = getpass.getuser()

    # Recupera l'hostname del PC
    hostname = socket.gethostname()

    # Recupera l'indirizzo IP locale
    try:
        # Questo metodo è il più affidabile per trovare l'IP attivo in LAN
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
    except Exception:
        ip_address = "Non connesso / Non trovato"

    return username, hostname, ip_address

def create_gui():
    username, hostname, ip_address = get_pc_info()

    # Configurazione finestra principale
    root = tk.Tk()
    root.title("Info Sistema Aziendale")
    root.geometry("350x180")
    root.resizable(False, False)

    # Stile minimale
    style = ttk.Style()
    style.configure("TLabel", font=("Segoe UI", 10))
    style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"))

    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)

    # Titolo
    ttk.Label(frame, text="Informazioni Postazione", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="w")

    # Username
    ttk.Label(frame, text="Utente Loggato:", style="TLabel").grid(row=1, column=0, sticky="w", pady=5)
    ttk.Label(frame, text=username, font=("Segoe UI", 10, "bold")).grid(row=1, column=1, sticky="w", pady=5, padx=10)

    # Hostname
    ttk.Label(frame, text="Nome PC (Hostname):", style="TLabel").grid(row=2, column=0, sticky="w", pady=5)
    ttk.Label(frame, text=hostname, font=("Segoe UI", 10, "bold")).grid(row=2, column=1, sticky="w", pady=5, padx=10)

    # IP
    ttk.Label(frame, text="Indirizzo IP:", style="TLabel").grid(row=3, column=0, sticky="w", pady=5)
    ttk.Label(frame, text=ip_address, font=("Segoe UI", 10, "bold"), foreground="blue").grid(row=3, column=1, sticky="w", pady=5, padx=10)

    # Avvia l'interfaccia
    root.mainloop()

if __name__ == "__main__":
    create_gui()
