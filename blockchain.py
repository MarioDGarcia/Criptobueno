# # blockchain.py
# """
# Mini-blockchain backend (módulo compartido)

# Define:
# - Block
# - Blockchain

# Uso: import Blockchain desde otros módulos.
# """
# import hashlib
# import json
# import os
# from datetime import datetime
# from typing import List, Dict, Any, Tuple

# CHAIN_FILE = "chain.json"


# class Block:
#     def __init__(self, id: int, timestamp: str, data: str, prev_hash: str, hash_actual: str = None):
#         self.id = id
#         self.timestamp = timestamp
#         self.data = data
#         self.prev_hash = prev_hash
#         self.hash_actual = hash_actual if hash_actual is not None else self.calcular_hash()

#     def calcular_hash(self) -> str:
#         contenido = f"{self.id}|{self.timestamp}|{self.data}|{self.prev_hash}"
#         return hashlib.sha256(contenido.encode("utf-8")).hexdigest()

#     def to_dict(self) -> Dict[str, Any]:
#         return {
#             "id": self.id,
#             "timestamp": self.timestamp,
#             "data": self.data,
#             "prev_hash": self.prev_hash,
#             "hash_actual": self.hash_actual,
#         }

#     @staticmethod
#     def from_dict(d: Dict[str, Any]) -> "Block":
#         return Block(
#             id=d["id"],
#             timestamp=d["timestamp"],
#             data=d["data"],
#             prev_hash=d["prev_hash"],
#             hash_actual=d.get("hash_actual"),
#         )


# class Blockchain:
#     def __init__(self, filename: str = CHAIN_FILE):
#         self.filename = filename
#         self.chain: List[Block] = []
#         self._load_or_create()

#     def _load_or_create(self) -> None:
#         if os.path.exists(self.filename):
#             try:
#                 with open(self.filename, "r", encoding="utf-8") as f:
#                     arr = json.load(f)
#                 self.chain = [Block.from_dict(b) for b in arr]
#             except Exception:
#                 self._create_genesis()
#         else:
#             self._create_genesis()

#     def _create_genesis(self) -> None:
#         genesis = Block(
#             id=0,
#             timestamp=datetime.utcnow().isoformat(),
#             data="Genesis Block",
#             prev_hash="0" * 64,
#         )
#         self.chain = [genesis]
#         self._save()

#     def _save(self) -> None:
#         with open(self.filename, "w", encoding="utf-8") as f:
#             json.dump([b.to_dict() for b in self.chain], f, indent=4, ensure_ascii=False)

#     def agregar_bloque(self, data: str) -> Block:
#         ultimo = self.chain[-1]
#         nuevo_id = ultimo.id + 1
#         ts = datetime.utcnow().isoformat()
#         nuevo = Block(id=nuevo_id, timestamp=ts, data=data, prev_hash=ultimo.hash_actual)
#         self.chain.append(nuevo)
#         self._save()
#         return nuevo

#     def verificar_cadena(self) -> Tuple[bool, List[str]]:
#         errores = []
#         valido = True
#         for i, b in enumerate(self.chain):
#             recalculado = b.calcular_hash()
#             if recalculado != b.hash_actual:
#                 errores.append(f"Bloque {b.id}: hash_actual inválido (recalculado {recalculado} != {b.hash_actual})")
#                 valido = False
#             if i > 0:
#                 prev = self.chain[i - 1]
#                 if b.prev_hash != prev.hash_actual:
#                     errores.append(f"Bloque {b.id}: prev_hash ({b.prev_hash}) != hash_actual anterior ({prev.hash_actual})")
#                     valido = False
#         return valido, errores

#     def corromper_bloque(self, id: int, nuevo_data: str) -> bool:
#         for b in self.chain:
#             if b.id == id:
#                 b.data = nuevo_data
#                 self._save()
#                 return True
#         return False

#     def export_json(self, out_file: str) -> None:
#         with open(out_file, "w", encoding="utf-8") as f:
#             json.dump([b.to_dict() for b in self.chain], f, indent=4, ensure_ascii=False)



#============================================================================================================================================

"""
Mini-blockchain backend (módulo compartido)

Define:
- Block  → representa un bloque individual de la cadena.
- Blockchain → administra la cadena completa, lectura/escritura, validación y corrupción.

Este archivo se importa desde los otros módulos del sistema de votación.
"""

import hashlib
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple

CHAIN_FILE = "chain.json"


