class persona:

    def __init__(self, nombre, apellido):
        self.nombre = nombre
        self.apellido = apellido



class cliente (persona):

    def __init__(self, nombre, apellido, numero_de_cuenta, balance = 0):
        super().__init__(nombre, apellido)
        self.numero_de_cuenta = numero_de_cuenta
        self.balance = balance


    def __str__(self):
        return f"Cliente: {self.nombre} {self.apellido}\nBalance de cuenta: {self.numero_de_cuenta} ${self.balance}"


    def depositar(self, monto):
        self.balance += monto
        print(f"Depositado correctamente")

    def retirar(self, monto):
        if self.balance >= monto:
            self.balance -= monto
            print(f"Retirado correctamente")
        else:
            print(f"Saldo insuficiente")


def crear_cliente():
    nombre = input("Nombre: ")
    apellido = input("Apellido: ")
    numero_de_cuenta = input("Numero de cuenta: ")
    cliente1 = cliente(nombre, apellido, numero_de_cuenta)
    return cliente1

def inicio():
    mi_cliente = crear_cliente()
    print(mi_cliente)
    opcion = 0

    while opcion != "e":

        print ("seleccione: Depositar (J) Retirar (o) Salir (e)")
        opcion = input()

        if opcion == "J":
            monto = int(input("Monto a depositar: "))
            mi_cliente.depositar(monto)

        elif opcion == "o":
            monto = int(input("Monto a retirar: "))
            mi_cliente.retirar(monto)

            print (mi_cliente)


    print ("Gracias por usar el sistema")

inicio()
