#!/usr/bin/env python3
"""
votacion_feu_blockchain.py
Versión A — Sistema de votación FEU + Mini-Blockchain + Tkinter + ttkbootstrap

Características principales:
- Interfaz con botón gigante "VOTAR"
- Formulario de estudiante (nombre, apellido, id)
- Boleta con 5 candidatos, cada tarjeta tiene:
    - columna izquierda para imagen (30% ancho) -- placeholder si no hay URL
    - columna derecha para texto (70%): nombre + descripción (lorem ipsum)
    - campo para pegar URL de imagen más adelante y botón "Cargar" para intentar cargar la imagen localmente
- Voto se registra como bloque en chain.json (id, timestamp, datos (json con estudiante+voto), prev_hash, hash_actual)
- Panel admin para ver cadena, verificar integridad, corromper bloques y exportar JSON
- Evita votos duplicados por ID de estudiante (simple)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter.scrolledtext import ScrolledText
import hashlib
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageTk
import io
import base64
import threading
import urllib.request

# -----------------------------
# Configuración / Constantes
# -----------------------------
CHAIN_FILE = "chain.json"
CANDIDATE_COUNT = 5

# Datos iniciales de los 5 candidatos (nombres y descripción Lorem Ipsum).
CANDIDATES = [
    {"name": f"Candidato {i+1}", "desc": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod."}
    for i in range(CANDIDATE_COUNT)
]


# -----------------------------
# Clases de Blockchain (idénticas a la versión previa)
# -----------------------------
class Block:
    def __init__(self, id: int, timestamp: str, data: str, prev_hash: str, hash_actual: str = None):
        self.id = id
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        self.hash_actual = hash_actual if hash_actual is not None else self.calcular_hash()

    def calcular_hash(self) -> str:
        contenido = f"{self.id}|{self.timestamp}|{self.data}|{self.prev_hash}"
        return hashlib.sha256(contenido.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "data": self.data,
            "prev_hash": self.prev_hash,
            "hash_actual": self.hash_actual,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Block":
        return Block(
            id=d["id"],
            timestamp=d["timestamp"],
            data=d["data"],
            prev_hash=d["prev_hash"],
            hash_actual=d.get("hash_actual"),
        )


class Blockchain:
    def __init__(self, filename: str = CHAIN_FILE):
        self.filename = filename
        self.chain: List[Block] = []
        self._load_or_create()

    def _load_or_create(self) -> None:
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    arr = json.load(f)
                self.chain = [Block.from_dict(b) for b in arr]
            except Exception:
                self._create_genesis()
        else:
            self._create_genesis()

    def _create_genesis(self) -> None:
        genesis = Block(
            id=0,
            timestamp=datetime.utcnow().isoformat(),
            data="Genesis Block",
            prev_hash="0" * 64,
        )
        self.chain = [genesis]
        self._save()

    def _save(self) -> None:
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=4, ensure_ascii=False)

    def agregar_bloque(self, data: str) -> Block:
        ultimo = self.chain[-1]
        nuevo_id = ultimo.id + 1
        ts = datetime.utcnow().isoformat()
        nuevo = Block(id=nuevo_id, timestamp=ts, data=data, prev_hash=ultimo.hash_actual)
        self.chain.append(nuevo)
        self._save()
        return nuevo

    def verificar_cadena(self) -> Tuple[bool, List[str]]:
        errores: List[str] = []
        valido = True
        for i, b in enumerate(self.chain):
            recalculado = b.calcular_hash()
            if recalculado != b.hash_actual:
                errores.append(f"Bloque {b.id}: hash_actual inválido (recalculado {recalculado} != {b.hash_actual})")
                valido = False
            if i > 0:
                prev = self.chain[i - 1]
                if b.prev_hash != prev.hash_actual:
                    errores.append(f"Bloque {b.id}: prev_hash ({b.prev_hash}) != hash_actual anterior ({prev.hash_actual})")
                    valido = False
        return valido, errores

    def corromper_bloque(self, id: int, nuevo_data: str) -> bool:
        for b in self.chain:
            if b.id == id:
                b.data = nuevo_data
                self._save()
                return True
        return False

    def export_json(self, out_file: str) -> None:
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=4, ensure_ascii=False)


# -----------------------------
# GUI Application
# -----------------------------
class FEUElectionApp(tb.Window):
    def __init__(self, master=None):
        super().__init__(title="Elecciones FEU - Mini-Blockchain", themename="cosmo")
        self.geometry("900x650")
        self.minsize(800, 600)

        # Blockchain backend
        self.bc = Blockchain()

        # Variables para formulario
        self.nombre_var = tk.StringVar()
        self.apellido_var = tk.StringVar()
        self.id_var = tk.StringVar()

        # Voto seleccionado (nombre del candidato)
        self.voto_var = tk.StringVar()

        # Imágenes por candidato (ImageTk.PhotoImage or None)
        # Also store original PIL images for resizing
        self.candidate_images: List[Optional[Image.Image]] = [None] * CANDIDATE_COUNT
        self.candidate_photoimgs: List[Optional[ImageTk.PhotoImage]] = [None] * CANDIDATE_COUNT

        # Entries for image URLs per candidate (user can paste later)
        self.image_url_vars = [tk.StringVar() for _ in range(CANDIDATE_COUNT)]

        # build UI
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.pantalla_inicio()

    # -------------------------
    # Utilidades de imagen
    # -------------------------
    def _make_placeholder_image(self, w: int, h: int) -> Image.Image:
        """Crea una imagen placeholder gris con texto 'Image' centrado."""
        img = Image.new("RGB", (w, h), color=(200, 200, 200))
        return img

    def _resize_and_get_photoimg(self, pil_img: Image.Image, w: int, h: int) -> ImageTk.PhotoImage:
        img = pil_img.copy()
        img.thumbnail((w, h), Image.LANCZOS)
        # create background and paste centered vertically
        bg = Image.new("RGB", (w, h), (230, 230, 230))
        x = 0
        y = (h - img.height) // 2
        bg.paste(img, (x, y))
        return ImageTk.PhotoImage(bg)

    def _try_load_image_from_url_or_file(self, url_or_path: str) -> Optional[Image.Image]:
        """Intenta cargar una imagen desde URL (http/https) o desde ruta local. Devuelve PIL.Image o None."""
        if not url_or_path:
            return None
        try:
            if url_or_path.startswith("http://") or url_or_path.startswith("https://"):
                # intentar descargar
                with urllib.request.urlopen(url_or_path, timeout=6) as resp:
                    data = resp.read()
                img = Image.open(io.BytesIO(data)).convert("RGB")
                return img
            else:
                img = Image.open(url_or_path).convert("RGB")
                return img
        except Exception:
            return None

    # -------------------------
    # Pantallas
    # -------------------------
    def clear_container(self):
        for child in self.container.winfo_children():
            child.destroy()

    def pantalla_inicio(self):
        self.clear_container()
        frame = ttk.Frame(self.container)
        frame.pack(expand=True)

        title = ttk.Label(frame, text="ELECCIONES FEU - UDG", font=("Helvetica", 30, "bold"))
        title.pack(pady=30)

        subtitle = ttk.Label(frame, text="Sistema de votación con auditoría (mini-blockchain)", font=("Helvetica", 12))
        subtitle.pack(pady=(0, 30))

        btn_votar = ttk.Button(frame, text="VOTAR", style="success.TButton", bootstyle=(SUCCESS, "outline"),
                               command=self.pantalla_formulario)
        btn_votar.pack(pady=20, ipadx=80, ipady=30)

        # Admin panel button small
        btn_admin = ttk.Button(frame, text="Panel administrativo", command=self.pantalla_admin)
        btn_admin.pack(side="bottom", pady=20)

    def pantalla_formulario(self):
        self.clear_container()
        frame = ttk.Frame(self.container, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Formulario de Registro", font=("Helvetica", 20, "bold")).pack(pady=10)

        form = ttk.Frame(frame)
        form.pack(pady=10)

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        nombre_entry = ttk.Entry(form, textvariable=self.nombre_var, width=40)
        nombre_entry.grid(row=0, column=1, pady=5)

        ttk.Label(form, text="Apellido:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        apellido_entry = ttk.Entry(form, textvariable=self.apellido_var, width=40)
        apellido_entry.grid(row=1, column=1, pady=5)

        ttk.Label(form, text="ID Estudiante UDG:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        id_entry = ttk.Entry(form, textvariable=self.id_var, width=40)
        id_entry.grid(row=2, column=1, pady=5)

        info = ttk.Label(frame, text="Presiona Enter en cualquier campo o pulsa Continuar para seguir", font=("Helvetica", 9))
        info.pack(pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        btn_continuar = ttk.Button(btn_frame, text="Continuar", style="info.TButton", command=self._on_form_submit)
        btn_continuar.pack(side="left", padx=10)
        btn_regresar = ttk.Button(btn_frame, text="Regresar", command=self.pantalla_inicio)
        btn_regresar.pack(side="left", padx=10)

        # bind Enter to submit
        for w in (nombre_entry, apellido_entry, id_entry):
            w.bind("<Return>", lambda e: self._on_form_submit())

    def _on_form_submit(self):
        nombre = self.nombre_var.get().strip()
        apellido = self.apellido_var.get().strip()
        id_est = self.id_var.get().strip()

        if not nombre or not apellido or not id_est:
            messagebox.showwarning("Formulario incompleto", "Todos los campos son obligatorios.")
            return

        if not id_est.isdigit():
            messagebox.showwarning("ID inválido", "El ID de estudiante debe ser numérico.")
            return

        # verificar votos duplicados: revisar la chain por registros con este ID
        already_voted = False
        for b in self.bc.chain:
            try:
                payload = json.loads(b.data)
                if isinstance(payload, dict) and payload.get("estudiante_id") == id_est:
                    already_voted = True
                    break
            except Exception:
                continue

        if already_voted:
            messagebox.showerror("Voto denegado", "Este ID ya emitió un voto. No se permiten votos duplicados.")
            return

        # todo ok -> ir a votación
        self.pantalla_votacion()

    def pantalla_votacion(self):
        self.clear_container()
        frame = ttk.Frame(self.container, padding=12)
        frame.pack(fill="both", expand=True)

        header = ttk.Frame(frame)
        header.pack(fill="x")
        ttk.Label(header, text=f"Votación — {self.nombre_var.get()} {self.apellido_var.get()} (ID: {self.id_var.get()})",
                  font=("Helvetica", 14, "bold")).pack(side="left", pady=6)
        ttk.Button(header, text="Cancelar", command=self.pantalla_inicio).pack(side="right")

        # area de candidatos: usaremos un canvas con scrollbar para acomodar tarjetas
        canvas_frame = ttk.Frame(frame)
        canvas_frame.pack(fill="both", expand=True, pady=10)

        canvas = tk.Canvas(canvas_frame, borderwidth=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        cards_frame = ttk.Frame(canvas)

        cards_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=cards_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # crear tarjetas de candidatos
        for idx, cand in enumerate(CANDIDATES):
            self._crear_tarjeta_candidato(cards_frame, idx, cand["name"], cand["desc"])

        # boton enviar
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        btn_votar = ttk.Button(btn_frame, text="ENVIAR VOTO", style="success.TButton", command=self._submit_vote)
        btn_votar.pack(ipadx=40, ipady=10)

    def _crear_tarjeta_candidato(self, parent, idx: int, nombre: str, descripcion: str):
        """
        Crea una tarjeta rectangular con imagen a la izquierda (30%) y texto a la derecha (70%).
        Incluye un Entry para pegar URL/local path de imagen, y botones "Cargar imagen" y "Seleccionar archivo".
        También incluye un radio button para seleccionar el candidato.
        """
        card = ttk.Frame(parent, relief="raised", bootstyle="secondary", padding=8)
        card.pack(fill="x", padx=12, pady=8)

        # Configuración de layout: 30% ancho imagen / 70% texto. Usaremos grid con weights.
        card.columnconfigure(0, weight=30)
        card.columnconfigure(1, weight=70)

        # area imagen (placeholder por defecto)
        img_frame = ttk.Frame(card, width=240, height=120)
        img_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        img_frame.propagate(False)  # keep size

        # placeholder PIL image
        placeholder = self._make_placeholder_image(240, 120)
        self.candidate_images[idx] = placeholder
        photo = self._resize_and_get_photoimg(placeholder, 240, 120)
        self.candidate_photoimgs[idx] = photo

        img_label = ttk.Label(img_frame, image=photo)
        img_label.image = photo
        img_label.pack(fill="both", expand=True)

        # area derecha con texto + controles de imagen
        right = ttk.Frame(card)
        right.grid(row=0, column=1, sticky="nsew")

        # nombre y descripcion
        ttk.Label(right, text=nombre, font=("Helvetica", 12, "bold")).pack(anchor="w")
        ttk.Label(right, text=descripcion, wraplength=520, font=("Helvetica", 10)).pack(anchor="w", pady=(4, 8))

        # radio button para seleccionar candidato
        rb = ttk.Radiobutton(right, text="Seleccionar", variable=self.voto_var, value=nombre)
        rb.pack(anchor="w")

        # campo URL / ruta de imagen y botones
        url_frame = ttk.Frame(right)
        url_frame.pack(fill="x", pady=(8, 0))

        url_entry = ttk.Entry(url_frame, textvariable=self.image_url_vars[idx], width=48)
        url_entry.pack(side="left", padx=(0, 6))
        btn_load = ttk.Button(url_frame, text="Cargar", command=lambda i=idx, l=img_label: self._on_load_image(i, l))
        btn_load.pack(side="left", padx=(0, 6))
        btn_file = ttk.Button(url_frame, text="Seleccionar archivo", command=lambda i=idx, l=img_label: self._on_select_file(i, l))
        btn_file.pack(side="left")

    def _on_load_image(self, idx: int, label_widget: ttk.Label):
        """
        Intenta cargar la imagen desde la URL o ruta pegada en la entrada correspondiente.
        Si falla, muestra un mensaje y mantiene el placeholder.
        """
        url = self.image_url_vars[idx].get().strip()
        if not url:
            messagebox.showinfo("Imagen", "Pega aquí la URL (http/https) o ruta local y pulsa Cargar.")
            return

        # cargar (puede tardar si es URL). Hacemos en hilo para no bloquear UI
        def worker():
            img = self._try_load_image_from_url_or_file(url)
            if img is None:
                self.after(0, lambda: messagebox.showerror("Error", f"No se pudo cargar la imagen desde: {url}"))
                return
            self.candidate_images[idx] = img
            photo = self._resize_and_get_photoimg(img, 240, 120)
            self.candidate_photoimgs[idx] = photo
            self.after(0, lambda: self._update_image_label(label_widget, photo))

        threading.Thread(target=worker, daemon=True).start()

    def _on_select_file(self, idx: int, label_widget: ttk.Label):
        """
        Abre un file dialog para seleccionar una imagen local. Carga y actualiza el label.
        """
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if not path:
            return
        img = self._try_load_image_from_url_or_file(path)
        if img is None:
            messagebox.showerror("Error", "No se pudo abrir el archivo de imagen.")
            return
        self.candidate_images[idx] = img
        photo = self._resize_and_get_photoimg(img, 240, 120)
        self.candidate_photoimgs[idx] = photo
        self._update_image_label(label_widget, photo)
        # también guardamos la ruta en la entrada para referencia
        self.image_url_vars[idx].set(path)

    def _update_image_label(self, label_widget: ttk.Label, photoimg: ImageTk.PhotoImage):
        label_widget.configure(image=photoimg)
        label_widget.image = photoimg

    # -------------------------
    # Acción de enviar voto
    # -------------------------
    def _submit_vote(self):
        seleccionado = self.voto_var.get()
        if not seleccionado:
            messagebox.showwarning("Sin selección", "Debes seleccionar un candidato.")
            return

        # construir payload con datos del estudiante y candidato
        payload = {
            "estudiante_nombre": self.nombre_var.get().strip(),
            "estudiante_apellido": self.apellido_var.get().strip(),
            "estudiante_id": self.id_var.get().strip(),
            "candidato": seleccionado
        }
        payload_json = json.dumps(payload, ensure_ascii=False)

        # agregar bloque a la blockchain
        nuevo = self.bc.agregar_bloque(payload_json)
        messagebox.showinfo("Voto registrado", f"Tu voto por '{seleccionado}' ha sido registrado.\nBloque ID: {nuevo.id}")

        # después de votar, volver a pantalla inicio (o mostrar recibo)
        self.pantalla_inicio()

    # -------------------------
    # Panel administrativo
    # -------------------------
    def pantalla_admin(self):
        self.clear_container()
        frame = ttk.Frame(self.container, padding=12)
        frame.pack(fill="both", expand=True)

        header = ttk.Frame(frame)
        header.pack(fill="x")
        ttk.Label(header, text="Panel Administrativo — Mini-Blockchain", font=("Helvetica", 14, "bold")).pack(side="left")
        ttk.Button(header, text="Regresar", command=self.pantalla_inicio).pack(side="right")

        # botones de acciones
        btns = ttk.Frame(frame)
        btns.pack(fill="x", pady=10)
        ttk.Button(btns, text="Mostrar Cadena", command=self._show_chain_window).pack(side="left", padx=6)
        ttk.Button(btns, text="Verificar integridad", command=self._verify_chain).pack(side="left", padx=6)
        ttk.Button(btns, text="Corromper bloque", command=self._ask_corrupt).pack(side="left", padx=6)
        ttk.Button(btns, text="Exportar JSON", command=self._export_chain).pack(side="left", padx=6)

        # area de logs
        self.admin_log = ScrolledText(frame, height=20)
        self.admin_log.pack(fill="both", expand=True, pady=8)
        self._log_admin("Panel administrativo listo.")

    def _log_admin(self, text: str):
        ts = datetime.utcnow().isoformat()
        self.admin_log.insert("end", f"{ts}  -  {text}\n")
        self.admin_log.see("end")

    def _show_chain_window(self):
        win = tb.Toplevel(self)
        win.title("Visualizar cadena (JSON)")
        win.geometry("800x600")
        txt = ScrolledText(win)
        txt.pack(fill="both", expand=True)
        try:
            with open(self.bc.filename, "r", encoding="utf-8") as f:
                contenido = f.read()
        except Exception:
            contenido = "No se pudo leer el archivo de cadena."
        txt.insert("end", contenido)

    def _verify_chain(self):
        valido, errores = self.bc.verificar_cadena()
        if valido:
            messagebox.showinfo("Verificación", "La cadena es válida. No se detectaron alteraciones.")
            self._log_admin("Verificación: OK — cadena válida.")
        else:
            messagebox.showerror("Verificación", "Se detectaron alteraciones. Revisa el log.")
            for e in errores:
                self._log_admin("ERROR: " + e)

    def _ask_corrupt(self):
        # pequeña ventana para pedir id y nuevo texto
        def do_corrupt():
            try:
                bid = int(entry_id.get().strip())
            except ValueError:
                messagebox.showerror("ID inválido", "El ID debe ser un entero.")
                return
            nuevo = entry_data.get("1.0", "end").strip()
            if not nuevo:
                messagebox.showwarning("Datos vacíos", "Introduce el nuevo contenido para 'data'.")
                return
            ok = self.bc.corromper_bloque(bid, nuevo)
            if ok:
                messagebox.showinfo("Corrompido", f"Bloque {bid} corrompido.")
                self._log_admin(f"Bloque {bid} corrompido manualmente.")
                top.destroy()
            else:
                messagebox.showerror("Error", f"No existe bloque con id {bid}.")

        top = tb.Toplevel(self)
        top.title("Corromper bloque")
        ttk.Label(top, text="ID del bloque a corromper:").pack(pady=4)
        entry_id = ttk.Entry(top)
        entry_id.pack(pady=4)
        ttk.Label(top, text="Nuevo valor para 'data' (sin recalcular hashes):").pack(pady=4)
        entry_data = ScrolledText(top, height=6, width=60)
        entry_data.pack(pady=6)
        ttk.Button(top, text="Corromper", command=do_corrupt).pack(pady=6)

    def _export_chain(self):
        out = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not out:
            return
        self.bc.export_json(out)
        messagebox.showinfo("Exportado", f"Cadena exportada a {out}")
        self._log_admin(f"Cadena exportada a {out}")

# -----------------------------
# Main
# -----------------------------
def main():
    app = FEUElectionApp()
    app.mainloop()


if __name__ == "__main__":
    main()
