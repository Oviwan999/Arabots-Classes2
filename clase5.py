#soluci
isdisjoint()
marcas_smartphones = {"Samsung", "Xiaomi", "Apple", "Huawei", "LG"}
marcas_tv = {"Sony", "Philips", "Samsung", "LG"}
marcas_smartphones.isdisjoint(marcas_tv)

t = ",:_#,,,,,,:::____##Pyt%on_ _Total,,,,,,::#"
t.upper()
#solucion2

#solucion3

#solucion4
def saludar():
    print("¡Hola mundo!")
saludar()
#solucion5
def bienvenida(nombre):
    print(f"¡Bienvenido {nombre}!")
bienvenida("Natalia")
bienvenida("Lucas")


#solucion6
un_numero=10
def cuadrado(un_numero) :
    print(un_numero**2)

#solucion7
def potencia(primer_argumento, segundo_argumento):
    return primer_argumento ** segundo_argumento


resultado = potencia(3, 4)

print(resultado)

#solucion8
dolares = 100


def usd_a_eur(dolares):
    resultado = dolares * 0.9
    return resultado


usd_a_eur(dolares)

#solucion9
palabra = "pythoooooon"


def invertir_palabra(palabra):
    palabra = palabra.upper()
    inversion = palabra[::-1]

    return inversion

#solucion10

lista_numeros = [-50, 502, -2500, 890, 628, 33, 61]


def todos_positivos(lista_numeros):
    for numero in lista_numeros:
        if numero < 0:
            return False
        else:
            pass
    return True

#solucion11

lista_numeros = [4, 500, 5000, 750, 600]


def suma_menores(lista_numeros):
    suma = 0
    for numero in lista_numeros:
        if numero in range(1, 1000):
            suma += numero
        else:
            pass
    return suma


#solucion12
lista_numeros = [45, 60, 502, 6000]


def cantidad_pares(lista_numeros):
    cantidad = 0
    for numero in lista_numeros:
        if numero % 2 == 0:
            cantidad += 1
        else:
            pass
    return cantidad


#solucion13
import random


def lanzar_dados():
    return random.randint(1, 6), random.randint(1, 6)


def evaluar_jugada(dado1, dado2):
    suma_dados = dado1 + dado2
    if suma_dados <= 6:
        return f"La suma de tus dados es {suma_dados}. Lamentable"
    elif suma_dados > 6 and suma_dados < 10:
        return f"La suma de tus dados es {suma_dados}. Tienes buenas chances"
    else:
        return f"La suma de tus dados es {suma_dados}. Parece una jugada ganadora"



#solucion14
lista_numeros = [1, 6, 30, 7, 6, 9]


def reducir_lista(lista):
    lista = list(set(lista))
    lista.sort()
    lista.pop(-1)
    return lista


def promedio(lista):
    valor_medio = sum(lista) / len(lista)
    return valor_medio


#solucion15
lista_numeros = [4, 6, 13, 2, 6]

import random


def lanzar_moneda():
    resultado = random.choice(["Cara", "Cruz"])
    return resultado


def probar_suerte(moneda, lista):
    if moneda == "Cara":
        print("La lista se autodestruirá")
        return []
    elif moneda == "Cruz":
        print("La lista fue salvada")
        return lista

#solucion16
def suma_cuadrados(*args):
    suma = 0

    for args in args:
        suma += args ** 2

    return suma


#solucion17
def suma_absolutos(*args):
    suma = 0
    for args in args:
        suma += abs(args)

    return suma

#solucion18
def numeros_persona(nombre, *args):
    suma_numeros = sum(args)
    return f"{nombre}, la suma de tus números es {suma_numeros}"


#solucion19
def cantidad_atributos(**kwargs) :
    cantidad = 0
    for clave in kwargs.items():
        cantidad += 1
    return cantidad


#solucion20
def lista_atributos(**kwargs):
    lista = []
    for valor in kwargs.values():
        lista.append(valor)

    return lista


#solucion21
def describir_persona(nombre, **kwargs):
    print(f"Características de {nombre}:")
    for clave, valor in kwargs.items():
        print(f'{clave}: {valor}')


#solucion22
def devolver_distintos(a,b,c):
    suma = a+b+c
    lista = [a,b,c]
    if suma > 15:
        return max(lista)
    elif suma > 10:
        return min(lista)

    else:
        lista.sort()
        return lista[1]

print(devolver_distintos(10,1,5))

#solucion23
def ordena_sin_que_se_repitan (palabra):
    mi_set = set()

    for letra in palabra:
        mi_set.add(letra)


    mi_lista = list(mi_set)
    mi_lista.sort()
    return mi_lista

print(ordena_sin_que_se_repitan("parangacutirimicuaro"))


#solucion24
def compañeros (*args):

    contador = 0
    for num in args:
        if contador + 1 == len(args) :
            return False
        elif  args [contador] == 0 and args [contador + 1] == 0:
            return True
        else:
            contador += 1
    return False
print(compañeros(1,2,5,5,6,8,0))

#solucion25
def contar_primos (numero):

    primos = [2]
    interacion = 3
    if numero > 2:
        return 0
    while interacion <= numero:
        for n in range(3,interacion,2):
            if interacion % n == 0:
                interacion += 2
                break
        else:
            primos.append(interacion)
            interaccion += 2
    print(primos)
    return len(primos)



print(contar_primos(160))






