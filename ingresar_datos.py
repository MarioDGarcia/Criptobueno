# ingresar_datos.py
"""
Frame: ingresar datos del estudiante
Se usa dentro del App principal (mismo root).
"""
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

class IngresarDatosFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.build_ui()

    def build_ui(self):
        ttk.Label(self, text="Formulario de Registro", font=("Helvetica", 20, "bold")).pack(pady=10)
        form = ttk.Frame(self)
        form.pack(pady=10)

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.nombre_entry = ttk.Entry(form, width=40)
        self.nombre_entry.grid(row=0, column=1, pady=5)

        ttk.Label(form, text="Apellido:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.apellido_entry = ttk.Entry(form, width=40)
        self.apellido_entry.grid(row=1, column=1, pady=5)

        ttk.Label(form, text="ID Estudiante UDG:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.id_entry = ttk.Entry(form, width=40)
        self.id_entry.grid(row=2, column=1, pady=5)

        controls = ttk.Frame(self)
        controls.pack(pady=12)
        ttk.Button(controls, text="Continuar", bootstyle="info", command=self.on_submit).pack(side="left", padx=6)
        ttk.Button(controls, text="Regresar", command=lambda: self.controller.show_frame("Inicio")).pack(side="left", padx=6)

        # bind Enter
        for e in (self.nombre_entry, self.apellido_entry, self.id_entry):
            e.bind("<Return>", lambda ev: self.on_submit())

    def on_submit(self):
        nombre = self.nombre_entry.get().strip()
        apellido = self.apellido_entry.get().strip()
        id_est = self.id_entry.get().strip()

        if not nombre or not apellido or not id_est:
            messagebox.showwarning("Formulario", "Todos los campos son obligatorios.")
            return
        if not id_est.isdigit():
            messagebox.showwarning("Formulario", "ID debe ser numérico.")
            return

        # revisar votos duplicados en la blockchain (backend compartido)
        already = False
        for b in self.controller.bc.chain:
            try:
                payload = json.loads(b.data)
                if isinstance(payload, dict) and payload.get("estudiante_id") == id_est:
                    already = True
                    break
            except Exception:
                continue

        if already:
            messagebox.showerror("Voto duplicado", "Este ID ya emitió un voto.")
            return

        # guardar datos compartidos
        self.controller.shared_data["nombre"] = nombre
        self.controller.shared_data["apellido"] = apellido
        self.controller.shared_data["id_estudiante"] = id_est

        # limpiar selección previa
        self.controller.shared_data["selection"] = ""
        # navegar a candidatos
        self.controller.show_frame("Candidatos")

# Nota: import json arriba (lo colocamos aquí)
import json
