import pygame
import math
import numpy as np
from track import BLOCK_SIZE


MAX_ANGLE_VELOCITY = 0.05
MAX_ACCELERATION = 0.25
initial_position = (75, 75)
initial_orientation = 0
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
        self.position = initial_position
        self.orientation = initial_orientation
        self.velocity = 0
        self.angular_velocity = 0
        self.acceleration = 0
        self.has_finished = False

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

        # on calcule la taille de l'écran
        width, height = self.screen_size(string)

        # on teste si on sort de l'écran
        if self.out_of_bounds(width, height):
            self.reset(initial_position, initial_orientation)
            self.draw(screen)
            return 0

        
        # cette fois-ci on calcule la friction à l'aide de la méthode get_friction(en bas)

        f = self.get_friction(string)
        
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

    def screen_size(self, string):
        # on modifie le string de façon à ce qu'il soit une matrice 2D
        string2D = string.split('\n')

        # on calcule la largeur et la hauteur de l'écran
        height = len(string2D)*BLOCK_SIZE
        width = len(string2D[0])*BLOCK_SIZE
        
        return width, height
    
    def out_of_bounds(self, width, height):
        
        # on vérifie si on sort de l'écran
        if int(self.position[0]) in range(0,width) and int(self.position[1]) in range(0, height):
            return False
        else:
            return True


    # methode pour calculer la friction en fonction de la surface actuelle du kart
    def get_friction(self, string):

        # on modifie le string de façon à ce qu'il soit une matrice 2D
        string2D = string.split('\n')

        # on normalise la position par la taille d'un block pour avoir les bonnes dimensions
        row_ind = int(self.position[1]/ BLOCK_SIZE)
        col_ind = int(self.position[0]/ BLOCK_SIZE)

        # on vérifie le type de surface
        surface = string2D[row_ind][col_ind]

        # on calcule la friction
        if surface == 'G':
            f = 0.2
        else:
            f = 0.02

        return f


    