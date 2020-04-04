import pygame
import constants as c

class Walls:

    def __init__(self, game):
        self.game = game
        self.width = 400
        self.target_width = self.width

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
            self.target_width = 600
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