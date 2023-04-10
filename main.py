from maps import *
from display import *

# Screen size
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

map = Map(4, 4)
#display(SCREEN_WIDTH, SCREEN_HEIGHT, map)
map.delWall(1, 1, [1, 0])
map.delWall(2, 2, [0, 1])

display(SCREEN_WIDTH, SCREEN_HEIGHT, map)