import pygame
from abc import ABC, abstractmethod



class Surface(ABC):

    def __init__(self, x, y):
        self._position = (x,y)
        
    @abstractmethod
    def draw(self,screen):
        pass
    