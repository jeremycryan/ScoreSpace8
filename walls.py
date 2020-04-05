import pygame
import constants as c
import os

class Walls:

    def __init__(self, game):
        self.game = game
        self.width = 360
        self.target_width = self.width
        self.texture = pygame.image.load(os.path.join(c.ASSETS_PATH, "wall_texture.png"))
        self.right_texture = pygame.transform.flip(self.texture, 1, 0)

    def update(self, dt, events):
        dw = self.target_width - self.width
        p = 5
        if dw > 0:
            self.width = min(self.width + dt * dw * p, self.target_width)
        else:
            self.width = max(self.width + dt * dw * p, self.target_width)

    def draw(self, surface):
        color = c.BLACK
        padding = 100
        if self.game.y_offset > 15000:
            self.target_width = 500
        if self.game.y_offset > 30000:
            self.target_width = 640
        rect_width = c.MIDDLE_X - self.width//2
        pygame.draw.rect(surface,
                         color,
                         (self.game.shake_offset - padding,
                          self.game.shake_offset - padding,
                          rect_width + padding,
                          c.WINDOW_HEIGHT + padding*2))
        pygame.draw.rect(surface,
                         color,
                         (c.WINDOW_WIDTH - rect_width + self.game.shake_offset,
                          self.game.shake_offset - padding,
                          rect_width + padding,
                          c.WINDOW_HEIGHT + padding*2))

        off = (-self.game.y_offset) % 1250
        surface.blit(self.texture,
                    (self.game.shake_offset + rect_width,
                    self.game.shake_offset - padding - off))
        surface.blit(self.texture,
                    (self.game.shake_offset + rect_width,
                    self.game.shake_offset - padding - off + 1250))
        off = (off + 400) % 1250
        surface.blit(self.right_texture,
                    (c.WINDOW_WIDTH + self.game.shake_offset - rect_width - self.texture.get_width(),
                    self.game.shake_offset - padding - off))
        surface.blit(self.right_texture,
                    (c.WINDOW_WIDTH + self.game.shake_offset - rect_width - self.texture.get_width(),
                    self.game.shake_offset - padding - off + 1250))


    def is_too_far_left(self, object):
        edge = object.x - object.radius
        if edge < c.MIDDLE_X - self.width//2:
            return True
        return False

    def is_too_far_right(self, object):
        edge = object.x + object.radius
        if edge > c.MIDDLE_X + self.width//2:
            return True
        return False