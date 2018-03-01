import math
import random
from level import Level
from game import Game, GameState
from utils import *

class Simulator:
    def __init__(self, frame_budget, level_num):
        self.frame_budget = frame_budget
        self.level_num = level_num
    
    
    def simulate_level(self, shots):
        game = Game(limit_framerate=False, render=False, level_num=self.level_num)
        
        if len(shots) != game.level.number_of_birds:
            return None
        
        frame_num = 0
        for shot in shots:
            if shot.wait_frames == -1:
                break
            mouse_pos = shot.mouse_pos(game)
            game.set_sling_target(mouse_pos[0], mouse_pos[1])
            for frame in range(shot.wait_frames):
                game.step()
                frame_num += 1
                if self.simulation_over(game, frame_num):
                    return game.score
            game.release_sling()
            
        while not self.simulation_over(game, frame_num):
            game.step()
            frame_num += 1
                    
        return game.score
        
        
    def simulation_over(self, game, frame_num):
        return (frame_num > self.frame_budget or
            game.game_state == GameState.LOST or
            game.game_state == GameState.WON)
        
        
        
class Shot:
    wait_frames_values = range(5, 251)
    
    
    def __init__(self, wait_frames, power, angle):
        # How long to wait before executing this shot
        self.wait_frames = wait_frames
        
        # Percent of max shot power
        self.power = power
        
        # Angle bird is fired towards
        self.angle = angle
      
      
    def mouse_pos(self, game):
        max_pull = game.rope_length
        pull = max_pull * self.power / 100
        mouse_x = game.sling_x + pull * math.cos(math.radians(self.angle + 180))
        mouse_y = game.sling_y + pull * math.sin(math.radians(self.angle + 180))
        return mouse_x, mouse_y
    
    
    def get_random():
        wait_frames = random.choice(Shot.wait_frames_values())
        power = random.choice(Shot.power_values())
        angle = random.choice(Shot.angle_values())
        return Shot(wait_frames, power, angle)
    
    
    def wait_frames_values():
        return range(1, 251)
        
        
    def power_values():
        return range(1, 101)
        
        
    def angle_values():
        return range(-90, 91)
