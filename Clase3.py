# solucion1
palabra = "ordenador"
print(palabra[4])

# solucion2
frase = "En teoría, la teoría y la práctica son los mismos. En la práctica, no lo son."
print(frase.index("práctica"))

# solucion3
frase = "En teoría, la teoría y la práctica son los mismos. En la práctica, no lo son."
print(frase.rindex("práctica"))

# solucion4
frase = "Controlar la complejidad es la esencia de la programación"
print(frase[:9])

# solucion5
frase = "Nunca confíes en un ordenador que no puedas lanzar por una ventana"
print(frase[8::3])

# solucion6
frase = "Es genial trabajar con ordenadores. No discuten, lo recuerdan todo y no se beben tu cerveza"

print(frase[::-1])

# solucion7
frase = "Especialmente en las comunicaciones electrónicas, la escritura enteramente en mayúsculas equivale a gritar."
print(frase.upper())

# solucion8
lista_palabras = ["La", "legibilidad", "cuenta."]
pr = " ".join(lista_palabras)
print(pr)

# solucion9
frase = "Si la implementación es difícil de explicar, puede que sea una mala idea."
print(frase.replace("difícil", "fácil").replace("mala", "buena"))

# solucion10
palabra = "Repetición"

print(palabra * 15)

# solucion11
haiku = '''
Tierra mojada
mis recuerdos de viaje,
entre las lluvias
'''

print("agua" not in haiku)

# solucion12
palabra = "electroencefalografista"

print(len(palabra))

# solucion13
mi_lista = ["uno", 2, 3.33, "four", True]

# solucion14
medios_transporte = ["avión", "auto", "barco", "bicicleta"]

medios_transporte.append("motocicleta")

# solucion15
frutas = ["manzana", "banana", "mango", "cereza", "sandía"]

eliminado = frutas.pop(2)

# solucion16
mi_dic = {"nombre": "Karen", "apellido": "Jurgens", "edad": 35, "ocupacion": "Periodista"}

# solucion17
mi_dict = {"valores_1": {"v1": 3, "v2": 6}, "puntos": {"points1": 9, "points2": [10, 300, 15]}}
print(mi_dict["puntos"]["points2"][1])

# solucion18
mi_dic3 = {"nombre": "Karen", "apellido": "Jurgens", "edad": 35, "ocupacion": "Periodista"}

mi_dic3["edad"] = 36
mi_dic3["ocupacion"] = "Editora"
mi_dic3["pais"] = "Colombia"

# solucion19
mi_tupla = (1, 2, 3, 2, 3, 1, 3, 2, 3, 3, 3, 1, 3, 2, 2, 1, 3, 2)
print(mi_tupla.count(2))

# solucion20
mi_tupla = (1, 2, 3, 2, 3, 1, 3, 2)

mi_lista2 = list(mi_tupla)
print(type(mi_tupla))

# solucion21
mi_tupla = (1, 2, 3, 4)

a, b, c, d = mi_tupla

# solucion22
mi_set_1 = {1, 2, "tres", "cuatro"}
mi_set_2 = {"tres", 4, 5}

mi_set_3 = mi_set_1.union(mi_set_2)

# solucion23
sorteo = {"Camila", "Margarita", "Axel", "Jorge", "Miguel", "Mónica"}
sorteo.pop()

# solucion24
sorteo = {"Camila", "Margarita", "Axel", "Jorge", "Miguel", "Mónica, "}

sorteo.add("Damián")

# solucion25
prueba = 5 > 6

print(type(prueba))
print(prueba)

# solucion28
r = 17834/34 > 87*56

print(r)

# solucion29
r = 25 ** 0.5 == 5

print(r)
