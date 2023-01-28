#solucion1
archivo = open("Prueba (1).txt")
print(archivo.read())

#solicion2
mi_archivo = open("texto.txt")
print(mi_archivo.readline())


#solucion3
archivo = open("texto.txt")
lineas = archivo.readlines()
print(lineas[1])

# Alternativa de solución admitida:
# lineas = archivo.readline()
# lineas = archivo.readline()
# print(lineas)archivo = open("texto.txt")
# lineas = archivo.readlines()
# print(lineas[1])
#
# # Alternativa de solución admitida:
# # lineas = archivo.readline()
# # lineas = archivo.readline()
# # print(lineas)

#solucion4
archivo = open("mi_archivo.txt", "w")
archivo.write("Nuevo texto")
archivo.close()
archivo = open("mi_archivo.txt", "r")
print(archivo.read())

#solucion5
archivo = open("mi_archivo.txt", "a")
archivo.write("Nuevo inicio de sesión")
archivo.close()
archivo = open("mi_archivo.txt", "r")
print(archivo.read())

#solucion6
registro_ultima_sesion = ["Federico", "20/12/2021", "08:17:32 hs", "Sin errores de carga"]

registro = open("registro.txt", "a")
for item in registro_ultima_sesion:
    registro.writelines(item + '\t')

registro.close()
registro = open("registro.txt", "r")
print(registro.read())

#solucion7
from pathlib import Path

ruta_base = Path.home()

#solucion8
"Curso Python"
"Día 6"
"practicas_path.py"
from pathlib import Path

ruta = Path("Curso Python", "Día 6", "practicas_path.py")


#solucion9

"Curso Python"
"Día 6"
"practicas_path.py"
from pathlib import Path

ruta = Path(Path.home(), "Curso Python", "Día 6", "practicas_path.py")


#solucion10
def abrir_leer(archivo):
    archivo = open(archivo)
    return archivo.read()

#solucion11
"contenido eliminado"
def sobrescribir(archivo):
    archivo_sobrescribir = open(archivo, "w")
    archivo_sobrescribir.write("contenido eliminado")


#solucion12
"se ha registrado un error de ejecución"
def registro_error(archivo):
    mi_archivo = open(archivo, "a")
    mi_archivo.write("se ha registrado un error de ejecución")
    mi_archivo.close()

#solucion13
"se ha registrado un error de ejecución"
def registro_error(archivo):
    mi_archivo = open(archivo, "a")
    mi_archivo.write("se ha registrado un error de ejecución")
    mi_archivo.close()




