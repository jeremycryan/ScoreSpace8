import pygame
import constants as c
import random


class Particle:

    def __init__(self, game, surface, position, rotation=0, angle=0, velocity=(0, 0), gravity=800):
        self.game = game
        self.surf = surface
        self.temp_surf = self.surf
        self.temp_surf.set_colorkey(c.BLACK)
        self.x = position[0]
        self.y = position[1]
        self.velocity = velocity
        self.gravity = gravity
        self.rotation = rotation # rotation speed in degrees per second
        self.angle = angle       # rotation relative to start
        self.age = 0

    def update(self, dt, events):
        self.angle += self.rotation * dt
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        self.velocity = (self.velocity[0], self.velocity[1] - self.gravity * dt)

        if self.y < self.game.y_offset - 200:
            self.destroy()

        self.age += dt

    def draw(self, surface):
        if self.rotation:
            self.temp_surf = pygame.transform.rotate(self.surf, self.angle)
        else:
            self.temp_surf = self.surf

        x, y = self.game.game_position_to_screen_position((self.x, self.y))
        x = int(x - self.temp_surf.get_width()/2)
        y = int(y - self.temp_surf.get_height()/2)
        surface.blit(self.temp_surf, (x, y))

    def destroy(self):
        self.game.particles.remove(self)


class Chunk(Particle):
    def __init__(self, game, position):
        color = random.choice([(255, 200, 150),
                               (225, 225, 100),
                               (235, 235, 200)])
        surface = pygame.Surface((5, 5))
        surface.fill(color)
        xv = random.random()**2 * 250 - 100 + 0.5 * game.player.velocity[0] * random.random()
        yv = random.random()**2 * 800 - 200 + 0.5 * game.player.velocity[1] * random.random()
        self.radius = 0
        super().__init__(game, surface, position, rotation=0, angle=0, velocity=(xv, yv), gravity=800)

    def update(self, dt, events):
        super().update(dt, events)
        decel = 0.7
        if self.game.walls.is_too_far_left(self):
            self.velocity = (abs(self.velocity[0])*decel, self.velocity[1])
        elif self.game.walls.is_too_far_right(self):
            self.velocity = (-abs(self.velocity[0])*decel, self.velocity[1])


class Fadeout(Particle):
    def __init__(self, game, surface, position, rate=300):
        self.game = game
        self.surf = surface
        self.x, self.y = position
        self.rate = rate
        self.alpha = self.surf.get_alpha()
        self.rotation = 0

    def update(self, dt, events):
        self.alpha -= self.rate * dt
        if self.alpha <= 0:
            self.destroy()
        else:
            self.surf.set_alpha(int(self.alpha))


