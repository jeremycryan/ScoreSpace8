# Python imports
import time
import sys
import random
import math
import os

# Third party libraries
import pygame

# Auxiliary modules
from player import Player
from walls import Walls
from slice import Slice
from enemy import Enemy, BigEnemy
from background import Background
import constants as c
import helpers as h


class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(c.WINDOW_SIZE)
        self.clock = pygame.time.Clock()

        self.slowdown = 1.0
        self.effect_slow = 1.0
        self.since_effect = 1000
        self.since_shake = 1000
        self.shake_amp = 0
        self.shake_frequency = 9
        self.shake_offset = 0

        self.score_font = pygame.font.Font(os.path.join(c.ASSETS_PATH, "no_continue.ttf"), 40)
        self.multiplier_font = pygame.font.Font(os.path.join(c.ASSETS_PATH, "no_continue.ttf"), 20)

        while True:
            self.reset()
            self.main()

    def reset(self):
        self.player = Player(self)
        self.walls = Walls(self)
        self.slice = Slice(self)
        self.enemies = [BigEnemy(self, y=c.WINDOW_HEIGHT/2, x=c.MIDDLE_X)]
        self.enemies[0].angle = 0
        for i in range(3, 120):
            y_random = (i**1.2)*c.WINDOW_HEIGHT//4 + random.random()*200 + c.MIDDLE_Y
            x_random = random.random()*300 + c.MIDDLE_X - 150
            if random.random() < 0.8:
                new_enemy = Enemy(self, y=y_random, x=x_random)
            else:
                new_enemy = BigEnemy(self, y=y_random, x=x_random)
            self.enemies.append(new_enemy)
        self.particles = []
        self.background = Background(self)
        self.player.velocity = (100, 600)
        self.aiming = False
        self.aimingness = 0

        self.shade = pygame.Surface(c.WINDOW_SIZE)
        self.shade.fill(c.BLACK)
        self.shade.set_alpha(0)

        self.multiplier = 1

        self.y_offset = 0
        self.queue_reset = False


    def update_effects(self, dt, events):
        self.since_effect += dt
        if self.since_effect > 0:
            self.effect_slow = 1.0
        else:
            self.effect_slow = 0.01

        self.since_shake += dt
        self.shake_offset = self.shake_amp * math.cos(self.since_shake * self.shake_frequency * 2 * math.pi)
        self.shake_amp *= 0.2**dt
        self.shake_amp = max(self.shake_amp - 200*dt, 0)

    def score(self):
        return int(self.y_offset//10)

    def draw_score(self):
        text = f"{self.score()}"
        surf = self.score_font.render(text, 0, c.WHITE)
        x = c.MIDDLE_X - surf.get_width()//2
        y = 40

        mult_text = f"x {self.multiplier}"
        mult_surf = self.multiplier_font.render(mult_text, 0, c.WHITE)
        mult_x = c.MIDDLE_X - mult_surf.get_width()//2
        mult_y = y + surf.get_height() + 10

        mpos = pygame.mouse.get_pos()
        padding = 30
        if mpos[0] < c.MIDDLE_X + surf.get_width()//2 + padding:
            if mpos[0] > c.MIDDLE_X - surf.get_width()//2 - padding:
                if mpos[1] > y - padding:
                    if mpos[1] < y + padding + surf.get_height():
                        if self.aiming:
                            surf.set_alpha(80)
                            mult_surf.set_alpha(80)

        self.screen.blit(surf, (x, y))
        if self.multiplier > 1:
            self.screen.blit(mult_surf, (mult_x, mult_y))



    def slowdown_effect(self, duration = 0.4):
        self.since_effect = -duration

    def shake_effect(self, amplitude=20):
        if amplitude < self.shake_amp:
            return
        self.since_shake = 0
        self.shake_amp = max(amplitude, self.shake_amp)

    def update_offset(self, dt, events):
        max_off = c.WINDOW_HEIGHT*0.7
        if self.player.y > self.y_offset + max_off:
            self.y_offset = self.player.y - max_off

    def update_aim(self, dt, events):
        speed = 7
        da = self.aiming - self.aimingness
        self.aimingness += h.sign(da) * dt * speed
        if self.aimingness > 1:
            self.aimingness = 1
        elif self.aimingness < 0:
            self.aimingness = 0

        self.shade.set_alpha(100 * self.aimingness)
        self.slowdown = 1 - 0.95 * self.aimingness

    def draw_shade(self):
        self.screen.blit(self.shade, (0, 0))

    def game_to_screen_y(self, y):
        return c.WINDOW_HEIGHT - y + self.y_offset

    def game_position_to_screen_position(self, pos):
        x = pos[0] + self.shake_offset
        y = self.game_to_screen_y(pos[1]) + self.shake_offset
        return x, y

    def screen_position_to_game_position(self, pos):
        x = pos[0]
        y = c.WINDOW_HEIGHT - pos[1] + self.y_offset
        return x, y

    def mouse_position(self):
        mpos = pygame.mouse.get_pos()
        return self.screen_position_to_game_position(mpos)

    def main(self):
        then = time.time()
        self.clock.tick(60)
        time.sleep(0.001)
        since_print = 0
        fpss = []

        while True:
            now = time.time()
            rdt = now - then
            if rdt > 1/30: rdt = 1/30
            then = now
            since_print += rdt
            fpss.insert(0, 1/rdt)
            fpss = fpss[:100]
            if since_print > 1:
                print(f"FPS: {sum(fpss)/len(fpss)}")
                since_print = 0

            # Do things
            dt, events = self.update_globals(rdt)
            self.slice.update(rdt, events)
            self.update_effects(rdt, events)
            self.player.update(dt, events)
            self.walls.update(dt, events)
            self.background.update(dt, events)
            self.update_aim(dt, events)
            self.update_offset(dt, events)
            for enemy in self.enemies[::-1]:
                enemy.update(dt, events)
            for particle in self.particles[::-1]:
                particle.update(dt, events)

            # Draw things
            # self.screen.fill((150, 150, 150))
            self.background.draw(self.screen)
            for particle in self.particles:
                particle.draw(self.screen)
            if self.shade.get_alpha() > 0:
                self.draw_shade()
            for enemy in self.enemies:
                enemy.draw(self.screen)
            self.walls.draw(self.screen)
            if self.aiming:
                self.slice.draw(self.screen)
            self.player.draw(self.screen)
            self.draw_score()
            self.update_screen()

            self.clock.tick(60)
            if self.queue_reset:
                break

    def update_globals(self, dt):
        events = pygame.event.get()
        if self.player_is_dead():
            print(f"SCORE: {self.y_offset//10}")
            self.queue_reset = True
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # 1 is left click
                    self.player.dash_toward(self.mouse_position(), 300)
                    self.aiming = False
                    self.aimingness = 0
            if event.type == pygame.MOUSEBUTTONDOWN and not self.player.cutting:
                if event.button == 1:
                    self.shade_target_alpha = 100
                    self.aiming = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.queue_reset = True
        return dt * min(self.slowdown, self.effect_slow), events

    def update_screen(self):
        pygame.display.flip()

    def player_is_dead(self):
        return self.player.y < self.y_offset - 50


if __name__=="__main__":
    Game()