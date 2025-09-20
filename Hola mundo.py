def trial(x,*z):
    print(x)
    print(z)
    for i in z:
        print(i)
        for j in i:
            print(j)
            print(x+j)
x=1
y=.125,231,321,312,312,312,123,123,312,13245,465,
trial(x,y)


def Cuadrado(**Lados):
    for key,value in Lados.items():
        perimetro = 0
        print(f"{key} = {value}")
        perimetro = perimetro + value
        area = value**2

    return print(f"El perimetro del cuadrado es: {perimetro}, y el area es: {area}")

Cuadrado(Lado1=5,Lado2=5,Lado3=5,Lado4=5)

def triangulo(**Lados):
    perimetro = 0
    for key,value in Lados.items():
       if key == "base":
           base = value
       elif key == "altura":
            altura = value
       else:

            print(f"{key} = {value}")
            perimetro = perimetro + value
            area = (base*altura)/2
    return print(f"El perimetro del triangulo es: {perimetro} y el area es: {area}")

triangulo(base=5,altura=5,Lado1=5,Lado2=5,Lado3=5)