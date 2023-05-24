import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from collections import deque, OrderedDict

GAMMA = 0.9
LEARNING_RATE = 0.001

MEMORY_SIZE = 1000000
BATCH_SIZE = 16

EXPLORATION_MAX = 1.0
EXPLORATION_MIN = 0.01
EXPLORATION_DECAY = 0.995
#Action space (right, bot, left, top)
#Observ (posX, posY, stopX, stopY, sX, sY, values)
class DQN(nn.Module):
 
    def __init__(self, observation_space, action_space):
        super(DQN, self).__init__()
        self.exploration_rate = EXPLORATION_MAX

        self.action_space = action_space

        self.memory = deque(maxlen=MEMORY_SIZE)

        self.sequence = OrderedDict()
        self.sequence['linear1'] = nn.Linear(observation_space, 128)
        self.sequence['Relu1'] = nn.ReLU()
        self.sequence['linear2'] = nn.Linear(128, 128)
        self.sequence['Relu2'] = nn.ReLU()
        self.sequence['linear3'] = nn.Linear(128, action_space)

        self.model = nn.Sequential(self.sequence)

        self.costFunction = nn.MSELoss()
        self.losses = []

        self.optimizer = optim.Adam(self.model.parameters(), lr=LEARNING_RATE)
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def predict(self, state):
        if np.random.rand() < self.exploration_rate:
            return np.asarray(random.randrange(self.action_space))
        q_values = self.model(torch.tensor(state).float())
        return torch.argmax(q_values).detach().numpy()
    
    def act(self, predict):
        match predict:
            case 0:
                return [1, 0]
            case 1:
                return [0, 1]
            case 2:
                return [-1, 0]
            case 3:
                return [0, -1]
            
    def experience_replay(self):
        if len(self.memory) < BATCH_SIZE:
            return
        batch = random.sample(self.memory, BATCH_SIZE)
        for state, action, reward, state_next, terminal in batch:
            q_update = reward
            if not terminal:
                tensor_update = reward + GAMMA * torch.amax(self.model(torch.tensor(state_next).float()))
                q_update = tensor_update.real 
            q_values = self.model(torch.tensor(state).float()).detach().numpy()
            qVal = np.copy(q_values)
            qVal[action] = q_update
            qVal[qVal < 0] = 0
            
            loss = self.costFunction(torch.tensor(q_values), torch.tensor(qVal))
            loss.requires_grad = True
            self.losses.append(loss.item())
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        self.exploration_rate *= EXPLORATION_DECAY
        self.exploration_rate = max(EXPLORATION_MIN, self.exploration_rate)


def learn(dqn, map, display, epoch=10000):
    # Initialize run counter
    run = 0
    # Initialize run counter
    scoreLog = []
    # Loop through tries
    while True:
        if (run >= epoch) : return dqn.losses
        run += 1
        # Build new map
        map.refresh()
        # Initialize state
        state = map.initialState()
        # Initialize step counter
        step, score = 0, 0
        # Loop through step until current try is not terminate
        while True:
            step += 1
            if (step >= 2*map.sX*map.sY): break
            #print("position :", state[0]*(map.sX-1), state[1]*(map.sY-1))
            # show env
            #if(not(step%1)): display.refresh(map)
            # Predict the action thanks to predict function
            prediction = dqn.predict(state)
            #print("Prediction :", prediction)
            # Define the action thanks to act function
            action = dqn.act(prediction)
            # Get the new state info
            state_next, reward, terminal = map.walk(state, action)
            #print("New position :", state_next[0], state_next[1])
            # global score
            score += reward
            # Do not add final reward if terminate
            #reward = reward if not terminal else -reward
            # Gather the evenment suite to replay later
            dqn.remember(state, prediction, reward, state_next, terminal)
            # Change state to new state
            state = state_next
            # If terminal, display some logs
            if terminal:
                print("Run: " + str(run) + ", exploration: " + str(dqn.exploration_rate) + ", score: " + str(score))
                scoreLog.append([step, run, score])
                break
            # Else, replay a previous experience
            if(not(run%3)):
                dqn.experience_replay()
            

