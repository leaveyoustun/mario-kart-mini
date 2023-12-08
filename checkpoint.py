import pygame


class Checkpoint():  

    friction = 0.02
    # Constructeur

    def __init__(self, x, y, checkpoint_id):
        
        # coordonnées du block
        self.x = x
        self.y = y
        
        # identifiant du checkpoint
        self.id = checkpoint_id

        # couleur du block
        self.color = (128, 128, 128)
    
    # methode draw qui va dessiner un carré sur l'écran
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, 50, 50))
    