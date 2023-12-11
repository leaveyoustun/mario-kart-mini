import pygame
from surface import Surface
from abc import ABC, abstractmethod

class Road(Surface): 
    
    __friction = 0.02
    
    # Constructeur

    def __init__(self, x, y):

        # initialisation d'une instance de Road à l'aide de la classe mère Surface
        Surface.__init__(self, x, y)
        self.__color = (0, 0, 0)

    @classmethod
    def friction(cls):
        return cls.__friction
    
    
    # methode draw qui va dessiner un carré sur l'écran
    def draw(self, screen):
        pygame.draw.rect(screen, self.__color, (self._position[0], self._position[1], 50, 50))
        
    
    