import numpy as np
import random

XB = 6
YB = 5
P = 6
A = 3
D = 4  # considering : 0 top-left  1 top right ...
Q = np.zeros((P, XB, YB, D, A), dtype=float)
alpha = 0.8
# x,y,direction
moveBall = {
    0: (1, 1),  # 45 top right
    1: (1, -1),  # -45 bottom right
    2: (-1, -1),  # -135 bottom left
    3: (-1, 1)  # 135 top-left
}


def updateBall(x, y, d, pad):
    #
    xD, yD = moveBall[d]
    nd = d
    nX, nY = x + xD, y + yD
    print(nX, nY, nd, "before update")
    if pad == nX and nY == 0 or YB - 1 == nY:
        nd = (d + 2) % 4
        print("1 elif")
    # if
    elif (XB - 1 == nX and d == 0) or (nX == 0 and d == 3):
        nd = d + (-3 if XB - 1 == nX and d == 0 else +3)
        print("2 elif")

    elif (XB - 1 == nX and d == 1) or (nX == 0 and d == 2):
        nd = d + (1 if XB - 1 == nX and d == 1 else -1)
        print("3 elif")
    # elif  YB - 1 == nY :
    #   nD = (d + 2) % 4

    print(nX, nY, nd, "update ball")

    return nX, nY, nd


def rewards(xb, yb, p):
    if p == xb and yb == 0:
        return 1
    return -5 if newYB == 0 and newDB in [1, 2] else 0


...

# iterations

N = 10000
for i in range(N):
    ## Create the pad here random position =
    xPad = 2
    epsilon = 1
    xBall, yBall, dirBall = 2, 2, 3
    while yBall != 0 and not dirBall in [1, 2]:
        # find the index of the max of the line of Q_state
        maxIndex = np.argmax(Q[xPad][xBall][yBall][dirBall])

        # e greedy
        r = random.random()
        action = random.choice([0, 1, 2] if r < epsilon else maxIndex)
        epsilon -= 0.05

        newXP = xPad + (action - 1 if P - 1 > xPad > 0 else 0)
        newXB, newYB, newDB = updateBall(xBall, yBall, dirBall, newXP)
        reward = rewards(newXB, newYB, newXP)

        Q[xPad][xBall][yBall][dirBall][action] += alpha * (
                reward + max(Q[newXP][newXB][newYB][newDB]) - Q[xPad][xBall][yBall][dirBall][action])

        xPad = newXP
        xBall, yBall, dirBall = newXB, newYB, newDB
        print("position pad :", xPad, "position ball :", xBall, yBall, dirBall)

print(Q)


