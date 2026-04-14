#ventana main
import tkinter as tk
def crear_pantalla_inicio(ventana):
    
    ventana.config(bg="lightblue")

    def abrir_ventana_about():
        ventana_about=tk.Toplevel()
        ventana_about.title("informacion")
        texto_about=tk.Label(ventana_about)
        texto_about.config(text="Proyecto 1 - Introducción a la Programación\n"
                "Tecnológico de Costa Rica\n"
                "Escuela de Ingeniería en Computadores\n"
                "I Semestre 2026\n\n"
                "Profesores:\n"
                "• Santiago Ramírez\n"
                "• Ellioth Ramírez\n\n"
                "Estudiante: \n"
                "Francisco Ramirez Delgado 2025112972\n\n"
                "Descripción:\n"
                "Juego de batalla por turnos.\n"
                "El jugador actúa como Guardián de las Historias,\n"
                "derrotando a los 5 Huecos para restaurar\n"
                "los Fragmentos de Memoria.\n\n"
                )
        texto_about.pack()
        
        
    #boton about
    boton_info=tk.Button(ventana, text="About", width=10, height=5, command=abrir_ventana_about)
    boton_info.place(x=1100, y=30)

    #etiqueta del nombre de usuario
    label_nombre=tk.Label(ventana, text="Ingrese su nombre:", bg="lightblue")
    label_nombre.place(x=500, y=200)
    
    #input del nombre de usuario
    nombre_entry=tk.Entry(ventana)
    nombre_entry.place(x=500, y=230)
    
    #boton de iniciar
    def iniciar_juego():
        nombre=nombre_entry.get()
        if nombre == "":
            mensaje_label.config(text="Debe ingresar un nombre")
        else:
            mensaje_label.config(text="")
            print("Jugador:", nombre)    
        
        
    boton_iniciar=tk.Button(ventana, text="INICIAR", command= iniciar_juego)
    boton_iniciar.place(x=550, y=300)
    
    #etiqueta para mensajes
    mensaje_label=tk.Label(ventana, text="", fg="red", bg="lightblue")
    mensaje_label.place(x=500, y=350)
    