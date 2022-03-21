import gym
import numpy as np
import pyglet
from gym.utils.play import play
import random
class AIQLearning :
    def __init__(self, P, XB, YB, N, epsilon, endStep, alpha, hDivide, wDivide):
        self.XB = XB
        self.YB = YB
        self.P = P
        self.A = 3
        self.D = 4  #  considering : 0 top-left  1 top right ...
        self.Q = np.zeros((self.P, self.XB, self.YB, self.D, self.A), dtype=float)
        self.alpha = alpha
        self.N = N
        self.epsilon = epsilon
        self.endStep = endStep
        # x,y,direction
        self.moveBall = {
            0: (1, 1),  # 45 top right
            1: (1, -1),  # -45 bottom right
            2: (-1, -1),  # -135 bottom left
            3: (-1, 1)  # 135 top-left
        }
        self.hDivide = hDivide
        self.wDivide = wDivide
        self.learn()

    def saveQState(self,file):
        with open(file, 'w') as f:
            for p in ai.Q:
                for xb in p:
                    for yb in xb:
                        np.savetxt(f, delimiter=' ', X=yb, fmt='%d')

    def readQState(self,file):
        self.Q = np.zeros((self.P, self.XB, self.YB, self.D, self.A), dtype=float)
        with open(file, 'r') as f:
            for p in range(self.P):
                for xb in range(self.XB):
                    for yb in range(self.YB):
                        for direction in range(self.D):
                            line = list(int(i) for i in f.readline().split())
                            R[p][xb][yb][direction] = line

    def randomState(self):
        xPad = random.choice(range(self.P))
        xBall = random.choice(range(self.XB-1))
        yBall = random.choice(range(1,self.YB-1))
        dirBall = random.choice(range(4))
        return xPad, xBall, yBall, dirBall

    def learn(self):
        for i in range(self.N):
            epsilon = 1
            endStep = self.endStep
            xPad, xBall, yBall, dirBall = self.randomState();
            while not ((yBall == 0 and dirBall in [1, 2]) or endStep == 0):
                # find the index of the max of the line of Q_state
                maxIndex = np.where(self.Q[xPad][xBall][yBall][dirBall]
                                    == max(self.Q[xPad][xBall][yBall][dirBall]))[0]

                r = random.random()
                action = random.choice([0, 1, 2] if r < epsilon else maxIndex)
                epsilon -= 0.05

                newXP = xPad + (action - 1 if self.P - 1 > xPad > 0 else 0)
                newXB, newYB, newDB = self.updateBall(dirBall, xPad, xBall, yBall)
                reward = self.rewards(xBall, yBall, newXB, newYB, newDB, xPad)

                self.Q[xPad][xBall][yBall][dirBall][action] += self.alpha * (
                        reward + max(self.Q[newXP][newXB][newYB][newDB])
                        - self.Q[xPad][xBall][yBall][dirBall][action])

                xPad = newXP
                xBall, yBall, dirBall = newXB, newYB, newDB
                endStep -= 1
                #print("position pad :", xPad, "position ball :", xBall, yBall, dirBall)


    def rewards(self, xb, yb, newXB, newYB, newDB, xPad):
        if xPad == xb and yb == 0:
            return 3
        return -5 if newYB == 0 and newDB in [1, 2] else 0

    def updateBall(self, d, pad, xB, yB):
        xD, yD = self.moveBall[d]
        nd = d
        nX, nY = xB + xD, yB + yD
        if pad == nX and nY == 0 or self.YB - 1 == nY:
            nd = (d + 2) % 4

        elif (self.XB - 1 == nX and d == 0) or (nX == 0 and d == 3):
            nd = d + (3 if self.XB - 1 == nX and d == 0 else -3)


        elif (self.XB - 1 == nX and d == 1) or (nX == 0 and d == 2):
            nd = d + (1 if self.XB - 1 == nX and d == 1 else -1)
        return nX, nY, nd

    def findNextMove(self,newBall, newPad):
        # find current state
        pad = newPad.discretPad(self.wDivide)
        print(pad)
        x, y, dirT = newBall.discretBall(self.hDivide, self.wDivide)
        if (dirT[0] == 0 or dirT[1] ==0):
            return 0
        print(x,y)
        print(newBall.x, newBall.y)
        dir = list(self.moveBall.keys())[list(self.moveBall.values()).index(dirT)]
        print(dir)
        indexes = np.where(self.Q[pad][x][y][dir]
                                    == max(self.Q[pad][x][y][dir]))[0]
        action = random.choice(indexes)
        # because not the same
        if (action == 0):
            return 2
        elif (action == 1):
            return 0
        return 3


