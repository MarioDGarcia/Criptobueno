# admin.py
"""
Frame: panel administrativo integrado.
Permite ver chain.json, verificar integridad, corromper bloques y exportar.
"""
import tkinter as tk
from ttkbootstrap import ttk
from tkinter import messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from datetime import datetime

class AdminFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.build_ui()

    def build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x")
        ttk.Label(header, text="Panel Administrativo — Mini-Blockchain", font=("Helvetica", 14, "bold")).pack(side="left")
        ttk.Button(header, text="Regresar", command=lambda: self.controller.show_frame("Inicio")).pack(side="right")

        btns = ttk.Frame(self)
        btns.pack(fill="x", pady=10)
        ttk.Button(btns, text="Mostrar Cadena", command=self.show_chain).pack(side="left", padx=6)
        ttk.Button(btns, text="Verificar integridad", command=self.verify_chain).pack(side="left", padx=6)
        ttk.Button(btns, text="Corromper bloque", command=self.ask_corrupt).pack(side="left", padx=6)
        ttk.Button(btns, text="Exportar JSON", command=self.export_chain).pack(side="left", padx=6)

        self.log = ScrolledText(self, height=20)
        self.log.pack(fill="both", expand=True, pady=8)
        self.log_insert("Panel administrativo listo.")

    def log_insert(self, text):
        ts = datetime.utcnow().isoformat()
        self.log.insert("end", f"{ts} - {text}\n")
        self.log.see("end")

    def show_chain(self):
        try:
            with open(self.controller.bc.filename, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            content = "No se pudo leer el archivo."
        win = tk.Toplevel(self)
        win.title("Visualizar cadena")
        txt = ScrolledText(win)
        txt.pack(fill="both", expand=True)
        txt.insert("end", content)

    def verify_chain(self):
        valido, errores = self.controller.bc.verificar_cadena()
        if valido:
            messagebox.showinfo("Verificación", "La cadena es válida.")
            self.log_insert("Verificación: OK — cadena válida.")
        else:
            messagebox.showerror("Verificación", "Se detectaron alteraciones. Revisa el log.")
            for e in errores:
                self.log_insert("ERROR: " + e)

    def ask_corrupt(self):
        top = tk.Toplevel(self)
        top.title("Corromper bloque")
        ttk.Label(top, text="ID bloque:").pack(pady=4)
        entry_id = ttk.Entry(top)
        entry_id.pack(pady=4)
        ttk.Label(top, text="Nuevo 'data':").pack(pady=4)
        txt = ScrolledText(top, height=6, width=60)
        txt.pack(pady=6)
        def do_corrupt():
            try:
                bid = int(entry_id.get().strip())
            except ValueError:
                messagebox.showerror("ID inválido","ID debe ser entero.")
                return
            nuevo = txt.get("1.0", "end").strip()
            if not nuevo:
                messagebox.showwarning("Vacío","Introduce nuevo contenido.")
                return
            ok = self.controller.bc.corromper_bloque(bid, nuevo)
            if ok:
                messagebox.showinfo("Corrompido", f"Bloque {bid} corrompido.")
                self.log_insert(f"Bloque {bid} corrompido.")
                top.destroy()
            else:
                messagebox.showerror("Error", f"No existe bloque {bid}.")
        ttk.Button(top, text="Corromper", command=do_corrupt).pack(pady=6)

    def export_chain(self):
        out = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")])
        if not out:
            return
        self.controller.bc.export_json(out)
        messagebox.showinfo("Exportado", f"Cadena exportada a {out}")
        self.log_insert(f"Exportado a {out}")

