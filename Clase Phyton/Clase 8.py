# solucion1
"""
Ejemplo de resolución:

def nombre_funcion(argumento):
    try:
        {Lo que haría la función habitualmente}
    except:
        {Excepción}
    else:
        ... etc.
"""


def suma(num1, num2):
    print(num1 + num2)


def suma(num1, num2):
    try:
        print(num1 + num2)
    except:
        print("Error inesperado")


# solucion2
"""
Ejemplo de resolución:

def nombre_funcion(argumento):
    try:
        {Lo que haría la función habitualmente}
    except:
        {Excepción}
    else:
        ... etc.
"""


def cociente(num1, num2):
    print(num1 / num2)


# MENSAJE EN PANTALLA
"Los argumentos a ingresar deben ser números"
"El segundo argumento no debe ser cero"


def cociente(num1, num2):
    try:
        print(num1 / num2)
    except TypeError:
        print("Los argumentos a ingresar deben ser números")
    except ZeroDivisionError:
        print("El segundo argumento no debe ser cero")


#solucion3
"""
Ejemplo de resolución:

def nombre_funcion(argumento):
    try:
        {Lo que haría la función habitualmente}
    except:
        {Excepción}
    else:
        ... etc.
"""

def abrir_archivo(nombre_archivo):
    archivo = open(nombre_archivo)


#MENSAJES EN PANTALLA:
"El archivo no fue encontrado"
"Error desconocido"
"Abriendo exitosamente"
"Finalizando ejecución"


def abrir_archivo(nombre_archivo):
    try:
        archivo = open(nombre_archivo)
    except FileNotFoundError:
        print("El archivo no fue encontrado")
    except:
        print("Error desconocido")
    else:
        print("Abriendo exitosamente")
    finally:
        print("Finalizando ejecución")

abrir_archivo("archivo.txt")

#solucion4
def secuencia_infinita():
    num = 0
    while True:
        num += 1
        yield num


generador = secuencia_infinita()
print(next(generador))
print(next(generador))
#solucion5
def multiplos_siete():
    num = 1
    while True:
        yield 7 * num
        num += 1


generador = multiplos_siete()
print(next(generador))
print(next(generador))

print(generador)
#solucion6
"Te quedan 3 vidas"
"Te quedan 2 vidas"
"Te queda 1 vida"
"Game Over"


def mensaje():
    x = "Te quedan 3 vidas"
    yield x

    x = "Te quedan 2 vidas"
    yield x

    x = "Te queda 1 vida"
    yield x

    x = "Game Over"
    yield x


perder_vida = mensaje()
print(next(perder_vida))
print(next(perder_vida))
print(next(perder_vida))
print(next(perder_vida))