"""
Frame: Lista de Candidatos (Votación)
Versión Limpia: Sin datos de estudiante en el header. Solo botón Cancelar.
"""
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import json

# Datos de candidatos 
CANDIDATOS_DATA = [
    {
        "id": "cand_1",
        "nombre": "Paquita la del Barrio",
        "desc": "Propuesta centrada en la mejora tecnológica de las aulas y laboratorios, con enfoque en sostenibilidad ambiental dentro del campus.",
        "img_file": "candidato_1.jpeg"
    },
    {
        "id": "cand_2",
        "nombre": "Vicente Fernández",
        "desc": "Fomento a la cultura, el deporte y la integración de todas las carreras. Más becas y apoyos alimenticios para estudiantes.",
        "img_file": "candidato_2.jpeg"
    },
    {
        "id": "cand_3",
        "nombre": "El Buki",
        "desc": "Auditoría constante de recursos, creación de espacios de descanso y mejora en el sistema de transporte universitario.",
        "img_file": "candidato_3.jpeg"
    }
]

class CandidatosFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#F0F2F5")
        self.controller = controller
        
        self.colors = {
            "verde": "#519530",
            "azul": "#178DB4",
            "blanco": "#FFFFFF",
            "fondo": "#F0F2F5",
            "texto": "#2B2B2B"
        }

        self.seleccion_var = ctk.StringVar(value="")
        self.build_ui()

    def build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0) # Header
        self.rowconfigure(1, weight=1) # Lista Scroll
        self.rowconfigure(2, weight=0) # Footer

        # --- 1. HEADER LIMPIO (Solo botón Cancelar) ---
        header = ctk.CTkFrame(self, fg_color=self.colors["blanco"], corner_radius=0, height=60)
        header.grid(row=0, column=0, sticky="ew")
        header.pack_propagate(False)

        # Botón Cancelar (Alineado a la derecha)
        ctk.CTkButton(
            header,
            text="Cancelar Votación",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#FF5252", 
            hover_color="#D32F2F",
            width=120,
            height=32,
            corner_radius=16, # Redondeado
            command=lambda: self.controller.show_frame("Inicio")
        ).pack(side="right", padx=20)

        # --- 2. LISTA DE CANDIDATOS ---
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent", 
            corner_radius=0
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        for cand in CANDIDATOS_DATA:
            self._crear_tarjeta_candidato(self.scroll_frame, cand)

        # --- 3. FOOTER ---
        footer = ctk.CTkFrame(self, fg_color="transparent", height=80)
        footer.grid(row=2, column=0, sticky="ew", pady=10)
        
        self.btn_votar = ctk.CTkButton(
            footer,
            text="CONFIRMAR Y ENVIAR VOTO",
            font=ctk.CTkFont(size=18, weight="bold"),
            width=300,
            height=55,
            corner_radius=28,
            fg_color=self.colors["verde"],
            hover_color="#3d7024",
            bg_color=self.colors["fondo"],
            command=self.submit_vote
        )
        self.btn_votar.pack()

    def _crear_tarjeta_candidato(self, parent, data):
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["blanco"],
            corner_radius=15,
            border_width=1,
            border_color="#D1D1D1"
        )
        card.pack(fill="x", pady=10, ipady=10)
        
        card.columnconfigure(0, weight=0)
        card.columnconfigure(1, weight=1)
        card.columnconfigure(2, weight=0)

        # Imagen
        img_widget = self._cargar_imagen(data["img_file"])
        ctk.CTkLabel(card, text="", image=img_widget).grid(row=0, column=0, padx=20, pady=10)

        # Texto
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="w", padx=10)

        ctk.CTkLabel(
            info_frame,
            text=data["nombre"],
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=self.colors["texto"],
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_frame,
            text=data["desc"],
            font=ctk.CTkFont(family="Arial", size=13),
            text_color="#555555",
            wraplength=400,
            justify="left",
            anchor="w"
        ).pack(anchor="w", pady=(5,0))

        # Radio Button
        ctk.CTkRadioButton(
            card,
            text="Votar",
            font=ctk.CTkFont(weight="bold"),
            variable=self.seleccion_var,
            value=data["nombre"],
            fg_color=self.colors["azul"],
            hover_color=self.colors["verde"],
            border_color=self.colors["azul"],
            bg_color="white"
        ).grid(row=0, column=2, padx=30)

    def _cargar_imagen(self, filename):
        size = (120, 120)
        try:
            if os.path.exists(filename):
                pil_img = Image.open(filename)
                return ctk.CTkImage(light_image=pil_img, size=size)
            else:
                raise FileNotFoundError
        except Exception:
            placeholder = Image.new("RGB", size, (220, 220, 220))
            return ctk.CTkImage(light_image=placeholder, size=size)

    def submit_vote(self):
        seleccionado = self.seleccion_var.get()
        
        if not seleccionado:
            messagebox.showwarning("Atención", "Por favor selecciona un candidato.")
            return

        confirm = messagebox.askyesno("Confirmar", f"¿Votar por: {seleccionado}?")
        if not confirm:
            return

        # Bloquear botón
        self.btn_votar.configure(state="disabled", text="Procesando...") 
        self.update()

        payload = {
            "estudiante_nombre": self.controller.shared_data.get("nombre"),
            "estudiante_apellido": self.controller.shared_data.get("apellido"),
            "estudiante_id": self.controller.shared_data.get("id_estudiante"),
            "candidato": seleccionado
        }
        
        try:
            payload_json = json.dumps(payload, ensure_ascii=False)
            
            # Registrar bloque (sin acceder a atributos que causen error)
            self.controller.bc.agregar_bloque(payload_json)
            
            messagebox.showinfo("Éxito", "Voto registrado correctamente en la Blockchain.")
            
            # Limpiar y salir
            self.controller.shared_data["nombre"] = ""
            self.controller.shared_data["apellido"] = ""
            self.controller.shared_data["id_estudiante"] = ""
            self.controller.shared_data["selection"] = ""
            self.controller.show_frame("Inicio")
            
        except Exception as e:
            self.btn_votar.configure(state="normal", text="CONFIRMAR Y ENVIAR VOTO")
            messagebox.showerror("Error", f"Fallo al registrar: {e}")