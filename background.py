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
        surface.blit(self.layer_3, (0, height/6/slowness - 600))
        surface.blit(self.layer_2, (0, height / 5 / slowness - 250))
        surface.blit(self.layer_1, (0, height / 4 / slowness))