nombre = input("Por favor, dime tu nombre: ")
ventas = int(input("Diga sus ventas totales del mes: "))

comision = round(ventas * 13 / 100,2)

print(f"Hola {nombre}, tus comisiones de este mes son de ${comision}")