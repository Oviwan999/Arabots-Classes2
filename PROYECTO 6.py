import os
from pathlib import Path
from os import system
mi_ruta = Path(Path.home(), "Recetas")

def contar_recetas(ruta):
    contador = 0
    for txt in Path(ruta).glob("**/*.txt"):
        contador += 1

    return contador

def inicio():
    system("cls")
    print('*' * 50)
    print("Bienvenido al sistema de recetas")
    print('*' * 50)
    print("\n)")
    print (f"las recetas se encuenran en {mi_ruta}")
    print(f"todas las recetas: {contar_recetas(mi_ruta)}")

    eleccion_menu = "x"
    while not eleccion_menu.isnumeric() or int(eleccion_menu) not in range(1,7):
        print("Elige una opción: ")
        print('''
        [1] - Leer receta 
        [2] - Agregar receta    
        [3] - Crer categoria nueva
        [4] - Eliminar receta
        [5] - Eliminar categoria
        [6] - Salir del programa''')
        eleccion_menu = input()
    return (eleccion_menu)


def mostrar_categorias (ruta):
    print("Categorias:")
    ruta_categorias = Path(ruta)
    lista_categorias = []
    contador = 1

    for carpeta in ruta_categorias.iterdir():
        carpeta_str = str(carpeta.name)
        print(f"[{contador}] - {carpeta_str}")
        lista_categorias.append(carpeta)
        contador += 1
    return lista_categorias

def elegir_categoria(lista) :
    eleccion_correcta = "x"

    while not eleccion_correcta.isnumeric() or int(eleccion_correcta) not in range(1,len(lista)+1):
        eleccion_correcta = input("\nElige una categoria: ")
    return lista[int(eleccion_correcta)-1]

def mostrar_recetas(ruta):
    print("Recetas:")
    ruta_recetas = Path(ruta)
    lista_recetas = []
    contador = 1
    for receta in ruta_recetas.glob('*.txt'):
        receta_str = str(receta.name)
        printa(f"[{contador}] - {receta_str}")
        lista_recetas.append(receta)
        contador += 1
    return lista_recetas

def elegir_receta(lista):
    eleccion_receta = "x"
    while not eleccion_receta.isnumeric() or int(eleccion_receta) not in range(1,len(lista)+1):
        eleccion_receta = input("\nElige una receta: ")
    return lista[int(eleccion_correcta)-1]

def leer_receta(receta):
    print(Path.read_text(receta))

def crear_nueva_receta(ruta):
    existe = False
    while not existe:
        print("escribe el nombre de la receta: ")
        nombre_receta = input() + ".txt"
        print("escribe tu nueva receta: ")
        contenido_receta = input()
        ruta_nueva = Path(ruta, nombre_receta)

        if not os.path.exists(ruta_nueva):
            Path.write_text(ruta_nueva, contenido_receta)
            print(f"tu receta {nombre_receta} se ha creado con exito")
            existe = True
        else:
            print("Lo siento, esa receta ya existe")

def crear_nueva_categoria(ruta):
    existe = False
    while not existe:
        print("escribe el nombre de la nueva categoria: ")
        nombre_categoria = input()
        print("escribe tu nueva categoria: ")
        contenido_receta = input()
        ruta_nueva = Path(ruta, nombre_receta)

        if not os.path.exists(ruta_nueva):
            Path.mkdir(ruta_nueva)
            print(f"tu categoria {nombre_categoria} se ha creado con exito")
            existe = True
        else:
            print("Lo siento, esa categoria ya existe")

def eliminar_receta(receta):
    Path(receta).unlink()
    print(f"la receta {receta.name} fue eliminada")

def eliminar_categoria(categoria):
    Path(categoria).rmdir()
    print(f"la categoria {categoria.name} fue eliminada")

def volver_a_inicio():
    eleccion_regresar = "x"

    while eleccion_regresar.lower () != "v" :
        eleccion_regresar = input("\nPresiona V para volver al menu: ")

finalizar_programa = False
while not finalizar_programa:
    menu = inicio()
    if menu == 1:
        mis_categorias = mostrar_categorias(mi_ruta)
        mis_categoria = elegir_categoria(mis_categorias)
        mis_recetas = mostrar_recetas(mis_categoria)
        mi_receta = elegir_receta(mis_recetas)
        leer_receta(mi_receta)
        volver_a_inicio()
    elif menu == 2:
        mis_categorias = mostrar_categorias(mi_ruta)
        mis_categoria = elegir_categoria(mis_categorias)
        crear_receta(mis_categoria)
        volver a inicio ()
    elif menu == 3:
        crear_receta(mi_ruta)
        volver_a_inicio()
    elif menu == 4:
        mis_categorias = mostrar_categorias(mi_ruta)
        mis_categoria = elegir_categoria(mis_categorias)
        mis_recetas = mostrar_recetas(mis_categoria)
        mi_receta = elegir_receta(mis_recetas)
        eliminar receta(mi_receta)
        volver_a_inicio()
    elif menu == 5:
        mis_categorias = mostrar_categorias(mi_ruta)
        mis_categoria = elegir_categoria(mis_categorias)
        eliminar_categoria(mi_categoria)
        volver_a_inicio()
    elif menu == 6:
        finalizar_programa = True






