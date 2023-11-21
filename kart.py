import pygame
import math
import numpy as np

MAX_ANGLE_VELOCITY = 0.05
MAX_ACCELERATION = 0.25


class Kart():  # Vous pouvez ajouter des classes parentes
    """
    Classe implementant l'affichage et la physique du kart dans le jeu
    """
    
    # Constructeur
    def __init__(self, controller):
        self.has_finished = False
        self.controller = controller

        # Valeurs initiales des parametres du kart 
        self.position = (75, 75)  
        self.orientation = 0 
        self.velocity = 0
        self.angular_velocity = 0
        self.acceleration = 0
    
       
    def reset(self, initial_position, initial_orientation):
        # A completer
        pass

    # Commande pour accelerer vers l'avant    
    def forward(self):
        self.acceleration = MAX_ACCELERATION
    
    # Commande pour accelerer vers l'arrière
    def backward(self):
        self.acceleration = -MAX_ACCELERATION

    # Commande pour tourner vers la gauche
    def turn_left(self):
        self.angular_velocity = -MAX_ANGLE_VELOCITY

    # Commande pour tourner vers la droite   
    def turn_right(self):
        self.angular_velocity = MAX_ANGLE_VELOCITY

    # Commande pour actualiser la position du kart
    def update_position(self, string, screen):
        # pour faire simple, pour l'instant on va
        # initialiser f à 0.02, comme si l'herbe
        # agissait pas sur le kart

        f = 0.02
        
        # Actualisation de l'orientation
        self.orientation += self.angular_velocity

        # Actualisation de la vitesse
        self.velocity = (self.acceleration - f * self.velocity * math.cos(self.angular_velocity)) + self.velocity * math.cos(self.angular_velocity)

        # Actualisation de la position
        self.position = (
            self.position[0] + self.velocity * math.cos(self.orientation),
            self.position[1] + self.velocity * math.sin(self.orientation)
        )
        
        # On remet à 0 l'acceleration et la vitesse angulaire pour 
        # le frame suivant

        self.acceleration = 0
        self.angular_velocity = 0

        # On dessine le kart à la nouvelle position
        self.draw(screen)

    # Methode pour dessiner le kart
    def draw(self, screen):
        
        kart_radius = 20
        
        # On va mettre en param plutôt la position actuelle
        pygame.draw.circle(screen, (255, 255, 255), self.position, kart_radius)

    