class Block:
    """
    La clase Block representa un solo bloque dentro de la cadena. Cada bloque contiene:
    - un ID numérico,
    - un timestamp,
    - datos arbitrarios (como resultados de una votación),
    - el hash del bloque anterior,
    - y su propio hash.

    El propósito de encapsular esta información es asegurar que cada bloque dependa del anterior
    mediante hashing. Si cualquier bloque pasado es modificado, el hash ya no coincide y la
    integridad de la cadena se rompe.
    """
    def __init__(self, id: int, timestamp: str, data: str, prev_hash: str, hash_actual: str = None):
        self.id = id
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        # Si no se proporciona un hash, se calcula automáticamente.
        self.hash_actual = hash_actual if hash_actual is not None else self.calcular_hash()

    def calcular_hash(self) -> str:
        """
        Este método calcula el hash criptográfico del bloque concatenando todos sus campos
        relevantes en un solo string y aplicando SHA-256. La idea es que cualquier cambio en los
        datos del bloque genere un hash completamente distinto, permitiendo detectar
        manipulación o corrupción. El formato es:

        hash = SHA256( ID | timestamp | data | prev_hash )
        """
        contenido = f"{self.id}|{self.timestamp}|{self.data}|{self.prev_hash}"
        return hashlib.sha256(contenido.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el bloque a un diccionario estándar de Python, lo cual permite guardarlo fácilmente
        en un archivo JSON. Esta función se usa durante la persistencia de la cadena.
        """
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "data": self.data,
            "prev_hash": self.prev_hash,
            "hash_actual": self.hash_actual,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Block":
        """
        Reconstruye un bloque a partir de un diccionario previamente almacenado en JSON.
        Esto permite recargar la blockchain desde disco sin perder la información de los hashes.
        """
        return Block(
            id=d["id"],
            timestamp=d["timestamp"],
            data=d["data"],
            prev_hash=d["prev_hash"],
            hash_actual=d.get("hash_actual"),
        )


class Blockchain:
    """
    La clase Blockchain administra toda la cadena. Se encarga de:
    - cargar los bloques desde un archivo,
    - crear el bloque génesis si no existe,
    - agregar nuevos bloques,
    - verificar la integridad de la cadena completa,
    - simular corrupción en un bloque,
    - exportar la cadena a un archivo JSON.

    Funciona como una "base de datos encadenada", donde cada elemento depende criptográficamente
    del anterior.
    """

    def __init__(self, filename: str = CHAIN_FILE):
        self.filename = filename
        self.chain: List[Block] = []
        self._load_or_create()  # Cargar archivo o crear bloque génesis

    def _load_or_create(self) -> None:
        """
        Este método revisa si el archivo de la blockchain existe. Si existe, intenta leer 
        los bloques almacenados y reconstruirlos. Si el archivo está dañado o no existe,
        se crea automáticamente un bloque génesis. Esto garantiza que la cadena siempre
        tenga un punto inicial válido.
        """
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
        """
        Crea el primer bloque de la cadena, conocido como bloque génesis. Este bloque no tiene
        un bloque previo, por lo que su prev_hash es una cadena fija de ceros. A partir de este
        bloque, todos los demás dependen de su hash. Esto establece el inicio de la cadena.
        """
        genesis = Block(
            id=0,
            timestamp=datetime.utcnow().isoformat(),
            data="Genesis Block",
            prev_hash="0" * 64,
        )
        self.chain = [genesis]
        self._save()

    def _save(self) -> None:
        """
        Guarda toda la cadena en el archivo JSON especificado. Se utiliza cada vez que se añade
        un nuevo bloque o se modifica el contenido. Esta función garantiza la persistencia
        de la cadena entre ejecuciones.
        """
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=4, ensure_ascii=False)

    def agregar_bloque(self, data: str) -> Block:
        """
        Agrega un nuevo bloque al final de la cadena. Para hacerlo:
        - obtiene el último bloque,
        - calcula un nuevo ID,
        - genera un timestamp,
        - define el prev_hash como el hash del último bloque,
        - calcula su propio hash,
        - lo almacena y lo guarda en disco.

        Este método es esencial, pues simula la creación de transacciones o registros dentro
        de la mini-blockchain.
        """
        ultimo = self.chain[-1]
        nuevo_id = ultimo.id + 1
        ts = datetime.utcnow().isoformat()
        nuevo = Block(id=nuevo_id, timestamp=ts, data=data, prev_hash=ultimo.hash_actual)
        self.chain.append(nuevo)
        self._save()
        return nuevo

    def verificar_cadena(self) -> Tuple[bool, List[str]]:
        """
        Verifica la integridad de toda la cadena. Para hacerlo recorre cada bloque y realiza
        dos comprobaciones fundamentales:

        1. Vuelve a calcular el hash del bloque (hash_actual debe coincidir).
        2. Verifica que el prev_hash del bloque coincida con el hash_actual del bloque anterior.

        Si cualquiera de estas condiciones falla, la cadena ha sido alterada. El método devuelve:
        - un booleano indicando si la cadena es válida,
        - una lista de textos describiendo los errores detectados.
        """
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
        """
        Modifica deliberadamente los datos de un bloque con un ID específico. Esto no actualiza
        el hash del bloque, por lo que rompe la cadena y permite simular un ataque o manipulación.
        El método devuelve True si la corrupción se realizó correctamente.
        """
        for b in self.chain:
            if b.id == id:
                b.data = nuevo_data
                self._save()
                return True
        return False

    def export_json(self, out_file: str) -> None:
        """
        Exporta toda la cadena a un archivo JSON externo, permitiendo análisis, respaldo
        o revisión manual. Simplemente escribe la representación de todos los bloques.
        """
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in self.chain], f, indent=4, ensure_ascii=False)
