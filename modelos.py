"""
Define las clases centrales del juego:
  - Personaje : un combatiente con HP, ATK y DEF.
  - Entrenador: agrupa hasta 3 personajes y lleva el puntaje.
  
"""
import random

class Personaje:
    """Representa un personaje del juego con sus estadísticas."""

    def __init__(self, nombre: str, hp: int, atk: int, defensa: int):
        self.nombre = nombre
        self.hp_max = hp        # Vida máxima (nunca cambia)
        self.hp_actual = hp     # Vida en combate (baja y sube)
        self.atk = atk
        self.defensa = defensa
        
        nombre_archivo=nombre.lower().replace(" ", "_")
        self.imagen_ruta=f"imagenes/{nombre_archivo}.png"

    # ── Propiedades de estado ──────────────────────────────
    def esta_ko(self) -> bool:
        """Devuelve True si el personaje no puede seguir peleando."""
        return self.hp_actual <= 0

    def restaurar_vida(self):
        """Restablece la vida al máximo (se usa al capturar)."""
        self.hp_actual = self.hp_max

    # ── Fórmula de daño (requerimiento 06) ────────────────
    def calcular_danio(self, defensor: "Personaje") -> int:
        """
        Daño = ATK del atacante - DEF del defensor.
        Si el resultado es <= 0, el daño mínimo es 1.
        """
        danio = self.atk - defensor.defensa
        return max(1, danio)   # max(1, x) garantiza el mínimo

    def recibir_danio(self, cantidad: int):
        """Descuenta HP; no puede bajar de 0."""
        self.hp_actual = max(0, self.hp_actual - cantidad)

    def __str__(self):
        return (f"{self.nombre} "
                f"[HP:{self.hp_actual}/{self.hp_max} "
                f"ATK:{self.atk} DEF:{self.defensa}]")


# ── Carga desde archivo ────────────────────────────────────
def cargar_personajes(ruta: str = "personajes.txt") -> list[Personaje]:
    """
    Lee el archivo de texto y devuelve una lista de Personaje.

    Formato:
        nombre,hp,atk,def
    """
    personajes = []
    with open(ruta, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea:           # Ignorar líneas vacías
                continue
            partes = linea.split(",")
            nombre  = partes[0].replace("_", " ")  # "Jose_David" → "Jose David"
            hp      = int(partes[1])
            atk     = int(partes[2])
            defensa = int(partes[3])
            personajes.append(Personaje(nombre, hp, atk, defensa))
    return personajes


# ── Entrenador ─────────────────────────────────────────────
class Entrenador:
    """
    Agrupa los personajes de un jugador (humano o IA) y su puntaje.

    Atributos:
        nombre      : nombre del jugador o "Hollow X"
        personajes  : lista de hasta 3 Personaje
        activo      : índice del personaje en juego ahora mismo
        puntaje     : +1 por cada personaje capturado (req. 04)
    """

    def __init__(self, nombre: str, personajes: list[Personaje]):
        self.nombre = nombre
        self.personajes = personajes    # Lista de 3 personajes
        self.activo = 0                 # El primero entra al campo
        self.puntaje = 0

    def personaje_activo(self) -> Personaje:
        """Devuelve el personaje que está peleando ahora."""
        if self.activo>=len(self.personajes):
            self.activo=max(0,len(self.personajes)-1)
        return self.personajes[self.activo]

    def tiene_personajes_vivos(self) -> bool:
        """True si al menos un personaje no está KO."""
        return any(not p.esta_ko() for p in self.personajes)

    def capturar(self, personaje: Personaje):
        """
        Agrega un personaje capturado al equipo y sube el puntaje.
        El personaje recupera toda su vida al ser capturado.
        """
        personaje.restaurar_vida()
        self.personajes.append(personaje)
        self.puntaje += 1

    def elegir_accion_random(self) -> str:
        """
        IA del Hollow: elige aleatoriamente entre ATACAR o CAMBIAR.
        """
        vivos = [p for p in self.personajes if not p.esta_ko()]
        # Si solo tiene un personaje vivo, no puede cambiar
        if len(vivos) <= 1:
            return "atacar"
        return random.choice(["atacar", "cambiar"])

    def siguiente_personaje_vivo(self) -> int | None:
        """
        Devuelve el índice del primer personaje vivo que NO
        sea el activo actual. Usado por la IA para cambiar.
        """
        for i, p in enumerate(self.personajes):
            if i != self.activo and not p.esta_ko():
                return i
        return None
