import pygame
from abc import ABC, abstractmethod


class Controller():

    def __init__(self):
        self.kart = None

    @abstractmethod
    def move(self, string):
        pass