import pygame
import math
import numpy as np
from track import Track, BLOCK_SIZE
from grass import Grass
from checkpoint import Checkpoint
from boost import Boost
from lava import Lava
from road import Road

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
        self.next_checkpoint = 0
        self.last_checkpoint = 0

        # Paramètres du kart en checkpoint

        self.position_checkpoint = (25,25)
        self.orientation_checkpoint= 0

        # Initialisation image pour kart
        self.image = pygame.image.load('kart.png')                 # chargement de l'image
        self.image = pygame.transform.scale(self.image, (50, 50))  # dimension du kart
        self.rect = self.image.get_rect()  

        # Initialisation commandes
        self.left = False
        self.right = False
        self.up = False
        self.down = False
       
    def reset(self, initial_position, initial_orientation):
        self.position = initial_position
        self.orientation = initial_orientation
        self.velocity = 0
        self.angular_velocity = 0
        self.acceleration = 0
        self.has_finished = False

    # Commande pour accelerer vers l'avant    
    def forward(self):
        self.up = True
        #print("UP", end="  ")
        
        self.acceleration = MAX_ACCELERATION
    
    # Commande pour accelerer vers l'arrière
    def backward(self):
        self.down = True
        #print("DOWN", end="  ")

        self.acceleration = -MAX_ACCELERATION

    # Commande pour tourner vers la gauche
    def turn_left(self):
        self.left = True
        #print("LEFT", end="  ")
        
        #direction = -1 if self.velocity < 0 else 1
        #self.angular_velocity = direction * -MAX_ANGLE_VELOCITY

        self.angular_velocity = -MAX_ANGLE_VELOCITY

    # Commande pour tourner vers la droite   
    def turn_right(self):
        self.right = True
        #print("RIGHT", end="  ")
        
        #direction = -1 if self.velocity < 0 else 1
        #self.angular_velocity = direction * MAX_ANGLE_VELOCITY
        self.angular_velocity = MAX_ANGLE_VELOCITY

    # Commande pour actualiser la position du kart
    def update_position(self, string, screen):

        # on itinialise une seule fois au début du jeu la matrice modifiée en deux dimensions string2D et les dimensions de l'écran
        if not hasattr(self, 'string2D'):  
            self.string2D = string.split('\n')
            self.screen_width, self.screen_height = self.screen_size(self.string2D)
            self.last_checkpoint = self.get_last_checkpoint(string)
            

        # on vérifie le type de la surface

        surface, checkpoint_id = self.get_surface(self.string2D, self.screen_width, self.screen_height)

        if surface == Checkpoint:
            if checkpoint_id == self.next_checkpoint:
                if checkpoint_id == self.last_checkpoint:
                    self.has_finished = True
                else:
                    self.position_checkpoint = self.position
                    self.orientation_checkpoint= self.orientation
                    self.next_checkpoint += 1
                

        
        if surface == Lava:
            self.return_to_checkpoint()
        else:
            # Actualisation de l'orientation

            if self.up == self.down:
                self.acceleration = 0
            
            if self.left == self.right:
                self.angular_velocity = 0
            
            self.orientation += self.angular_velocity

            # Actualisation de la vitesse

            if surface == Boost:
                self.velocity = 25.
            else:
                self.velocity = (self.acceleration - surface.friction * self.velocity * math.cos(self.angular_velocity)) + self.velocity * math.cos(self.angular_velocity)

            # Actualisation de la position
            self.position = (
                self.position[0] + self.velocity * math.cos(self.orientation),
                self.position[1] + self.velocity * math.sin(self.orientation)
            )
        
            # On remet à 0 l'acceleration et la vitesse angulaire pour 
            # le frame suivant

            self.acceleration = 0
            self.angular_velocity = 0

            # Initialisation commandes
            self.left = False
            self.right = False
            self.up = False
            self.down = False

            print("\n")
            # On dessine le kart à la nouvelle position
            self.draw(screen)

    # Methode pour dessiner le kart
    def draw(self, screen):
        
        """kart_radius = 20
        
        # On va mettre en param plutôt la position actuelle
        pygame.draw.circle(screen, (255, 255, 255), self.position, kart_radius)
"""
        """size = 20
        point1 = (self.position[0] + size * math.cos(self.orientation),
            self.position[1] + size * math.sin(self.orientation))
        point2 = (self.position[0] + size * math.cos(self.orientation + 2.0944),  # 120 degrés en radians
            self.position[1] + size * math.sin(self.orientation + 2.0944))
        point3 = (self.position[0] + size * math.cos(self.orientation - 2.0944),  # 240 degrés en radians
            self.position[1] + size * math.sin(self.orientation - 2.0944))

        # Dessine le triangle
        pygame.draw.polygon(screen, (255, 255, 255), [point1, point2, point3])
""" 
        # Initialisation du centre du kart
        self.rect.center = self.position

        # Rotation de l'image du kart en fonction de l'orientation
        rotated_image = pygame.transform.rotate(self.image, -math.degrees(self.orientation+math.pi/2))
        new_rect = rotated_image.get_rect(center=self.rect.center)

        # Affichage de l'image sur l'écran
        screen.blit(rotated_image, new_rect.topleft)

    # méthode pour calculer la taille de l'écran en utilisant la matrice modifiée string2D
    def screen_size(self, string2D):

        # on calcule la largeur et la hauteur de l'écran
        height = len(string2D)*BLOCK_SIZE
        width = len(string2D[0])*BLOCK_SIZE
        
        return width, height
    
    # methode pour vérifier si on sort de l'écran
    def out_of_bounds(self, width, height):
        
        # on vérifie si on sort de l'écran
        if int(self.position[0]) in range(0,width) and int(self.position[1]) in range(0, height):
            return False
        else:
            return True


    # methode pour calculer la friction en fonction de la surface actuelle du kart avec la matrice modifiée string2D
    def get_surface(self, string2D, width, height):

        # on vérifie tout d'abord si l'on sort de l'écran

        if self.out_of_bounds(width, height):
            return Lava, None     #si l'on sort de l'écran on va considérer que cela sera de la lave
        

        # on normalise la position par la taille d'un block pour avoir les bonnes dimensions
        row_ind = int(self.position[1]/ BLOCK_SIZE)
        col_ind = int(self.position[0]/ BLOCK_SIZE)

        # on vérifie le caractère 
        char = string2D[row_ind][col_ind]

        # on vérifie le type de la surface
        surface = Track.char_to_track_element[char]['class']

        # on vérifie le id
        checkpoint_id = None
        if surface == Checkpoint:
            checkpoint_id = Track.char_to_track_element[char]['params'][0]


        return surface, checkpoint_id
    


    def get_last_checkpoint(self, string):
        last_checkpoint = 0
        for char in string:
            if char != '\n':
                if Track.char_to_track_element[char]['class'] == Checkpoint:
                    if Track.char_to_track_element[char]['params'][0] > last_checkpoint:
                        last_checkpoint = Track.char_to_track_element[char]['params'][0]
        return last_checkpoint
    
    def return_to_checkpoint(self):

        self.position = self.position_checkpoint
        self.orientation = self.orientation_checkpoint
        self.velocity = 0



    