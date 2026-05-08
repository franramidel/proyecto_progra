"""
ventanas/pantalla_batalla.py
-----------------------------
Pantalla de batalla por turnos. Cumple el requerimiento 02:

  1. El jugador se enfrenta al Hollow.
  2. El Hollow actúa de forma completamente aleatoria.
  3. El jugador puede elegir qué personaje enviar.
  4. Al hacer KO, el personaje vencido pasa al ganador.
  5. Se puede cambiar personaje (si no está KO).
  6. Al capturar, el personaje recupera vida completa.
  7. Gana quien deje al rival sin personajes.
  8. Puntaje: +1 por cada personaje capturado (req. 04).

RECURSIVIDAD:
  El combate se controla mediante ejecutar_turno_recursivo()
  de logica_batalla.py. Ver ese archivo para la explicación
  detallada de cómo funciona la recursión.

Diseño de la pantalla:
  ┌─────────────────────────────────────────────┐
  │  [Panel Hollow]        [Panel Jugador]       │
  │  Nombre, HP, equipo    Nombre, HP, equipo    │
  ├─────────────────────────────────────────────┤
  │          [Log de batalla / mensajes]         │
  ├─────────────────────────────────────────────┤
  │     [ATACAR]  [CAMBIAR]  (o turno IA)        │
  └─────────────────────────────────────────────┘

Conceptos para la defensa:
  P: ¿Cómo se actualiza la interfaz en cada turno?
  R: Tenemos una función redibujar_ui() que actualiza las
     barras de HP y etiquetas. Se llama después de cada acción.

  P: ¿Cómo se "bloquean" los botones en el turno del Hollow?
  R: Usamos btn.config(state="disabled") para desactivarlos
     y "normal" para reactivarlos.
"""

import tkinter as tk
from tkinter import messagebox
import sys, os, random, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modelos import Entrenador, Personaje
from logica_batalla import ejecutar_turno_recursivo, calcular_turno

# ── Paleta ─────────────────────────────────────────────────
COLOR_FONDO   = "#0d0d1a"
COLOR_PANEL   = "#1a1a2e"
COLOR_ACENTO  = "#c9a84c"
COLOR_TEXTO   = "#e8e8e8"
COLOR_BOTON   = "#16213e"
COLOR_HOV     = "#0f3460"
COLOR_VERDE   = "#4caf72"
COLOR_ROJO    = "#e05c5c"
COLOR_HP_OK   = "#4caf72"
COLOR_HP_LOW  = "#e05c5c"
COLOR_HP_MED  = "#f0a500"


