
import random

import imageio
import numpy as np
import gym
from gym.utils.play import play

def callback(obs_t, obs_tp1, action, rew, done, info) :
    imageio.imwrite('outfile1.png', obs_t[58:196:2, 8:152:2, 1])
    with open('X.txt', 'a') as outfileX:
        np.savetxt(outfileX, delimiter=' ', X=obs_t[58:196:2, 8:152:2, 1], fmt='%d')

    with open('Y.txt', 'a') as outfileY:
       np.savetxt(outfileY, delimiter=' ', X=[[action, rew]], fmt='%d')



if __name__ == '__main__':
    env = gym.make('Breakout-v0')
    play(env, zoom=3, fps=12, callback=callback)
    env.reset()
    env.close()
