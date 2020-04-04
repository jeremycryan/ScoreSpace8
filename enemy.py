import constants as c
import pygame
import math
from particle import Particle, Chunk, Fadeout
import os
import random


class Enemy:

    def __init__(self, game, radius = 30, x=c.WINDOW_WIDTH//2, y=c.WINDOW_HEIGHT//2):
        self.game = game
        self.radius = radius
        self.x = x
        self.y = y
        self.angle = random.random() * 60 + 15
        self.surf = pygame.image.load(os.path.join(c.ASSETS_PATH, "lantern.png"))
        self.draw_surf = pygame.transform.rotate(self.surf, self.angle)
        self.touched_surf = pygame.image.load(os.path.join(c.ASSETS_PATH, "lantern_touched.png"))
        self.touched_surf = pygame.transform.rotate(self.touched_surf, self.angle)
        # self.draw_surf.set_colorkey(c.BLACK)
        # self.touched_surf.set_colorkey(c.BLACK)
        self.touched = False
        self.launch_factor=1.0
        self.glow = self.generate_glow()
        self.age = 0

    def generate_glow(self, radius=1.7):
        glow_radius = int(radius * self.radius)
        self.glow = pygame.Surface((glow_radius*2, glow_radius*2))
        pygame.draw.circle(self.glow, c.WHITE, (glow_radius, glow_radius), glow_radius)
        self.glow.set_alpha(32)
        self.glow.set_colorkey(c.BLACK)
        return self.glow

    def update(self, dt, events):
        if self.y < self.game.y_offset - self.radius*3:
            self.remove()

        self.age += dt
        radius = 1.7 + 0.1*math.sin(self.age*20)
        self.glow = self.generate_glow(radius)

    def draw(self, surface):
        if self.y > self.game.y_offset + c.WINDOW_HEIGHT*2:
            return
        x, y = self.game.game_position_to_screen_position((self.x, self.y))
        surface.blit(self.glow, (int(x - self.glow.get_width()//2), int(y - self.glow.get_height()//2)))
        if not self.touched:
            surface.blit(self.draw_surf,
                         (int(x - self.draw_surf.get_width()/2), int(y - self.draw_surf.get_height()/2)))
        else:
            surface.blit(self.touched_surf,
                         (int(x - self.draw_surf.get_width()/2), int(y - self.draw_surf.get_height()/2)))

    def touch(self):
        self.touched = True

    def remove(self):
        self.game.enemies.remove(self)

    def destroy(self, cut_prop=0.5):
        self.remove()

        angle = self.game.player.get_angle()
        cutoff = int(cut_prop*self.radius*2)
        top_offset = self.radius - cutoff//2
        bottom_offset = -cutoff//2
        angle_rad = -angle/180 * math.pi
        top_offset = (top_offset * math.sin(angle_rad), top_offset * math.cos(angle_rad))
        bottom_offset = (bottom_offset * math.sin(angle_rad), bottom_offset * math.cos(angle_rad))

        particle_surf = pygame.Surface((self.radius*2, cutoff))
        particle_surf.blit(self.surf, (0, 0))
        top_half = Particle(self.game,
                                particle_surf,
                                (self.x + top_offset[0], self.y + top_offset[1]),
                                rotation=120,
                                velocity=(-30, 500),
                                angle=angle)
        self.game.particles.append(top_half)

        particle_surf = pygame.Surface((self.radius*2, self.radius*2 - cutoff))
        particle_surf.blit(self.surf, (0, -cutoff))
        bottom_half = Particle(self.game,
                                particle_surf,
                                (self.x + bottom_offset[0], self.y + bottom_offset[1]),
                                rotation=-40,
                                velocity=(60, 150),
                                angle=angle)
        self.game.particles.append(bottom_half)

        if abs(cut_prop - 0.5) < 0.02:
            self.glow.set_alpha(100)
        self.game.particles.append(Fadeout(self.game, self.glow, (self.x, self.y)))

        for i in range(30):
            self.game.particles.append(Chunk(self.game, (self.x, self.y)))


class BigEnemy(Enemy):
    def __init__(self, game, x=c.WINDOW_WIDTH//2, y=c.WINDOW_HEIGHT//2):
        self.game = game
        self.radius = 40
        self.x = x
        self.y = y
        self.angle = random.random() * 60 - 30
        self.surf = pygame.image.load(os.path.join(c.ASSETS_PATH, "big_lantern.png"))
        self.draw_surf = pygame.transform.rotate(self.surf, self.angle)
        self.touched_surf = pygame.image.load(os.path.join(c.ASSETS_PATH, "big_lantern_touched.png"))
        self.touched_surf = pygame.transform.rotate(self.touched_surf, self.angle)
        self.touched = False
        self.launch_factor = 1.3
        self.age = 0
        self.glow = self.generate_glow()
