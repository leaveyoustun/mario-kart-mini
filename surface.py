import pygame
from abc import ABC, abstractmethod
#from track import BLOCK_SIZE


class Surface(ABC):

    def __init__(self, x, y):
        self._position = (x,y)
        
    @abstractmethod
    def draw(self,screen):
        pass
    