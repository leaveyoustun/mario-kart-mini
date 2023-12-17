import time
import pygame
from controller import Controller

class Human(Controller):
    
    def __init__(self):
        Controller.__init__(self)
        
    def move(self, string):
        time.sleep(0.02)
        return pygame.key.get_pressed()