import pygame
import random
import math
from pygame import mixer

#Inicializamos el juego
pygame.init()

# crear pantalla
pantalla = pygame.display.set_mode((800, 600))

# Titulo e Icono
pygame.display.set_caption("Invasión Espacial")
icono = pygame.image.load("ovni.png")
pygame.display.set_icon(icono)
fondo = pygame.image.load("Fondo.jpg")

# agregar musica
mixer.music.load('MusicaFondo.mp3')
mixer.music.set_volume(0.3)
mixer.music.play(-1)

# variables del Jugador
img_jugador = pygame.image.load("cohete.png")
jugador_x = 368
jugador_y = 500
jugador_x_cambio = 0

# variables del enemigo
img_enemigo = []
enemigo_x = []
enemigo_y = []
enemigo_x_cambio = []
enemigo_y_cambio = []
cantidad_enemigos = 8 #cada spawm de enemigos

for e in range(cantidad_enemigos):
    img_enemigo.append(pygame.image.load("enemigo.png"))
    enemigo_x.append(random.randint(0, 736))
    enemigo_y.append(random.randint(50, 200))
    enemigo_x_cambio.append(0.5)
    enemigo_y_cambio.append(50)

# variables de la bala
img_bala = pygame.image.load("bala.png")
bala_x = 0
bala_y = 500
bala_x_cambio = 0
bala_y_cambio = 3
bala_visible = False

# puntaje
puntaje = 0
fuente = pygame.font.Font('fastest.ttf', 32)
texto_x = 10
texto_y = 10

# texto final de juego
fuente_final = pygame.font.Font('fastest.ttf', 40)

def texto_final():
    mi_fuente_final = fuente_final.render("GAME OVER", True, (255, 255, 255))
    pantalla.blit(mi_fuente_final, (60, 200))

#mostrar puntaje
def mostrar_puntaje(x, y):
    mi_fuente = fuente.render("Puntaje: " + str(puntaje), True, (255, 255, 255))
    pantalla.blit(mi_fuente, (x, y))

# funcion para el jugador
def jugador(x, y):
    pantalla.blit(img_jugador, (x, y))

#funcion para el enemigo
def enemigo(x, y, i):
    pantalla.blit(img_enemigo[i], (x, y))

# funcion para la bala
def disparar_balas(x, y):
    global bala_visible
    bala_visible = True
    pantalla.blit(img_bala, (x + 16, y + 10))

def hay_colision(enemigo_x, enemigo_y, bala_x, bala_y):
    distancia = math.sqrt(math.pow(enemigo_x - bala_x, 2) + (math.pow(enemigo_y - bala_y, 2)))
    if distancia < 27:
        return True
    else:
        return False


# bucle principal del juego
se_ejecuta = True
while se_ejecuta:

    #imagen de fondo
    pantalla.blit(fondo, (0, 0))

    # iterar sobre los eventos de pygame
    for evento in pygame.event.get():

        #evento de cierre
        if evento.type == pygame.QUIT:
            se_ejecuta = False

        # si se presiona una tecla
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_LEFT:
                jugador_x_cambio = -0.5
            if evento.key == pygame.K_RIGHT:
                jugador_x_cambio = 0.5
            if evento.key == pygame.K_SPACE:
                bala_sonido = mixer.Sound('Space Invaiders/disparo.mp3')
                bala_sonido.set_volume(0.3)
                bala_sonido.play()
                if not bala_visible:
                    bala_x= jugador_x
                    disparar_balas(bala_x, bala_y)
        #soltar tecla
        if evento.type == pygame.KEYUP:
            if evento.key == pygame.K_LEFT or evento.key == pygame.K_RIGHT:
                jugador_x_cambio = 0
    #modificar la posicion del jugador
    jugador_x += jugador_x_cambio

    #limites del jugador
    if jugador_x <= 0:
        jugador_x = 0
    elif jugador_x >= 736:
        jugador_x = 736

    #modificar la posicion del enemigo
    for i in range(cantidad_enemigos):

        #fin del juego
        if enemigo_y[i] > 440:
            for j in range(cantidad_enemigos):
                enemigo_y[j] = 1000
            texto_final()
            break

        enemigo_x[i] += enemigo_x_cambio[i]

    #mantener dentro de los limites
        if enemigo_x[i] <= 0:
            enemigo_x_cambio[i] = 0.5
            enemigo_y[i] += enemigo_y_cambio[i]
        elif enemigo_x[i] >= 736:
            enemigo_x_cambio[i] = -0.5
            enemigo_y[i] += enemigo_y_cambio[i]

        #colision
        colision = hay_colision(enemigo_x[i], enemigo_y[i], bala_x, bala_y)
        if colision:
            explosion_sonido = mixer.Sound('golpe.mp3')
            explosion_sonido.set_volume(0.3)
            explosion_sonido.play()
            bala_y = 500
            bala_visible = False
            puntaje += 1
            enemigo_x[i] = random.randint(0, 736)
            enemigo_y[i] = random.randint(50, 200)
        enemigo(enemigo_x[i], enemigo_y[i], i)

    #modificar la posicion de la bala
    if bala_y <= -64:
        bala_y = 500
        bala_visible = False
    if bala_visible:
        disparar_balas(bala_x, bala_y)
        bala_y -= bala_y_cambio

    jugador(jugador_x, jugador_y)
    mostrar_puntaje(texto_x, texto_y)
    #actualizar la pantalla
    pygame.display.update()
