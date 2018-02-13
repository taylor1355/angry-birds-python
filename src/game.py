import pymunk as pm
import pygame
import time
from utils import *
from level import Level
from characters import Bird

pygame.init()

RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

bold_font = pygame.font.SysFont("arial", 30, bold=True)
bold_font2 = pygame.font.SysFont("arial", 40, bold=True)
bold_font3 = pygame.font.SysFont("arial", 50, bold=True)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((1200, 650))
        
        self.redbird = pygame.image.load("../resources/images/red-bird3.png").convert_alpha()
        self.background2 = pygame.image.load("../resources/images/background3.png").convert_alpha()
        self.sling_image = pygame.image.load("../resources/images/sling-3.png").convert_alpha()
        self.full_sprite = pygame.image.load("../resources/images/full-sprite.png").convert_alpha()
        self.buttons = pygame.image.load("../resources/images/selected-buttons.png").convert_alpha()
        self.pig_happy = pygame.image.load("../resources/images/pig_failed.png").convert_alpha()
        self.stars = pygame.image.load("../resources/images/stars-edited.png").convert_alpha()
        
        rect = pygame.Rect(181, 1050, 50, 50)
        cropped = self.full_sprite.subsurface(rect).copy()
        self.pig_image = pygame.transform.scale(cropped, (30, 30))
        
        rect = pygame.Rect(0, 0, 200, 200)
        self.star1 = self.stars.subsurface(rect).copy()
        
        rect = pygame.Rect(204, 0, 200, 200)
        self.star2 = self.stars.subsurface(rect).copy()
        
        rect = pygame.Rect(426, 0, 200, 200)
        self.star3 = self.stars.subsurface(rect).copy()
        
        rect = pygame.Rect(164, 10, 60, 60)
        self.pause_button = self.buttons.subsurface(rect).copy()
        
        rect = pygame.Rect(24, 4, 100, 100)
        self.replay_button = self.buttons.subsurface(rect).copy()
        
        rect = pygame.Rect(142, 365, 130, 100)
        self.next_button = self.buttons.subsurface(rect).copy()
        
        rect = pygame.Rect(18, 212, 100, 100)
        self.play_button = self.buttons.subsurface(rect).copy()
        
        self.clock = pygame.time.Clock()
        
        # the base of the physics
        self.space = pm.Space()
        self.space.gravity = (0.0, -700.0)
        self.pigs = []
        self.birds = []
        self.balls = []
        self.polys = []
        self.beams = []
        self.columns = []
        self.poly_points = []
        self.ball_number = 0
        self.polys_dict = {}
        self.angle = 0
        self.count = 0
        self.t1 = 0
        self.t2 = 0
        self.tick_to_next_circle = 10
        
        self.rope_length = 90
        self.pull_distance = 0
        self.sling_target_x, self.sling_target_y = None, None
        self.sling_x, self.sling_y = 135, 450
        self.sling2_x, self.sling2_y = 160, 450
        
        self.score = 0
        self.game_state = 0
        self.bird_path = []
        self.counter = 0
        self.restart_counter = False
        self.bonus_score_once = True
        self.wall = False

        # Static floor
        static_body = pm.Body(body_type=pm.Body.STATIC)
        self.static_lines = [pm.Segment(static_body, (0.0, 060.0), (1200.0, 060.0), 0.0)]
        static_lines1 = [pm.Segment(static_body, (1200.0, 060.0), (1200.0, 800.0), 0.0)]
        for line in self.static_lines:
            line.elasticity = 0.95
            line.friction = 1
            line.collision_type = 3
        for line in static_lines1:
            line.elasticity = 0.95
            line.friction = 1
            line.collision_type = 3
        self.space.add(self.static_lines)
        
        # bird and pig
        self.space.add_collision_handler(0, 1).post_solve=self.post_solve_bird_pig
        # bird and wood
        self.space.add_collision_handler(0, 2).post_solve=self.post_solve_bird_wood
        # pig and wood
        self.space.add_collision_handler(1, 2).post_solve=self.post_solve_pig_wood
        
        self.level = Level(self.pigs, self.columns, self.beams, self.space)
        self.level.number = 0
        self.level.load_level()
        
        
    def step(self):
        # Draw background
        self.screen.fill((130, 200, 100))
        self.screen.blit(self.background2, (0, -50))
        # Draw first part of the sling
        rect = pygame.Rect(50, 0, 70, 220)
        self.screen.blit(self.sling_image, (138, 420), rect)
        # Draw the trail left behind
        for point in self.bird_path:
            pygame.draw.circle(self.screen, WHITE, point, 5, 0)
        # Draw the birds in the wait line
        if self.level.number_of_birds > 0:
            for i in range(self.level.number_of_birds-1):
                x = 100 - (i*35)
                self.screen.blit(self.redbird, (x, 508))
        # Draw sling behavior
        if self.sling_target_x is not None and self.level.number_of_birds > 0:
            self.sling_action()
        else:
            if time.time()*1000 - self.t1 > 300 and self.level.number_of_birds > 0:
                self.screen.blit(self.redbird, (130, 426))
            else:
                pygame.draw.line(self.screen, (0, 0, 0), (self.sling_x, self.sling_y-8),
                                 (self.sling2_x, self.sling2_y-7), 5)
        birds_to_remove = []
        pigs_to_remove = []
        self.counter += 1
        # Draw birds
        for bird in self.birds:
            if bird.shape.body.position.y < 0:
                birds_to_remove.append(bird)
            p = to_pygame(bird.shape.body.position)
            x, y = p
            x -= 22
            y -= 20
            self.screen.blit(self.redbird, (x, y))
            pygame.draw.circle(self.screen, BLUE,
                               p, int(bird.shape.radius), 2)
            if self.counter >= 3 and time.time() - self.t1 < 5:
                bird_path.append(p)
                self.restart_counter = True
        if self.restart_counter:
            self.counter = 0
            self.restart_counter = False
        # Remove birds and pigs
        for bird in birds_to_remove:
            self.space.remove(bird.shape, bird.shape.body)
            self.birds.remove(bird)
        for pig in pigs_to_remove:
            self.space.remove(pig.shape, pig.shape.body)
            self.pigs.remove(pig)
        # Draw static lines
        for line in self.static_lines:
            body = line.body
            pv1 = body.position + line.a.rotated(body.angle)
            pv2 = body.position + line.b.rotated(body.angle)
            p1 = to_pygame(pv1)
            p2 = to_pygame(pv2)
            pygame.draw.lines(self.screen, (150, 150, 150), False, [p1, p2])
        i = 0
        # Draw pigs
        for pig in self.pigs:
            i += 1
            # print (i,pig.life)
            pig = pig.shape
            if pig.body.position.y < 0:
                pigs_to_remove.append(pig)

            p = to_pygame(pig.body.position)
            x, y = p

            angle_degrees = math.degrees(pig.body.angle)
            img = pygame.transform.rotate(self.pig_image, angle_degrees)
            w,h = img.get_size()
            x -= w*0.5
            y -= h*0.5
            self.screen.blit(img, (x, y))
            pygame.draw.circle(self.screen, BLUE, p, int(pig.radius), 2)
        # Draw columns and Beams
        for column in self.columns:
            column.draw_poly('columns', self.screen)
        for beam in self.beams:
            beam.draw_poly('beams', self.screen)
        # Update physics
        dt = 1.0/50.0/2.
        for x in range(2):
            self.space.step(dt) # make two updates per frame for better stability
        # Drawing second part of the sling
        rect = pygame.Rect(0, 0, 60, 200)
        self.screen.blit(self.sling_image, (120, 420), rect)
        # Draw score
        score_font = bold_font.render("SCORE", 1, WHITE)
        number_font = bold_font.render(str(self.score), 1, WHITE)
        self.screen.blit(score_font, (1060, 90))
        if self.score == 0:
            self.screen.blit(number_font, (1100, 130))
        else:
            self.screen.blit(number_font, (1060, 130))
        self.screen.blit(self.pause_button, (10, 90))
        # Pause option
        if self.game_state == 1:
            self.screen.blit(self.play_button, (500, 200))
            self.screen.blit(self.replay_button, (500, 300))
        self.draw_level_cleared()
        self.draw_level_failed()
        pygame.display.flip()
        self.clock.tick(50)
        pygame.display.set_caption("fps: " + str(self.clock.get_fps()))
        
    def set_sling_target(self, x, y):
        self.sling_target_x = x
        self.sling_target_y = y
        
        
    def release_sling(self):
        if self.level.number_of_birds > 0:
            self.level.number_of_birds -= 1
            t1 = time.time()*1000
            xo = 154
            yo = 156
            self.pull_distance = min(self.pull_distance, self.rope_length)
            if self.sling_target_x < self.sling_x+5:
                bird = Bird(self.pull_distance, self.angle, xo, yo, self.space)
                self.birds.append(bird)
            else:
                bird = Bird(-self.pull_distance, self.angle, xo, yo, self.space)
                self.birds.append(bird)
            if self.level.number_of_birds == 0:
                self.t2 = time.time()
        
        
    def sling_action(self):
        """Set up sling behavior"""
        # Fixing bird to the sling rope
        v = vector((self.sling_x, self.sling_y), (self.sling_target_x, self.sling_target_y))
        pull_direction = unit_vector(v)
        self.pull_distance = magnitude(v)
        pu = (pull_direction[0]*self.rope_length+self.sling_x, pull_direction[1]*self.rope_length+self.sling_y)
        bigger_rope = 102
        x_redbird = self.sling_target_x - 20
        y_redbird = self.sling_target_y - 20
        if self.pull_distance > self.rope_length:
            pux, puy = pu
            pux -= 20
            puy -= 20
            pul = pux, puy
            self.screen.blit(self.redbird, pul)
            pu2 = (pull_direction[0]*bigger_rope+self.sling_x, pull_direction[1]*bigger_rope+self.sling_y)
            pygame.draw.line(self.screen, (0, 0, 0), (self.sling2_x, self.sling2_y), pu2, 5)
            self.screen.blit(self.redbird, pul)
            pygame.draw.line(self.screen, (0, 0, 0), (self.sling_x, self.sling_y), pu2, 5)
        else:
            self.pull_distance += 10
            pu3 = (pull_direction[0]*self.pull_distance+self.sling_x, pull_direction[1]*self.pull_distance+self.sling_y)
            pygame.draw.line(self.screen, (0, 0, 0), (self.sling2_x, self.sling2_y), pu3, 5)
            self.screen.blit(self.redbird, (x_redbird, y_redbird))
            pygame.draw.line(self.screen, (0, 0, 0), (self.sling_x, self.sling_y), pu3, 5)
        # Angle of impulse
        dy = self.sling_target_y - self.sling_y
        dx = self.sling_target_x - self.sling_x
        if dx == 0:
            dx = 0.00000000000001
        self.angle = math.atan((float(dy))/dx)
        

    def draw_level_cleared(self):
        """Draw level cleared"""
        level_cleared = bold_font3.render("Level Cleared!", 1, WHITE)
        score_level_cleared = bold_font2.render(str(self.score), 1, WHITE)
        if self.level.number_of_birds >= 0 and len(self.pigs) == 0:
            if self.bonus_score_once:
                self.score += (self.level.number_of_birds-1) * 10000
            self.bonus_score_once = False
            self.game_state = 4
            rect = pygame.Rect(300, 0, 600, 800)
            pygame.draw.rect(self.screen, BLACK, rect)
            self.screen.blit(level_cleared, (450, 90))
            if self.score >= self.level.one_star and self.score <= self.level.two_star:
                self.screen.blit(self.star1, (310, 190))
            if self.score >= self.level.two_star and self.score <= self.level.three_star:
                self.screen.blit(self.star1, (310, 190))
                self.screen.blit(self.star2, (500, 170))
            if self.score >= self.level.three_star:
                self.screen.blit(self.star1, (310, 190))
                self.screen.blit(self.star2, (500, 170))
                self.screen.blit(self.star3, (700, 200))
            self.screen.blit(score_level_cleared, (550, 400))
            self.screen.blit(self.replay_button, (510, 480))
            self.screen.blit(self.next_button, (620, 480))


    def draw_level_failed(self):
        """Draw level failed"""
        failed = bold_font3.render("Level Failed", 1, WHITE)
        if self.level.number_of_birds <= 0 and time.time() - self.t2 > 5 and len(self.pigs) > 0:
            self.game_state = 3
            rect = pygame.Rect(300, 0, 600, 800)
            pygame.draw.rect(self.screen, BLACK, rect)
            self.screen.blit(failed, (450, 90))
            self.screen.blit(self.pig_happy, (380, 120))
            self.screen.blit(self.replay_button, (520, 460))


    def restart(self):
        """Delete all objects of the level"""
        self.pigs_to_remove = []
        self.birds_to_remove = []
        self.columns_to_remove = []
        self.beams_to_remove = []
        for pig in self.pigs:
            self.pigs_to_remove.append(pig)
        for pig in self.pigs_to_remove:
            self.space.remove(pig.shape, pig.shape.body)
            self.pigs.remove(pig)
        for bird in self.birds:
            self.birds_to_remove.append(bird)
        for bird in self.birds_to_remove:
            self.space.remove(bird.shape, bird.shape.body)
            self.birds.remove(bird)
        for column in self.columns:
            self.columns_to_remove.append(column)
        for column in self.columns_to_remove:
            self.space.remove(column.shape, column.shape.body)
            self.columns.remove(column)
        for beam in self.beams:
            self.beams_to_remove.append(beam)
        for beam in self.beams_to_remove:
            self.space.remove(beam.shape, beam.shape.body)
            self.beams.remove(beam)


    def post_solve_bird_pig(self, arbiter, space, _):
        """Collision between bird and pig"""
        surface=self.screen
        a, b = arbiter.shapes
        bird_body = a.body
        pig_body = b.body
        p = to_pygame(bird_body.position)
        p2 = to_pygame(pig_body.position)
        r = 30
        pygame.draw.circle(surface, BLACK, p, r, 4)
        pygame.draw.circle(surface, RED, p2, r, 4)
        self.pigs_to_remove = []
        for pig in self.pigs:
            if pig_body == pig.body:
                pig.life -= 20
                self.pigs_to_remove.append(pig)
                self.score += 10000
        for pig in self.pigs_to_remove:
            space.remove(pig.shape, pig.shape.body)
            self.pigs.remove(pig)


    def post_solve_bird_wood(self, arbiter, space, _):
        """Collision between bird and wood"""
        poly_to_remove = []
        if arbiter.total_impulse.length > 1100:
            a, b = arbiter.shapes
            for column in self.columns:
                if b == column.shape:
                    poly_to_remove.append(column)
            for beam in self.beams:
                if b == beam.shape:
                    poly_to_remove.append(beam)
            for poly in poly_to_remove:
                if poly in self.columns:
                    self.columns.remove(poly)
                if poly in self.beams:
                    self.beams.remove(poly)
            space.remove(b, b.body)
            self.score += 5000


    def post_solve_pig_wood(self, arbiter, space, _):
        """Collision between pig and wood"""
        pigs_to_remove = []
        if arbiter.total_impulse.length > 700:
            pig_shape, wood_shape = arbiter.shapes
            for pig in self.pigs:
                if pig_shape == pig.shape:
                    pig.life -= 20
                    self.score += 10000
                    if pig.life <= 0:
                        pigs_to_remove.append(pig)
        for pig in pigs_to_remove:
            space.remove(pig.shape, pig.shape.body)
            self.pigs.remove(pig)
            
            
class GameGraphics:
    