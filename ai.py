import math
import pygame
from kart import Kart
from lava import Lava
from track import Track
from grass import Grass
from checkpoint import Checkpoint
from boost import Boost
from controller import Controller
import time


MAX_ANGLE_VELOCITY = 0.05
BLOCK_SIZE = 50
DISTANCE_TURN = 3

class AI(Controller):
    
    def __init__(self):
        Controller.__init__(self)

        # Les coordonnées du kart dans le grid
        self.__x_act = 0
        self.__y_act = 0

    def move(self, string):
        time.sleep(0.02)

        # On normalise la position actuelle du kart pour avoir les coordonnées dans le grid
        self.__x_act = int(self.kart._position[0]/BLOCK_SIZE)
        self.__y_act = int(self.kart._position[1]/BLOCK_SIZE)
    
        """
        Cette methode contient l'implémentation d'une IA qui utilise l'algorithme A* pour trouver
        le meilleur chemin pour atteindre les checkpoints un par un.
        On vérifie si sur le chemin existe un virage à une distance DISTANCE_TURN et si oui, on ralentit.
        Au début, l'algorithme va chercher à passer par les boosts. Mais si on meurt, c'est à dire si on tombe
        et revient au checkpoint, l'algorithme ne va plus chercher à passer par des boosts et va les traiter comme
        l'herbe. Mais si on tombe une deuxième fois, l'algorithme va eviter les boosts quitte à aller dans l'herbe.


        :param string: La chaine de caractere decrivant le circuit
        :param x_act: La position x actuelle du kart dans le grid
        :param y_act: La position y actuelle du kart dans le grid
        :param orientation: L'orientation actuelle du kart
        :param velocity: La vitesse actuelle du kart
        :param next_checkpoint: Un entier indiquant le prochain checkpoint a atteindre
        :returns: un tableau de 4 boolean decrivant quelles touches [UP, DOWN, LEFT, RIGHT] activer
        """

        """
        Cette IA aura deux chemins en mémoire à tout instant, un chemin qu'on va calculer au début
        pour toute la longueur du circuit, et un deuxième chemin qu'on va calculer à chaque instant pour 
        pouvoir arriver au but même s'il y a des imprévus sur le chemin (vu que l'algorithme A* ne tient pas 
        compte de l'inertie, une vitesse trop grande peut éloigner le kart du chemin le plus court). Le premier chemin,
        celui qu'on calcule une seule fois, sera utilisé pour vérifier s'il y a des virages qui s'approchent.
        Ce chemin-ci sera recalculé si jamais on meurt.
        """

        # Initialisation du grid et du tableau à deux dimensions qui décrit le terrain du circuit

        if not hasattr(self, '__grid'):

            self.__string2D = string.split('\n')
            self.__grid = self.__create_grid(self.__string2D)

        # On actualise à chaque frame les voisins dans le grid
            
        for row in self.__grid:
            for spot in row:
                spot.update_neighbors(self.__grid)

        # On calcule une seule fois au début le meilleur chemin avec l'algorithme A*
                
        if not hasattr(self, 'full_path'):

            self.full_path = self.__find_full_path(self.__grid, string)

        # On recalcule le full_path si jamais on meurt
        if self.kart.death:
            self.__reset_grid(self.__grid)

            self.full_path = self.__find_full_path(self.__grid, string)
            self.__reset_grid(self.__grid)
            self.kart.death = False



        # =================================================
        # Maintenant on va trouver la position du checkpoint
        # =================================================
        if self.kart.next_checkpoint == 0:
            char = 'C'
        elif self.kart.next_checkpoint == 1:
            char = 'D'
        elif self.kart.next_checkpoint == 2:
            char = 'E'
        elif self.kart.next_checkpoint == 3:
            char = 'F'

        # On utilise x_next et y_next pour decrire les coordonnees du checkpoint dans la chaine de caractere
        # x_next indique le numero de colonne
        # y_next indique le numero de ligne
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

        # On calcule la position dans le gride du node correspondant à la position du kart et 
        # du node correspondant au prochan checkpoint
        start_node = self.__grid[self.__y_act][self.__x_act]
        next_checkpoint_node = self.__grid[y_next][x_next]
        
        # On calcule à chaque frame le meilleur chemin jusqu'au prochain checkpoint
        path = self.__algorithm_A_star(self.__grid, start_node, next_checkpoint_node)


        # Maintentant on va essayer de trouver les commandes pour arriver à la prochaine position

        next_position = path[0] if path else (self.__x_act, self.__y_act)

        # =================================================
        # Ensuite, trouver l'angle vers le checkpoint
        # =================================================
        relative_x = next_position[1]*BLOCK_SIZE+25 - self.kart._position[0]
        relative_y = next_position[0]*BLOCK_SIZE+25 - self.kart._position[1]
        
        # On utilise la fonction arctangente pour calculer l'angle du vecteur [relative_x, relative_y]
        next_checkpoint_angle = math.atan2(relative_y, relative_x)
        
        # L'angle relatif correspond a la rotation que doit faire le kart pour se trouver face au checkpoint
        # On applique l'operation (a + pi) % (2*pi) - pi pour obtenir un angle entre -pi et pi
        relative_angle = (next_checkpoint_angle - self.kart.orientation + math.pi) % (2 * math.pi) - math.pi
    
    
        # =================================================
        # Enfin, commander le kart en fonction de l'angle
        # =================================================

        DOWN = False
        UP = True

        # On applique une vitesse maximale au kart pour eviter d'avoir trop d'inertie dans les virages
        max_speed = 15

        # S'il y a un virage qui s'approche, on réduit la vitesse maximale
        if self.__turn_incoming(self.full_path, DISTANCE_TURN, self.__x_act, self.__y_act):
            max_speed = 1.75

            # si on meurt deux fois de suite avant de toucher un checkpoint, on réduit encore la vitesse maximale
            if self.kart.death_count >= 2:
                max_speed = 1.25


        # On freine si on dépasse la vitesse maximale
        if self.kart.velocity >  max_speed:
            DOWN = True
            UP = False
        else:
            DOWN = False
            UP = True

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
        return keys
    
    # Méthode pour calculer le chemin entier avec l'algorithme A*

    def __find_full_path(self, grid, string):
        full_path = [(int(self.kart.position_checkpoint[1]/50),int(self.kart.position_checkpoint[0]/50))]
        self.kart.last_checkpoint = self.kart._get_last_checkpoint(string)
        for checkpoint in range(self.kart.next_checkpoint, self.kart.last_checkpoint+1):

            if checkpoint == 0:
                char = 'C'
            elif checkpoint == 1:
                char = 'D'
            elif checkpoint == 2:
                char = 'E'
            elif checkpoint == 3:
                char = 'F'
            
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

            start_node = grid[full_path[-1][0]][full_path[-1][1]]
            next_checkpoint_node = grid[y_next][x_next]

            path = self.__algorithm_A_star(grid, start_node, next_checkpoint_node)

            full_path += path
        
        return full_path
                
            
    # Méthode pour vérifier s'il y a un virage qui s'approche

    def __turn_incoming(self, path, distance, x_act, y_act):

        #On cherche les coordonnées dans la liste path, les plus approchées de la position actuelle
        index = [i for i in range(len(path))]
        index_act = min(index, key = lambda coord: math.sqrt((path[coord][1] - x_act) ** 2 + (path[coord][0] - y_act) ** 2))

        
        if len(path[index_act::])>distance:
            pos_test = index_act + distance
            
        else:
            pos_test = index_act + len(path[index_act::])-1


        for i in range(index_act+1, pos_test+1):
            next_position = path[i] if path else (self.kart._position[0], self.kart._position[1])

            relative_x = next_position[1]*BLOCK_SIZE+25 - self.kart._position[0]
            relative_y = next_position[0]*BLOCK_SIZE+25 - self.kart._position[1]

            # On utilise la fonction arctangente pour calculer l'angle du vecteur [relative_x, relative_y]
            next_checkpoint_angle = math.atan2(relative_y, relative_x)
        
            # L'angle relatif correspond a la rotation que doit faire le kart pour se trouver face au checkpoint
            # On applique l'operation (a + pi) % (2*pi) - pi pour obtenir un angle entre -pi et pi
            relative_angle = (next_checkpoint_angle - self.kart.orientation + math.pi) % (2 * math.pi) - math.pi

            if abs(relative_angle)>= 0.1:
                return True
            
        return False
    

    # Méthode pour créer le grid contenant tous les noeuds du circuit

    def __create_grid(self, string2D):
        width, height = self.kart._screen_size(string2D)
        grid = []
        for i in range(len(string2D)):
            grid.append([])
            for j in range(len(string2D[0])):
                char = string2D[i][j]

                # On ajoute aussi la surface du node
                surface = Track.char_to_track_element[char]['class']
                checkpoint_id = None
                if surface == Checkpoint:
                    checkpoint_id = Track.char_to_track_element[char]['params'][0]

                grid[i].append(Node(i, j, surface, checkpoint_id))

        return grid
    

    # Méthode pour réinitialiser les coûts de chaque node

    def __reset_grid(self, grid):
        for row in grid:
            for node in row:
                if node.surface == Lava:
                    self.g_cost = float("inf")
                elif node.surface == Grass:
                    node.g_cost = 50
                else:
                    self.g_cost = 10

    # Méthode pour reconstruire le chemin en utilisant le dictionnaire came_from
                    
    def __reconstruct_path(self, came_from, current):
        path = []
        while current in came_from:
            path.append(current.position)
            current = came_from[current]
        return path[::-1]  

    # Méthode pour trouver le node qui a le coût le moins élevé dans l'open set

    def __get_lowest_cost_node(self, open_set):
        lowest_index = 0
        for i in range(len(open_set)):
            if open_set[i].f_cost < open_set[lowest_index].f_cost or \
                (open_set[i].f_cost == open_set[lowest_index].f_cost and open_set[i].h_cost < open_set[lowest_index].h_cost):
                lowest_index = i
        return open_set.pop(lowest_index) # on renvoie et on supprime la valeur qu'on trouve
    
    # Méthode pour calculer la distance de Manhattan entre deux points
    def __h(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return abs(x1 - x2) + abs(y1 - y2)
    

    # Méthode pour l'implémentation de l'algorithme A*
    def __algorithm_A_star(self, grid, start, end):

        # On initialise l'open set, le dictionnaire came_from et les dictionnaires des coûts g(le vrai coût du début jusqu'à
        #un point) et f (la somme entre les coût g et h(la distance de Manhattan de la fin jusqu'à ce point))

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
        start.update_h_cost(self.__h(start.position, end.position))


        while len(open_set) > 0:

            # on cherche le node avec le coût le moins élevé

            current = self.__get_lowest_cost_node(open_set)

            # si c'est la fin, on reconstruit le chemin
            if current == end:
                return self.__reconstruct_path(came_from, end)
            
            
            # on regarde tous les voisins
            for neighbor in current.neighbors:
                
                if neighbor.surface == Lava: # on ignore les blocks Lava
                    continue
                
                temp_g_score = g_score_dict[current] + neighbor.g_cost
                # si on trouve un meilleur g_score, on continue par ici

                if temp_g_score < g_score_dict[neighbor]:
                    came_from[neighbor] = current
                    neighbor.update_g_cost(temp_g_score, self.kart.death_count)
                    neighbor.update_h_cost(self.__h(neighbor.position, end.position))
                    neighbor.f_cost = neighbor.g_cost + neighbor.h_cost
                    g_score_dict[neighbor] = temp_g_score
                    f_score_dict[neighbor] = neighbor.f_cost

                    if neighbor not in open_set:
                        open_set.append(neighbor)
                        
            
        
        return None

       

# Création d'une nouvelle classe Node qui va représenter chaque noeud du grid
class Node:
    def __init__(self, x, y, surface, checkpoint_id):

        self.position = (x, y)
        self.surface = surface

        # on initialise les coûts g en fonction de la surface ( par exemple, vu que l'herbe induit un frottement 10 fois plus
        # grand que le block Road, on pourrait mettre un coût 10 fois plus grand, mais vu que notre kart freine aussi
        # sur le chemin, on va mettre un coût 5 fois plus grand pour l'herbe)
        if self.surface == Lava:
            self.g_cost = float("inf")
        elif self.surface == Grass:
            self.g_cost = 50
        else:
            self.g_cost = 10

        self.checkpoint_id = checkpoint_id

        self.h_cost = 0
        self.f_cost = self.g_cost + self.h_cost
        self.neighbors = []

    # Méthode pour réactualiser les voisins des noeuds

    def update_neighbors(self, grid):

        self.neighbors = []
        if self.position[0] < len(grid) - 1 and not grid[self.position[0] + 1][self.position[1]]==Lava: # le voisin en haut
            self.neighbors.append(grid[self.position[0] + 1][self.position[1]])
        if self.position[0] > 0 and not grid[self.position[0] - 1][self.position[1]] == Lava: # le voisin en bas
            self.neighbors.append(grid[self.position[0] - 1][self.position[1]])
        if self.position[1] < len(grid[0]) - 1 and not grid[self.position[0]][self.position[1] + 1] == Lava: # le voisin à droite
            self.neighbors.append(grid[self.position[0]][self.position[1] + 1])
        if self.position[1] > 0 and not grid[self.position[0]][self.position[1] - 1] == Lava: # le voisin à gauche
            self.neighbors.append(grid[self.position[0]][self.position[1] - 1]) 

    # Méthode pour réactualiser le coût g des noeuds
    def update_g_cost(self, new_g_cost, death_count):

        if self.surface == Grass:
            self.g_cost = new_g_cost + 50
        elif self.surface == Boost:
            if death_count == 0:
                # Si on n'est jamais mort, on cherche à atteindre les boosts
                self.g_cost =  new_g_cost - 10

            elif death_count == 1:
                # Si on meurt une fois, on ne cherche plus à atteindre les boosts et on les traite comme si c'était de l'herbe
                self.g_cost = new_g_cost + 50

            else:
                # Si on meurt une deuxième fois, on va eviter les boosts, quitte à aller dans l'herbe
                self.g_cost = new_g_cost + 1000
        else:
            self.g_cost = new_g_cost

    # Métohde pour réactualiser les coût h des noeuds
    def update_h_cost(self, new_h_cost):
        self.h_cost = new_h_cost
     


