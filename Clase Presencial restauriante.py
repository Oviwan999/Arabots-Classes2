from tkinter import *
import random
import datetime
from tkinter import messagebox,filedialog

operador=""
precios_comida = [1.32, 1.65, 2.31, 3.22, 1.22, 1.99, 2.05, 2.65,1,2]
precios_bebida = [0.25, 0.99, 1.21, 1.54, 1.08, 1.10, 2.00, 1.58,1,2]
precios_postres = [1.54, 1.68, 1.32, 1.97, 2.55, 2.14, 1.94, 1.74,1,2]

#funciones
def click_boton(numero):
    global operador
    operador = operador + str(numero)
    visor_calculadora.delete(0,END)
    visor_calculadora.insert(END,operador)

def borrar():
    global operador
    operador=""
    visor_calculadora.delete(0,END)

def obtener_resultado ():
    global operador
    resultado =str(eval(operador))
    visor_calculadora.delete(0,END)
    visor_calculadora.insert(0,resultado)
    operador=""
#revisar Check
def revisar_check():
    x=0

    for c in cuadros_comida:
        if variables_comida[x].get()==1:
            cuadros_comida[x].config(state=NORMAL)
            if cuadros_comida[x].get() == "0":
                cuadros_comida[x].delete(0,END)
            cuadros_comida[x].focus()
        else:
            cuadros_comida[x].config(state=DISABLED)
            texto_comida[x].set("0")
        x+=1

    x=0
    for c in cuadros_bebidas:
        if variables_bebidas[x].get()==1:
            cuadros_bebidas[x].config(state=NORMAL)
            if cuadros_bebidas[x].get() == "0":
                cuadros_bebidas[x].delete(0,END)
            cuadros_bebidas[x].focus()
        else:
            cuadros_bebidas[x].config(state=DISABLED)
            texto_bebidas[x].set("0")
        x+=1

    x=0
    for c in cuadros_postres:
        if variables_postres[x].get()==1:
            cuadros_postres[x].config(state=NORMAL)
            if cuadros_postres[x].get() == "0":
                cuadros_postres[x].delete(0,END)
            cuadros_postres[x].focus()
        else:
            cuadros_postres[x].config(state=DISABLED)
            texto_postres[x].set("0")
        x+=1
# definicion del total
def total():
    sub_total_comida = 0
    p=0
    for cantidad in texto_comida:
        sub_total_comida=sub_total_comida+(float(cantidad.get())*precios_comida[p])
        p+=1

    sub_total_bebidas = 0
    p=0
    for cantidad in texto_bebidas:
        sub_total_bebidas=sub_total_bebidas+(float(cantidad.get())*precios_bebida[p])
        p+=1

    sub_total_postres = 0
    p=0
    for cantidad in texto_postres:
        sub_total_postres=sub_total_postres+(float(cantidad.get())*precios_postres[p])
        p+=1

    sub_total = sub_total_comida+sub_total_bebidas+sub_total_postres
    impuesto = sub_total*0.15
    total = sub_total+impuesto

    var_costo_comida.set("$ "+str(round(sub_total_comida,2)))
    var_costo_bebida.set("$ "+str(round(sub_total_bebidas,2)))
    var_costo_postres.set("$ "+str(round(sub_total_postres,2)))
    var_subtotal.set("$ "+str(round(sub_total,2)))
    var_impuesto.set("$ "+str(round(impuesto,2)))
    var_total.set("$ "+str(round(total,2)))

#definicion de recibo
def recibo():
    texto_recibo.delete(1.0,END)
    num_recibo= f'N#'-{random.randint(1000,9999)}
    fecha= datetime.datetime.now()
    fecha_recibo=f'{fecha.day}/{fecha.month}/{fecha.year}-{fecha.hour}:{fecha.minute}''
    texto_recibo.insert(END,f'Datos:t\t{num_recibo}\t\t{fecha_recibo}\n')
    texto_recibo.insert(END,f'*'*47+'\n')
    texto_recibo.insert(END,'Items\t\tCant.\tCosto Items\n')
    texto_recibo.insert(END,f'-'* 54 + '\n')

    x=0

    for comida in texto_comida:
        if comida.get()!='0':
            texto_recibo.insert(END,f'{ lista_comidas[x]}\t\t{comida.get()}\t'
                                f'${int(comida.get())* precios_comida}\n')

    for bebida in texto_bebidas:
        if bebida.get() != '0':
            texto_recibo.insert(END, f'{lista_bebidas[x]}\t\t{bebida.get()}\t'
                                     f'$ {int(bebida.get()) * precios_bebida[x]}\n')
        x += 1

    x = 0
    for postres in texto_postres:
        if postres.get() != '0':
            texto_recibo.insert(END, f'{lista_postres[x]}\t\t{postres.get()}\t'
                                     f'$ {int(postres.get()) * precios_postres[x]}\n')

