from random import choice
Pal = {"Pala": ["roca", "oso", "torta", "escuela", "señor", "carro", "parangaricutirimicuaro", "rata", "lobo", "panda"]}
pala = choice(Pal["Pala"])
print("La palabra tiene", len(pala), "letras.")
num = list(pala)
guion = "-" * len(pala)
print(guion)
resp = list(guion)
vidas = 6
proba = ""

def letras():
    while True:
        l = input("Escribe una sola letra: ").lower()
        if len(l) == 1 and l.isalpha():
            return l        # <- regresa la letra válida
        else:
            print("Error: escribe SOLO una letra.")

def checa(letra, num, resp, proba):
    proba = proba + letra if letra not in proba else proba
    acierto = False
    for i in range(len(num)):
        if letra == num[i]:
            resp[i] = letra
            acierto = True
    return resp, proba, acierto

def final(acierto, vidas, resp, proba):
    if not acierto:
        print("No le sabes")
        vidas -= 1
    print("Letras bien:", "".join(resp))
    print("Letras probadas:", proba)
    print("Tus vidas:", vidas)
    print("\n")
    return vidas

while resp != num and vidas > 0:
    letra = letras()
    resp, proba, acierto = checa(letra, num, resp, proba)
    vidas = final(acierto, vidas, resp, proba)

if resp == num:
    print("Ganaste :)")
else:
    print("Perdiste :(")
print("\nPalabra secreta:", "".join(num))
