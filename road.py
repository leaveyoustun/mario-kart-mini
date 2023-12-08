import pygame

class Road(): 
    
    friction = 0.02
    
    # Constructeur

    def __init__(self, x, y):

        # coordonnées du block
        self.x = x
        self.y = y

        # couleur du block
        self.color = (0, 0, 0)
    
    # methode draw qui va dessiner un carré sur l'écran
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, 50, 50))
 
    