"""
logica_batalla.py
-----------------
Motor de combate del juego. Maneja los turnos de la batalla
y contiene la función RECURSIVA requerida por el enunciado.

¿Por qué un archivo separado para la lógica?
  Separa la "regla del juego" de la "pantalla gráfica".
  Si mañana cambias la interfaz, la lógica de combate no
  se toca.

Recursividad utilizada (req. obligatorio):
  La función `ejecutar_turno_recursivo` se llama a sí misma
  para procesar cada turno del combate. En lugar de un
  bucle while, usamos recursión: cuando un turno termina,
  la función decide si el combate sigue y se llama de nuevo.

Preguntas frecuentes en defensa:
  P: ¿Qué es recursividad?
  R: Una función que se llama a sí misma. Necesita un caso
     base (condición de parada) para no ser infinita.

  P: ¿Cuál es el caso base aquí?
  R: Cuando alguno de los dos entrenadores se queda sin
     personajes vivos. Ahí la función deja de llamarse.

  P: ¿Por qué no usaste un while?
  R: El enunciado exige recursividad. Además, la recursión
     aquí es natural: "un turno genera el siguiente turno".
"""

import random
from modelos import Entrenador, Personaje


def calcular_turno(atacante: Entrenador, defensor: Entrenador) -> dict:
    """
    Procesa un turno completo de batalla.

    Devuelve un diccionario con:
      - accion   : "atacar" o "cambiar"
      - danio    : daño causado (0 si cambió)
      - mensaje  : texto descriptivo del turno
      - ko       : True si el defensor activo quedó KO
      - personaje_anterior : nombre del personaje antes de cambiar
      - personaje_nuevo    : nombre del personaje tras cambiar
    """
    resultado = {
        "accion": "",
        "danio": 0,
        "mensaje": "",
        "ko": False,
        "personaje_anterior": "",
        "personaje_nuevo": "",
    }

    # La IA del Hollow elige su acción de forma aleatoria
    accion = atacante.elegir_accion_random()
    resultado["accion"] = accion

    if accion == "cambiar":
        idx_nuevo = atacante.siguiente_personaje_vivo()
        if idx_nuevo is not None:
            resultado["personaje_anterior"] = atacante.personaje_activo().nombre
            atacante.activo = idx_nuevo
            resultado["personaje_nuevo"] = atacante.personaje_activo().nombre
            resultado["mensaje"] = (
                f"{atacante.nombre} cambió a "
                f"{resultado['personaje_nuevo']}."
            )
        else:
            # No puede cambiar → ataca igualmente
            accion = "atacar"
            resultado["accion"] = "atacar"

    if accion == "atacar":
        act = atacante.personaje_activo()
        dfd = defensor.personaje_activo()
        danio = act.calcular_danio(dfd)
        dfd.recibir_danio(danio)
        resultado["danio"] = danio
        resultado["ko"] = dfd.esta_ko()
        resultado["mensaje"] = (
            f"{act.nombre} atacó a {dfd.nombre} "
            f"causando {danio} de daño."
        )
        if resultado["ko"]:
            resultado["mensaje"] += f" ¡{dfd.nombre} fue derrotado!"

    return resultado


def ejecutar_turno_recursivo(
    jugador: Entrenador,
    hollow: Entrenador,
    turno_jugador: bool,
    callback_actualizar_ui,
    callback_fin,
    profundidad: int = 0,
):
    """
    Función RECURSIVA que ejecuta los turnos del combate.

    Parámetros:
      jugador            : entrenador del jugador humano
      hollow             : entrenador del hollow (IA)
      turno_jugador      : True si le toca al jugador, False al hollow
      callback_actualizar_ui : función que redibuja la pantalla de batalla
      callback_fin       : función llamada cuando el combate termina
      profundidad        : contador interno para debugging

    Caso base (parada de la recursión):
      Alguno de los dos se queda sin personajes vivos.

    ¿Por qué callbacks?
      Tkinter no permite llamadas bloqueantes dentro de la UI.
      Los callbacks permiten que la pantalla gráfica decida
      CUÁNDO continuar el siguiente turno (después de que el
      usuario aprete un botón, por ejemplo).
    """

    # ── Caso base ──────────────────────────────────────────
    if not jugador.tiene_personajes_vivos():
        callback_fin(ganador=hollow, perdedor=jugador)
        return

    if not hollow.tiene_personajes_vivos():
        callback_fin(ganador=jugador, perdedor=hollow)
        return

    # ── Caso recursivo ────────────────────────────────────
    # El callback_actualizar_ui recibe quién ataca y la función
    # para continuar con el siguiente turno cuando el usuario
    # tome su decisión.
    def continuar_con_siguiente_turno(resultado_turno: dict):
        """
        Esta función es el "puente" entre la UI y la recursión.
        La UI la llama cuando el usuario ya tomó su decisión,
        y nosotros lanzamos el siguiente turno.
        """
        # Procesar captura si hubo KO
        if resultado_turno.get("ko"):
            _procesar_captura(
                turno_jugador, jugador, hollow, resultado_turno
            )

        # Llamada recursiva: cambiar turno
        ejecutar_turno_recursivo(
            jugador,
            hollow,
            not turno_jugador,   # Alternamos el turno
            callback_actualizar_ui,
            callback_fin,
            profundidad + 1,
        )

    # Notificar a la UI que es momento de mostrar opciones
    callback_actualizar_ui(
        turno_jugador=turno_jugador,
        continuar=continuar_con_siguiente_turno,
    )


def _procesar_captura(
    turno_jugador: bool,
    jugador: Entrenador,
    hollow: Entrenador,
    resultado: dict,
):
    """
    Cuando hay un KO, el ganador captura el personaje del perdedor.

    ¿Por qué función privada (prefijo _)?
      Convención de Python: el prefijo _ indica que es de uso
      interno del módulo, no parte de la API pública.
    """
    if turno_jugador:
        # El jugador venció al hollow: captura su personaje activo
        capturado = hollow.personaje_activo()
        hollow.personajes.remove(capturado)
        jugador.capturar(capturado)
    else:
        # El hollow venció al jugador: captura su personaje activo
        capturado = jugador.personaje_activo()
        jugador.personajes.remove(capturado)
        hollow.capturar(capturado)

        # El jugador debe elegir su siguiente personaje activo
        for i, p in enumerate(jugador.personajes):
            if not p.esta_ko():
                jugador.activo = i
                break
