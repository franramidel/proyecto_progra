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
    """
    resultado = {
        "accion": "",
        "danio": 0,
        "mensaje": "",
        "ko": False,
    }
 
    # La IA del Hollow elige su acción de forma aleatoria
    accion = atacante.elegir_accion_random()
    resultado["accion"] = accion
 
    if accion == "cambiar":
        idx_nuevo = atacante.siguiente_personaje_vivo()
        if idx_nuevo is not None:
            anterior = atacante.personaje_activo().nombre
            atacante.activo = idx_nuevo
            resultado["mensaje"] = (
                f"{atacante.nombre} cambió a "
                f"{atacante.personaje_activo().nombre}."
            )
        else:
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
 
    Caso base: alguno de los dos se queda sin personajes.
    Caso recursivo: procesa el turno y se llama a sí misma
    con el turno alternado.
 
    ¿Por qué callbacks?
      Tkinter no permite llamadas bloqueantes dentro de la UI.
      Los callbacks permiten que la pantalla gráfica decida
      CUÁNDO continuar el siguiente turno.
    """
 
    # Caso base: verificar fin de combate ANTES de continuar
    if not jugador.personajes or not jugador.tiene_personajes_vivos():
        callback_fin(ganador=hollow, perdedor=jugador)
        return
 
    if not hollow.personajes or not hollow.tiene_personajes_vivos():
        callback_fin(ganador=jugador, perdedor=hollow)
        return
 
    def continuar_con_siguiente_turno(resultado_turno: dict):
        """
        Puente entre la UI y la recursión.
        Se llama cuando el usuario tomó su decisión o la IA actuó.
        Procesa la captura si hubo KO y lanza el siguiente turno.
        """
        # Procesar captura si hubo KO
        if resultado_turno.get("ko"):
            _procesar_captura(turno_jugador, jugador, hollow)
 
        # Llamada recursiva: cambiar turno
        ejecutar_turno_recursivo(
            jugador,
            hollow,
            not turno_jugador,
            callback_actualizar_ui,
            callback_fin,
            profundidad + 1,
        )
 
    callback_actualizar_ui(
        turno_jugador=turno_jugador,
        continuar=continuar_con_siguiente_turno,
    )
 
 
def _procesar_captura(
    turno_jugador: bool,
    jugador: Entrenador,
    hollow: Entrenador,
):
    """
    Cuando hay un KO, el ganador captura el personaje del perdedor.
    Usa índice seguro para evitar IndexError si la lista cambió.
 
    ¿Por qué función privada (prefijo _)?
      Convención de Python: indica que es de uso interno del módulo.
    """
    if turno_jugador:
        # Jugador venció al hollow
        if not hollow.personajes:
            return
        # Índice seguro: nunca mayor que el último elemento
        idx = min(hollow.activo, len(hollow.personajes) - 1)
        capturado = hollow.personajes[idx]
        hollow.personajes.remove(capturado)
        jugador.capturar(capturado)
        # Ajustar índice activo del hollow
        if hollow.personajes:
            hollow.activo = 0
            for i, p in enumerate(hollow.personajes):
                if not p.esta_ko():
                    hollow.activo = i
                    break
    else:
        # Hollow venció al jugador
        if not jugador.personajes:
            return
        idx = min(jugador.activo, len(jugador.personajes) - 1)
        capturado = jugador.personajes[idx]
        jugador.personajes.remove(capturado)
        hollow.capturar(capturado)
        # Ajustar índice activo del jugador
        if jugador.personajes:
            jugador.activo = 0
            for i, p in enumerate(jugador.personajes):
                if not p.esta_ko():
                    jugador.activo = i
                    break
 