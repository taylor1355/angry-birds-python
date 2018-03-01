import math
import pygame
import pymunk as pm
from level import Level
from game import Game, GameState
from simulator import Simulator, Shot
from utils import *

def main():
    sim = Simulator(1500, 11)
    
    shots = []
    for i in range(4):
        shots.append(Shot.get_random())
        
    print("Score: " + str(sim.simulate_level(shots)))

if __name__ == "__main__":
    main()