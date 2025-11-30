import hashlib
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple

CHAIN_FILE = "chain.json"


class Block:
    def __init__(self, id: int, timestamp: str, data: str, prev_hash: str, hash_actual: str = None):
        self.id = id
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        # Si no se proporciona un hash, se calcula automáticamente.
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
        self._load_or_create()  # Cargar archivo o crear bloque génesis
        

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
        errores = []
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
