import pygame
from surface import Surface
from abc import ABC, abstractmethod

class Road(Surface): 
    
    __friction = 0.02
    
    # Constructeur

    def __init__(self, x, y):

        # initialisation d'une instance de Road à l'aide de la classe mère Surface
        Surface.__init__(self, x, y)
        self.__image = pygame.image.load('road.jpg')                   # chargement de l'image
        self.__image = pygame.transform.scale(self.__image, (50, 50))  # dimension de l'image
        self.__rect = self.__image.get_rect()  
        self.__rect.center = (self._position[0]+25, self._position[1]+25)

    # Methode pour dessiner la surface
    def draw(self, screen):
        screen.blit(self.__image, self.__rect.topleft)

    @classmethod
    def friction(cls):
        return cls.__friction
