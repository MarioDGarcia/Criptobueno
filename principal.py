import customtkinter as ctk

from blockchain import Blockchain
from ingresar_datos import IngresarDatosFrame
from candidatos import CandidatosFrame
from admin import AdminFrame

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. Configuración de la Ventana Principal
        self.title("Elecciones FEU | CUTonalá")
        self.geometry("800x550")
        self.resizable(False, False)
        
        # 2. Paleta de Colores (Institucional)
        self.colors = {
            "verde": "#519530",       
            "verde_hover": "#3d7024", 
            "azul": "#178DB4",        
            "blanco": "#FFFFFF",
            "fondo": "#F0F2F5",       
            "texto": "#2B2B2B"
        }

        # 3. Datos y Backend
        self.bc = Blockchain()
        self.shared_data = {
            "nombre": "", "apellido": "", "id_estudiante": "", "selection": ""
        }

        # 4. Configuración del Grid Principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 5. Sistema de Navegación Simple
        self.frames_classes = {
            "Inicio": InicioFrame,
            "IngresarDatos": IngresarDatosFrame,
            "Candidatos": CandidatosFrame,
            "Admin": AdminFrame
        }
        
        self.current_frame = None
        self.show_frame("Inicio")

    def show_frame(self, frame_name):
        """Destruye el frame actual y construye el nuevo. 
        Esto es más limpio visualmente que apilar frames."""
        
        if self.current_frame is not None:
            self.current_frame.destroy()

        frame_class = self.frames_classes.get(frame_name)
        if frame_class:
            # Creamos la nueva vista y la pasamos a self
            self.current_frame = frame_class(self, controller=self)
            self.current_frame.grid(row=0, column=0, sticky="nsew")


class InicioFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=controller.colors["fondo"])
        self.controller = controller
        self.colors = controller.colors

        # Layout
        self.columnconfigure(0, weight=1)

        self.header = ctk.CTkFrame(
            self, 
            fg_color=self.colors["verde"], 
            height=160, 
            corner_radius=0
        )
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.pack_propagate(False) # Fija el tamaño del header

        # Título Principal
        ctk.CTkLabel(
            self.header,
            text="ELECCIONES",
            font=ctk.CTkFont(family="Arial", size=50, weight="bold"),
            text_color=self.colors["blanco"],
            fg_color=self.colors["verde"] 
        ).pack(pady=(30, 0))

        # Subtítulo
        ctk.CTkLabel(
            self.header,
            text="F E U  •  C U T O N A L Á",
            font=ctk.CTkFont(family="Arial", size=16, weight="bold"),
            text_color="#E8F5E9",
            fg_color=self.colors["verde"]
        ).pack(pady=(5, 0))

        
        self.card = ctk.CTkFrame(
            self,
            fg_color=self.colors["blanco"],
            bg_color=self.colors["fondo"], 
            corner_radius=20,
            border_width=1,
            border_color="#D1D1D1"
        )
        self.card.grid(row=2, column=0, pady=(40, 30), ipadx=40, ipady=20)

        ctk.CTkLabel(
            self.card,
            text="🔐",
            font=("Arial", 30),
            text_color=self.colors["texto"]
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            self.card,
            text="Sistema de Votación Auditado",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["texto"]
        ).pack()

        ctk.CTkLabel(
            self.card,
            text="Blockchain rudimentario",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["azul"]
        ).pack(pady=(5, 0))

        # --- BOTÓN DE ACCIÓN (VOTAR) ---
        self.btn_votar = ctk.CTkButton(
            self,
            text="VOTAR AHORA",
            font=ctk.CTkFont(family="Arial", size=22, weight="bold"),
            width=300,
            height=70,
            corner_radius=35,
            fg_color=self.colors["verde"],
            hover_color=self.colors["verde_hover"],
            # LA CLAVE DEL ÉXITO: bg_color debe ser igual al fondo de la ventana
            bg_color=self.colors["fondo"], 
            command=lambda: controller.show_frame("IngresarDatos")
        )
        self.btn_votar.grid(row=3, column=0, pady=10)

        # --- FOOTER (ADMIN) ---
        self.btn_admin = ctk.CTkButton(
            self,
            text="Panel Administrativo",
            font=ctk.CTkFont(size=12),
            width=150,
            height=30,
            fg_color="transparent",
            text_color=self.colors["azul"],
            hover_color="#E1E8EB",
            border_width=1,
            border_color=self.colors["azul"],
            bg_color=self.colors["fondo"],
            command=lambda: controller.show_frame("Admin")
        )
        self.btn_admin.grid(row=4, column=0, pady=(40, 20))


if __name__ == "__main__":
    app = App()
    app.mainloop()