class Pad:
    def __init__(self, x):
        self.x = x

    def discretPad(self, width):
        return self.x // width


class Ball:
    def __init__(self, coord):
        self.x, self.y = coord
        self.dir = (0, 0)

    def setDirection(self, ball):
        self.dir = (self.x - ball.x, self.y - ball.y)

    # Give xBall,yBall,(direction)
    def discretBall(self, height, width):
        # temporary rescale direction for our usage
        xDir = self.dir[0] if self.dir[0] == 0 else self.dir[0] / abs(self.dir[0])
        yDir = self.dir[1] if self.dir[1] == 0 else self.dir[1] / abs(self.dir[1])
        return round(self.x / width)-1, round(self.y / height)-1, (xDir, yDir)


class Breakout:
    def __init__(self):
        self.lives = 5
        self.env = gym.make('Breakout-v0')
        self.env.reset()
        self.previousGrid = None
        self.needSpawn = True
        self.nextMove = -1

    def gridReshape(self, grid):
        return grid[74:194:2, 8:152:2, 1]

    # This method is used to set the ball on the grid.
    # Loop until ball spawn
    def spawnBall(self):
        obs, rew, d, inf = self.env.step(1)
        self.previousGrid = self.gridReshape(obs)
        self.env.render()
        ball = self.findBall(self.previousGrid)
        return ball is None

    def lose(self):
        self.needSpawn = True
        self.lives -= 1

    def play(self, IAQState):
        # While IA still has balls : play
        while self.lives > 0:
            if self.needSpawn:
                self.needSpawn = self.spawnBall()
                continue
            ball = self.findBall(self.previousGrid)
            obs, rew, d, inf = self.env.step(0 if self.nextMove == -1 else self.nextMove)
            grid = self.gridReshape(obs)
            self.env.render()
            newBall = self.findBall(grid)
            if newBall is None:
                self.lose()
                continue
            newPad = self.findPad(grid[59])
            newBall.setDirection(ball)
            self.nextMove = IAQState.findNextMove(newBall, newPad)
            self.previousGrid = grid
        self.env.close()

    def findBall(self, grid):
        coordinates = [(colIndex, rowIndex) for rowIndex, rowArray in enumerate(grid)
                       for colIndex, colValue in enumerate(rowArray)
                       if colValue == 72 and self.emptyEdge(rowArray, colIndex)]
        return None if len(coordinates) == 0 else Ball(coordinates[0])

    def emptyEdge(self, rowArray, index):
        if index == 0:
            return rowArray[index + 1] != 72
        if index == 71:
            return rowArray[index - 1] != 72
        return rowArray[index + 1] != 72 and rowArray[index - 1] != 72

    def findPad(self, row):
        pad = [index for index, elem in enumerate(row) if
               elem == 72 and all(pixel == 72 for pixel in row[index:index + 8])]
        return Pad(pad[0])

game = Breakout()
ai = AIQLearning(6,6,5, 100, 1, 100, 0.7, 12, 12)


#np.zeros((P, XB, YB, self.D, self.A), dtype=float)
with open('register.txt', 'w') as f:
    for  p in ai.Q :
        for xb in p :
            for yb in xb :
                    np.savetxt(f, delimiter=' ', X=yb, fmt='%d')


R =  np.zeros((6, 6, 5, 4, 3), dtype=float)
with open('register.txt', 'r') as f:
    for p in range(6) :
        for xb in range(6):
            for yb in range(5):
                for direction in range(4):
                    line =list(int(i) for i in  f.readline().split())
                    R[p][xb][yb][direction] = line


print(R)

#game.play(ai)


# Bon j'arrete chu ko la tout marche, faudrait code une petite classe generique pour le learning , j'ai creer les methode en haut, pour que ce soit plus facile a tester apres avec diffenrete configuration.
