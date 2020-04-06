import pygame
import os
import constants as c


class Button:

    def __init__(self, position, text, dimensions=(100, 50), visible=True, true_scale=1.0):
        self.x = position[0]
        self.y = position[1]
        self.width = dimensions[0]
        self.height = dimensions[1]
        self.text = text
        self.visible = visible
        self.disabled = False
        self.clicked = False

        self.true_scale = true_scale
        self.scale = 1.0
        self.target_scale = 1.0
        self.font_size = 40
        self.target_font_size = 40
        self.font = pygame.font.Font(os.path.join(c.ASSETS_PATH, "no_continue.ttf"), self.font_size)

    def hovered(self):
        if self.disabled:
            return False
        mx, my = pygame.mouse.get_pos()
        if self.x + self.width // 2 > mx > self.x - self.width // 2:
            if self.y + self.height // 2 > my > self.y - self.height // 2:
                return True
        return False

    def update(self, dt, events):
        self.clicked = False
        if not self.visible:
            self.font_size = 0
            return

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.hovered():
                        self.clicked = True

        ds = self.target_font_size - self.font_size
        if ds > 0:
            self.font_size = min(self.font_size + ds * 16 * dt, self.target_font_size)
        else:
            self.font_size = max(self.font_size + ds * 12 * dt, self.target_font_size)

        if not self.hovered():
            self.target_scale = 1.0
            self.target_font_size = 40
        else:
            self.target_scale = 1.5
            self.target_font_size = 50
        ds = self.target_scale - self.scale
        if ds > 0:
            self.scale = min(self.scale + ds * 5 * dt, self.target_scale)
        else:
            self.scale = max(self.scale + ds * 5 * dt, self.target_scale)

        if self.disabled:
            self.clicked = False

    def color(self):
        shade = int(255*self.scale/1.5)
        if self.disabled:
            shade -= 100
        return (shade, shade, shade)

    def draw(self, surface):
        if not self.visible:
            return
        self.font = pygame.font.Font(os.path.join(c.ASSETS_PATH, "no_continue.ttf"), int(self.font_size * self.true_scale))
        surf = self.font.render(self.text, 0, self.color())
        self.width = surf.get_width()
        self.height = surf.get_height()
        x = self.x - surf.get_width()//2
        y = self.y - surf.get_height()//2
        surface.blit(surf, (int(x), int(y)))