#iniciar app
aplicacion = Tk()
aplicacion.geometry("1300x630+0+0")
#No maximizar
aplicacion.resizable(0, 0)
#titulo
aplicacion.title("Restaurante")
aplicacion.config(bg="DarkSlateGray")

#panel superior
panel_superior = Frame(aplicacion,bd=1,relief=FLAT)
panel_superior.pack(side=TOP)
#titulos
etiqueta_titulo = Label(panel_superior,text="Restaurante",
                        font=("Arial",30,"bold"),bg="DarkOrange4",width=27)
etiqueta_titulo.grid(row=0,column=0)

#panel izquierdo
panel_izquierdo = Frame(aplicacion,bd=1,relief=FLAT)
panel_izquierdo.pack(side=LEFT)

#panel de costos
panel_costos = Frame(panel_izquierdo,bd=1,relief=FLAT,bg="Azure",padx=50)
panel_costos.pack(side=BOTTOM)

#panel de comida
panel_comida = LabelFrame(panel_izquierdo,text="Comida",font=("Dosis", 19, "bold"),
                          bd=1, relief=FLAT, bg="Azure4")
panel_comida.pack(side=LEFT)

#panel de bebidas
panel_bebidas = LabelFrame(panel_izquierdo,text="Bebidas",font=("Dosis", 19, "bold"),
                            bd=1, relief=FLAT, bg="Azure")
panel_bebidas.pack(side=LEFT)

#panel de postres
panel_postres = LabelFrame(panel_izquierdo,text="Postres",font=("Dosis", 19, "bold"),
                            bd=1, relief=FLAT, bg="Azure2")
panel_postres.pack(side=LEFT)

#panel derecho
panel_derecha = Frame(aplicacion,bd=1,relief=FLAT)
panel_derecha.pack(side=RIGHT)

#panel calculadora
panel_calculadora= Frame(panel_derecha,bd=1,relief=FLAT,bg="burlywood")
panel_calculadora.pack()

#panel recibo
panel_recibo = Frame(panel_derecha,bd=1,relief=FLAT,bg="burlywood")
panel_recibo.pack()

#panel de botones
panel_botones = Frame(panel_derecha, bd=1, relief=FLAT, bg='burlywood')
panel_botones.pack()
#lista de productos
lista_comidas=["Hamburguesa","Pizza","Hot Dog","Tacos","Burritos","Torta","Torta Cubana","Torta Hawaiana","Torta de Jamon","Torta de Queso"]
lista_bebidas=["Coca Cola","Pepsi","Fanta","Sprite","Agua","Agua Mineral","Agua de Sabor","Agua de Frutas","Agua de Jamaica","Agua de Horchata"]
lista_postres=["Pastel de Chocolate","Pastel de Vainilla","Pastel de Fresa","Pastel de Limon","Pastel de Nuez","Pastel de Zanahoria","Pastel de Moka","Pastel de Cafe","Pastel de Tres Leches","Pastel de Queso"]

#generar items de comida
variables_comida = []
cuadros_comida = []
texto_comida = []
contador=0

#iniciar llenado de datos
for comida in lista_comidas:
    #crear checkbox
    variables_comida.append("")
    variables_comida[contador] = IntVar()
    comida = Checkbutton(panel_comida,
                         text=comida.title(),
                         font=("Arial", 15, "bold"),
                         onvalue=1,
                         offvalue=0,
                         variable=variables_comida[contador],
                         command=revisar_check
                         )
    comida.grid(row=contador, column=0, sticky=W)

    #crear cuadro de texto
    cuadros_comida.append("")
    texto_comida.append("")
    texto_comida[contador] = StringVar()
    texto_comida[contador].set("0")
    cuadros_comida[contador] = Entry(panel_comida,
                                     font=("Arial", 15, "bold"),
                                     bd=1,
                                     width=6,
                                     state=DISABLED,
                                     textvariable=texto_comida[contador])
    cuadros_comida[contador].grid(row=contador, column=1)

    contador += 1
