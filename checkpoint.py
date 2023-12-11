import pygame
from surface import Surface
from abc import ABC, abstractmethod


class Checkpoint(Surface):  

    __friction = 0.02
    # Constructeur

    def __init__(self, x, y, checkpoint_id):
        
        # initialisation d'une instance de Checkpoint à l'aide de la classe mère Surface
        Surface.__init__(self, x, y)
        
        # identifiant du checkpoint
        self.__id = checkpoint_id

        self.__color = (128, 128, 128)

    @classmethod
    def friction(cls):
        return cls.__friction
    
    
    # methode draw qui va dessiner un carré sur l'écran
    def draw(self, screen):
        pygame.draw.rect(screen, self.__color, (self._position[0], self._position[1], 50, 50))
        
    