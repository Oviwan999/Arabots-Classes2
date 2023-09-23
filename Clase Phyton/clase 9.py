#solucion1
from collections import Counter
lista = [1, 2, 3, 6, 7, 1, 2, 4, 5, 5, 5, 5, 3, 2, 6, 7]

contador = Counter(lista)

#solucion2
from collections import defaultdict
mi_diccionario = defaultdict(lambda:"Valor no hallado")
mi_diccionario["edad"] = 44


#solucion3
from collections import deque

lista_ciudades = deque(["Londres", "Berlin", "París", "Madrid", "Roma", "Moscú"])

#solucion4
from datetime import date

mi_fecha = date(1999, 2, 3)

#solucion5
from datetime import date

hoy = date.today()

#solucion6
from datetime import datetime

minutos = datetime.now().minute


#solucion7
import math

resultado = math.log10(25)

#solucion8
import math

resultado = math.sqrt(math.pi)

#solucion9
import math

resultado = math.factorial(7)

#solucion10
import re

import re


def verificar_email(email):
    patron = r'@\w+\.com'
    verificar = re.search(patron, email)
    if verificar:
        print("Ok")
    else:
        print("La dirección de email es incorrecta")




#solucion11
import re


def verificar_saludo(frase):
    patron = r'^Hola'
    verificar = re.search(patron, frase)
    if verificar:
        print("Ok")
    else:
        print("No has saludado")

#solucion12
import re


def verificar_cp(cp):
    patron = r'\w{2}\d{4}'
    verificar = re.search(patron, cp)
    if verificar:
        print("Ok")
    else:
        print("El código postal ingresado no es correcto")