#generar items de bebidas
variables_bebidas = []
cuadros_bebidas = []
texto_bebidas = []
contador=0

for bebida in lista_bebidas:
    # Checkbox
    variables_bebidas.append("")
    variables_bebidas[contador] = IntVar()
    bebida = Checkbutton(panel_bebidas,
                            text=bebida.title(),
                            font=("Arial", 15, "bold"),
                            onvalue=1,
                            offvalue=0,
                            variable=variables_bebidas[contador],
                            command=revisar_check
                            )
    bebida.grid(row=contador, column=0, sticky=W)

    # Cuadro de texto
    cuadros_bebidas.append("")
    texto_bebidas.append("")
    texto_bebidas[contador] = StringVar()
    texto_bebidas[contador].set("0")
    cuadros_bebidas[contador] = Entry(panel_bebidas,
                                        font=("Arial", 15, "bold"),
                                        bd=1,
                                        width=6,
                                        state=DISABLED,
                                        textvariable=texto_bebidas[contador])
    cuadros_bebidas[contador].grid(row=contador, column=1)

    contador += 1

#generar items de postres

variables_postres = []
cuadros_postres = []
texto_postres = []
contador=0

for postre in lista_postres:
    # Checkbox
    variables_postres.append("")
    variables_postres[contador] = IntVar()
    postre = Checkbutton(panel_postres,
                            text=postre.title(),
                            font=("Arial", 15, "bold"),
                            onvalue=1,
                            offvalue=0,
                            variable=variables_postres[contador],
                            command=revisar_check
                            )
    postre.grid(row=contador, column=0, sticky=W)

    # Cuadro de texto
    cuadros_postres.append("")
    texto_postres.append("")
    texto_postres[contador] = StringVar()
    texto_postres[contador].set("0")
    cuadros_postres[contador] = Entry(panel_postres,
                                        font=("Arial", 15, "bold"),
                                        bd=1,
                                        width=6,
                                        state=DISABLED,
                                        textvariable=texto_postres[contador])
    cuadros_postres[contador].grid(row=contador, column=1)

    contador += 1

#variables dela calculadora
var_costo_comida = StringVar()
var_costo_bebida = StringVar()
var_costo_postres = StringVar()
var_subtotal = StringVar()
var_impuesto = StringVar()
var_total = StringVar()

#etiqueta de costo de comida y costo de entrada

etiqueta_costo_comida = Label(panel_costos,
                                text="Costo de Comida:",
                                font=("Arial", 15, "bold"),
                                bg="azure4",
                              fg="white")
etiqueta_costo_comida.grid(row=0, column=0)

texto_costo_comida = Entry(panel_costos,
                             font=("Arial", 15, "bold"),
                             bd=1,
                             width=10,
                            state='readonly',
                             textvariable=var_costo_comida)
texto_costo_comida.grid(row=0, column=1,padx=41)

etiqueta_costo_bebida = Label(panel_costos,
                                text="Costo de Bebida:",
                                font=("Arial", 15, "bold"),
                                bg="azure4",
                                fg="white")
etiqueta_costo_bebida.grid(row=1, column=0)

texto_costo_bebida = Entry(panel_costos,
                           font=("Arial", 15, "bold"),
                            bd=1,
                            width=10,
                            state='readonly',
                            textvariable=var_costo_bebida)
texto_costo_bebida.grid(row=1, column=1, padx=41)

etiqueta_costo_postres = Label(panel_costos,
                              text='Costo Postres',
                              font=('Dosis', 12, 'bold'),
                              bg='azure4',
                              fg='white')
etiqueta_costo_postres.grid(row=2, column=0)

texto_costo_postres = Entry(panel_costos,
                           font=('Dosis', 12, 'bold'),
                           bd=1,
                           width=10,
                           state='readonly',
                           textvariable=var_costo_postres)
texto_costo_postres.grid(row=2, column=1, padx=41)

