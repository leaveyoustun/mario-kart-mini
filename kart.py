import pygame
import math
import numpy as np
from track import Track, BLOCK_SIZE
from grass import Grass
from checkpoint import Checkpoint
from boost import Boost
from lava import Lava
from road import Road
from surface import Surface

MAX_ANGLE_VELOCITY = 0.05
MAX_ACCELERATION = 0.25

class Kart(Surface): 

    """
    Classe implementant l'affichage et la physique du kart dans le jeu
    """
    
    
    # Constructeur
    def __init__(self, controller):
        self.__has_finished = False
        self.__controller = controller

        # Valeurs initiales des parametres du kart 
        Surface.__init__(self, 75, 75)  
        self.__orientation = 0 
        self.__velocity = 0
        self.__angular_velocity = 0
        self.__acceleration = 0
        self.__next_checkpoint = 0
        self.__last_checkpoint = 0

        # Paramètres du kart en checkpoint

        self.__position_checkpoint = (75,75)
        self.__orientation_checkpoint= 0

        # Initialisation image pour kart
        self.__image = pygame.image.load('kart.png')                   # chargement de l'image
        self.__image = pygame.transform.scale(self.__image, (50, 50))  # dimension du kart
        self.__rect = self.__image.get_rect()  

        # Initialisation des commandes
        self.__left = False
        self.__right = False
        self.__up = False
        self.__down = False

        # Initialisation du compteur de morts et du booléen qui nous dit si le kart est mort ou pas
        self.__death_count = 0
        self.__death = False
        
        # Attribution de l'attribut kart
        self.__controller.kart = self

    #Getter pour has_finished
    @property
    def has_finished(self):
        return self.__has_finished
    
    #Getter pour controller
    @property
    def controller(self):
        return self.__controller
    
    #Getter pour next_checkpoint
    @property
    def next_checkpoint(self):
        return self.__next_checkpoint
    
    #Getter pour death
    @property
    def death(self):
        return self.__death
    
    #Setter pour death
    @death.setter
    def death(self, value):
        self.__death = value
    
    #Getter pour death_count
    @property
    def death_count(self):
        return self.__death_count
    
    #Getter pour orientation
    @property
    def orientation(self):
        return self.__orientation
    
    #Getter pour velocity
    @property
    def velocity(self):
        return self.__velocity
    
    #Getter pour last_checkpoint
    @property
    def last_checkpoint(self):
        return self.__last_checkpoint
    
    #Setter pour last_checkpoint
    @last_checkpoint.setter
    def last_checkpoint(self, value):
        self.__last_checkpoint = value

    #Getter pour position_checkpoint
    @property
    def position_checkpoint(self):
        return self.__position_checkpoint
    
    
    
       
    # Commande permettant de remettre le kart en position initiale
    def reset(self, initial_position, initial_orientation):
        self._position = initial_position
        self.__orientation = initial_orientation
        self.__velocity = 0
        self.__angular_velocity = 0
        self.__acceleration = 0
        self.__has_finished = False

    # Commande pour accelerer vers l'avant    
    def forward(self):
        self.__up = True
        self.__acceleration = MAX_ACCELERATION
    
    # Commande pour accelerer vers l'arrière
    def backward(self):
        self.__down = True
        self.__acceleration = -MAX_ACCELERATION

    # Commande pour tourner vers la gauche
    def turn_left(self):
        self.__left = True
        self.__angular_velocity = -MAX_ANGLE_VELOCITY

    # Commande pour tourner vers la droite   
    def turn_right(self):
        self.__right = True
        self.__angular_velocity = MAX_ANGLE_VELOCITY

    # Commande pour actualiser la position du kart
    def update_position(self, string, screen):

        # on itinialise une seule fois au début du jeu la matrice modifiée en deux dimensions string2D et les dimensions de l'écran
        if not hasattr(self, '__string2D'):  
            self.__string2D = string.split('\n')
            self.__screen_width, self.screen_height = self._screen_size(self.__string2D)
            self.__last_checkpoint = self._get_last_checkpoint(string)
            

        # on vérifie le type de la surface

        surface, checkpoint_id = self.__get_surface(self.__string2D, self.__screen_width, self.screen_height)


        if surface == Checkpoint:

            # si c'est le bon checkpoint, on réinitialise death_count et on vérifie si c'est la fin
            if checkpoint_id == self.__next_checkpoint:
                self.__death_count = 0

                # si c'est le dernier checkpoint, on finit le jeu
                if checkpoint_id == self.__last_checkpoint:
                    self.__has_finished = True

                # sinon, on stocke en mémoire la position et l'orientation du kart
                else:
                    self.__position_checkpoint = self._position
                    self.__orientation_checkpoint= self.__orientation
                    self.__next_checkpoint += 1
                

        
        # si c'est de la lave, on retourne au checkpoint
        if surface == Lava:
            self.__return_to_checkpoint()
        else:
            # Actualisation de l'orientation

            if self.__up == self.__down:
                self.__acceleration = 0
            
            if self.__left == self.__right:
                self.__angular_velocity = 0
            
            self.__orientation += self.__angular_velocity

            # Actualisation de la vitesse

            if surface == Boost:
                self.__velocity = 25.
            else:
                self.__velocity = (self.__acceleration - surface.friction() * self.__velocity * math.cos(self.__angular_velocity)) + self.__velocity * math.cos(self.__angular_velocity)

            # Actualisation de la position
            self._position = (
                self._position[0] + self.__velocity * math.cos(self.__orientation),
                self._position[1] + self.__velocity * math.sin(self.__orientation)
            )
        
            # On remet à 0 l'acceleration et la vitesse angulaire pour 
            # le frame suivant
            self.__acceleration = 0
            self.__angular_velocity = 0

            # Rénitialisation commandes
            self.__left = False
            self.__right = False
            self.__up = False
            self.__down = False

            # On dessine le kart à la nouvelle position
            self.draw(screen)

    # Methode pour dessiner le kart
    def draw(self, screen):
        
        # Initialisation du centre du kart
        self.__rect.center = self._position

        # Rotation de l'image du kart en fonction de l'orientation
        rotated_image = pygame.transform.rotate(self.__image, -math.degrees(self.__orientation+math.pi/2))
        new_rect = rotated_image.get_rect(center=self.__rect.center)

        # Affichage de l'image sur l'écran
        screen.blit(rotated_image, new_rect.topleft)

    # méthode pour calculer la taille de l'écran en utilisant la matrice modifiée string2D
    def _screen_size(self, string2D):

        # on calcule la largeur et la hauteur de l'écran
        height = len(string2D)*BLOCK_SIZE
        width = len(string2D[0])*BLOCK_SIZE
        
        return width, height
    
    # methode pour vérifier si on sort de l'écran
    def __out_of_bounds(self, width, height):
        
        # on vérifie si on sort de l'écran
        if int(self._position[0]) in range(0,width) and int(self._position[1]) in range(0, height):
            return False
        else:
            return True


    # methode pour calculer la friction en fonction de la surface actuelle du kart avec la matrice modifiée string2D
    def __get_surface(self, string2D, width, height):

        # on vérifie tout d'abord si l'on sort de l'écran

        if self.__out_of_bounds(width, height):
            return Lava, None     #si l'on sort de l'écran on va considérer que cela sera de la lave
        

        # on normalise la position par la taille d'un block pour avoir les bonnes dimensions
        row_ind = int(self._position[1]/ BLOCK_SIZE)
        col_ind = int(self._position[0]/ BLOCK_SIZE)

        # on vérifie le caractère 
        char = string2D[row_ind][col_ind]

        # on vérifie le type de la surface
        surface = Track.char_to_track_element[char]['class']

        # on vérifie le id
        checkpoint_id = None
        if surface == Checkpoint:
            checkpoint_id = Track.char_to_track_element[char]['params'][0]


        return surface, checkpoint_id
    
    # méthode pour calculer le dernier checkpoint du track
    def _get_last_checkpoint(self, string):
        last_checkpoint = 0
        for char in string:
            if char != '\n':
                if Track.char_to_track_element[char]['class'] == Checkpoint:
                    if Track.char_to_track_element[char]['params'][0] > last_checkpoint:
                        last_checkpoint = Track.char_to_track_element[char]['params'][0]
        return last_checkpoint
    
    # méthode pour remettre le kart à sa position au dernier checkpoint
    def __return_to_checkpoint(self):

        self._position = self.__position_checkpoint
        self.__orientation = self.__orientation_checkpoint
        self.__velocity = 0
        self.__death_count +=1
        self.__death = True



    