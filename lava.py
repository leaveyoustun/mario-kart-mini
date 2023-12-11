import pygame
from surface import Surface
from abc import ABC, abstractmethod

class Lava(Surface): 
    #friction = 0.02
    # Constructeur

    def __init__(self, x, y): 
        
        # initialisation d'une instance de Lava à l'aide de la classe mère Surface
        Surface.__init__(self, x, y)

        # couleur du block
        self.__color = (255, 0, 0)
    
    # methode draw qui va dessiner un carré sur l'écran
    def draw(self, screen):
        pygame.draw.rect(screen, self.__color, (self._position[0], self._position[1], 50, 50))
        
    