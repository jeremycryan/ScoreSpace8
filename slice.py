import pygame
import constants as c
import os
import math


class Slice:

    def __init__(self, game):
        self.game = game
        self.time = 0
        self.touched = set()
        self.pointer = pygame.image.load(os.path.join(c.ASSETS_PATH, "pointer.png"))
        self.pointer_missing = pygame.image.load(os.path.join(c.ASSETS_PATH, "pointer_missing.png"))

    def update(self, dt, events):
        self.touched = self.enemies_touched()
        #self.time += dt

    def draw(self, surface):
        period = 1
        space = 8
        radius = 2
        color = (255, 255, 255)
        start_x = self.game.player.x
        start_y = self.game.player.y
        end_x, end_y = self.game.mouse_position()
        dx = end_x - start_x
        dy = end_y - start_y
        mag = (dx**2 + dy**2)**0.5
        dxu = dx/mag * space
        dyu = dy/mag * space

        index_x = dxu * (self.time % period)/period
        index_y = dyu * (self.time % period)/period


        if dyu == 0:
            dyu = -1
        angle = math.atan2(-dxu, dyu)/math.pi * 180
        if self.touched:
            surf = pygame.transform.rotate(self.pointer, int(angle))
        else:
            surf = pygame.transform.rotate(self.pointer_missing, int(angle))
            color = (120, 120, 120)

        i = 0
        while abs(index_x) < abs(dx) and abs(index_y) < abs(dy):
            x, y = self.game.game_position_to_screen_position((start_x + index_x, start_y + index_y))
            pygame.draw.circle(surface,
                               color,
                               (int(x), int(y)),
                               radius)
            if i+3 > self.game.player.cut_distance/space:
                break
            elif i+5 > self.game.player.cut_distance/space and self.touched:
                break
            index_x += dxu
            index_y += dyu
            i += 1

        x, y = self.game.game_position_to_screen_position((start_x + index_x, start_y + index_y))
        surface.blit(surf, (int(x - surf.get_width()//2), int(y - surf.get_height()//2)))

    def enemies_touched(self):
        # return a set of all enemies within path
        for enemy in self.game.enemies:
            enemy.touched = False
        if not self.game.aiming:
            self.touched = set()
            return self.touched
        points = 25
        start_x = self.game.player.x
        start_y = self.game.player.y
        end_x, end_y = self.game.mouse_position()
        dx = end_x - start_x
        dy = end_y - start_y
        mag = (dx**2 + dy**2)**0.5
        dxu = dx/mag
        dyu = dy/mag
        enemies_touched = set()
        for i in range(points):
            distance = i/points * self.game.player.cut_distance
            x = start_x + dxu*distance
            y = start_y + dyu*distance
            for enemy in self.game.enemies:
                if enemy.y > self.game.y_offset + 2*c.WINDOW_HEIGHT:
                    continue
                dist = ((x - enemy.x)**2 + (y - enemy.y)**2)**0.5
                if dist < enemy.radius:
                    enemies_touched.add(enemy)

        for enemy in enemies_touched:
            enemy.touch()
        self.touched = enemies_touched
        return enemies_touched
