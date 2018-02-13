import os
import sys
import math
import time
import pygame
current_path = os.getcwd()
import pymunk as pm
from characters import Bird
from level import Level
from game import Game
from utils import *

def load_music():
    """Load the music"""
    song1 = '../resources/sounds/angry-birds.ogg'
    pygame.mixer.music.load(song1)
    pygame.mixer.music.play(-1)


def main():
    pygame.init()
    load_music()
    
    mouse_pressed = False
    
    game = Game()
    
    while True:
        x_mouse, y_mouse = pygame.mouse.get_pos()
        
        # Input handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            #elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            #    # Toggle wall
            #    if wall:
            #        space.remove(static_lines1)
            #        wall = False
            #    else:
            #        space.add(static_lines1)
            #        wall = True
            #elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            #    space.gravity = (0.0, -10.0)
            #    level.bool_space = True
            #elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
            #    space.gravity = (0.0, -700.0)
            #    level.bool_space = False
            
            if (pygame.mouse.get_pressed()[0] and x_mouse > 100 and
                    x_mouse < 250 and y_mouse > 370 and y_mouse < 550):
                mouse_pressed = True
                
            if mouse_pressed:
                game.set_sling_target(x_mouse, y_mouse)
                
            if (event.type == pygame.MOUSEBUTTONUP and event.button == 1 and mouse_pressed):
                # Release new bird
                game.release_sling()
                mouse_pressed = False
                game.set_sling_target(None, None)
            
            # Interacting with UI elements            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if (x_mouse < 60 and y_mouse < 155 and y_mouse > 90):
                    game.game_state = 1
                if game.game_state == 1:
                    if x_mouse > 500 and y_mouse > 200 and y_mouse < 300:
                        # Resume in the paused screen
                        game.game_state = 0
                    if x_mouse > 500 and y_mouse > 300:
                        # Restart in the paused screen
                        game.restart()
                        game.level.load_level()
                        game.game_state = 0
                        game.bird_path = []
                if game.game_state == 3:
                    # Restart in the failed level screen
                    if x_mouse > 500 and x_mouse < 620 and y_mouse > 450:
                        game.restart()
                        game.level.load_level()
                        game.game_state = 0
                        game.bird_path = []
                        game.score = 0
                if game.game_state == 4:
                    # Build next level
                    if x_mouse > 610 and y_mouse > 450:
                        game.restart()
                        game.level.number += 1
                        game.game_state = 0
                        game.level.load_level()
                        game.score = 0
                        game.bird_path = []
                        game.bonus_score_once = True
                    if x_mouse < 610 and x_mouse > 500 and y_mouse > 450:
                        # Restart in the level cleared screen
                        game.restart()
                        game.level.load_level()
                        game.game_state = 0
                        game.bird_path = []
                        game.score = 0
                        
        game.step()
        
        
if __name__ == "__main__":
    main()
