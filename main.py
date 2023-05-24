from maps import *
from display import *
from qLearn import *

# Device selection
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Screen size
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500


map = Map(3, 3)
D = display(SCREEN_WIDTH, SCREEN_HEIGHT)
Dqn = DQN(6+map.sX*map.sY, 4).to(device)
scoreLog = learn(Dqn, map, D, 1000)
#scoreLog = np.asarray(scoreLog)
plt.figure()
#plt.plot(scoreLog[:,2])
plt.plot(Dqn.losses)
plt.show()

