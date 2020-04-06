import pygame
import constants as c
import math
import time
import os

from enemy import TutorialEnemy


class Player:

    def __init__(self, game):
        self.game = game

        self.velocity = (0, 0)
        self.x = c.MIDDLE_X
        self.y = 0
        self.accel = 0.6     # reduce speed to this proportion each second
        self.gravity = 800   # pixels per second per second
        self.max_fall_speed = 600
        self.cutting = False
        self.cut_so_far = 0

        self.surf = pygame.image.load(os.path.join(c.ASSETS_PATH, "player.png"))

        self.cut_distance = 250
        self.cut_speed = 1500

        self.max_speed = 4000

        # Radius for collisions
        self.radius = 10

    def bounce_left(self):
        self.velocity = (-abs(self.velocity[0]),
                         self.velocity[1])
        self.game.bounce.play()

    def bounce_right(self):
        self.velocity = (abs(self.velocity[0]),
                         self.velocity[1])
        self.game.bounce.play()

    def dash_toward(self, position, speed):
        if not self.game.slice.touched:
            return

        self.cut_so_far = 0
        self.cutting = True

        rel_x = position[0] - self.x
        rel_y = position[1] - self.y
        mag = (rel_x**2 + rel_y**2)**0.5

        self.velocity = (rel_x * speed/mag,
                         rel_y * speed/mag)

        self.game.dash.play()

    def add_speed(self, amount):
        mag = (self.velocity[0]**2 + self.velocity[1]**2)**0.5
        unit_x = self.velocity[0]/mag
        unit_y = self.velocity[1]/mag
        self.velocity = (self.velocity[0] + unit_x*amount,
                        self.velocity[1] + unit_y*amount)
        self.apply_max_velocity()

    def apply_max_velocity(self):
        mag = (self.velocity[0]**2 + self.velocity[1]**2)**0.5
        if mag > self.max_speed:
            self.velocity = (self.velocity[0] * self.max_speed/mag,
                             self.velocity[1] * self.max_speed/mag)
    def colliding_with(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        mag = (dx**2 + dy**2)**0.5
        return mag < other.radius

    def get_angle(self):
        # Get velocity angle in degrees
        angle = math.atan2(self.velocity[1], self.velocity[0])
        return angle/math.pi * 180

    def update(self, dt, events):
        if not self.cutting:
            self.x += self.velocity[0] * dt
            self.y += self.velocity[1] * dt
            self.velocity = (self.velocity[0] * self.accel**dt,
                             self.velocity[1] * self.accel**dt - self.gravity * dt)
            self.velocity = (self.velocity[0],
                             max(-self.max_fall_speed, self.velocity[1]))

        else:
            x_component = self.velocity[0] / (self.velocity[0]**2 + self.velocity[1]**2)**0.5
            self.x += self.cut_speed * x_component * dt
            y_component = self.velocity[1] / (self.velocity[0] ** 2 + self.velocity[1] ** 2) ** 0.5
            self.y += self.cut_speed * y_component * dt
            self.cut_so_far += self.cut_speed * dt

        if self.game.walls.is_too_far_left(self):
            self.bounce_right()
            self.x = c.MIDDLE_X - self.game.walls.width//2 + self.radius
            self.game.shake_effect(4)
        elif self.game.walls.is_too_far_right(self):
            self.bounce_left()
            self.x = c.MIDDLE_X + self.game.walls.width // 2 - self.radius
            self.game.shake_effect(4)

        for enemy in self.game.enemies:
            if self.colliding_with(enemy) and (self.velocity[1] > 550 or self.cutting):
                self.slice(enemy)

        if self.cut_so_far >= self.cut_distance:
            self.cutting = False

        self.apply_max_velocity()

    def slice(self, enemy):
        x, y = self.x, self.y
        ex, ey = enemy.x, enemy.y
        dx, dy = ex - x, ey - y
        angle = self.get_angle()
        enemy_angle = math.atan2(dy, dx)/math.pi * 180
        diff = (angle - enemy_angle) % 360
        inverted = diff < 180
        amt = 0.5 * math.cos(diff/180 * math.pi)
        if inverted:
            enemy.destroy(amt % 1)
        else:
            enemy.destroy(1 - (amt % 1))

        speed_to_add = 1000
        minimum_y = 1300
        if 0.5 - abs(amt) < 0.02:
            amt = 0.5
            self.game.slowdown_effect()
            self.game.shake_effect(25)
            speed_to_add = 2000 * self.game.launch_factor_multiplier()
            minimum_y = 2000 * self.game.launch_factor_multiplier()
            self.game.multiplier += 1
        else:
            if type(enemy) == TutorialEnemy:
                amt = 0.12
            else:
                self.game.shake_effect(10)
                self.game.slowdown_effect(0.05)
        speed_to_add *= enemy.launch_factor
        minimum_y *= enemy.launch_factor
        self.add_speed(speed_to_add * (amt*2)**2)
        self.velocity = (self.velocity[0], max(self.velocity[1], minimum_y*((amt*2)**2)))

    def draw(self, surface):
        x, y = self.game.game_position_to_screen_position((self.x, self.y))
        x, y = int(x), int(y)
        mag = (self.velocity[0]**2 + self.velocity[1]**2) ** 0.5
        msize = (3 + 3*mag/self.max_speed)
        medium = pygame.Surface((self.radius * msize, self.radius * msize))
        pygame.draw.circle(medium, c.WHITE, (int(self.radius*msize//2), int(self.radius*msize//2)), int(self.radius*msize//2))
        medium.set_colorkey(c.BLACK)
        medium.set_alpha(100 + 20*mag/self.max_speed)

        lsize = 4 + 6*mag/self.max_speed
        color_bump = int(50*mag/self.max_speed)
        large = pygame.Surface((self.radius * lsize, self.radius * lsize))
        pygame.draw.circle(large, (100 + color_bump//2, 150 + color_bump//2, 255),
                           (int(self.radius*lsize//2),
                            int(self.radius*lsize//2)),
                           int(self.radius*lsize//2))
        large.set_colorkey(c.BLACK)
        large.set_alpha(40 + 40 * mag/self.max_speed)

        surface.blit(medium, (x - medium.get_width()//2, y - medium.get_width()//2))
        surface.blit(large, (x - large.get_width()//2, y - large.get_width()//2))
        surface.blit(self.surf, (x - self.surf.get_width()//2, y - self.surf.get_width()//2))