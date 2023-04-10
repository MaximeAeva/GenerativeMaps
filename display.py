import matplotlib.pyplot as plt
from maps import *



class display():

    def __init__(self, width, height, map, factor = 5):
        plt.style.use('dark_background')
        plt.figure(figsize=(width, height))
        plt.xticks([])
        plt.yticks([])
        ax = plt.gca()
        ax.set_aspect('equal', adjustable='box')
        self.factor = factor

        self.drawAll(map)

        plt.show()
        

    def drawAWall(self, x, y, linestyle = 'w-'):
        plt.plot(x, y, linestyle)

    def drawARect(self, x, y, facecolor = 'green'):
        rectangle = plt.Rectangle((x+(2*self.factor/10),y-(2*self.factor/10)), 
                                  6*self.factor/10, -6*self.factor/10, fc=facecolor)
        plt.gca().add_patch(rectangle)
    
    def borderVertices(self, x, y, wallMapping):
        # Right, Bottom, Left, Top
        borderX = [[x+5, x+5], [x+5, x], [x, x], [x, x+5]]
        borderY = [[y, y-5], [y-5, y-5], [y-5, y], [y, y]]
        borderXFiltered = [borderX[i] for i in range(len(borderX)) if wallMapping[i]]
        borderYFiltered = [borderY[i] for i in range(len(borderY)) if wallMapping[i]]
        return borderXFiltered, borderYFiltered
    
    def drawAll(self, map):
        for cell in map.cellBuffer:
            x, y = self.factor*cell.posX, -self.factor*cell.posY
            borderX, borderY = self.borderVertices(x, y, map.wallMapping(cell.wall))
            match cell.event:
                case "start":
                    self.drawARect(x, y, facecolor = 'green')
                case "stop":
                    self.drawARect(x, y, facecolor = 'blue')
                case "treasure":
                    self.drawARect(x, y, facecolor = 'yellow')
            for i, j in zip(borderX, borderY):
                self.drawAWall(i, j)


