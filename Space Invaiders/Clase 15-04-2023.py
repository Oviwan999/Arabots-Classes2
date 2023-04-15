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
icono = pygame.image.load("Space Invaiders/ovni.png")
pygame.display.set_icon(icono)
fondo = pygame.image.load('Space Invaiders/Fondo.jpg')

