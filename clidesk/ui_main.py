# ui_main.py
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Callable, List, Dict, Any


class MainUI:
    def __init__(self, on_run: Callable[..., Any]):
        self.on_run = on_run
        self.root = tk.Tk()
        self.root.title("Licitante - Generador de Paquete (AES-GCM + RSA-OAEP + Ed25519)")

        self.input_files: List[Path] = []
        self.rsa_pub_path: str = ""
        self.ed_priv_path: str = ""
        self.out_dir: str = ""

        frm = tk.Frame(self.root, padx=10, pady=10)
        frm.pack(fill="both", expand=True)

        # --- Datos del licitante ---
        tk.Label(frm, text="Nombre licitante:").grid(row=0, column=0, sticky="e")
        self.bidder_name = tk.Entry(frm, width=42)
        self.bidder_name.grid(row=0, column=1, sticky="we")

        tk.Label(frm, text="Identificador licitante:").grid(row=1, column=0, sticky="e")
        self.bidder_id = tk.Entry(frm, width=42)
        self.bidder_id.grid(row=1, column=1, sticky="we")

        # --- Identificadores de convocatoria ---
        tk.Label(frm, text="Call ID:").grid(row=2, column=0, sticky="e")
        self.call_id_in = tk.Entry(frm, width=42)
        self.call_id_in.grid(row=2, column=1, sticky="we")

        tk.Label(frm, text="Key ID (RSA pública):").grid(row=3, column=0, sticky="e")
        self.key_id_in = tk.Entry(frm, width=42)
        self.key_id_in.grid(row=3, column=1, sticky="we")

        # --- Selección de archivos a cifrar ---
        tk.Button(frm, text="Seleccionar archivos a incluir...", command=self._pick_files)\
            .grid(row=4, column=0, columnspan=2, sticky="we", pady=(8, 2))
        self.files_lbl = tk.Label(frm, text="(0 archivos seleccionados)")
        self.files_lbl.grid(row=5, column=0, columnspan=2, sticky="w")

        # --- Claves ---
        tk.Button(frm, text="Clave RSA pública (.pem)...", command=self._pick_rsa_pub)\
            .grid(row=6, column=0, columnspan=2, sticky="we", pady=(8, 2))
        self.rsa_lbl = tk.Label(frm, text="(no seleccionada)")
        self.rsa_lbl.grid(row=7, column=0, columnspan=2, sticky="w")

        tk.Button(frm, text="Clave Ed25519 privada (.pem)...", command=self._pick_ed_priv)\
            .grid(row=8, column=0, columnspan=2, sticky="we", pady=(8, 2))
        self.ed_lbl = tk.Label(frm, text="(no seleccionada)")
        self.ed_lbl.grid(row=9, column=0, columnspan=2, sticky="w")

        # --- Carpeta de salida ---
        tk.Button(frm, text="Carpeta de salida...", command=self._pick_outdir)\
            .grid(row=10, column=0, columnspan=2, sticky="we", pady=(8, 2))
        self.out_lbl = tk.Label(frm, text="(no seleccionada)")
        self.out_lbl.grid(row=11, column=0, columnspan=2, sticky="w")

        # --- Ejecutar ---
        tk.Button(frm, text="Generar paquete", command=self.run, bg="#2d7", fg="white")\
            .grid(row=12, column=0, columnspan=2, sticky="we", pady=(12, 4))

        # --- Log ---
        self.log_txt = tk.Text(frm, height=12)
        self.log_txt.grid(row=13, column=0, columnspan=2, sticky="nsew", pady=(8, 0))

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(13, weight=1)

    # ---- Helpers selección ----
    def _pick_files(self):
        paths = filedialog.askopenfilenames(title="Selecciona archivos para content.zip")
        if paths:
            self.input_files = [Path(p) for p in paths]
            self.files_lbl.config(text=f"({len(self.input_files)} archivos seleccionados)")

    def _pick_rsa_pub(self):
        p = filedialog.askopenfilename(title="Selecciona RSA pública (.pem)",
                                       filetypes=[("PEM files", "*.pem"), ("All files", "*.*")])
        if p:
            self.rsa_pub_path = p
            self.rsa_lbl.config(text=Path(p).name)

    def _pick_ed_priv(self):
        p = filedialog.askopenfilename(title="Selecciona Ed25519 privada (.pem)",
                                       filetypes=[("PEM files", "*.pem"), ("All files", "*.*")])
        if p:
            self.ed_priv_path = p
            self.ed_lbl.config(text=Path(p).name)

    def _pick_outdir(self):
        d = filedialog.askdirectory(title="Selecciona carpeta de salida")
        if d:
            self.out_dir = d
            self.out_lbl.config(text=d)

    # ---- Log ----
    def logln(self, s: str):
        self.log_txt.insert("end", s + "\n")
        self.log_txt.see("end")
        self.root.update_idletasks()

    def clear_log(self):
        self.log_txt.delete("1.0", "end")

    # ---- Ejecutar ----
    def run(self):
        if not self.input_files:
            messagebox.showerror("Error", "Selecciona al menos un archivo.")
            return
        if not self.rsa_pub_path or not self.ed_priv_path or not self.out_dir:
            messagebox.showerror("Error", "Faltan archivos/paths: RSA pública, Ed25519 privada o carpeta de salida.")
            return
        bidder = {
            "name": self.bidder_name.get().strip(),
            "identifier": self.bidder_id.get().strip(),
        }
        call_id = self.call_id_in.get().strip()
        key_id = self.key_id_in.get().strip()
        if not call_id or not key_id:
            messagebox.showerror("Error", "Completa Call ID y Key ID.")
            return

        self.clear_log()
        try:
            self.on_run(
                input_files=self.input_files,
                rsa_pub_path=self.rsa_pub_path,
                ed_priv_path=self.ed_priv_path,
                out_dir=self.out_dir,
                bidder=bidder,
                call_id=call_id,
                key_id=key_id,
            )
        except Exception as e:
            self.logln(f"❌ Error: {e}")

    def show(self):
        self.root.mainloop()
