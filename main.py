import tkinter as tk
from ventanas.pantalla_inicial import crear_pantalla_inicio

#hacer la ventana main
ventana=tk.Tk()
ventana.title("Proyecto intro programación")
ventana.geometry("1200x800")

crear_pantalla_inicio(ventana)
ventana.mainloop()
