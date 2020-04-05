import pygame
import constants as c
import os


class Background:

    def __init__(self, game):
        self.game = game

        self.gray_rect = pygame.Surface((c.WINDOW_WIDTH, 100))
        self.gray_rect.fill(c.WHITE)
        self.gray_rect.set_alpha(20)

        self.layer_1 = pygame.image.load(os.path.join(c.ASSETS_PATH, "background_layer_1.png"))
        self.layer_2 = pygame.image.load(os.path.join(c.ASSETS_PATH, "background_layer_2.png"))
        self.layer_2_5 = pygame.image.load(os.path.join(c.ASSETS_PATH, "background_layer_2.5.png"))
        self.layer_3 = pygame.image.load(os.path.join(c.ASSETS_PATH, "background_layer_3.png"))

    def update(self, dt, events):
        pass

    def draw(self, surface):
        offset = -self.game.y_offset % 200

        height = self.game.y_offset
        slowness = 10
        while offset < c.WINDOW_HEIGHT + 200:
            surface.blit(self.gray_rect,
                         (self.game.shake_offset, c.WINDOW_HEIGHT - offset + self.game.shake_offset))
            offset += 200

        padding = 20
        x = c.MIDDLE_X - self.game.walls.width//2 - padding
        y = height/12/slowness - 800
        w = self.game.walls.width + padding * 2
        surface.blit(self.layer_3, (x, y), (x, 0, w, self.layer_3.get_height()))

        padding = 20
        x = c.MIDDLE_X - self.game.walls.width//2 - padding
        y = height/9/slowness - 150
        w = self.game.walls.width + padding * 2
        surface.blit(self.layer_2_5, (x, y), (x, 0, w, self.layer_2_5.get_height()))

        padding = 20
        x = c.MIDDLE_X - self.game.walls.width//2 - padding
        y = height / 7 / slowness - 200
        w = self.game.walls.width + padding * 2
        surface.blit(self.layer_2, (x, y), (x, 0, w, self.layer_2.get_height()))

        padding = 20
        x = c.MIDDLE_X - self.game.walls.width//2 - padding
        y = height/5/slowness
        w = self.game.walls.width + padding * 2
        surface.blit(self.layer_1, (x, y), (x, 0, w, self.layer_1.get_height()))