#etiqueta de subtotal, impuesto y total

etiqueta_subtotal = Label(panel_costos,
                            text="Subtotal:",
                            font=("Arial", 15, "bold"),
                            bg="azure4",
                              fg="white")
etiqueta_subtotal.grid(row=0, column=2)

texto_subtotal = Entry(panel_costos,
                            font=("Arial", 15, "bold"),
                            bd=1,
                            width=10,
                            state='readonly',
                            textvariable=var_subtotal)
texto_subtotal.grid(row=0, column=3,padx=41)

etiqueta_impuesto = Label(panel_costos,
                            text="Impuesto:",
                            font=("Arial", 15, "bold"),
                            bg="azure4",
                            fg="white")
etiqueta_impuesto.grid(row=1, column=2)

texto_impuesto = Entry(panel_costos,
                            font=("Arial", 15, "bold"),
                            bd=1,
                            width=10,
                            state='readonly',
                            textvariable=var_impuesto)
texto_impuesto.grid(row=1, column=3, padx=41)

etiqueta_total = Label(panel_costos,
                            text="Total:",
                            font=("Arial", 15, "bold"),
                            bg="azure4",
                            fg="white")
etiqueta_total.grid(row=2, column=2)

texto_total = Entry(panel_costos,
                            font=("Arial", 15, "bold"),
                            bd=1,
                            width=10,
                            state='readonly',
                            textvariable=var_total)
texto_total.grid(row=2, column=3, padx=41)

#creacion de botones
botones= ['total','recibo','guardar','resetear']
botones_creados=[]

columnas=0

for boton in botones:
    boton=Button(panel_botones,
                    text=boton.title(),
                    font=("Arial", 15, "bold"),
                    fg="white",
                    bg="azure4",
                    bd=1,
                    width=9)

    botones_creados.append(boton)
    boton.grid(row=0,column=columnas)
    columnas+=1
botones_creados[0].config(command=total)
#botones_creados[1].config(command=recibo)
#botones_creados[2].config(command=guardar)
#botones_creados[3].config(command=resetear)

#area de recibo
texto_recibo = Text(panel_recibo,
                    font=('Dosis', 12, 'bold'),
                    bd=1,
                    width=42,
                    height=10)
texto_recibo.grid(row=0,
                  column=0)

#calculadora
visor_calculadora = Entry(panel_calculadora,
                            font=('Dosis', 12, 'bold'),
                          width=32,
                            bd=1)
visor_calculadora.grid(row=0,
                          column=0,
                            columnspan=4)

botones_calculadora = ['7', '8', '9', '+', '4', '5', '6', '-',
                       '1', '2', '3', 'x', 'R', 'B', '0', '/']
botones_guardados = []

fila = 1
columna = 0

for boton in botones_calculadora:
    boton = Button(panel_calculadora,
                   text=boton.title(),
                   font=('Dosis', 12, 'bold'),
                   fg='black',
                   bg='azure4',
                   bd=1,
                     width=8)
    botones_guardados.append(boton)
    boton.grid(row=fila, column=columna)

    if columna == 3:
        fila += 1
    columna += 1

    if columna == 4:
        columna = 0

botones_guardados[0].config(command=lambda : click_boton('7'))
botones_guardados[1].config(command=lambda : click_boton('8'))
botones_guardados[2].config(command=lambda : click_boton('9'))
botones_guardados[3].config(command=lambda : click_boton('+'))
botones_guardados[4].config(command=lambda : click_boton('4'))
botones_guardados[5].config(command=lambda : click_boton('5'))
botones_guardados[6].config(command=lambda : click_boton('6'))
botones_guardados[7].config(command=lambda : click_boton('-'))
botones_guardados[8].config(command=lambda : click_boton('1'))
botones_guardados[9].config(command=lambda : click_boton('2'))
botones_guardados[10].config(command=lambda : click_boton('3'))
botones_guardados[11].config(command=lambda : click_boton('*'))
botones_guardados[12].config(command=obtener_resultado)
botones_guardados[13].config(command=borrar)
botones_guardados[14].config(command=lambda : click_boton('0'))
botones_guardados[15].config(command=lambda : click_boton('/'))


#eviar cierrre
aplicacion.mainloop()