from dataclasses import dataclass
import random as rand
import numpy as np


@dataclass
class Cell(object):
    '''
    Create a cell
    ----------

    Parameters:

    posX : int
        Cell X position on grid
    posY : int
        Cell Y position on grid
    value : int
        Cell reward
    wall : int*[,4]
        Walls index that surround the cell

    Returns:

    None
    '''
    def __init__(self, posX, posY, value = 1, wall = [-1, -1, -1, -1]):
        self.posX = posX
        self.posY = posY
        self.value = value
        self.wall = wall
        self.event = None

    def setEvent(self, event, value):
        self.event = event
        self.value = value

class Map(object):
    '''
    Create a cell + wall assembly called Map
    ----------

    Parameters:

    sX : int
        Map X size
    sY : int
        Map Y size

    Returns:

    None
    '''
    def __init__(self, sX = 4, sY = 4):
        self.cellBuffer = []
        self.wallBuffer = [True]*(sY*(sX+1)+sX*(sY+1))
        self.sX = sX
        self.sY = sY

        self.populate()
        self.place(0)

        self.values = [cell.value for cell in self.cellBuffer]

    def refresh(self):
        self.cellBuffer = []
        self.wallBuffer = [True]*(self.sY*(self.sX+1)+self.sX*(self.sY+1))

        self.populate()
        self.place(0)

        self.values = [cell.value for cell in self.cellBuffer]

    def populate(self):
    # Push cells in the map
        i, x, y = 0, 0, 0
        while(i<self.sX*self.sY):
            x, y = i//self.sX, i%self.sY
            self.cellBuffer.append(Cell(x, y, 0.2, self.wallCoordinates(x, y)))
            i+=1
    
    def wallCoordinates(self, cellX, cellY):
        top = cellY*(2*self.sX+1) + cellX
        left = top + self.sX
        bottom = top + 2*self.sX+1
        right = left + 1
        return [right, bottom, left, top]

    def cell(self, x, y):
    # Return a cell by its index
        return self.cellBuffer[int(self.sX*x+y)]
    
    def wallMapping(self, wallIndex = [-1, -1, -1, -1]):
        res = []
        for i in wallIndex:
            res.append(self.wallBuffer[i])
        return res

    def place(self, seed):
    # Add special cells
        index = list(range(self.sX*self.sY))
        self.start = rand.randrange(self.sX*self.sY)
        self.cellBuffer[self.start].setEvent('start', 0.8)
        index.pop(self.start)

        r = rand.randrange(self.sX*self.sY - 1)
        self.stop = index[r]
        self.cellBuffer[self.stop].setEvent('stop', 0.1)
        index.pop(r)

        r = rand.randrange(self.sX*self.sY - 2)
        self.treasure = index[r]
        self.cellBuffer[self.treasure].setEvent('treasure', 0)

    def delWall(self, x, y, vec):
    # Delete the wall if possible according to the vec([x move, y move]) 
        # No diagonale move or empty moves
        if(vec[0]*vec[1]):
            return -1
        
        currentCell = self.cell(x, y)
        wallIndex = 0
        # Check if not a border
        if(x+vec[0] < 0 or x+vec[0]>=self.sX):
            return -1
        elif(y+vec[1] < 0 or y+vec[1]>=self.sY):
            return -1

        else:
            if(vec[0]): 
                wallIndex = currentCell.wall[-1*(vec[0]-1)] 
            else :
                wallIndex = currentCell.wall[-1*(vec[1]-1) + 1]

            if(not(self.wallBuffer[wallIndex])):
               return 0
            
            self.wallBuffer[wallIndex] = False
        return 1
    
    def addWall(self, x, y, vec):
    # Delete the wall if possible according to the vec([x move, y move]) 
        currentCell = self.cell(x, y)
        wallIndex = 0
        # Check if not a border
        if(x+vec[0] < 0 or x+vec[0]>=self.sX):
            pass
        elif(y+vec[1] < 0 or y+vec[1]>=self.sY):
            pass

        else:
            if(vec[0]): 
                wallIndex = currentCell.wall[-1*(vec[0]-1)] 
            else :
                wallIndex = currentCell.wall[-1*(vec[1]-1) + 1]
            
            self.wallBuffer[wallIndex] = True

    def walk(self, state, action):
        # Initialize
        terminal = True
        # Catch current cell position
        statePos = np.array([state[0]*(self.sX-1), state[1]*(self.sY-1)])
        # Compute new state
        newState = statePos+action
        # If out of range -> terminate
        if(newState[0] not in range(0, self.sX) or newState[1] not in range(0, self.sY)):
            state_next = state
            reward = -1
            return state_next, reward, terminal
        # If available, delete the wall
        self.delWall(state[0]*(self.sX-1), state[1]*(self.sY-1), action)
        # remove player from previous cell
        prevCell = self.cell(state[0]*(self.sX-1), state[1]*(self.sY-1))
        prevCell.event = None
        # Walk to the next cell
        Cell = self.cell(newState[0], newState[1])
        # If do not stop, continue
        if (Cell.event != "stop"):
            terminal = False
        # Add player in the new cell
        Cell.event = "player"
        # Add cell value to score
        reward = Cell.value
        # Remove 1 to cell value
        if (Cell.value>0):
            Cell.value *= -1
        else:
            Cell.value*= 2
        # Build state_next
        state_next = state

        state_next[0] =  (newState[0])/(self.sX-1)
        state_next[1] =  (newState[1])/(self.sY-1)
        # Start position
        state_next[2] =  (self.cellBuffer[self.start].posX - newState[0])/(self.sX-1)
        state_next[3] =  (self.cellBuffer[self.start].posY - newState[1])/(self.sY-1)
        # Stop position
        state_next[4] =  (self.cellBuffer[self.stop].posX - newState[0])/(self.sX-1)
        state_next[5] =  (self.cellBuffer[self.stop].posY - newState[1])/(self.sY-1)

        state_next[6:] = np.asarray(self.values)
        

        self.values = [cell.value for cell in self.cellBuffer]
        return state_next, reward, terminal
     
    def initialState(self):
        state = np.zeros((6+self.sX*self.sY,), dtype=float)

        Cell = self.cell(self.cellBuffer[self.treasure].posX, self.cellBuffer[self.treasure].posY)
        Cell.event = "player"
        # Starting position = Treasure position
        state[0] =  (self.cellBuffer[self.treasure].posX)/(self.sX-1)
        state[1] =  (self.cellBuffer[self.treasure].posY)/(self.sY-1)
        # Start position
        state[2] =  (self.cellBuffer[self.start].posX - self.cellBuffer[self.treasure].posX)/(self.sX-1)
        state[3] =  (self.cellBuffer[self.start].posY - self.cellBuffer[self.treasure].posY)/(self.sY-1)
        # Stop position
        state[4] =  (self.cellBuffer[self.stop].posX - self.cellBuffer[self.treasure].posX)/(self.sX-1)
        state[5] =  (self.cellBuffer[self.stop].posY - self.cellBuffer[self.treasure].posY)/(self.sY-1)
        # Map
        state[6:] = np.asarray(self.values)

        return state

    


