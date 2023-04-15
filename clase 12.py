from tkinter import *


# iniciar tkinter

aplicacion = Tk()

# tamano de la ventana

aplicacion.geometry("1020x630+0+0")

# evitar maximizar

aplicacion.resizable(0,0)

# titulo de la ventana

aplicacion.title("Damn Craving - SISTEMA DE FACTURACION")

# color de fondo

aplicacion.config(bg= "cornflowerblue")

#panel superior

panel_superior = Frame(aplicacion, bd=1, relief=FLAT)
panel_superior.pack(side=TOP)

# Etiqueta de titulo

etiqueta_titulo = Label(panel_superior, text="Sistema de Facturación", fg="AntiqueWhite",
                       font=('Dosis', 55), bg="cornflowerblue", width=23)
etiqueta_titulo.grid(row=0, column=0)

# panel izquierdo

panel_izquierdo = Frame(aplicacion, bd=1, relief=FLAT)
panel_izquierdo.pack(side=LEFT)

#panel de costos

panel_costos = Frame(panel_izquierdo, bd=1, relief=FLAT)
panel_costos.pack(side=BOTTOM)

# Panel comidas

panel_comidas = LabelFrame(panel_izquierdo, text='Comidas', font=('Dosis', 19, 'bold'),

                           bd=1, relief=FLAT, fg='azure4')
panel_comidas.pack(side=LEFT)

# Panel bebidas

panel_bebidas = LabelFrame(panel_izquierdo, text='Bebidas', font=('Dosis', 19, 'bold'),
                           bd=1, relief=FLAT, fg='azure4')
panel_bebidas.pack(side=LEFT)

# Panel postres

panel_postres = LabelFrame(panel_izquierdo, text='Postres', font=('Dosis', 19, 'bold'),
                           bd=1, relief=FLAT, fg='azure4')
panel_postres.pack(side=LEFT)

# panel derecha
panel_derecha = Frame(aplicacion, bd=1, relief=FLAT)
panel_derecha.pack(side=RIGHT)

# panel calculadora

panel_calculadora = Frame(panel_derecha, bd=1, relief=FLAT, bg='burlywood')
panel_calculadora.pack()

# panel recibo

panel_recibo = Frame(panel_derecha, bd=1, relief=FLAT, bg='burlywood')
panel_recibo.pack()

# panel botones

panel_botones = Frame(panel_derecha, bd=1, relief=FLAT, bg='burlywood')
panel_botones.pack()

# Lista de comidas

Lista_comidas = ['Boneles', 'Hamburguesa', 'Hot Dog', 'Pizza', 'Papas Fritas', 'Sandwich', 'Tacos']
Lista_bebidas = ['Coca Cola', 'Fanta', 'Sprite', 'Agua', 'Jugo', 'Te', 'Cafe']
Lista_postres = ['Helado', 'Pastel', 'Gelatina', 'Flan', 'Torta', 'Tiramisu', 'Brownie']

#generar items de comidas
variables_comida = []
cuadros_comida = []
texto_comida = []
contador = 0
for comida in Lista_comidas:
    # crear checkbutton
    variables_comida.append("")
    variables_comida[contador] = IntVar()
    comida = Checkbutton(panel_comidas, text=comida.title(), font=('Dosis', 19, 'bold'),
                         onvalue=1, offvalue=0, variable=variables_comida[contador])
    comida.grid(row=contador, column=0, sticky=W)

    # crear cuadros de entrada
    cuadros_comida.append("")
    cuadros_comida[contador] = IntVar()
    cuadros_comida[contador] = Entry(panel_comidas,
                                    font=('Dosis', 19, 'bold'),
                                    bd=1,
                                    width=6,
                                    state=DISABLED,
                                    textvariable=cuadros_comida[contador])
    cuadros_comida[contador].grid(row=contador,
                                  column=1)


    contador += 1

#generar items de bebidas
variables_bebidas = []
cuadros_bebida = []
texto_bebida = []
contador = 0
for bebidas in Lista_bebidas:
    # crear checkbutton
    variables_bebidas.append("")
    variables_bebidas[contador] = IntVar()
    bebidas = Checkbutton(panel_bebidas,
                         text=bebidas.title(),
                         font=('Dosis', 19, 'bold'),
                         onvalue=1,
                         offvalue=0,
                         variable=variables_bebidas[contador])
    bebidas.grid(row=contador,
                column=0,
                sticky=W)

    # crear cuadros de entrada
    cuadros_bebida.append("")
    texto_bebida.append("")
    cuadros_bebida[contador] = Entry(panel_bebidas,
                                    font=('Dosis', 19, 'bold'),
                                    bd=1,
                                    width=6,
                                    state   =DISABLED,
                                    textvariable=cuadros_bebida[contador])
    cuadros_bebida[contador].grid(row=contador,
                                  column=1)
    contador += 1

#generar items de postres
variables_postres = []
cuadros_postres = []
texto_postres = []
contador = 0
for postres in Lista_postres:
    # crear checkbutton
    variables_postres.append("")
    variables_postres[contador] = IntVar()
    postres= Checkbutton(panel_postres,
                         text=postres.title(),
                         font=('Dosis', 19, 'bold'),
                         onvalue=1,
                         offvalue=0,
                         variable=variables_postres[contador])
    postres.grid(row=contador,
                 column=0,
                 sticky=W)

    # crear cuadros de entrada
    cuadros_postres.append("")
    texto_postres.append("")
    cuadros_postres[contador] = Entry(panel_postres,
                                    font=('Dosis', 18, 'bold'),
                                    bd=1,
                                    width=6,
                                    state=DISABLED,
                                    textvariable=cuadros_postres[contador])
    cuadros_postres[contador].grid(row=contador,
                                  column=1)



    contador += 1

#evitar que la ventana se cierre

aplicacion.mainloop()