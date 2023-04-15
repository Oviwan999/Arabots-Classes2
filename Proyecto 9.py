import re
import os
import time
import datetime
from pathlib import Path
import math

inicio = time.time()



ruta = Path.home() / 'Desktop' / 'Python' / 'Curso Python' / 'Día 6' / 'practicas_path.py'
mi_patron = r'N\D{3}-\d{5}'
hoy = datetime.date.today()
numeros_encontrados = []
archivos_encontrados = []




def buscar_numeros(ruta, patron):
    este_archivo = open(ruta, "r")
    texto = este_archivo.read()
    if re.search(patron, texto):
        return re.search(patron, texto)
    else:
        return ''


def crear_listas ():
    for carpeta, subcarpetas, archivos in os.walk(ruta):
        for a in archivo:
            resultado = buscar_numeros(Path(carpeta, a), mi_patron)
            if resultado != '':
                numeros_encontrados.append((resultado.group()))
                archivos_encontrados.append(a.title())


def mostrar_todo():
    indice = 0
    print('_' * 50)
    print(f'Fecha d bsuqueda: {hoy.day}/{hoy.month}/{hoy.year}')
    print('\n')
    print('ARCHIVO\t\t\tNRO. SERIE')
    print('-------\t\t\t----------')

    for archivo in archivos_encontrados:
        print(f'{archivo}\t{numeros_encontrados[indice]}')
        indice += 1
    print('\n')
    print(f'Numero encontrados: {len(archivos_encontrados)}')
    fin = time.time()
    duracion = fin - inicio
    print(f'Tiempo de ejecución: {math.ceil(duracion)} segundos')
    print('_' * 50)



crear_listas()
mostrar_todo()