#pantalla de batalla
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
 
from modelos import Entrenador, Personaje
from logica_batalla import ejecutar_turno_recursivo, calcular_turno
 
# colores
COLOR_FONDO  = "#0d0d1a"
COLOR_PANEL  = "#1a1a2e"
COLOR_ACENTO = "#c9a84c"
COLOR_TEXTO  = "#e8e8e8"
COLOR_BOTON  = "#16213e"
COLOR_HOV    = "#0f3460"
COLOR_VERDE  = "#4caf72"
COLOR_ROJO   = "#e05c5c"
COLOR_HP_OK  = "#4caf72"
COLOR_HP_LOW = "#e05c5c"
COLOR_HP_MED = "#f0a500"
 
 
# ── Manejo de imágenes ─────────────────────────────────────
# Guardado a nivel global para que Tkinter no borre las
# imágenes de memoria mientras se están mostrando.
_cache_imagenes: dict = {}
 
def cargar_imagen_personaje(ruta: str, ancho: int = 180, alto: int = 180):
    """
    Carga una imagen PNG con Pillow, la redimensiona y la
    convierte a formato que entiende Tkinter (PhotoImage).
    Si el archivo no existe devuelve None y se muestra
    la inicial del personaje como placeholder.
    """
    if ruta in _cache_imagenes:
        return _cache_imagenes[ruta]
    try:
        img = Image.open(ruta)
        img = img.resize((ancho, alto), Image.LANCZOS)
        foto = ImageTk.PhotoImage(img)
        _cache_imagenes[ruta] = foto
        return foto
    except FileNotFoundError:
        return None
 
 
# ── Helpers ────────────────────────────────────────────────
 
def _boton(parent, texto: str, comando) -> tk.Button:
    btn = tk.Button(
        parent, text=texto, command=comando,
        font=("Georgia", 12, "bold"),
        fg=COLOR_ACENTO, bg=COLOR_BOTON,
        activeforeground=COLOR_FONDO,
        activebackground=COLOR_ACENTO,
        relief="flat", padx=18, pady=8,
        cursor="hand2",
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=COLOR_HOV) if str(btn["state"]) != "disabled" else None)
    btn.bind("<Leave>", lambda e: btn.config(bg=COLOR_BOTON) if str(btn["state"]) != "disabled" else None)
    return btn
 
 
def _crear_panel_entrenador(parent, entrenador: Entrenador, lado: str) -> dict:
    """
    Crea el panel visual de un entrenador (nombre, imagen, HP, equipo).
    Devuelve un diccionario con referencias a los widgets
    para poder actualizarlos durante la batalla.
    """
    frame = tk.Frame(parent, bg=COLOR_PANEL, pady=12, padx=16, relief="flat")
    frame.pack(side=lado, expand=True, fill="both", padx=10)
 
    tk.Label(
        frame, text=entrenador.nombre,
        font=("Georgia", 12, "bold"),
        fg=COLOR_ACENTO, bg=COLOR_PANEL,
    ).pack()
 
    p = entrenador.personaje_activo()
 
    # imagen del personaje activo
    # si no existe el archivo muestra la inicial del nombre
    foto = cargar_imagen_personaje(p.imagen_ruta)
    label_imagen = tk.Label(
        frame,
        image=foto if foto else None,
        text="" if foto else p.nombre[0],
        font=("Georgia", 48, "bold"),
        fg=COLOR_ACENTO, bg=COLOR_PANEL,
        width=180, height=180,
    )
    label_imagen.imagen = foto  # evita que Python borre la imagen de memoria
    label_imagen.pack(pady=4)
 
    label_personaje = tk.Label(
        frame, text=p.nombre,
        font=("Courier", 11),
        fg=COLOR_TEXTO, bg=COLOR_PANEL,
    )
    label_personaje.pack(pady=(4, 2))
 
    # barra de HP usando Canvas
    canvas_hp = tk.Canvas(frame, width=200, height=18, bg="#333", highlightthickness=0)
    canvas_hp.pack(pady=2)
    rect_hp = canvas_hp.create_rectangle(0, 0, 200, 18, fill=COLOR_HP_OK, outline="")
 
    label_hp = tk.Label(
        frame, text=f"{p.hp_actual} / {p.hp_max} HP",
        font=("Courier", 9),
        fg=COLOR_TEXTO, bg=COLOR_PANEL,
    )
    label_hp.pack()
 
    label_puntaje = tk.Label(
        frame, text=f"Puntaje: {entrenador.puntaje}",
        font=("Courier", 10),
        fg=COLOR_ACENTO, bg=COLOR_PANEL,
    )
    label_puntaje.pack(pady=(6, 2))
 
    # iconos del equipo
    frame_equipo = tk.Frame(frame, bg=COLOR_PANEL)
    frame_equipo.pack()
 
    iconos = []
    for _ in range(6):
        lbl = tk.Label(frame_equipo, text=" ", font=("Arial", 14),
                       bg=COLOR_PANEL, width=2)
        lbl.pack(side="left")
        iconos.append(lbl)
 
    return {
        "label_imagen":    label_imagen,
        "label_personaje": label_personaje,
        "label_hp":        label_hp,
        "label_puntaje":   label_puntaje,
        "canvas_hp":       canvas_hp,
        "rect_hp":         rect_hp,
        "iconos_equipo":   iconos,
    }
 
 