def crear_pantalla_batalla(
    ventana: tk.Tk,
    jugador: Entrenador,
    hollow: Entrenador,
    avatar: str,
    todos_personajes: list[Personaje],
    completadas: list,
    idx_tierra: int,
):
    """
    Construye la pantalla de batalla y arranca el motor de turnos.
    """
    ventana.config(bg=COLOR_FONDO)

    # ═══════════════════════════════════════════════════════
    # SECCIÓN 1 — Construcción de la UI
    # ═══════════════════════════════════════════════════════

    # ── Título ─────────────────────────────────────────────
    tk.Label(
        ventana,
        text="⚔  BATALLA  ⚔",
        font=("Georgia", 20, "bold"),
        fg=COLOR_ACENTO, bg=COLOR_FONDO,
    ).pack(pady=(16, 4))

    tk.Frame(ventana, height=2, bg=COLOR_ACENTO).pack(fill="x", padx=60, pady=4)

    # ── Paneles de combatientes (Hollow izq, Jugador der) ──
    frame_combate = tk.Frame(ventana, bg=COLOR_FONDO)
    frame_combate.pack(fill="x", padx=40, pady=8)

    panel_hollow  = _crear_panel_entrenador(frame_combate, hollow,  lado="left")
    panel_jugador = _crear_panel_entrenador(frame_combate, jugador, lado="right")

    # ── Log de batalla ─────────────────────────────────────
    tk.Label(
        ventana, text="— Registro de batalla —",
        font=("Georgia", 10, "italic"),
        fg=COLOR_ACENTO, bg=COLOR_FONDO,
    ).pack()

    frame_log = tk.Frame(ventana, bg=COLOR_PANEL, pady=6)
    frame_log.pack(fill="x", padx=40)

    log_texto = tk.Text(
        frame_log,
        height=5, width=90,
        font=("Courier", 10),
        bg=COLOR_PANEL, fg=COLOR_TEXTO,
        relief="flat", state="disabled",
        wrap="word",
    )
    log_texto.pack(padx=10)

    # ── Botones de acción ──────────────────────────────────
    frame_acciones = tk.Frame(ventana, bg=COLOR_FONDO)
    frame_acciones.pack(pady=12)

    btn_atacar = _boton(frame_acciones, "⚔  ATACAR", None)
    btn_atacar.pack(side="left", padx=10)

    btn_cambiar = _boton(frame_acciones, "🔄  CAMBIAR", None)
    btn_cambiar.pack(side="left", padx=10)

    label_turno = tk.Label(
        ventana, text="",
        font=("Georgia", 11, "italic"),
        fg=COLOR_TEXTO, bg=COLOR_FONDO,
    )
    label_turno.pack(pady=4)

    # ═══════════════════════════════════════════════════════
    # SECCIÓN 2 — Funciones de actualización de UI
    # ═══════════════════════════════════════════════════════

    def escribir_log(mensaje: str):
        """Agrega una línea al log de batalla (widget Text)."""
        log_texto.config(state="normal")
        log_texto.insert("end", f"▸ {mensaje}\n")
        log_texto.see("end")   # Auto-scroll al final
        log_texto.config(state="disabled")

    def redibujar_panel(panel_widgets: dict, entrenador: Entrenador):
        """
        Actualiza el panel de un entrenador:
          - Nombre del personaje activo
          - Barra y texto de HP
          - Marcas de equipo (✓ vivo, ✗ KO)
        """
        p = entrenador.personaje_activo()

        panel_widgets["label_personaje"].config(text=p.nombre)
        panel_widgets["label_puntaje"].config(
            text=f"Puntaje: {entrenador.puntaje}"
        )

        # HP como porcentaje para la barra
        porcentaje = p.hp_actual / p.hp_max
        ancho_barra = int(200 * porcentaje)
        color_barra = (
            COLOR_HP_OK  if porcentaje > 0.5 else
            COLOR_HP_MED if porcentaje > 0.25 else
            COLOR_HP_LOW
        )
        panel_widgets["canvas_hp"].coords(
            panel_widgets["rect_hp"], 0, 0, ancho_barra, 18
        )
        panel_widgets["canvas_hp"].itemconfig(
            panel_widgets["rect_hp"], fill=color_barra
        )
        panel_widgets["label_hp"].config(
            text=f"{p.hp_actual} / {p.hp_max} HP"
        )

        # Actualizar íconos del equipo
        for i, icono_label in enumerate(panel_widgets["iconos_equipo"]):
            if i < len(entrenador.personajes):
                per = entrenador.personajes[i]
                if per.esta_ko():
                    icono_label.config(text="✗", fg=COLOR_ROJO)
                elif i == entrenador.activo:
                    icono_label.config(text="★", fg=COLOR_ACENTO)
                else:
                    icono_label.config(text="●", fg=COLOR_VERDE)
            else:
                icono_label.config(text=" ")

    def redibujar_todo():
        redibujar_panel(panel_hollow,  hollow)
        redibujar_panel(panel_jugador, jugador)

    # ═══════════════════════════════════════════════════════
    # SECCIÓN 3 — Motor de turnos con RECURSIVIDAD
    # ═══════════════════════════════════════════════════════

    def deshabilitar_botones():
        btn_atacar.config(state="disabled", bg="#333")
        btn_cambiar.config(state="disabled", bg="#333")

    def habilitar_botones():
        btn_atacar.config(state="normal", bg=COLOR_BOTON)
        btn_cambiar.config(state="normal", bg=COLOR_BOTON)

    def callback_actualizar_ui(turno_jugador: bool, continuar):
        """
        Función que recibe el motor recursivo en cada turno.

        Si es turno del jugador: activa botones y espera click.
        Si es turno del Hollow:  ejecuta la IA y llama continuar().

        ¿Qué es el parámetro 'continuar'?
          Es la función de logica_batalla que dispara el siguiente
          turno recursivo. La llamamos cuando la acción del turno
          actual ya se procesó.
        """
        redibujar_todo()

        if turno_jugador:
            # ── Turno del jugador ──────────────────────────
            label_turno.config(
                text=f"Tu turno, {jugador.nombre}. ¿Qué harás?",
                fg=COLOR_ACENTO,
            )
            habilitar_botones()

            def accion_atacar():
                deshabilitar_botones()
                # Calculamos el daño usando calcular_turno del motor
                resultado = _turno_jugador_ataca(jugador, hollow)
                escribir_log(resultado["mensaje"])
                redibujar_todo()
                continuar(resultado)   # ← Llama al siguiente turno recursivo

            def accion_cambiar():
                """Abre un menú para que el jugador elija a quién cambiar."""
                _ventana_cambio(ventana, jugador, lambda: (
                    deshabilitar_botones(),
                    redibujar_todo(),
                    escribir_log(f"{jugador.nombre} cambió de personaje."),
                    continuar({"ko": False})   # Cambiar no hace KO
                ))

            btn_atacar.config(command=accion_atacar)
            btn_cambiar.config(command=accion_cambiar)

        else:
            # ── Turno del Hollow (IA aleatoria) ───────────
            label_turno.config(
                text=f"Turno del {hollow.nombre}...",
                fg=COLOR_ROJO,
            )
            deshabilitar_botones()

            # after(ms, func): ejecuta la función tras una pausa
            # Simula que el Hollow "piensa" (800ms de delay)
            def turno_ia():
                resultado = calcular_turno(hollow, jugador)
                escribir_log(resultado["mensaje"])
                redibujar_todo()
                ventana.after(400, lambda: continuar(resultado))

            ventana.after(800, turno_ia)

    def callback_fin(ganador: Entrenador, perdedor: Entrenador):
        """
        Caso base de la recursión: el combate terminó.
        Determina si el jugador ganó o perdió y navega.
        """
        deshabilitar_botones()
        redibujar_todo()

        jugador_gano = (ganador is jugador)

        if jugador_gano:
            completadas[idx_tierra] = True
            escribir_log(f"¡Victoria! Has derrotado al {hollow.nombre}.")
            mensaje = (
                f"¡Ganaste! Fragmento de {_nombre_tierra(idx_tierra)} restaurado.\n"
                f"Puntaje: {jugador.puntaje}"
            )
        else:
            escribir_log(f"Derrota... El {hollow.nombre} te venció.")
            mensaje = (
                f"Perdiste contra {hollow.nombre}.\n"
                f"Puntaje final: {jugador.puntaje}"
            )

        # Mostrar resultado y volver al mapa
        ventana.after(1200, lambda: _mostrar_resultado_y_volver(
            ventana, jugador, avatar, todos_personajes,
            completadas, idx_tierra, jugador_gano, mensaje
        ))

    # ── Arrancar la recursión (primer turno: jugador) ──────
    escribir_log(f"¡Que comience la batalla! {jugador.nombre} vs {hollow.nombre}")
    redibujar_todo()

    ejecutar_turno_recursivo(
        jugador=jugador,
        hollow=hollow,
        turno_jugador=True,
        callback_actualizar_ui=callback_actualizar_ui,
        callback_fin=callback_fin,
    )


