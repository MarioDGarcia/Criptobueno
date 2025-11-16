# principal.py
"""
Ventana principal — inicia la aplicación y registra las pantallas (frames).
Ejecuta este archivo para iniciar la app.
"""
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk

from blockchain import Blockchain
from ingresar_datos import IngresarDatosFrame
from candidatos import CandidatosFrame
from admin import AdminFrame

class App(tb.Window):
    def __init__(self):
        super().__init__(title="Elecciones FEU - Mini-Blockchain", themename="cosmo")
        self.geometry("800x500")
        self.minsize(800, 500)
        self.maxsize(800, 500)
        self.resizable=False
        

        # backend compartido
        self.bc = Blockchain()

        # datos compartidos entre pantallas
        self.shared_data = {
            "nombre": "",
            "apellido": "",
            "id_estudiante": "",
            "selection": "",
            # opcional: images urls/listas si quieres persistirlas
        }

        # container para frames
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # registro de frames
        self.frames = {}
        for F in (InicioFrame := self._make_inicio_frame, IngresarDatosFrame, CandidatosFrame, AdminFrame):
            pass  # placeholder for readability

        # crear instancias de frames
        self.frames["Inicio"] = self._make_inicio_frame(container, self)
        self.frames["IngresarDatos"] = IngresarDatosFrame(container, self)
        self.frames["Candidatos"] = CandidatosFrame(container, self)
        self.frames["Admin"] = AdminFrame(container, self)

        # colocar frames en grid (stack)
        for f in self.frames.values():
            f.grid(row=0, column=0, sticky="nsew")

        self.show_frame("Inicio")

    def _make_inicio_frame(self, parent, controller):
        frame = tk.Frame(parent)
        frame.columnconfigure(0, weight=1)
        title = tb.Label(frame, text="ELECCIONES FEU - UDG", font=("Helvetica", 30, "bold"))
        title.pack(pady=30)
        subtitle = tb.Label(frame, text="Sistema de votación con auditoría (mini-blockchain)", font=("Helvetica", 12))
        subtitle.pack(pady=(0, 30))
        btn_votar = tb.Button(frame, text="VOTAR", bootstyle=(SUCCESS, "outline"), command=lambda: controller.show_frame("IngresarDatos"))
        btn_votar.pack(pady=20, ipadx=80, ipady=30)
        btn_admin = tb.Button(frame, text="Panel administrativo", command=lambda: controller.show_frame("Admin"))
        btn_admin.pack(side="bottom", pady=20)
        return frame

    def show_frame(self, name: str):
        frame = self.frames.get(name)
        if frame:
            frame.tkraise()

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