def _turno_jugador_ataca(jugador: Entrenador, hollow: Entrenador) -> dict:
    """
    Procesa el ataque del jugador contra el hollow.
 
    CORRECCIÓN: se eliminó la captura inline que hacía aquí.
    La captura se delega completamente a _procesar_captura()
    en logica_batalla.py para evitar la doble captura que
    ocurría cuando ko=True: antes se capturaba aquí Y luego
    _procesar_captura volvía a capturar otro personaje del hollow.
    """
    act = jugador.personaje_activo()
    dfd = hollow.personaje_activo()
    danio = act.calcular_danio(dfd)
    dfd.recibir_danio(danio)
    ko = dfd.esta_ko()
    msg = f"{act.nombre} atacó a {dfd.nombre} causando {danio} de daño."
    if ko:
        msg += f" ¡{dfd.nombre} fue derrotado!"
    return {"ko": ko, "mensaje": msg, "accion": "atacar"}
 
 
def _ventana_cambio(ventana_padre, jugador: Entrenador, al_cambiar):
    """
    Abre una ventana con barra de scroll para elegir el personaje de
    reemplazo. Muestra solo los personajes vivos que no sean el activo.
    """
    disponibles = [
        (i, p) for i, p in enumerate(jugador.personajes)
        if i != jugador.activo and not p.esta_ko()
    ]
 
    # Altura dinámica: 80px por botón, máximo 400px
    alto_ventana = min(120 + len(disponibles) * 80, 400)
 
    win = tk.Toplevel(ventana_padre)
    win.title("Cambiar personaje")
    win.geometry(f"300x{alto_ventana}")
    win.config(bg=COLOR_FONDO)
    win.resizable(False, True)
 
    tk.Label(
        win, text="Elige un personaje:",
        font=("Georgia", 12, "bold"),
        fg=COLOR_ACENTO, bg=COLOR_FONDO,
    ).pack(pady=10)
 
    if not disponibles:
        tk.Label(
            win, text="No hay personajes disponibles.",
            font=("Courier", 10), fg=COLOR_TEXTO, bg=COLOR_FONDO,
        ).pack(pady=20)
        tk.Button(win, text="Cerrar", command=win.destroy,
                  bg=COLOR_BOTON, fg=COLOR_TEXTO, relief="flat").pack()
        return
 
    # Área scrolleable: Canvas + Scrollbar
    frame_scroll = tk.Frame(win, bg=COLOR_FONDO)
    frame_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
 
    scrollbar = tk.Scrollbar(frame_scroll, orient="vertical")
    scrollbar.pack(side="right", fill="y")
 
    canvas = tk.Canvas(
        frame_scroll,
        bg=COLOR_FONDO,
        highlightthickness=0,
        yscrollcommand=scrollbar.set,
    )
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=canvas.yview)
 
    frame_botones = tk.Frame(canvas, bg=COLOR_FONDO)
    canvas_window = canvas.create_window((0, 0), window=frame_botones, anchor="nw")
 
    def _ajustar_ancho(event):
        canvas.itemconfig(canvas_window, width=event.width)
    canvas.bind("<Configure>", _ajustar_ancho)
 
    def _actualizar_scroll(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    frame_botones.bind("<Configure>", _actualizar_scroll)
 
    def _rueda(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind("<MouseWheel>", _rueda)
 
    for idx, p in disponibles:
        def elegir(i=idx):
            jugador.activo = i
            win.destroy()
            al_cambiar()
 
        tk.Button(
            frame_botones,
            text=f"{p.nombre}\nHP: {p.hp_actual}/{p.hp_max}",
            font=("Courier", 10),
            bg=COLOR_BOTON, fg=COLOR_TEXTO,
            activebackground=COLOR_ACENTO, activeforeground=COLOR_FONDO,
            relief="flat", pady=6, width=24,
            command=elegir,
        ).pack(pady=4, padx=10, fill="x")
 
 
def _nombre_tierra(idx: int) -> str:
    nombres = [
        "Radiator Springs", "Pride Rock", "Monstropolis",
        "Neverland", "Agrabah"
    ]
    return nombres[idx] if idx < len(nombres) else "Desconocida"
 
 
def _mostrar_resultado_y_volver(
    ventana, jugador, avatar, todos_personajes,
    completadas, idx_tierra, jugador_gano, mensaje
):
    """
    Muestra el resultado de la batalla y vuelve al mapa.
    Si se completaron todas las tierras muestra pantalla de victoria.
 
    CORRECCIÓN: se cambió askokcancel por showinfo y la navegación
    de vuelta al mapa es siempre incondicional.  Antes, si el jugador
    perdía y presionaba "Cancel" en askokcancel, la condición
    (resultado_ok or jugador_gano) era False y la pantalla quedaba
    congelada sin forma de volver al mapa.
    """
    if all(completadas):
        for w in ventana.winfo_children():
            w.destroy()
        ventana.config(bg=COLOR_FONDO)
        tk.Label(
            ventana,
            text="✦  ¡VICTORIA TOTAL!  ✦",
            font=("Georgia", 32, "bold"),
            fg=COLOR_ACENTO, bg=COLOR_FONDO,
        ).pack(pady=80)
        tk.Label(
            ventana,
            text=f"¡{jugador.nombre} restauró todos los Fragmentos de Memoria!\n"
                 f"Puntaje final: {jugador.puntaje}",
            font=("Courier", 16),
            fg=COLOR_TEXTO, bg=COLOR_FONDO,
        ).pack()
        return
 
    # Mostrar resultado y siempre volver al mapa al cerrar el diálogo
    messagebox.showinfo("Resultado de batalla", mensaje)
 
    for w in ventana.winfo_children():
        w.destroy()
    from ventanas.pantalla_mapa import crear_pantalla_mapa
    crear_pantalla_mapa(
        ventana, jugador, avatar, todos_personajes,
        completadas, idx_tierra
    )
 
 
# ── Pantalla principal de batalla ──────────────────────────
 
def crear_pantalla_batalla(
    ventana: tk.Tk,
    jugador: Entrenador,
    hollow: Entrenador,
    avatar: str,
    todos_personajes: list[Personaje],
    completadas: list,
    idx_tierra: int,
):
    """Construye la pantalla de batalla y arranca el motor de turnos."""
    ventana.config(bg=COLOR_FONDO)
 
    tk.Label(
        ventana,
        text="⚔  BATALLA  ⚔",
        font=("Georgia", 20, "bold"),
        fg=COLOR_ACENTO, bg=COLOR_FONDO,
    ).pack(pady=(16, 4))
 
    tk.Frame(ventana, height=2, bg=COLOR_ACENTO).pack(fill="x", padx=60, pady=4)
 
    # paneles de combatientes
    frame_combate = tk.Frame(ventana, bg=COLOR_FONDO)
    frame_combate.pack(fill="x", padx=40, pady=8)
 
    panel_hollow  = _crear_panel_entrenador(frame_combate, hollow,  lado="left")
    panel_jugador = _crear_panel_entrenador(frame_combate, jugador, lado="right")
 
    # log de batalla
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
 
    # botones de accion
    frame_acciones = tk.Frame(ventana, bg=COLOR_FONDO)
    frame_acciones.pack(pady=12)
 
    btn_atacar  = _boton(frame_acciones, "⚔  ATACAR",   None)
    btn_atacar.pack(side="left", padx=10)
 
    btn_cambiar = _boton(frame_acciones, "🔄  CAMBIAR", None)
    btn_cambiar.pack(side="left", padx=10)
 
    label_turno = tk.Label(
        ventana, text="",
        font=("Georgia", 11, "italic"),
        fg=COLOR_TEXTO, bg=COLOR_FONDO,
    )
    label_turno.pack(pady=4)
 
    # funciones de actualizacion de UI
 
    def escribir_log(mensaje: str):
        """Agrega una línea al log de batalla."""
        log_texto.config(state="normal")
        log_texto.insert("end", f"▸ {mensaje}\n")
        log_texto.see("end")
        log_texto.config(state="disabled")
 
    def redibujar_panel(panel_widgets: dict, entrenador: Entrenador):
        """Actualiza imagen, HP y equipo del panel de un entrenador."""
        # sino quedan personajes no hay nada q mostrar
        if not entrenador.personajes:
            return
        p = entrenador.personaje_activo()
 
        # actualizar imagen al cambiar de personaje
        foto = cargar_imagen_personaje(p.imagen_ruta)
        panel_widgets["label_imagen"].config(
            image=foto if foto else None,
            text="" if foto else p.nombre[0],
        )
        panel_widgets["label_imagen"].imagen = foto
 
        panel_widgets["label_personaje"].config(text=p.nombre)
        panel_widgets["label_puntaje"].config(text=f"Puntaje: {entrenador.puntaje}")
 
        porcentaje = p.hp_actual / p.hp_max
        ancho_barra = int(200 * porcentaje)
        color_barra = (
            COLOR_HP_OK  if porcentaje > 0.5 else
            COLOR_HP_MED if porcentaje > 0.25 else
            COLOR_HP_LOW
        )
        panel_widgets["canvas_hp"].coords(panel_widgets["rect_hp"], 0, 0, ancho_barra, 18)
        panel_widgets["canvas_hp"].itemconfig(panel_widgets["rect_hp"], fill=color_barra)
        panel_widgets["label_hp"].config(text=f"{p.hp_actual} / {p.hp_max} HP")
 
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
 
    # motor de turnos con recursividad
 
    def deshabilitar_botones():
        btn_atacar.config(state="disabled",  bg="#333")
        btn_cambiar.config(state="disabled", bg="#333")
 
    def habilitar_botones():
        btn_atacar.config(state="normal",  bg=COLOR_BOTON)
        btn_cambiar.config(state="normal", bg=COLOR_BOTON)
 
    def callback_actualizar_ui(turno_jugador: bool, continuar):
        """
        Recibida por el motor recursivo en cada turno.
        Si es turno del jugador activa los botones y espera click.
        Si es turno del Hollow ejecuta la IA aleatoria.
 
        ¿Qué es 'continuar'?
          Es la función de logica_batalla que dispara el siguiente
          turno recursivo. La llamamos cuando la acción del turno
          actual ya se procesó.
        """
        redibujar_todo()
 
        if turno_jugador:
            label_turno.config(
                text=f"Tu turno, {jugador.nombre}. ¿Qué harás?",
                fg=COLOR_ACENTO,
            )
            habilitar_botones()
 
            def accion_atacar():
                deshabilitar_botones()
                resultado = _turno_jugador_ataca(jugador, hollow)
                escribir_log(resultado["mensaje"])
                redibujar_todo()
                continuar(resultado)
 
            def accion_cambiar():
                _ventana_cambio(ventana, jugador, lambda: (
                    deshabilitar_botones(),
                    redibujar_todo(),
                    escribir_log(f"{jugador.nombre} cambió de personaje."),
                    continuar({"ko": False})
                ))
 
            btn_atacar.config(command=accion_atacar)
            btn_cambiar.config(command=accion_cambiar)
 
        else:
            label_turno.config(text=f"Turno del {hollow.nombre}...", fg=COLOR_ROJO)
            deshabilitar_botones()
 
            # after(ms, func): espera ms milisegundos antes de ejecutar func
            # Simula que el Hollow "piensa" antes de actuar
            def turno_ia():
                resultado = calcular_turno(hollow, jugador)
                escribir_log(resultado["mensaje"])
                redibujar_todo()
                ventana.after(400, lambda: continuar(resultado))
 
            ventana.after(800, turno_ia)
 
    def callback_fin(ganador: Entrenador, perdedor: Entrenador):
        """
        Caso base de la recursión: el combate terminó.
        Determina si el jugador ganó o perdió y navega de vuelta al mapa.
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
 
        ventana.after(1200, lambda: _mostrar_resultado_y_volver(
            ventana, jugador, avatar, todos_personajes,
            completadas, idx_tierra, jugador_gano, mensaje
        ))
 
    # arrancar la recursión (primer turno: jugador)
    escribir_log(f"¡Que comience la batalla! {jugador.nombre} vs {hollow.nombre}")
    redibujar_todo()
 
    ejecutar_turno_recursivo(
        jugador=jugador,
        hollow=hollow,
        turno_jugador=True,
        callback_actualizar_ui=callback_actualizar_ui,
        callback_fin=callback_fin,
    )
 