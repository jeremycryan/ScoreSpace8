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
from enemy import Enemy, BigEnemy, SmallEnemy
from background import Background
import constants as c
import helpers as h


class Game:

    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 2, 1024)
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

        self.tear_sounds = [pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "tear1.wav")),
                            pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "tear2.wav")),
                            pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "tear3.wav")),
                            pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "tear4.wav"))]
        self.bad_tear_sounds = [pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "bad_tear1.wav")),
                                pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "bad_tear2.wav"))]

        while True:
            self.reset()
            self.main()

    def tear_sound(self):
        pass
        #random.choice(self.tear_sounds).play()

    def bad_tear_sound(self):
        pass
        #random.choice(self.bad_tear_sounds).play()

    def update_enemies(self, dt, events):
        while len(self.enemies) < 30:
            spacing = (c.WINDOW_HEIGHT//4) * (self.enemies[-1].y + 10000)/10000 \
                      + random.random() * c.WINDOW_HEIGHT//3 \
                      - c.WINDOW_HEIGHT//8
            padding = 50
            x = random.random()*(self.walls.width - 2 * padding) \
                       + c.MIDDLE_X \
                       - (self.walls.width - 2 * padding)/2
            y = self.enemies[-1].y + spacing
            seed = random.random()
            if seed < 0.6:
                new_enemy = Enemy
            elif seed < 0.8:
                new_enemy = BigEnemy
            else:
                new_enemy = SmallEnemy
            self.enemies.append(new_enemy(self, x=x, y=y))

    def reset(self):
        self.y_offset = 0
        self.player = Player(self)
        self.walls = Walls(self)
        self.slice = Slice(self)
        self.enemies = [BigEnemy(self, y=c.WINDOW_HEIGHT/2, x=c.MIDDLE_X)]
        self.enemies[0].angle = 0
        self.update_enemies(0, [])
        self.particles = []
        self.text_particles = []
        self.background = Background(self)
        self.player.velocity = (100, 600)
        self.aiming = False
        self.aimingness = 0

        self.score_yoff = 40
        self.score_size = 40
        self.target_score_size = 40
        self.score_bumped = True

        self.shade = pygame.Surface(c.WINDOW_SIZE)
        self.shade.fill(c.BLACK)
        self.shade.set_alpha(0)

        self.shade_2 = pygame.Surface(c.WINDOW_SIZE)
        self.shade.fill(c.BLACK)
        self.shade_2.set_alpha(0)

        self.flare = pygame.Surface(c.WINDOW_SIZE)
        self.flare.fill((255, 226, 140))
        self.flare.set_alpha(0)
        self.flare_alpha = 0

        self.multiplier = 1

        self.queue_reset = False

        self.game_end = False


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

        self.flare_alpha *= 0.7**dt
        self.flare_alpha -= 300 * dt
        self.flare_alpha = max(0, self.flare_alpha)
        self.flare.set_alpha(self.flare_alpha)


        if not self.queue_reset:
            if self.score() % 1000 < 500 and not self.score_bumped:
                self.score_bumped = True
                self.score_size = 80
            if self.score() % 1000 > 500 and self.score_bumped:
                self.score_bumped = False

        ds = self.target_score_size - self.score_size
        if ds > 0:
            self.score_size = min(self.score_size + ds * 5 * dt,
                                  self.target_score_size)
        else:
            self.score_size = max(self.score_size + ds * 5 * dt,
                                  self.target_score_size)

        if self.queue_reset:
            self.target_score_size = 80
            dy = c.MIDDLE_Y - self.score_yoff
            self.score_yoff = min(self.score_yoff + dy*5*dt, c.MIDDLE_Y - self.score_size//2)


    def score(self):
        return int(self.y_offset//10)

    def draw_score(self):
        text = f"{self.score()}"
        self.score_font = pygame.font.Font(os.path.join(c.ASSETS_PATH, "no_continue.ttf"), int(self.score_size))
        self.multiplier_font = pygame.font.Font(os.path.join(c.ASSETS_PATH, "gothland.ttf"), 20)
        surf = self.score_font.render(text, 0, c.WHITE)
        surf2 = self.score_font.render(text, 0, c.BLACK)
        x = c.MIDDLE_X - surf.get_width()//2
        y = self.score_yoff

        mult_text = f"x {self.multiplier}"
        mult_surf = self.multiplier_font.render(mult_text, 0, c.WHITE)
        mult_x = c.MIDDLE_X - mult_surf.get_width()//2
        mult_y = y + surf.get_height() + 6

        mpos = pygame.mouse.get_pos()
        padding = 35
        inner_padding = 12
        dx = max(x - mpos[0], mpos[0] - x - surf.get_width())
        dy = max(y - mpos[1], mpos[1] - mult_y - mult_surf.get_height())
        small_alpha = 80
        if dx < inner_padding and dy < inner_padding:
            if self.aiming:
                surf.set_alpha(small_alpha)
                surf2.set_alpha(small_alpha)
                mult_surf.set_alpha(small_alpha)
        elif dx < padding + inner_padding and dy < padding + inner_padding:
            diff = padding - (max(dx, dy) - inner_padding)
            if self.aiming:
                small_alpha = 255 - (255 - small_alpha)*(diff/padding)
                surf.set_alpha(small_alpha)
                surf2.set_alpha(small_alpha)
                mult_surf.set_alpha(small_alpha)

        self.screen.blit(surf2, (x, y+self.score_size//10))
        self.screen.blit(surf, (x, y))
        if self.multiplier > 1:
            pass
            #self.screen.blit(mult_surf, (mult_x, mult_y))



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

        self.shade.set_alpha(128 * self.aimingness)
        self.slowdown = 1 - 0.95 * self.aimingness



    def draw_shade(self):
        self.screen.blit(self.shade, (0, 0))

    def flare_up(self, amt):
        self.flare_alpha = amt

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
        self.clock.tick(c.MAX_FPS)
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

            # Do things
            dt, events = self.update_globals(rdt)
            if self.queue_reset:
                new_alpha = self.shade_2.get_alpha() + 500 * dt
                self.shade_2.set_alpha(min(new_alpha, 160))
            self.slice.update(rdt, events)
            self.update_effects(rdt, events)
            self.player.update(dt, events)
            self.walls.update(dt, events)
            self.background.update(dt, events)
            self.update_aim(dt, events)
            self.update_offset(dt, events)
            self.update_enemies(dt, events)
            for enemy in self.enemies[::-1]:
                enemy.update(dt, events)
            for particle in self.particles[::-1]:
                particle.update(dt, events)
            for particle in self.text_particles[::-1]:
                particle.update(rdt, events)

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
            for particle in self.text_particles:
                particle.draw(self.screen)
            if self.flare_alpha > 0:
                self.screen.blit(self.flare, (0, 0))
            if self.aiming:
                self.slice.draw(self.screen)
            self.player.draw(self.screen)
            if self.queue_reset:
                self.screen.blit(self.shade_2, (0, 0))
            self.draw_score()
            self.update_screen()

            self.clock.tick(c.MAX_FPS)

    def update_globals(self, dt):
        events = pygame.event.get()
        if self.player_is_dead():
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