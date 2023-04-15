
def mensaje(data=input("Ingrese un dato: ")):
    if data.isnumeric():
        return "El dato ingresado es un número"
    elif data.isalpha():
        return "El dato ingresado es un texto"
    else:
        return "El dato ingresado es un dato desconocido"


print(mensaje())