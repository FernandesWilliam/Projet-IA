import gym
import numpy as np
import pyglet
from gym.utils.play import play
import random


class AIQLearning:
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

    def saveQState(self, file):
        with open(file, 'w') as f:
            for p in self.Q:
                for xb in p:
                    for yb in xb:
                        print(yb)
                        np.savetxt(f, delimiter=' ', X=yb, fmt='%d')

    def readQState(self, file):
        self.Q = np.zeros((self.P, self.XB, self.YB, self.D, self.A), dtype=float)
        with open(file, 'r') as f:
            for p in range(self.P):
                for xb in range(self.XB):
                    for yb in range(self.YB):
                        for direction in range(self.D):
                            actions = list(int(i) for i in f.readline().split())
                            self.Q[p][xb][yb][direction] = actions

    def randomState(self):
        xPad = random.choice(range(self.P))
        xBall = random.choice(range(self.XB - 1))
        yBall = random.choice(range(1, self.YB - 1))
        dirBall = random.choice(range(4))
        return xPad, xBall, yBall, dirBall

    def learn(self):


        for i in range(self.N):
            trainingSameSituation = 50
            epsilon = 1
            rPad, rXBall, rYBall, rDirBall = self.randomState()
            while trainingSameSituation !=0 :
                xPad, xBall, yBall, dirBall =  rPad, rXBall, rYBall, rDirBall
                endStep = self.endStep
                # while ball isn't touching bottom edge
                while not ((yBall == 0 and dirBall in [1, 2]) or endStep == 0):
                    # find the index of the max of the line of Q_state
                    maxIndex = np.where(self.Q[xPad][xBall][yBall][dirBall]
                                        == max(self.Q[xPad][xBall][yBall][dirBall]))[0]

                    # E greedy
                    r = random.random()
                    action = random.choice([0, 1, 2] if r < epsilon else maxIndex)
                    epsilon -= self.epsilon

                    newXP = self.updatePad(xPad,action)
                    newXB, newYB, newDB = self.updateBall(dirBall, xPad, xBall, yBall)
                    reward = self.rewards(xBall, yBall, newXB, newYB, newDB, xPad)

                    self.Q[xPad][xBall][yBall][dirBall][action] += self.alpha * (
                            reward + max(self.Q[newXP][newXB][newYB][newDB])
                            - self.Q[xPad][xBall][yBall][dirBall][action])

                    xPad = newXP
                    xBall, yBall, dirBall = newXB, newYB, newDB
                    endStep -= 1
                    #print(endStep)

                trainingSameSituation-=1
                #print("same situation",trainingSameSituation)
    # action are representing 0 1 2 -> so -1 0 1 for the movement
    def updatePad(self, xPad, action):
        if self.P - 1 > xPad > 0 or xPad == self.P and action == 0 or xPad == 0 and action == 2:
            return xPad + action - 1
        return xPad + 0

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

    def findNextMove(self, newBall, newPad):
        # find current state
        pad = newPad.discretPad(self.wDivide)
        print("pad" ,newPad.x)
        # print("pad discretiwe",pad)
        x, y, dirT = newBall.discretBall(self.hDivide, self.wDivide)
        if (dirT[0] == 0 or dirT[1] == 0):
            print("eeeeee")
            return 0
        #print("x et y",x,y)
        #  print(newBall.x, newBall.y)
        dir = list(self.moveBall.keys())[list(self.moveBall.values()).index(dirT)]
        #   print("dir " ,dir)
        indexes = np.where(self.Q[pad][x][y][dir]
                           == max(self.Q[pad][x][y][dir]))[0]
        action = random.choice(indexes)
        #
        print(action,"action suggere")
        print("x ball",newBall.x,"y ball",newBall.y,"dir",dir)
        print("discretization")
        print("x ball",x,"y ball",y,"dir",dirT)
        # because not the same
        print(all(el for el in  indexes if el ==0 ))
        if (action == 0):
            return 3
        elif (action == 1):
            return 0
        return 2


class Pad:
    def __init__(self, x):
        self.x = x

    def discretPad(self, width):
        return (self.x // width)-1


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
        return (self.x // width)-1, (self.y // height)-1, (xDir, -yDir)


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
                obs, rew, d, inf = self.env.step(0 if self.nextMove == -1 else self.nextMove)
                grid = self.gridReshape(obs)
                newBall = self.findBall(grid)
                if newBall is None:
                    print("ENCORE PERDU ")
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
        return Pad(pad[0]+4)


game = Breakout()
#AI = AIQLearning(6, 6, 5, 5000, 0.1, 100, 0.7, 12, 12)
AI = AIQLearning(18, 18, 15, 5000, 0.1, 100, 0.7, 4, 4)
#AI.learn()
AI.readQState('read4.txt')
#AI.saveQState('read4.txt')
game.play(AI)
