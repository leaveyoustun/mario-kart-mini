import pygame
#from track import BLOCK_SIZE


class Surface:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 50, 50)

    def contains_point(self, x, y):
        return self.rect.collidepoint(x, y)