# ── Helpers ────────────────────────────────────────────────

def _turno_jugador_ataca(jugador: Entrenador, hollow: Entrenador) -> dict:
    """
    Procesa el ataque del jugador. Idéntico a calcular_turno
    pero con la acción fijada a 'atacar'.
    """
    act = jugador.personaje_activo()
    dfd = hollow.personaje_activo()
    danio = act.calcular_danio(dfd)
    dfd.recibir_danio(danio)
    ko = dfd.esta_ko()
    msg = f"{act.nombre} atacó a {dfd.nombre} causando {danio} de daño."
    if ko:
        msg += f" ¡{dfd.nombre} fue derrotado!"
        capturado = dfd
        hollow.personajes.remove(capturado)
        jugador.capturar(capturado)
        # Cambiar activo del hollow al siguiente vivo
        for i, p in enumerate(hollow.personajes):
            if not p.esta_ko():
                hollow.activo = min(hollow.activo, len(hollow.personajes) - 1)
                break
    return {"ko": ko, "mensaje": msg, "accion": "atacar"}


def _ventana_cambio(ventana_padre, jugador: Entrenador, al_cambiar):
    """
    Abre una pequeña ventana para elegir el personaje de reemplazo.
    Solo muestra los personajes vivos que no sean el activo.
    """
    win = tk.Toplevel(ventana_padre)
    win.title("Cambiar personaje")
    win.geometry("280x260")
    win.config(bg="#0d0d1a")
    win.resizable(False, False)

    tk.Label(
        win, text="Elige un personaje:",
        font=("Georgia", 12, "bold"),
        fg="#c9a84c", bg="#0d0d1a",
    ).pack(pady=12)

    disponibles = [
        (i, p) for i, p in enumerate(jugador.personajes)
        if i != jugador.activo and not p.esta_ko()
    ]

    if not disponibles:
        tk.Label(
            win, text="No hay personajes disponibles.",
            font=("Courier", 10), fg="#e8e8e8", bg="#0d0d1a",
        ).pack(pady=20)
        tk.Button(win, text="Cerrar", command=win.destroy,
                  bg="#16213e", fg="#e8e8e8", relief="flat").pack()
        return

    for idx, p in disponibles:
        def elegir(i=idx):
            jugador.activo = i
            win.destroy()
            al_cambiar()

        tk.Button(
            win,
            text=f"{p.nombre}\nHP: {p.hp_actual}/{p.hp_max}",
            font=("Courier", 10),
            bg="#16213e", fg="#e8e8e8",
            activebackground="#c9a84c", activeforeground="#0d0d1a",
            relief="flat", pady=6, width=22,
            command=elegir,
        ).pack(pady=4, padx=20, fill="x")


