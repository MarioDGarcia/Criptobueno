"""
Frame: Ingresar datos del estudiante
Estilo moderno con tarjeta central y validación de Blockchain.
"""
import customtkinter as ctk
from tkinter import messagebox
import json

class IngresarDatosFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        # 1. Fondo general (El mismo gris de la ventana principal)
        super().__init__(parent, fg_color="#F0F2F5")
        self.controller = controller
        
        # Colores CUTonalá
        self.colors = {
            "verde": "#519530",
            "azul": "#178DB4",
            "blanco": "#FFFFFF",
            "texto": "#2B2B2B",
            "fondo_card": "#FFFFFF",
            "fondo_app": "#F0F2F5"
        }

        self.build_ui()

    def build_ui(self):
        # Configuración del Grid para centrar todo
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # --- TARJETA CENTRAL (Blanca) ---
        # bg_color = #F0F2F5 (Para que las esquinas de la tarjeta se fundan con el fondo gris)
        self.card = ctk.CTkFrame(
            self,
            fg_color=self.colors["fondo_card"],
            bg_color=self.colors["fondo_app"], 
            corner_radius=20,
            border_width=1,
            border_color="#D1D1D1"
        )
        self.card.grid(row=0, column=0, ipadx=40, ipady=40)

        # Título
        ctk.CTkLabel(
            self.card,
            text="Registro de Estudiante",
            font=ctk.CTkFont(family="Arial", size=24, weight="bold"),
            text_color=self.colors["verde"]
        ).pack(pady=(20, 25))

        # --- CAMPOS DE TEXTO ---
        # Helper para crear inputs consistentes
        def crear_input(parent, titulo, placeholder):
            ctk.CTkLabel(
                parent, 
                text=titulo, 
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#555555",
                anchor="w"
            ).pack(fill="x", pady=(10, 2), padx=(30, 0))
            
            entry = ctk.CTkEntry(
                parent,
                width=300,
                height=40,
                placeholder_text=placeholder,
                corner_radius=10,
                border_color="#CCCCCC",
                fg_color="#FAFAFA", # Un gris casi blanco para el input
                bg_color="white",   # IMPORTANTE: Para que las esquinas del input se vean bien en la tarjeta
                text_color="black"
            )
            entry.pack(pady=(0, 5))
            return entry

        self.nombre_entry = crear_input(self.card, "Nombre(s)", "Ej. Juan Pablo")
        self.apellido_entry = crear_input(self.card, "Apellido(s)", "Ej. Pérez García")
        self.id_entry = crear_input(self.card, "Código de Estudiante (ID)", "Ej. 215489632")

        # Separador visual
        ctk.CTkFrame(self.card, height=2, fg_color="#F0F0F0").pack(fill="x", pady=20)

        # --- BOTONES ---
        
        # Botón Continuar (Verde)
        self.btn_submit = ctk.CTkButton(
            self.card,
            text="CONTINUAR",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=300,
            height=45,
            corner_radius=22,
            fg_color=self.colors["verde"],
            hover_color="#3d7024",
            bg_color="white", # Se funde con la tarjeta blanca
            command=self.on_submit
        )
        self.btn_submit.pack(pady=(0, 10))

        # Botón Regresar (Outline Azul)
        self.btn_back = ctk.CTkButton(
            self.card,
            text="Regresar al inicio",
            font=ctk.CTkFont(size=12),
            width=300,
            height=35,
            fg_color="transparent",
            text_color=self.colors["azul"],
            hover_color="#F0F8FF",
            bg_color="white", # Se funde con la tarjeta blanca
            command=lambda: self.controller.show_frame("Inicio")
        )
        self.btn_back.pack()

        # Bind Enter Key (Para que al dar Enter funcione igual que hacer clic)
        self.nombre_entry.bind("<Return>", lambda ev: self.on_submit())
        self.apellido_entry.bind("<Return>", lambda ev: self.on_submit())
        self.id_entry.bind("<Return>", lambda ev: self.on_submit())

    def on_submit(self):
        nombre = self.nombre_entry.get().strip()
        apellido = self.apellido_entry.get().strip()
        id_est = self.id_entry.get().strip()

        # Validaciones básicas
        if not nombre or not apellido or not id_est:
            messagebox.showwarning("Datos Incompletos", "Por favor llena todos los campos.")
            return
        
        if not id_est.isdigit():
            messagebox.showwarning("Formato Incorrecto", "El código de estudiante debe contener solo números.")
            return

        # --- Lógica Blockchain (Buscar duplicados) ---
        already = False
        # Accedemos a la blockchain a través del controlador principal
        if hasattr(self.controller, 'bc') and self.controller.bc:
            for b in self.controller.bc.chain:
                try:
                    payload = json.loads(b.data)
                    # Verificamos si es un diccionario y si coincide el ID
                    if isinstance(payload, dict) and payload.get("estudiante_id") == id_est:
                        already = True
                        break
                except Exception:
                    continue

        if already:
            messagebox.showerror("Acceso Denegado", f"El código {id_est} ya ha registrado un voto en la Blockchain.")
            return

        # Guardar datos en memoria compartida
        self.controller.shared_data["nombre"] = nombre
        self.controller.shared_data["apellido"] = apellido
        self.controller.shared_data["id_estudiante"] = id_est
        
        # Limpiar selección previa por seguridad
        self.controller.shared_data["selection"] = ""

        # Navegar a la pantalla de candidatos
        print(f"Login exitoso: {nombre} {apellido} ({id_est})") # Log para consola
        self.controller.show_frame("Candidatos")