from random import randint
dado_1 = 0
dado_2 = 0

punto1 = 0
punto2 = 0

while not punto1 == 2 or punto2 == 2:
    print("\n")
    input("Jugador 1 precione para lanzar el dado")
    dado_1 = randint(1, 6)
    print("El numero 1 es: ", dado_1)
    input("Jugador 2 pressione para lanzar el dado")
    dado_2 = randint(1, 6)
    print("El numero 2 es: ", dado_2)

    if dado_1 == dado_2:
        print("Empate")
    elif dado_1 > dado_2:
        print("jugador 1 se suma un punto")
        punto1 = punto1 + 1
    else:
        print("jugador 2 se suma un punto")
        punto2 = punto2 + 1
print("\n")
if punto1 > punto2:
    print("Gano el jugador1")
else:
    print("Gano el jugador2")