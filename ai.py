import math
import pygame
from kart import Kart
from lava import Lava
from track import Track
from grass import Grass
from checkpoint import Checkpoint
from boost import Boost
import time


MAX_ANGLE_VELOCITY = 0.05
BLOCK_SIZE = 50

class AI(Kart):
    
    def __init__(self):
        Kart.__init__(self, self)
        self.kart = None

    def move(self, string):

        x_act = int(self.kart._position[0]/BLOCK_SIZE)
        y_act = int(self.kart._position[1]/BLOCK_SIZE)
        """
        Cette methode contient une implementation d'IA tres basique.
        L'IA identifie la position du prochain checkpoint et se dirige dans sa direction.

        :param string: La chaine de caractere decrivant le circuit
        :param screen: L'affichage du jeu
        :param position: La position [x, y] actuelle du kart
        :param angle: L'angle actuel du kart
        :param velocity: La vitesse [vx, vy] actuelle du kart
        :param next_checkpoint_id: Un entier indiquant le prochain checkpoint a atteindre
        :returns: un tableau de 4 boolean decrivant quelles touches [UP, DOWN, LEFT, RIGHT] activer
        """

        # =================================================
        # D'abord trouver la position du checkpoint
        # =================================================
        if self.kart._next_checkpoint == 0:
            char = 'C'
        elif self.kart._next_checkpoint == 1:
            char = 'D'
        elif self.kart._next_checkpoint == 2:
            char = 'E'
        elif self.kart._next_checkpoint == 3:
            char = 'F'

        # On utilise x et y pour decrire les coordonnees dans la chaine de caractere
        # x indique le numero de colonne
        # y indique le numero de ligne
        x_next, y_next = 0, 0
        for c in string:

            # Si on trouve le caractere correpsondant au checkpoint, on s'arrete
            if c == char:
                break

            # Si on trouve le caractere de retour a la ligne "\n" on incremente y et on remet x a 0
            # Sinon on incremente x
            if c == "\n":
                y_next += 1
                x_next = 0
            else:
                x_next += 1

        #next_checkpoint_position = [x * BLOCK_SIZE + .5 * BLOCK_SIZE, y * BLOCK_SIZE + .5 * BLOCK_SIZE]
        #print(self._position)
        #print(x_next, y_next)
        string2D = string.split('\n')

        grid = self.create_grid(string2D)
        #print(string2D[10][21])
        #print(grid[10][21].surface)
        for row in grid:
            for spot in row:
                spot.update_neighbors(grid)
        #print(x_act, y_act)
        start_node = grid[y_act][x_act]
        next_checkpoint_node = grid[y_next][x_next]
        

        path = self.algorithm_A_star(grid, start_node, next_checkpoint_node)
        #smooth_path = self.smooth_path(path)
        #print(path)
        #print(path)
        next_position = path[0] if path else (x_act, y_act)
        # =================================================
        # Ensuite, trouver l'angle vers le checkpoint
        # =================================================
        relative_x = next_position[1]*BLOCK_SIZE+25 - self.kart._position[0]
        relative_y = next_position[0]*BLOCK_SIZE+25 - self.kart._position[1]
        
        # On utilise la fonction arctangente pour calculer l'angle du vecteur [relative_x, relative_y]
        next_checkpoint_angle = math.atan2(relative_y, relative_x)
        
        # L'angle relatif correspond a la rotation que doit faire le kart pour se trouver face au checkpoint
        # On applique l'operation (a + pi) % (2*pi) - pi pour obtenir un angle entre -pi et pi
        relative_angle = (next_checkpoint_angle - self.kart._orientation + math.pi) % (2 * math.pi) - math.pi
        #print(relative_angle)
        # =================================================
        # Enfin, commander le kart en fonction de l'angle
        # =================================================
        DOWN = False
        UP = True
        #print(self.kart._velocity)
        
        #print(self.kart._death)
        if self.kart._velocity > 8 - self.kart._death:
            DOWN = True
            UP = False
        if relative_angle > MAX_ANGLE_VELOCITY:
            # On tourne a droite
            command = [UP, DOWN, False, True]
        elif relative_angle < -MAX_ANGLE_VELOCITY:
            # On tourne a gauche
            command = [UP, DOWN, True, False]
        else:
            # On avance
            command = [UP, DOWN, False, False]
        
            
        key_list = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
        keys = {key: command[i] for i, key in enumerate(key_list)}
        #if pygame.key.get_pressed()[pygame.K_UP]:
        #    time.sleep(0.5)
        time.sleep(0.02)
        #print(time.process_time())
        return keys
    
    def create_grid(self, string2D):
        width, height = self._screen_size(string2D)
        grid = []
        for i in range(len(string2D)):
            grid.append([])
            for j in range(len(string2D[0])):
                char = string2D[i][j]
                surface = Track.char_to_track_element[char]['class']
                checkpoint_id = None
                if surface == Checkpoint:
                    checkpoint_id = Track.char_to_track_element[char]['params'][0]

                grid[i].append(Node(i, j, surface, checkpoint_id))

        return grid
    
    def reconstruct_path(self, came_from, current):
        path = []
        while current in came_from:
            path.append(current.position)
            current = came_from[current]
        return path[::-1]  # Return reversed path
    
    def update(self, string):
        # Calculate the path to the next checkpoint or finish line
        path = self.algorithm_A_star(string, self.position, self.__next_checkpoint)
        if path:
            next_position = path[0]  # Get the next position to move towards
            self.move_towards(next_position)



            
    def get_lowest_cost_node(self, open_set):
        lowest_index = 0
        for i in range(len(open_set)):
            if open_set[i].f_cost < open_set[lowest_index].f_cost or \
                (open_set[i].f_cost == open_set[lowest_index].f_cost and open_set[i].h_cost < open_set[lowest_index].h_cost):
                lowest_index = i
        return open_set.pop(lowest_index) ##return and remove the lowest cost node
    
    
    def h(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    

    def algorithm_A_star(self, grid, start, end):
        open_set = [start]
        came_from = {}
        g_score_dict = {}
        for row in grid:
            for spot in row:
                g_score_dict[spot] = float("inf")
        g_score_dict[start] = 0
        f_score_dict = {}
        for row in grid:
            for spot in row:
                f_score_dict[spot] = float("inf")
        start.g_cost = 0
        start.update_h_cost(self.h(start.position, end.position))

        while len(open_set) > 0:
            current = self.get_lowest_cost_node(open_set)

            if current == end:
                return self.reconstruct_path(came_from, end)
            
            
            for neighbor in current.neighbors:
                temp_g_score = g_score_dict[current] + (1.414 if self.is_diagonal(current, neighbor) else 1)

                if temp_g_score < g_score_dict[neighbor]:
                    came_from[neighbor] = current
                    neighbor.update_g_cost(temp_g_score)
                    neighbor.update_h_cost(self.h(neighbor.position, end.position))
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    g_score_dict[neighbor] = temp_g_score
                    f_score_dict[neighbor] = neighbor.f_cost

                    if neighbor not in open_set:
                        open_set.append(neighbor)
            
        
        return None
    
    def is_diagonal(self, node1, node2):
	    return node1.position[0] != node2.position[0] and node1.position[1] != node2.position[1]
    
    

    
    
    
class Node:
    def __init__(self, x, y, surface, checkpoint_id):
        self.position = (x, y)
        self.surface = surface
        if self.surface == Lava:
            self.g_cost = float("inf")
        elif self.surface == Grass:
            self.g_cost = 10000
        elif self.surface == Boost:
            self.g_cost = -float("inf")
        else:
            self.g_cost = 100

        self.checkpoint_id = checkpoint_id
        #self.g_cost = float("inf")
        self.h_cost = 0
        self.f_cost = self.g_cost + self.h_cost
        self.neighbors = []

    def update_neighbors(self, grid):
        self.neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue          # Skip the current spot itself
                row = self.position[0] + dx
                col = self.position[1] + dy
                if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                    neighbor = grid[row][col]
                    if not neighbor.surface == Lava:
                        self.neighbors.append(neighbor)  

    def update_g_cost(self, new_g_cost):
        if self.surface == Lava:
            self.g_cost = float("inf")
        elif self.surface == Grass:
            self.g_cost == new_g_cost + 1000
        elif self.surface == Boost:
            self.g_cost =  - float("inf")
        else:
            self.g_cost = new_g_cost

    def update_h_cost(self, new_h_cost):
        self.h_cost = new_h_cost
     


