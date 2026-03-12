from random import randint

def dados():
    input("Tira los dados")
    dado_1 = randint(1, 6)
    print("El dado 1 es: ", dado_1)
    input("Tira los dados")
    dado_2 = randint(1, 6)
    print("El dado 2 es: ", dado_2)
    return dado_1, dado_2

def dif(dado_1, dado_2, punto1, punto2):

    if dado_1 == dado_2:
        print("Empate")
    elif dado_1 > dado_2:
        print("jugador 1 se suma un punto")
        punto1 += 1
    else:
        print("jugador 2 se suma un punto")
        punto2 += 1
    return punto1, punto2
punto1 = 0
punto2 = 0
while not punto2 == 2 or punto1 == 2:
    dado_1, dado_2 = dados()
    punto1, punto2 = dif(dado_1, dado_2, punto1, punto2)
    print("Marcador:", punto1, "-", punto2)
    print("\n")
    if punto2 == 2 or punto1 == 2:
        break
print("\n")
if punto1 > punto2:
    print("Gano el jugador1")
else:
    print("Gano el jugador2")
