from dataclasses import dataclass
import random as rand


@dataclass
class Cell:
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

class Map():
###
# A Map is a cell assembly
    def __init__(self, sX = 4, sY = 4):
        self.cellBuffer = []
        self.wallBuffer = [True]*(sY*(sX+1)+sX*(sY+1))
        self.sX = sX
        self.sY = sY

        self.populate()
        self.place(0)

    def populate(self):
    # Push cells in the map
        i, x, y = 0, 0, 0
        while(i<self.sX*self.sY):
            x, y = i//self.sX, i%self.sY
            self.cellBuffer.append(Cell(x, y, 1, self.wallCoordinates(x, y)))
            i+=1
    
    def wallCoordinates(self, cellX, cellY):
        top = cellY*(2*self.sX+1) + cellX
        left = top + self.sX
        bottom = top + 2*self.sX+1
        right = left + 1
        return [right, bottom, left, top]

    def cell(self, x, y):
    # Return a cell by its index
        return self.cellBuffer[self.sX*x+y]
    
    def wallMapping(self, wallIndex = [-1, -1, -1, -1]):
        res = []
        for i in wallIndex:
            res.append(self.wallBuffer[i])
        return res

    def place(self, seed):
    # Add special cells
        index = list(range(self.sX*self.sY))
        self.start = rand.randrange(self.sX*self.sY)
        self.cellBuffer[self.start].setEvent('start', 0)
        index.pop(self.start)

        r = rand.randrange(self.sX*self.sY - 1)
        self.stop = index[r]
        self.cellBuffer[self.stop].setEvent('stop', 0)
        index.pop(r)

        r = rand.randrange(self.sX*self.sY - 2)
        self.treasure = index[r]
        self.cellBuffer[self.treasure].setEvent('treasure', 3)

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