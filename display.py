import matplotlib.pyplot as plt
from maps import *



class display():

    def __init__(self, width, height, factor = 5):
        plt.style.use('dark_background')
        plt.figure(figsize=(width, height))

        self.factor = factor

    def drawAWall(self, x, y, linestyle = 'w-'):
        plt.gca().plot(x, y, linestyle)

    def drawARect(self, x, y, facecolor = 'green'):
        rectangle = plt.Rectangle((x+(2*self.factor/10),y-(2*self.factor/10)), 
                                  6*self.factor/10, -6*self.factor/10, fc=facecolor)
        plt.gca().add_patch(rectangle)
    
    def drawACircle(self, x, y, r, facecolor = 'white'):
        circle = plt.Circle((x+(self.factor/2),y-(self.factor/2)), r, fc=facecolor)
        plt.gca().add_patch(circle)

    def reset(self, map):
        rectangle = plt.Rectangle((0, 0), 
                                  self.factor*map.sX, -self.factor*map.sY, fc='black')
        plt.gca().add_patch(rectangle)
    
    def borderVertices(self, x, y, wallMapping):
        # Right, Bottom, Left, Top
        borderX = [[x+5, x+5], [x+5, x], [x, x], [x, x+5]]
        borderY = [[y, y-5], [y-5, y-5], [y-5, y], [y, y]]
        borderXFiltered = [borderX[i] for i in range(len(borderX)) if wallMapping[i]]
        invBorderXFiltered = [borderX[i] for i in range(len(borderX)) if not(wallMapping[i])]
        borderYFiltered = [borderY[i] for i in range(len(borderY)) if wallMapping[i]]
        invBorderYFiltered = [borderY[i] for i in range(len(borderY)) if not(wallMapping[i])]
        return borderXFiltered, borderYFiltered, invBorderXFiltered, invBorderYFiltered
    
    def refresh(self, map):
        self.reset(map)
        for cell in map.cellBuffer:
            x, y = self.factor*cell.posX, -self.factor*cell.posY
            borderX, borderY, invBorderX, invBorderY = self.borderVertices(x, y, map.wallMapping(cell.wall))
            match cell.event:
                case "start":
                    self.drawARect(x, y, facecolor = 'green')
                case "stop":
                    self.drawARect(x, y, facecolor = 'blue')
                case "treasure":
                    self.drawARect(x, y, facecolor = 'yellow')
                case "player":
                    self.drawACircle(x, y, 1)

            for i, j in zip(borderX, borderY):
                self.drawAWall(i, j)
            for i, j in zip(invBorderX, invBorderY):
                self.drawAWall(i, j, 'k-')
        
        plt.xticks([])
        plt.yticks([])
        ax = plt.gca()
        ax.set_aspect('equal', adjustable='box')
        plt.show()
