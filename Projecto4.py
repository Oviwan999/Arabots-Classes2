#solucion1
num1 = 36
num2 = 17

mi_bool = num1 >= num2

print(mi_bool)

#solucion2
num1 = 5
num2 = 5

mi_bool = num1 == num2

print(mi_bool)

#solucion3
num1 = 192
num2 = 192

mi_bool = num1 != num2

print(mi_bool)

#solucion4
num1 = 36
num2 = 36
num3 = 48

mi_bool = (num1 > num2) and (num2 < num3 )

print(mi_bool)

#solucion5
num1 = 36
num2 = 36
num3 = 48

mi_bool = (num1 > num2) or (num2 < num3 )

print(mi_bool)

#solucion6
texto = "Cuando algo es lo suficientemente importante, lo haces incluso si las probabilidades de que salga bien no te acompañan"

palabra1 = "éxito"
palabra2 = "tecnología"

mi_bool = not (palabra1 in texto) or (palabra2 in texto)


print(mi_bool)

#solucion7
num1 = input("Ingresa un número:")
num2 = input("Ingresa otro número:")
if num1 > num2:
    print(num1, "es mayor que" ,num2)
if num2 > num1:
    print(num2, "es mayor que" ,num1)

if num1 == num2:
    print(num1, "y" ,num2 ,'son iguales')


#solucion8
edad = 16
tiene_licencia = False

if tiene_licencia:
    print("Puedes conducir")

if edad:
    print("No puedes conducir aún. Debes tener 18 años y contar con una licencia")

if tiene_licencia:
    print ("No puedes conducir. Necesitas contar con una licencia")


#solucion9
habla_ingles = True
sabe_python = False
if sabe_python:
    print("Cumples con los requisitos para postularte")

if sabe_python:
    print("Para postularte, necesitas saber programar en Python y tener conocimientos de inglés")

if sabe_python:
    print("Para postularte, necesitas tener conocimientos de inglés")

if habla_ingles:
    print("Para postularte, necesitas saber programar en Python")

#solucion10
alumnos_clase = ["María", "José", "Carlos", "Martina", "Isabel", "Tomás", "Daniela"]

for elemento in alumnos_clase:
    print("Hola" + " " + elemento)

#solucion11
lista_numeros = [1, 5, 8, 7, 6, 8, 2, 5, 2, 6, 4, 8, 5, 9, 8, 3, 5, 4, 2, 5, 6, 4]
suma_numeros = 0

for numero in lista_numeros:
    suma_numeros = suma_numeros + numero

print(suma_numeros)

#solucion12
lista_numeros = [1, 5, 8, 7, 6, 8, 2, 5, 2, 6, 4, 8, 5, 9, 8, 3, 5, 4, 2, 5, 6, 4]
suma_pares = 0
suma_impares = 0

for numero in lista_numeros:
    if numero%2.== 0:
        suma_pares = suma_pares + numero
    else:
        suma_impares = suma_impares + numero

print (suma_pares)
print (suma_impares)

#solucion13
numero = 10

while numero > 0:
    print(numero)
    numero = numero - 1
else:
    print("0")

#solucion14
numero = 50

while numero > 0:
    print(numero)
    numero = numero - 5

else:
    print(0)

#solucion15
lista_numeros = [4,5,8,7,6,9,8,2,4,5,7,1,9,5,6,-1,-5,6,-6,-4,-3]

for numero in lista_numeros:
    if numero == -1:
        break
    print(numero)

#solucion16
mi_lista = list (range (2500,2586))

print(mi_lista)

#solucion17
mi_lista = list(range(3,301,3))

print (mi_lista)

#solucion18
suma_cuadrados = 1240

for numero in range(1,16,2):
    print (numero)


#solucion19
lista_nombres = ["Marcos", "Laura", "Mónica", "Javier", "Celina", "Marta", "Darío", "Emiliano", "Melisa"]
for indice, nombre  in enumerate(lista_nombres):
    print(f'{nombre} se encuentra en el índice {indice}')


#solucion20
lista = []

for indice, letra in enumerate("Python"):
    lista.append((indice, letra))
print(lista)

#solucion21
lista_nombres = ["Marcos", "Laura", "Mónica", "Javier", "Celina", "Marta", "Darío", "Emiliano", "Melisa"]

for i, nombre in enumerate(lista_nombres):
    if nombre[0] == "M":
        print(i)

#solucion22
capitales = ["Berlín", "Tokio", "París", "Helsinki", "Ottawa", "Canberra"]
paises = ["Alemania", "Japón", "Francia", "Finlandia", "Canadá"]
print("aqui")
print(zip(capitales, paises))
for pais, capital in zip(paises, capitales):
    print(f"La capital de {pais} es {capital}")

#solucion23
marcas = ["Nike", "Lenovo", "Nissan"]
productos = ["zapatillas", "notebook", "automóviles"]

mi_zip = zip(marcas, productos)

#solucion24
espaniol = ["uno", "dos", "tres", "cuatro", "cinco"]
portugues = ["um", "dois", "três", "quatro", "cinco"]
ingles = ["one", "two", "three", "four", "five"]

numeros = list(zip(espaniol, portugues, ingles))

#solucion25
lista_numeros = [44542247 / 2, 21310 / 5, 2134747 * 33, 44556475, 121676, 6654067, 353254, 123134, 55 ** 12, 611 ** 5]

valor_maximo = max(lista_numeros)

#solucion26
lista_numeros = [44542247, 21310, 2134747, 44556475, 121676, 6654067, 353254, 123134, 552512, 611665]

rango = max(lista_numeros) - min(lista_numeros)

#solucion27
diccionario_edades = {"Carlos": 55, "María": 42, "Mabel": 78, "José": 44, "Lucas": 24, "Rocío": 35, "Sebastián": 19,
                      "Catalina": 2, "Darío": 49}

edad_minima = min(diccionario_edades.values())
ultimo_nombre = max(diccionario_edades.keys())

#solucion28
from random import randint

aleatorio = randint(1, 10)

#solucion29
from random import *

aleatorio = random()

#solucion30
from random import *

nombres = ["Carlos", "Julia", "Nicole", "Laura", "Mailen"]

sorteo = choice(nombres)

#solucion31
valores = [1, 2, 3, 4, 5, 6, 9.5]

valores_cuadrado = [valor ** 2 for valor in valores]

#solucion32
valores = [1, 2, 3, 4, 5, 6, 9.5]

valores_pares = [valor for valor in valores if valor % 2 == 0]

#solucion33
temperatura_fahrenheit = [32, 212, 275]

grados_celsius = [(temperatura - 32) * (5 / 9) for temperatura in temperatura_fahrenheit]
