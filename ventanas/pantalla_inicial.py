#ventana main
import tkinter as tk
from tkinter import messagebox
from modelos import cargar_personajes,Personaje,Entrenador

color_fondo="#0d0d1a"
color_panel="#1a1a2e"
color_acento="#c9a84c"
color_texto="#e8e8e8"
color_boton="#16213e"
color_boton_hover="#0f3460" #color de cuando se pasa el mouse encima
color_check_selec="#c9a84c" #color del checkbox seleccionado
color_error="#e05c5c"

#helpers de ui
def _label(parent, texto: str) -> tk.Label:
    #Crea un Label con estilo estándar del juego.
    return tk.Label(
            parent, text=texto,
            font=("Georgia", 11, "bold"),
            fg=color_acento, bg=color_fondo,
        )
 
 
def _boton(parent, texto: str, comando) -> tk.Button:
    
   
    #hover_enter / hover_leave cambian el color al pasar el mouse
    btn = tk.Button(
        parent, text=texto, command=comando,
        font=("Georgia", 12, "bold"),
        fg=color_acento, bg=color_boton,
        activeforeground=color_fondo,
        activebackground=color_acento,
        relief="flat", padx=18, pady=8,
        cursor="hand2",
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=color_boton_hover))
    btn.bind("<Leave>", lambda e: btn.config(bg=color_boton))
    return btn
 
 
def _fila_personaje(
    parent,
    personaje: Personaje,
    var: tk.IntVar,
    todos_vars: dict,
):
    
    #Dibuja una fila interactiva para un personaje.
 
    #Al marcar el 4to personaje se muestra aviso; al desmarcar
    #se restaura el estado sin problema.
 
    
    frame_fila = tk.Frame(parent, bg=color_fondo)
    frame_fila.pack(fill="x", pady=1)
 
    def al_cambiar():
        seleccionados = sum(v.get() for v in todos_vars.values())
        if seleccionados > 3:
            var.set(0)   # Rechaza la selección del 4to
 
    tk.Checkbutton(
        frame_fila,
        variable=var,
        command=al_cambiar,
        bg=color_fondo,
        fg=color_texto,
        selectcolor=color_panel,
        activebackground=color_fondo,
        width=2,
    ).pack(side="left")
 
    for texto, ancho in [
        (personaje.nombre, 18),
        (str(personaje.hp_max), 6),
        (str(personaje.atk), 6),
        (str(personaje.defensa), 6),
    ]:
        tk.Label(
            frame_fila, text=texto, width=ancho,
            font=("Courier", 10),
            fg=color_texto, bg=color_fondo,
            anchor="w",
        ).pack(side="left", padx=2)
 
 
def _abrir_about():
    
    #Abre una ventana emergente con información del proyecto.
    
    ventana_about = tk.Toplevel()
    ventana_about.title("Acerca del proyecto")
    ventana_about.geometry("480x400")
    ventana_about.config(bg=color_fondo)
    ventana_about.resizable(False, False)
 
    tk.Label(
        ventana_about,
        text="✦  ABOUT  ✦",
        font=("Georgia", 18, "bold"),
        fg=color_acento, bg=color_fondo,
    ).pack(pady=(20, 4))
 
    tk.Frame(ventana_about, height=2, bg=color_acento).pack(fill="x", padx=40, pady=4)
 
    info = (
        "Proyecto 1 — Introducción a la Programación\n"
        "Tecnológico de Costa Rica\n"
        "Escuela de Ingeniería en Computadores\n"
        "I Semestre 2026\n\n"
        "Profesores:\n"
        "  • Santiago Ramírez\n"
        "  • Ellioth Ramírez\n\n"
        "Estudiante:\n"
        "  Francisco Ramirez Delgado\n"
        "  Carné: 2025112972\n\n"
        "Descripción:\n"
        "  Juego de batalla por turnos.\n"
        "  El jugador actúa como Guardián de las Historias,\n"
        "  derrotando a los 5 Huecos para restaurar\n"
        "  los Fragmentos de Memoria."
    )
 
    tk.Label(
        ventana_about,
        text=info,
        font=("Courier", 10),
        fg=color_texto, bg=color_fondo,
        justify="left",
    ).pack(padx=30, pady=8)
 
    _boton(ventana_about, "Cerrar", ventana_about.destroy).pack(pady=10)
    
    #transicion hacia el mapa
def _ir_a_mapa(ventana, jugador, avatar, todos_personajes):
    #limpia los widgets y carga la pantalla del mapa
    for widget in ventana.winfo_children():
        widget.destroy()
        # importación aquí adentro para evitar importaciones circulares
    from ventanas.pantalla_mapa import crear_pantalla_mapa
    crear_pantalla_mapa(ventana, jugador, avatar, todos_personajes)

#pantalla main

