from track import Track
from ai import AI
from human import Human
from kart import Kart

# La chaine de caractere decrivant le terrain
string = """GGGGGGGGGGGGGGGGGGGGGGGGGG
GRRRRRRCRRRRRRRRRBRRRRRRRG
GRRRRRRCRRRRRRRRRBRRRRRRRG
GRRRRRRCRRRRRRRRRRRRRRRRRG
GRRRRRRCRRRRRRRRRRRRRRRRRG
GGGGGGGGGGGGGGGGGGGGGLLRRG
GGGGGGGGGGGGGGGGGGGGGRRRRG
GRRRRGGGGGGGGGGGGGGGGRRLLG
GFFRRGGGGGGGGGGGGGGGGRRRRG
GLRRRGGGGGGGGGGGGGGGGLLRRG
GRRRRGGGGGGGGGGGGGGGGDDDDG
GRRRRRERRRRRRRBRRRRRRRRLLG
GRRRRRERRRRRRRBRRRRRRRRRRG
GLRRRRERRRRRGGBRRRRRRRRRRG
GLLRRRERRRRRGGBRRRRRRRRRRG
GGGGGGGGGGGGGGGGGGGGGGGGGG"""



# La position et l'orientation initiale du kart
initial_position = [75, 75]
initial_angle = 0
controller =  Human()  # ou AI()
"""
==================== ATTENTION =====================
Vous ne devez pas modifier ces quatre lignes de code 
====================================================
"""
kart = Kart(controller)
track = Track(string, initial_position, initial_angle)
track.add_kart(kart)
track.play()



