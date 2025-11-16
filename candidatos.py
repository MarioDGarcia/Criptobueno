# candidatos.py
"""
Frame: lista de candidatos con tarjetas (imagen 30% / texto 70%).
Carga de imágenes (URL o archivo local). Enviar voto -> registra bloque en blockchain.
"""
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import io
import urllib.request
import threading
import json

# candidates placeholders (5)
CANDIDATE_COUNT = 5
CANDIDATES = [
    {"name": f"Candidato {i+1}", "desc": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod."}
    for i in range(CANDIDATE_COUNT)
]

class CandidatosFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # storage for PIL images and PhotoImage
        self.pil_images = [None] * CANDIDATE_COUNT
        self.photo_images = [None] * CANDIDATE_COUNT
        self.image_vars = [tk.StringVar() for _ in range(CANDIDATE_COUNT)]
        self.selection_var = tk.StringVar()
        self.build_ui()

    # ---------- image utils ----------
    def _placeholder(self, w, h):
        img = Image.new("RGB", (w, h), color=(200, 200, 200))
        return img

    def _resize_to_photo(self, pil_img, w, h):
        img = pil_img.copy()
        img.thumbnail((w, h), Image.Resampling.LANCZOS)
        bg = Image.new("RGB", (w, h), (230, 230, 230))
        x = 0
        y = (h - img.height) // 2
        bg.paste(img, (x, y))
        return ImageTk.PhotoImage(bg)

    def _try_load(self, url_or_path):
        if not url_or_path:
            return None
        try:
            if url_or_path.startswith("http://") or url_or_path.startswith("https://"):
                with urllib.request.urlopen(url_or_path, timeout=6) as resp:
                    data = resp.read()
                img = Image.open(io.BytesIO(data)).convert("RGB")
                return img
            else:
                img = Image.open(url_or_path).convert("RGB")
                return img
        except Exception:
            return None

    # ---------- UI ----------
    def build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=6)
        ttk.Label(header, text=f"Votación — {self.controller.shared_data.get('nombre')} {self.controller.shared_data.get('apellido')} (ID: {self.controller.shared_data.get('id_estudiante')})", font=("Helvetica", 12, "bold")).pack(side="left")
        ttk.Button(header, text="Cancelar", command=lambda: self.controller.show_frame("Inicio")).pack(side="right")

        # canvas + scrollbar for cards
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill="both", expand=True, pady=10)

        canvas = tk.Canvas(canvas_frame, borderwidth=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        cards_frame = ttk.Frame(canvas)

        cards_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=cards_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # create candidate cards
        for idx, cand in enumerate(CANDIDATES):
            self._create_card(cards_frame, idx, cand["name"], cand["desc"])

        # submit button
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="ENVIAR VOTO", bootstyle="success", command=self.submit_vote).pack(ipadx=40, ipady=8)

    def _create_card(self, parent, idx, name, desc):
        card = ttk.Frame(parent, padding=8, bootstyle="secondary")
        card.pack(fill="x", padx=12, pady=8)
        card.columnconfigure(0, weight=30)
        card.columnconfigure(1, weight=70)

        # image area
        img_frame = ttk.Frame(card, width=240, height=120)
        img_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        img_frame.propagate(False)
        placeholder = self._placeholder(240, 120)
        self.pil_images[idx] = placeholder
        photo = self._resize_to_photo(placeholder, 240, 120)
        self.photo_images[idx] = photo
        img_label = ttk.Label(img_frame, image=photo)
        img_label.image = photo
        img_label.pack(fill="both", expand=True)

        # right side
        right = ttk.Frame(card)
        right.grid(row=0, column=1, sticky="nsew")
        ttk.Label(right, text=name, font=("Helvetica", 12, "bold")).pack(anchor="w")
        ttk.Label(right, text=desc, wraplength=520).pack(anchor="w", pady=(4,8))
        ttk.Radiobutton(right, text="Seleccionar", variable=self.selection_var, value=name).pack(anchor="w")

        # URL entry + load/select
        url_frame = ttk.Frame(right)
        url_frame.pack(fill="x", pady=(8,0))
        url_entry = ttk.Entry(url_frame, textvariable=self.image_vars[idx], width=48)
        url_entry.pack(side="left", padx=(0,6))
        ttk.Button(url_frame, text="Cargar", command=lambda i=idx, l=img_label: self.load_image(i, l)).pack(side="left", padx=(0,6))
        ttk.Button(url_frame, text="Seleccionar archivo", command=lambda i=idx, l=img_label: self.select_file(i, l)).pack(side="left")

    def load_image(self, idx, label_widget):
        url = self.image_vars[idx].get().strip()
        if not url:
            messagebox.showinfo("Imagen", "Pega URL o ruta y pulsa Cargar.")
            return

        def worker():
            img = self._try_load(url)
            if img is None:
                self.after(0, lambda: messagebox.showerror("Error", f"No se pudo cargar: {url}"))
                return
            self.pil_images[idx] = img
            photo = self._resize_to_photo(img, 240, 120)
            self.photo_images[idx] = photo
            self.after(0, lambda: self.update_label(label_widget, photo))
        threading.Thread(target=worker, daemon=True).start()

    def select_file(self, idx, label_widget):
        path = filedialog.askopenfilename(filetypes=[("Images","*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if not path:
            return
        img = self._try_load(path)
        if img is None:
            messagebox.showerror("Error", "No se pudo abrir el archivo.")
            return
        self.pil_images[idx] = img
        photo = self._resize_to_photo(img, 240, 120)
        self.photo_images[idx] = photo
        self.update_label(label_widget, photo)
        self.image_vars[idx].set(path)

    def update_label(self, label_widget, photo):
        label_widget.configure(image=photo)
        label_widget.image = photo

    def submit_vote(self):
        seleccionado = self.selection_var.get()
        if not seleccionado:
            messagebox.showwarning("Sin selección", "Debes seleccionar un candidato.")
            return
        payload = {
            "estudiante_nombre": self.controller.shared_data.get("nombre"),
            "estudiante_apellido": self.controller.shared_data.get("apellido"),
            "estudiante_id": self.controller.shared_data.get("id_estudiante"),
            "candidato": seleccionado
        }
        payload_json = json.dumps(payload, ensure_ascii=False)
        nuevo = self.controller.bc.agregar_bloque(payload_json)
        messagebox.showinfo("Registrado", f"Voto registrado para {seleccionado} (Bloque {nuevo.id}).")
        # limpiar datos y volver a inicio
        self.controller.shared_data["nombre"] = ""
        self.controller.shared_data["apellido"] = ""
        self.controller.shared_data["id_estudiante"] = ""
        self.controller.shared_data["selection"] = ""
        self.controller.show_frame("Inicio")
