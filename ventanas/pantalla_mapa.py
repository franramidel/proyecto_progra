import tkinter as tk
from tkinter import messagebox
import random, sys, os
from modelos import cargar_personajes, Entrenador, Personaje
 
# ── Paleta ────────────────────────────────────────────────
COLOR_FONDO    = "#0d0d1a"
COLOR_PANEL    = "#1a1a2e"
COLOR_ACENTO   = "#c9a84c"
COLOR_TEXTO    = "#e8e8e8"
COLOR_BOTON    = "#16213e"
COLOR_HOV      = "#0f3460"
COLOR_VERDE    = "#4caf72"   # Ubicación completada
COLOR_ROJO     = "#e05c5c"   # Hollow activo / peligro
 
# ── Definición de las 5 tierras ───────────────────────────
TIERRAS = [
    {"nombre": "Radiator Springs",  "hollow": "Hollow del Camino"},
    {"nombre": "Pride Rock",         "hollow": "Hollow del Rey"},
    {"nombre": "Monstropolis",       "hollow": "Hollow del Miedo"},
    {"nombre": "Neverland",          "hollow": "Hollow del Olvido"},
    {"nombre": "Agrabah",            "hollow": "Hollow del Engaño"},
]
 
 
def crear_pantalla_mapa(
    ventana: tk.Tk,
    jugador: Entrenador,
    avatar: str,
    todos_personajes: list[Personaje],
    completadas: list = None,
    ubicacion_actual: int = 0,
):
    """
    Dibuja el mapa con las 5 ubicaciones y el estado del jugador.
 
    Parámetros:
      ventana          : ventana principal de Tkinter
      jugador          : entrenador del jugador con su equipo
      avatar           : string del avatar elegido
      todos_personajes : lista completa de 15 personajes (para Hollows)
      completadas      : lista de bool indicando tierras terminadas
      ubicacion_actual : índice de la tierra seleccionada ahora
    """
    ventana.config(bg=COLOR_FONDO)
 
    # Primera vez: ninguna tierra completada
    if completadas is None:
        completadas = [False] * len(TIERRAS)
 
    # Variable mutable para la selección actual del mapa.
    # Usamos una lista de un elemento para poder modificarla
    # desde funciones internas (las variables normales serían
    # de solo lectura dentro de las funciones anidadas).
    seleccion = [ubicacion_actual]
 
    # ── Título ─────────────────────────────────────────────
    tk.Label(
        ventana,
        text="✦  MAPA DEL IMAGINARIO  ✦",
        font=("Georgia", 22, "bold"),
        fg=COLOR_ACENTO, bg=COLOR_FONDO,
    ).pack(pady=(24, 4))
 
    # Progreso
    n_completadas = sum(completadas)
    tk.Label(
        ventana,
        text=f"Fragmentos restaurados: {n_completadas} / {len(TIERRAS)}",
        font=("Courier", 11),
        fg=COLOR_TEXTO, bg=COLOR_FONDO,
    ).pack()
 
    tk.Frame(ventana, height=2, bg=COLOR_ACENTO).pack(fill="x", padx=60, pady=10)
 
    # ── Fila de ubicaciones ────────────────────────────────
    frame_mapa = tk.Frame(ventana, bg=COLOR_FONDO)
    frame_mapa.pack(pady=10)
 
    botones_tierra = []   # Guardamos referencias para actualizar colores
 
    def seleccionar_tierra(idx: int):
        """
        Actualiza la tierra seleccionada y redibuja los botones.
        Los botones que ya están completados no se pueden pelear
        (muestran un ícono de completado).
        """
        seleccion[0] = idx
        for i, btn in enumerate(botones_tierra):
            if i == idx:
                btn.config(bg=COLOR_ACENTO, fg=COLOR_FONDO)
            elif completadas[i]:
                btn.config(bg=COLOR_VERDE, fg=COLOR_FONDO)
            else:
                btn.config(bg=COLOR_BOTON, fg=COLOR_TEXTO)
        # Actualizar el panel de info de la tierra seleccionada
        actualizar_info_tierra(idx)
 
    for i, tierra in enumerate(TIERRAS):
        icono = "✓" if completadas[i] else str(i + 1)
        color_bg = COLOR_VERDE if completadas[i] else COLOR_BOTON
        # lambda i=i: captura el valor ACTUAL de i en cada iteración
        # Sin el i=i, todos los botones usarían el último valor de i
        btn = tk.Button(
            frame_mapa,
            text=f"{icono}\n{tierra['nombre']}",
            font=("Georgia", 10, "bold"),
            fg=COLOR_TEXTO, bg=color_bg,
            activeforeground=COLOR_FONDO,
            activebackground=COLOR_ACENTO,
            relief="flat", padx=12, pady=14,
            width=14, cursor="hand2",
            command=lambda i=i: seleccionar_tierra(i),
        )
        btn.pack(side="left", padx=6)
        botones_tierra.append(btn)
 
    # ── Panel de información de la tierra seleccionada ────
    frame_info = tk.Frame(ventana, bg=COLOR_PANEL, pady=16)
    frame_info.pack(fill="x", padx=60, pady=12)
 
    label_tierra_nombre = tk.Label(
        frame_info, text="", font=("Georgia", 14, "bold"),
        fg=COLOR_ACENTO, bg=COLOR_PANEL,
    )
    label_tierra_nombre.pack()
 
    label_hollow = tk.Label(
        frame_info, text="", font=("Courier", 11),
        fg=COLOR_TEXTO, bg=COLOR_PANEL,
    )
    label_hollow.pack()
 
    label_estado = tk.Label(
        frame_info, text="", font=("Courier", 10, "italic"),
        fg=COLOR_VERDE, bg=COLOR_PANEL,
    )
    label_estado.pack(pady=4)
 
    def actualizar_info_tierra(idx: int):
        tierra = TIERRAS[idx]
        label_tierra_nombre.config(text=f"📍 {tierra['nombre']}")
        label_hollow.config(text=f"Hollow: {tierra['hollow']}")
        if completadas[idx]:
            label_estado.config(text="✓ Fragmento restaurado", fg=COLOR_VERDE)
        else:
            label_estado.config(text="⚠ Hollow activo — ¡Debes derrotarlo!", fg=COLOR_ROJO)
 
    # Mostrar info de la tierra inicial
    actualizar_info_tierra(seleccion[0])
    seleccionar_tierra(seleccion[0])
 
    # ── Panel del jugador ──────────────────────────────────
    frame_jugador = tk.Frame(ventana, bg=COLOR_FONDO)
    frame_jugador.pack(pady=6)
 
    tk.Label(
        frame_jugador,
        text=f"{avatar}  {jugador.nombre}   |   "
             f"Puntaje: {jugador.puntaje}   |   "
             f"Personajes: {len([p for p in jugador.personajes if not p.esta_ko()])} activos",
        font=("Courier", 11),
        fg=COLOR_TEXTO, bg=COLOR_FONDO,
    ).pack()
 
    # ── Botón PELEAR ───────────────────────────────────────
    frame_botones = tk.Frame(ventana, bg=COLOR_FONDO)
    frame_botones.pack(pady=14)
 
    def ir_a_batalla():
        """
        Valida que la tierra no esté completada y lanza la batalla.
        El Hollow recibe 3 personajes aleatorios distintos a los del jugador.
 
        CORRECCIÓN: la variable local para el equipo del hollow se llama
        'equipo_seleccion' para no pisar la variable de cierre 'seleccion'
        (que almacena el índice de tierra activo).  Antes se llamaba igual
        y Python la trataba como local en toda la función, provocando un
        UnboundLocalError al leer seleccion[0] y el botón no hacía nada.
        """
        idx = seleccion[0]
        if completadas[idx]:
            messagebox.showinfo(
                "Tierra libre",
                f"Ya restauraste {TIERRAS[idx]['nombre']}. "
                "Elige otra tierra."
            )
            return
 
        # Construir equipo del Hollow: 3 personajes aleatorios
        # preferentemente distintos a los del jugador
        nombres_jugador = {p.nombre for p in jugador.personajes}
        disponibles = [
            p for p in todos_personajes if p.nombre not in nombres_jugador
        ]
        # Si no hay suficientes distintos, tomamos de la lista completa
        if len(disponibles) < 3:
            disponibles = list(todos_personajes)
 
        # CORRECCIÓN: nombre diferente a 'seleccion' para no crear
        # variable local que tape la del cierre externo.
        equipo_seleccion = random.sample(disponibles, 3)
        equipo_hollow = [
            Personaje(p.nombre, p.hp_max, p.atk, p.defensa)
            for p in equipo_seleccion
        ]
 
        # Restauramos vida de los personajes del hollow (nuevos)
        for p in equipo_hollow:
            p.restaurar_vida()
 
        hollow = Entrenador(TIERRAS[idx]["hollow"], equipo_hollow)
 
        # Limpiar ventana y cargar batalla
        for widget in ventana.winfo_children():
            widget.destroy()
 
        from ventanas.pantalla_batalla import crear_pantalla_batalla
        crear_pantalla_batalla(
            ventana, jugador, hollow, avatar,
            todos_personajes, completadas, idx
        )
 
    btn_pelear = tk.Button(
        frame_botones,
        text="⚔  PELEAR",
        font=("Georgia", 13, "bold"),
        fg=COLOR_FONDO, bg=COLOR_ACENTO,
        activeforeground=COLOR_FONDO,
        activebackground=COLOR_TEXTO,
        relief="flat", padx=20, pady=10,
        cursor="hand2",
        command=ir_a_batalla,
    )
    btn_pelear.pack(side="left", padx=10)
    btn_pelear.bind("<Enter>", lambda e: btn_pelear.config(bg="#e8c86a"))
    btn_pelear.bind("<Leave>", lambda e: btn_pelear.config(bg=COLOR_ACENTO))