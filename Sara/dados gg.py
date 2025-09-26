from random import randint

def JugadorUno():
    print("***Jugador 1***")
    input("Tira el dado :)")
    dado = randint(1, 6)
    print(dado)
    return dado

def JugadorDos():
    print("***Jugador 2***")
    input("Tira el dado :)")
    dado = randint(1, 6)
    print(dado)
    return dado

def Comparacion(a, b, pun1, pun2):
    if a > b:
        print("Va ganando el jugador 1 :D")
        pun1 += 1
    elif a == b:
        print("lol, que mal, están empates")
    else:
        print("Va ganando el jugador 2 :D")
        pun2 += 1
    return pun1, pun2

pun1 = 0
pun2 = 0

while pun1 < 2 and pun2 < 2:
    variable1 = JugadorUno()
    variable2 = JugadorDos()
    pun1, pun2 = Comparacion(variable1, variable2, pun1, pun2)
    print("Puntitos: Jugador 1:", pun1, "Jugador 2:", pun2, "\n")

if pun1 == 2:
    print("Ganó el Jugador 1! :)")
else:
    print("Ganó el Jugador 2! :)")
