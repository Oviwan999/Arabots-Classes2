#import números

def preguntar():
    print("Bienvenido a Farmacias Similares")

    while True:
        print("[P] - Perfumeria\n[F] - Farmacia\n[C] - Cosmetica")
        try:
            mi_rubro = input("Ingrese su rubro: ").upper()
            ["P", "F", "C"].index(mi_rubro)

        except ValueError:
            print("Lo siento, no es una opcion valida")

        else:
               break

    números.decorador(mi_rubro)


def inicio():

    while True:
        preguntar()

        try:
            otro_turno = input("Desea otro turno? [S/N]: ").upper()
            ["S", "N"].index(otro_turno)
        except ValueError:
            print("Lo siento, no es una opcion valida")

        else:
            if otro_turno == "N":
                print("Gracias por su visita")
                break

inicio()
