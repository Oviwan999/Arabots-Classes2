import random
from random import choice

palabritas= ["planta", "pompompurin", "lol"]


def escoge(pal):
    return choice(pal)

def linea(xd):
    espacio = "_" * len(xd)
    return(espacio)


def imprime_pantalla(palabra):
    espacio = linea(palabra)
    print(espacio)


palabra=escoge(palabritas)
imprime_pantalla(palabra)



variable = linea(palabra)
palabra_secreta = palabra
print (variable)
print(palabra_secreta)

def letra():
    return choice(palabra_secreta)
print (letra())

miau= letra()


for v in range (1, 6 + 1):
    escribe = input(str("Pon una letra"))
    if escribe == miau:
         print ("nice")
         break

    else:
        print("lol, q mal")




