def _crear_panel_entrenador(parent, entrenador: Entrenador, lado: str) -> dict:
    """
    Crea el panel visual de un entrenador (nombre, HP, equipo).
    Devuelve un diccionario con referencias a los widgets
    para poder actualizarlos durante la batalla.
    """
    frame = tk.Frame(parent, bg="#1a1a2e", pady=12, padx=16, relief="flat")
    frame.pack(side=lado, expand=True, fill="both", padx=10)

    tk.Label(
        frame, text=entrenador.nombre,
        font=("Georgia", 12, "bold"),
        fg="#c9a84c", bg="#1a1a2e",
    ).pack()

    p = entrenador.personaje_activo()

    label_personaje = tk.Label(
        frame, text=p.nombre,
        font=("Courier", 11),
        fg="#e8e8e8", bg="#1a1a2e",
    )
    label_personaje.pack(pady=(4, 2))

    # Barra de HP usando Canvas
    canvas_hp = tk.Canvas(frame, width=200, height=18, bg="#333", highlightthickness=0)
    canvas_hp.pack(pady=2)
    rect_hp = canvas_hp.create_rectangle(0, 0, 200, 18, fill="#4caf72", outline="")

    label_hp = tk.Label(
        frame, text=f"{p.hp_actual} / {p.hp_max} HP",
        font=("Courier", 9),
        fg="#e8e8e8", bg="#1a1a2e",
    )
    label_hp.pack()

    label_puntaje = tk.Label(
        frame, text=f"Puntaje: {entrenador.puntaje}",
        font=("Courier", 10),
        fg="#c9a84c", bg="#1a1a2e",
    )
    label_puntaje.pack(pady=(6, 2))

    # Íconos del equipo (hasta 3 + los capturados)
    frame_equipo = tk.Frame(frame, bg="#1a1a2e")
    frame_equipo.pack()

    iconos = []
    for _ in range(6):   # máximo 6 (3 iniciales + 3 posibles capturas)
        lbl = tk.Label(frame_equipo, text=" ", font=("Arial", 14),
                       bg="#1a1a2e", width=2)
        lbl.pack(side="left")
        iconos.append(lbl)

    return {
        "label_personaje": label_personaje,
        "label_hp":        label_hp,
        "label_puntaje":   label_puntaje,
        "canvas_hp":       canvas_hp,
        "rect_hp":         rect_hp,
        "iconos_equipo":   iconos,
    }


def _boton(parent, texto: str, comando) -> tk.Button:
    btn = tk.Button(
        parent, text=texto, command=comando,
        font=("Georgia", 12, "bold"),
        fg="#c9a84c", bg="#16213e",
        activeforeground="#0d0d1a",
        activebackground="#c9a84c",
        relief="flat", padx=18, pady=8,
        cursor="hand2",
    )
    btn.bind("<Enter>", lambda e: btn.config(bg="#0f3460") if str(btn["state"]) != "disabled" else None)
    btn.bind("<Leave>", lambda e: btn.config(bg="#16213e") if str(btn["state"]) != "disabled" else None)
    return btn


def _nombre_tierra(idx: int) -> str:
    NOMBRES = [
        "Radiator Springs", "Pride Rock", "Monstropolis",
        "Neverland", "Agrabah"
    ]
    return NOMBRES[idx] if idx < len(NOMBRES) else "Desconocida"


def _mostrar_resultado_y_volver(
    ventana, jugador, avatar, todos_personajes,
    completadas, idx_tierra, jugador_gano, mensaje
):
    """
    Muestra el resultado final de la batalla.
    Si el jugador ganó todas las tierras, muestra pantalla de victoria.
    Si perdió, ofrece volver al mapa (si aún tiene personajes).
    """
    if all(completadas):
        # ── Victoria total ─────────────────────────────────
        for w in ventana.winfo_children():
            w.destroy()
        ventana.config(bg="#0d0d1a")
        tk.Label(
            ventana,
            text="✦  ¡VICTORIA TOTAL!  ✦",
            font=("Georgia", 32, "bold"),
            fg="#c9a84c", bg="#0d0d1a",
        ).pack(pady=80)
        tk.Label(
            ventana,
            text=f"¡{jugador.nombre} restauró todos los Fragmentos de Memoria!\n"
                 f"Puntaje final: {jugador.puntaje}",
            font=("Courier", 16),
            fg="#e8e8e8", bg="#0d0d1a",
        ).pack()
        return

    resultado_ok = messagebox.askokcancel(
        "Resultado de batalla",
        mensaje + "\n\n¿Volver al mapa?"
    )

    if resultado_ok or jugador_gano:
        for w in ventana.winfo_children():
            w.destroy()
        from ventanas.pantalla_mapa import crear_pantalla_mapa
        crear_pantalla_mapa(
            ventana, jugador, avatar, todos_personajes,
            completadas, idx_tierra
        )
