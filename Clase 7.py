#solucion1
class Personaje:
    pass


harry_potter = Personaje()

#solucion2
class Dinosaurio:
    pass
velociraptor = Dinosaurio()
tiranosaurio_rex = Dinosaurio()
braquiosaurio = Dinosaurio()

#solucion3
class PlataformaStreaming:
    pass

netflix = PlataformaStreaming()
hbo_max = PlataformaStreaming()
amazon_prime_video = PlataformaStreaming()

#solucion4
class Casa:
    def __init__(self, color, cantidad_pisos):
        self.color = color
        self.cantidad_pisos = cantidad_pisos


casa_blanca = Casa("blanco", 4)

#solucion5
class Cubo:
    caras = 6

    def __init__(self, color):
        self.color = color


cubo_rojo = Cubo("rojo")

#solucion6
class Personaje:
    real = False

    def __init__(self, especie, magico, edad):
        self.especie = especie
        self.magico = magico
        self.edad = edad


harry_potter = Personaje("humano", True, 17)

#solucion7
class Perro:
    def ladrar(self):
        print("Guau!")


pluto = Perro()
pluto.ladrar()

#solucion8
class Mago:
    def lanzar_hechizo(self):
        print("¡Abracadabra!")


merlin = Mago()
merlin.lanzar_hechizo()

#solucion9
class Alarma:
    def postergar(self,cantidad_minutos):
        print(f"La alarma ha sido pospuesta {cantidad_minutos} minutos")


#solucion10
class Mascota:
    @staticmethod
    def respirar():
        print("Inhalar... Exhalar")


#solucion11
class Jugador:
    vivo = False

    @classmethod
    def revivir(cls):
        cls.vivo = True

#solucion12
class Personaje:
    def __init__(self, cantidad_flechas):
        self.cantidad_flechas = cantidad_flechas

    def lanzar_flecha(self):
        self.cantidad_flechas = self.cantidad_flechas - 1

#solucion13
class Persona:
    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad


class Alumno(Persona):
    pass


#solucion14
class Mascota:
    def __init__(self, edad, nombre, cantidad_patas):
        self.edad = edad
        self.nombre = nombre
        self.cantidad_patas = cantidad_patas


class Perro(Mascota):
    pass


teo = Perro(6, "Teo", 4)


#solucion15
class Vehiculo:
    def acelerar(self):
        pass

    def frenar(self):
        pass


class Automovil(Vehiculo):
    pass



#solucion16
class Padre():
    def trabajar(self):
        print("Trabajando en el Hospital")

    def reir(self):
        print("Ja ja ja!")


class Madre():
    def trabajar(self):
        print("Trabajando en la Fiscalía")


class Hija(Madre, Padre):
    pass


#solucion17
class Vertebrado():
    vertebrado = True


class Ave(Vertebrado):
    tiene_pico = True

    def poner_huevos(self):
        print("Poniendo huevos")


class Reptil(Vertebrado):
    venenoso = True


class Pez(Vertebrado):
    def nadar(self):
        print("Nadando")

    def poner_huevos(self):
        print("Poniendo huevos")


class Mamifero(Vertebrado):
    def caminar(self):
        print("Caminando")

    def amamantar(self):
        print("Amamantando crías")


class Ornitorrinco(Mamifero, Pez, Reptil, Ave):
    pass


#solucion18
class Padre():
    color_ojos = "marrón"
    tipo_pelo = "rulos"
    altura = "media"
    voz = "grave"
    deporte_preferido = "tenis"

    def reir(self):
        return "Jajaja"

    def hobby(self):
        return "Pinto madera en mi tiempo libre"

    def caminar(self):
        return "Caminando con pasos largos y rápidos"


class Hijo(Padre):
    def hobby(self):
        return "Juego videojuegos en mi tiempo libre"


#solucion19
palabra = "polimorfismo"
lista = ["Clases", "POO", "Polimorfismo"]
tupla = (1, 2, 3, 80)

for dato in [palabra, lista, tupla]:
    print(len(dato))

#solucion20
class Mago():
    def atacar(self):
        print("Ataque mágico")


class Arquero():
    def atacar(self):
        print("Lanzamiento de flecha")


class Samurai():
    def atacar(self):
        print("Ataque con katana")


gandalf = Mago()
hawkeye = Arquero()
jack = Samurai()

personajes = [hawkeye, gandalf, jack]

for personaje in personajes:
    personaje.atacar()


#solucion21
class Mago():
    def defender(self):
        print("Escudo mágico")


class Arquero():
    def defender(self):
        print("Esconderse")


class Samurai():
    def defender(self):
        print("Bloqueo")


def personaje_defender(personaje):
    personaje.defender()



#solucion22

class Libro():
    def __init__(self, titulo, autor, cantidad_paginas):
        self.titulo = titulo
        self.autor = autor
        self.cantidad_paginas = cantidad_paginas

    def __str__(self):
        return f'"{self.titulo}", de {self.autor}'



#solucion23
class Libro():
    def __init__(self, titulo, autor, cantidad_paginas):
        self.titulo = titulo
        self.autor = autor
        self.cantidad_paginas = cantidad_paginas

    def __len__(self):
        return self.cantidad_paginas




#solucion24
class Libro():
    def __init__(self, titulo, autor, cantidad_paginas):
        self.titulo = titulo
        self.autor = autor
        self.cantidad_paginas = cantidad_paginas

    def __del__(self):
        print(f'Libro eliminado')


        