from maps import *
from display import *
from qLearn import *

# Screen size
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500


map = Map(4, 4)
D = display(SCREEN_WIDTH, SCREEN_HEIGHT)
Dqn = DQN(6+4*4, 4)
learn(Dqn, map, D)

