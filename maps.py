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
        # Where we gather cells from grid
        self.cellBuffer = []
        # Where we gather walls (between cells + grid edges)
        self.wallBuffer = [True]*(sY*(sX+1)+sX*(sY+1))
        # Grid dimensions
        self.sX = sX
        self.sY = sY
        # Player position initialization
        self.playerX, self.playerY = 0, 0
        # Reward values :
            # Default cell value
        self.classicCellValue = 0
            # Start cell value
        self.startValue = 0
            # Stop cell value
        self.stopValue = 1
            # Out of the grid value
        self.punishValue = -1

        # Build the grid
        self.populate()
        self.place(0)
        # Grid cells values
        self.values = [cell.value for cell in self.cellBuffer]

    def refresh(self):

        # Reset cell buffer
        self.cellBuffer = []
        # Reset wall buffer
        self.wallBuffer = [True]*(self.sY*(self.sX+1)+self.sX*(self.sY+1))
        # Build grid
        self.populate()
        self.place(0)
        # Grid cells values
        self.values = [cell.value for cell in self.cellBuffer]

    def populate(self):
    # Push cells in the map
    # Initialize iterators
        i, x, y = 0, 0, 0
        # Loop through cells
        while(i<self.sX*self.sY):
            # Compute cells index
            x, y = i//self.sX, i%self.sY
            # Add cell to buffer with default value
            self.cellBuffer.append(Cell(x, y, self.classicCellValue, self.wallCoordinates(x, y)))
            i+=1
    
    def wallCoordinates(self, cellX, cellY):
        # Top wall coordinate
        top = cellY*(2*self.sX+1) + cellX
        # Left wall coordinate
        left = top + self.sX
        # Bottom wall coordinate
        bottom = top + 2*self.sX+1
        # Right wall coordinate
        right = left + 1
        return [right, bottom, left, top]

    def cell(self, x, y):
    # Return a cell by its index
        return self.cellBuffer[int(self.sX*x+y)]
    
    def wallMapping(self, wallIndex = [-1, -1, -1, -1]):
        # Initialize result buffer 
        res = []
        # Append wall state 
        for i in wallIndex:
            res.append(self.wallBuffer[i])
        return res

    def place(self, seed):
    # Add special cells
        # Get all the index from cellBuffer
        index = list(range(self.sX*self.sY))
        # Randomly choose a cell from cellBuffer
        self.start = rand.randrange(self.sX*self.sY)
        # Define it as Start cell
        self.cellBuffer[self.start].setEvent('start', self.startValue)
        # Remove it from the list choices
        index.pop(self.start)

        # Randomly choose another cell
        r = rand.randrange(self.sX*self.sY - 1)
        self.stop = index[r]
        # Define it as Stop cell
        self.cellBuffer[self.stop].setEvent('stop', self.stopValue)
        # Remove it from the list choice
        index.pop(r)

        # Randomly choose anoter cell
        r = rand.randrange(self.sX*self.sY - 2)
        self.treasure = index[r]
        # Define it as Treasure cell
        self.cellBuffer[self.treasure].setEvent('treasure', 0)

    def delWall(self, x, y, vec):
    # Delete the wall if possible according to the vec([x move, y move]) 
        # Check if not diagonale move or empty moves
        if(vec[0]*vec[1]):
            return -1
        
        # Get current cell
        currentCell = self.cell(x, y)
        # Initialize wallIndex variable
        wallIndex = 0

        # Check if not an edge, else return
        if(x+vec[0] < 0 or x+vec[0]>=self.sX):
            return -1
        elif(y+vec[1] < 0 or y+vec[1]>=self.sY):
            return -1
        # If not an edge, get the wallIndex from the action vector
        else:
            if(vec[0]): 
                wallIndex = currentCell.wall[-1*(vec[0]-1)] 
            else :
                wallIndex = currentCell.wall[-1*(vec[1]-1) + 1]

            if(not(self.wallBuffer[wallIndex])):
               return 0
            # Disable the wall
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
            reward = self.punishValue
            return state_next, reward, terminal
        # If available, delete the wall
        self.delWall(state[0]*(self.sX-1), state[1]*(self.sY-1), action)
        # Move Player
        self.playerX = newState[0]
        self.playerY = newState[1]
        # Walk to the next cell
        Cell = self.cell(newState[0], newState[1])
        # If do not stop, continue
        if (Cell.event != "stop"):
            terminal = False
        # Add cell value to score
        reward = Cell.value
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
        # State shape (Player position, start position, stop position, grid values)
        state = np.zeros((6+self.sX*self.sY,), dtype=float)

        # Get the starting point info
        Cell = self.cell(self.cellBuffer[self.treasure].posX, self.cellBuffer[self.treasure].posY)
        # Place player on starting point
        self.playerX = Cell.posX
        self.playerY = Cell.posY

        # Player position
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

    


