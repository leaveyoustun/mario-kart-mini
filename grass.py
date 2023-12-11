import pygame
from surface import Surface
from abc import ABC, abstractmethod

class Grass(Surface):  

    __friction = 0.2
    
    # Constructeur
    
    def __init__(self, x, y):

        # initialisation d'une instance de Grass à l'aide de la classe mère Surface
        Surface.__init__(self, x, y)
        self.__color = (0, 255, 0)

    @classmethod
    def friction(cls):
        return cls.__friction
    
    
    # methode draw qui va dessiner un carré sur l'écran
    def draw(self, screen):
        pygame.draw.rect(screen, self.__color, (self._position[0], self._position[1], 50, 50))
        
    