def crear_pantalla_inicio(ventana:tk.Tk):
    
    todos_personajes=cargar_personajes("personajes.txt")
    
    ventana.config(bg=color_fondo)
    
    #encabezado

    frame_titulo=tk.Frame(ventana,bg=color_fondo)
    frame_titulo.pack(pady=(30,10))
    
    tk.Label(frame_titulo,text="Imaginary Battles",font=("Georgia",26,"bold"),fg=color_acento,bg=color_fondo).pack()
    tk.Label(frame_titulo,text="guardian de las historias",font=("Georgia",13,"italic"),fg=color_texto,bg=color_fondo).pack(pady=(2,0))    

    #separador decorativo
    tk.Frame(ventana, height=2, bg=color_acento).pack(fill="x", padx=60, pady=8)

    #area central (nombre, personajes y el avatar)
    frame_central=tk.Frame(ventana,bg=color_fondo)
    frame_central.pack(fill="both",expand=True,padx=60)

    #columna izq: nombre y avatar
    frame_izq = tk.Frame(frame_central, bg=color_fondo)
    frame_izq.pack(side="left", fill="y", padx=(0, 30))

    #nombre
    _label(frame_izq, "⟣  Tu nombre de Guardián:").pack(anchor="w", pady=(0, 4))
    nombre_entry = tk.Entry(
        frame_izq,
        font=("Courier", 13),
        bg=color_panel,
        fg=color_texto,
        insertbackground=color_acento,
        relief="flat",
        width=22,
    )
    nombre_entry.pack(anchor="w", ipady=6)
    
    #avatar
    _label(frame_izq, "\n⟣  Elige tu avatar:").pack(anchor="w", pady=(16, 4))
 
    avatares = ["⚔️  Guerrero", "🛡️  Defensor", "✨  Mago"]
    avatar_var = tk.StringVar(value=avatares[0])   # Seleccionado por defecto
 
    for av in avatares:
        tk.Radiobutton(
            frame_izq,
            text=av,
            variable=avatar_var,
            value=av,
            font=("Courier", 11),
            bg=color_fondo,
            fg=color_texto,
            selectcolor=color_panel,
            activebackground=color_fondo,
            activeforeground=color_acento,
        ).pack(anchor="w", pady=2)
        
        
    #columna derecha: lista de personajes
    frame_der = tk.Frame(frame_central, bg=color_fondo)
    frame_der.pack(side="left", fill="both", expand=True)
 
    _label(frame_der, "⟣  Selecciona exactamente 3 personajes:").pack(anchor="w", pady=(0, 6))
    
    #encabezado de la tabla
    frame_header = tk.Frame(frame_der, bg=color_panel)
    frame_header.pack(fill="x", pady=(0, 2))
    for texto, ancho in [("✔", 3), ("Nombre", 18), ("HP", 6), ("ATK", 6), ("DEF", 6)]:
        tk.Label(
            frame_header, text=texto, width=ancho,
            font=("Courier", 10, "bold"),
            fg=color_acento, bg=color_panel,
        ).pack(side="left", padx=2)
        
    #diccionario: nombre personaje a intvar (1=seleccionado, 0=no)
    checks_vars: dict[str, tk.IntVar] = {}
 
    # Frame con scroll para los 15 personajes
    frame_lista = tk.Frame(frame_der, bg=color_fondo)
    frame_lista.pack(fill="both")
 
    for p in todos_personajes:
        var = tk.IntVar()
        checks_vars[p.nombre] = var
        _fila_personaje(frame_lista, p, var, checks_vars)

    #mensaje de error/validacion
    mensaje_label = tk.Label(
        ventana, text="", font=("Courier", 11),
        fg=color_error, bg=color_fondo,
    )
    mensaje_label.pack(pady=4)

    #botones
    
    frame_botones = tk.Frame(ventana, bg=color_fondo)
    frame_botones.pack(pady=12)
 
    def iniciar_juego():
        """
        Valida la selección y pasa a la pantalla de mapa.
        Reglas:
          el nombre no puede estar vacío.
          se deben seleccionar EXACTAMENTE 3 personajes.
        """
        nombre = nombre_entry.get().strip()
        if not nombre:
            mensaje_label.config(text="⚠  Debes ingresar un nombre.")
            return

        # Filtramos los personajes cuya IntVar vale 1
        seleccionados = [
            p for p in todos_personajes
            if checks_vars[p.nombre].get() == 1
        ]

        if len(seleccionados) != 3:
            mensaje_label.config(
                text=f"⚠  Selecciona exactamente 3 personajes "
                     f"(tienes {len(seleccionados)})."
            )
            return

        # Todo válido: creamos el entrenador del jugador
        jugador = Entrenador(nombre, seleccionados)
        avatar  = avatar_var.get()

        mensaje_label.config(text="")
        _ir_a_mapa(ventana, jugador, avatar, todos_personajes)
 
    _boton(frame_botones, "⚔  INICIAR", iniciar_juego).pack(side="left", padx=12)
    _boton(frame_botones, "  ABOUT",  _abrir_about).pack(side="left", padx=12)
    
    
    
 
    
    
    

    