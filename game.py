# Python imports
import time
import sys
import random
import math
import os
import threading

# Third party libraries
import pygame

# Auxiliary modules
from player import Player
from walls import Walls
from slice import Slice
from enemy import Enemy, BigEnemy, SmallEnemy, TutorialEnemy
from scoreboard import Scoreboard
from background import Background
from button import Button
from sprocket import Sprocket
import constants as c
import helpers as h

import urllib.request


tutorial_clicked = pygame.image.load(os.path.join(c.ASSETS_PATH, "tutorial_clicked.png"))
tutorial_unclicked = pygame.image.load(os.path.join(c.ASSETS_PATH, "tutorial_unclicked.png"))


class Game:

    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 2, 1024)
        pygame.init()
        self.music = pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "luminary.wav"))
        self.screen = pygame.display.set_mode(c.WINDOW_SIZE)
        pygame.display.set_caption(c.GAME_NAME)
        self.clock = pygame.time.Clock()
        self.name = "WWWW"
        self.max_score = None

        self.port_on_load = get_server_port()
        self.error_message = ""

        self.slowdown = 1.0
        self.effect_slow = 1.0
        self.since_effect = 1000
        self.since_shake = 1000
        self.shake_amp = 0
        self.shake_frequency = 9
        self.shake_offset = 0
        self.score_background = pygame.image.load(os.path.join(c.ASSETS_PATH, "score_background.png"))
        self.title_background = pygame.image.load(os.path.join(c.ASSETS_PATH, "title.png"))

        self.tear_sounds = [pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "tear1.wav")),
                            pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "tear2.wav")),
                            pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "tear3.wav")),
                            pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "tear4.wav"))]
        self.bad_tear_sounds = [pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "bad_tear1.wav")),
                                pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "bad_tear2.wav"))]
        self.explosion = pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "explosion.wav"))
        self.explosion.set_volume(0.8)
        self.dash = pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "dashing.wav"))
        self.dash.set_volume(0.4)
        for sound in self.tear_sounds + self.bad_tear_sounds:
            sound.set_volume(0.16)
        self.nope = pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "nope.wav"))
        self.nope.set_volume(0.3)
        self.fifths = pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "fifths.wav"))
        self.typing = pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "type.wav"))
        self.bounce = pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "bounce_wall.wav"))
        self.bounce.set_volume(0.13)
        self.reset_sound = pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "reset.wav"))
        self.reset_sound.set_volume(1.5)
        self.typing.set_volume(0.7)
        self.wings_charged = pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "wings_charged.wav"))
        self.wings_used = pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "wings_used.wav"))
        self.sus = pygame.mixer.Sound(os.path.join(c.ASSETS_PATH, "sus.wav"))
        self.retry_button = Button((c.MIDDLE_X, c.MIDDLE_Y + 50), "Retry", visible=False)
        self.submit_button = Button((c.MIDDLE_X, c.MIDDLE_Y + 100), "Submit", visible=False)
        self.buttons = [self.retry_button,
                        self.submit_button]

        self.name_input()
        self.screen.fill(c.BLACK)
        pygame.display.flip()
        start = time.time()
        while time.time() < start + 2:
            self.update_globals(0.01)
        self.music.play(-1)
        while True:
            self.title_sequence()
            result = 1
            while result == 1:
                result = self.main()

    def launch_factor_multiplier(self):
        if self.score() < 1000:
            return 1
        else:
            return min(10, (self.score() - 1000)/4000 + 1)

    def title_sequence(self):
        self.error_message = ""
        now = time.time()
        time.sleep(0.001)
        self.phase = c.TITLE
        play = Button((c.MIDDLE_X, c.MIDDLE_Y + 100), "Play", (1, 1))
        scoreboard = Button((c.MIDDLE_X, c.MIDDLE_Y + 155), "High scores", (1, 1))
        while True:
            dt = self.clock.tick(60)/1000
            dt, events = self.update_globals(dt)
            play.update(dt, events)
            scoreboard.update(dt, events)
            self.screen.blit(self.title_background, (0, 0))
            play.draw(self.screen)
            scoreboard.draw(self.screen)
            self.draw_error_text(self.screen)
            pygame.display.flip()
            if scoreboard.clicked:
                container = []
                self.get_sprocket(container)
                if len(container):
                    self.error_message = ""
                    self.score_phase(container[0])
                    scoreboard.font_size = 40
                    scoreboard.target_font_size = 40
                    scoreboard.scale = 1.0
                else:
                    self.error_message = "No internet connection"
            if play.clicked:
                break
        black = pygame.Surface(c.WINDOW_SIZE)
        black.fill(c.BLACK)
        black.set_alpha(0)
        start = time.time()
        while True:
            dt = self.clock.tick(60)/1000
            diff = time.time() - start
            dt, events = self.update_globals(dt)
            self.screen.blit(self.title_background, (0, 0))
            play.draw(self.screen)
            scoreboard.draw(self.screen)
            self.screen.blit(black, (0, 0))
            pygame.display.flip()

            black.set_alpha(min(255 * diff * 6, 255))
            if (255 * diff * 6) > 255:
                break


    def name_input(self):
        now = time.time()
        time.sleep(0.001)

        name_font = pygame.font.Font(os.path.join(c.ASSETS_PATH, "great_answer.ttf"), 70)
        prompt_font = pygame.font.Font(os.path.join(c.ASSETS_PATH, "great_answer.ttf"), 30)

        self.name = ""
        self.phase = c.NAME_PHASE
        continue_button = Button((c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT - 60), "continue", (5, 5), visible=False, true_scale = 0.65)
        while True:
            dt = self.clock.tick(60)/1000
            dt, events = self.update_globals(dt)
            continue_button.disabled = not len(self.name) > 0
            if self.name:
                continue_button.visible=True
            for word in c.PROFANITY:
                if word.upper() in self.name:
                    continue_button.disabled = True
            continue_button.update(dt, events)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and not continue_button.disabled:
                        continue_button.clicked = True

            self.screen.fill(c.BLACK)

            surf = prompt_font.render("Type your name", 1, (150, 150, 150))
            self.screen.blit(surf, (c.MIDDLE_X - surf.get_width()//2, c.MIDDLE_Y - 85))

            name_render = name_font.render(self.name, 1, c.WHITE)
            self.screen.blit(name_render,
                             (c.WINDOW_WIDTH//2 - name_render.get_width()//2,
                              c.WINDOW_HEIGHT//2 - name_render.get_height()//2))
            continue_button.draw(self.screen)

            if self.name and continue_button.clicked:
                break


            for event in events:
                if event.type == pygame.KEYDOWN:
                    k = pygame.key.name(event.key)
                    if k in "abcdefghijklmnopqrstuvwxyz1234567890":
                        self.name += k.capitalize()
                        if len(self.name) < 6:
                            self.typing.play()
                    if k.lower() == "backspace":
                        self.name = self.name[:-1]
            self.name = self.name[:5]
            pygame.display.flip()
        self.fifths.play()


    def tear_sound(self):
        random.choice(self.tear_sounds).play()
        self.explosion.play()

    def bad_tear_sound(self):
        random.choice(self.tear_sounds).play()

    def update_enemies(self, dt, events, n=10):
        while len(self.enemies) < n:
            if len(self.enemies) == 1:
                spacing = int(c.WINDOW_HEIGHT*0.85)
            else:
                spacing = (c.WINDOW_HEIGHT//4) * (self.enemies[-1].y + 20000)/20000 \
                          + random.random() * c.WINDOW_HEIGHT//3 \
                          - c.WINDOW_HEIGHT//8
            if spacing > c.WINDOW_HEIGHT*0.8:
                spacing = c.WINDOW_HEIGHT*0.8
            padding = 60
            x = random.random()*(self.walls.width - 2 * padding) \
                       + c.MIDDLE_X \
                       - (self.walls.width - 2 * padding)/2
            y = self.enemies[-1].y + spacing
            seed = random.random()
            if self.y_offset < 2000:
                if seed < 0.3:
                    new_enemy = Enemy
                elif seed < 0.7:
                    new_enemy = BigEnemy
                else:
                    new_enemy = SmallEnemy
            elif self.y_offset < 5000:
                if seed < 0.5:
                    new_enemy = Enemy
                elif seed < 0.7:
                    new_enemy = BigEnemy
                else:
                    new_enemy = SmallEnemy
            else:
                if seed < 0.7:
                    new_enemy = Enemy
                elif seed < 0.8:
                    new_enemy = BigEnemy
                else:
                    new_enemy = SmallEnemy
            self.enemies.append(new_enemy(self, x=x, y=y))

    def loading_text(self):
        dots = int(time.time()*2)%3 + 1
        return f"Connecting{'.' * dots}"

    def draw_tutorial(self, surface):
        if self.y_offset > c.WINDOW_HEIGHT or self.tutorial_offset > c.WINDOW_HEIGHT:
            return
        surf = tutorial_clicked if time.time()%1<0.5 else tutorial_unclicked
        surf = surf.copy().convert()
        surf.set_colorkey((255, 0, 255))
        surface.blit(surf, (c.MIDDLE_X - surf.get_width()//2 - 30,
                            c.WINDOW_HEIGHT - surf.get_height() - 60 + self.y_offset//2 + self.tutorial_offset))

    def draw_loading_text(self, surface):
        self.loading_font = pygame.font.Font(os.path.join(c.ASSETS_PATH, "gothland.ttf"), 20)
        w = self.loading_font.render("Connecting.", 1, c.WHITE).get_width()
        surf = self.loading_font.render(self.loading_text(), 1, c.WHITE)
        surface.blit(surf, (c.MIDDLE_X - w//2, c.WINDOW_HEIGHT - 30))

    def draw_error_text(self, surface):
        self.loading_font = pygame.font.Font(os.path.join(c.ASSETS_PATH, "gothland.ttf"), 20)
        surf = self.loading_font.render(self.error_message, 0, c.WHITE)
        if self.phase == c.GAME_PHASE:
            surf = surf.convert()
            surf.set_colorkey(c.BLACK)
            surf.set_alpha(255 - 155*self.aimingness)
        surface.blit(surf, (c.MIDDLE_X - surf.get_width()//2, c.WINDOW_HEIGHT - 30))

    def reset(self):
        self.y_offset = 0
        self.player = Player(self)
        self.walls = Walls(self)
        self.slice = Slice(self)
        self.enemies = [TutorialEnemy(self, y=c.WINDOW_HEIGHT/2, x=c.MIDDLE_X)]
        self.enemies[0].angle = 0
        self.update_enemies(0, [])
        self.particles = []
        self.text_particles = []
        self.background = Background(self)
        self.player.velocity = (100, 600)
        self.aiming = False
        self.aimingness = 0

        self.score_yoff = 50
        self.score_size = 40
        self.target_score_size = 40
        self.score_bumped = True

        self.shade = pygame.Surface(c.WINDOW_SIZE)
        self.shade.fill(c.BLACK)
        self.shade.set_alpha(0)

        self.shade_2 = pygame.Surface(c.WINDOW_SIZE)
        self.shade.fill(c.BLACK)
        self.shade_2.set_alpha(0)

        self.shade_3 = pygame.Surface(c.WINDOW_SIZE)
        self.shade.fill(c.BLACK)
        self.shade_3.set_alpha(255)

        self.flare = pygame.Surface(c.WINDOW_SIZE)
        self.flare.fill((255, 226, 140))
        self.flare.set_alpha(0)
        self.flare_alpha = 0

        self.multiplier = 1

        self.queue_reset = False

        self.game_end = False

        self.retry_button.visible = False
        self.submit_button.visible = False
        self.closing = False
        self.freeze_surf = None

        for button in self.buttons:
            button.disabled = False

        self.error_message = ""
        self.tutorial = True
        self.tutorial_offset = 0


    def update_tutorial(self, dt, events):
        if not self.tutorial:
            return
        if self.player.y > 150 and self.player.velocity[1] >= 0 or self.player.y > 60 and self.player.velocity[1] <= 0:
            self.aiming = True
            self.tutorial = False


    def update_effects(self, dt, events):
        if self.max_score is not None and self.score() > self.max_score:
            self.error_message = "NEW HIGH SCORE"
        self.music.set_volume(0.8 - 0.6 * self.aimingness)

        if self.player_is_dead():
            self.aiming = False
            self.tutorial_offset += dt * 750

        if self.queue_reset and self.player_is_dead():
            self.retry_button.visible = True
            self.submit_button.visible = True

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
                self.score_size = 120
                self.sus.play()
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
            self.score_yoff = min(self.score_yoff + dy*5*dt, c.MIDDLE_Y - 100)

    def score(self):
        if not self.phase == c.GAME_PHASE:
            return -1
        return int(self.y_offset//10)

    def draw_score(self):
        text = f"{self.score()}"
        self.score_font = pygame.font.Font(os.path.join(c.ASSETS_PATH, "no_continue.ttf"), int(self.score_size))
        surf = self.score_font.render(text, 0, c.WHITE)
        surf2 = self.score_font.render(text, 0, c.BLACK)
        x = c.MIDDLE_X - surf.get_width()//2
        y = self.score_yoff

        mpos = pygame.mouse.get_pos()
        padding = 35
        inner_padding = 12
        dx = max(x - mpos[0], mpos[0] - x - surf.get_width())
        dy = max(y - mpos[1], mpos[1] - y - surf.get_height())
        small_alpha = 80
        if dx < inner_padding and dy < inner_padding:
            if self.aiming:
                surf.set_alpha(small_alpha)
                surf2.set_alpha(small_alpha)
        elif dx < padding + inner_padding and dy < padding + inner_padding:
            diff = padding - (max(dx, dy) - inner_padding)
            if self.aiming:
                small_alpha = 255 - (255 - small_alpha)*(diff/padding)
                surf.set_alpha(small_alpha)
                surf2.set_alpha(small_alpha)

        self.screen.blit(surf2, (x, y+self.score_size//10))
        self.screen.blit(surf, (x, y))



    def slowdown_effect(self, duration = 0.4):
        self.since_effect = -duration

    def shake_effect(self, amplitude=20):
        if amplitude < self.shake_amp:
            return
        self.since_shake = 0
        self.shake_amp = max(amplitude, self.shake_amp)

    def update_offset(self, dt, events):
        max_off = c.WINDOW_HEIGHT*0.7
        if self.player.y > self.y_offset + max_off and type(self.enemies[0]) is not TutorialEnemy:
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
        self.reset()
        self.phase = c.GAME_PHASE

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
            # if since_print > 1.0:
            #     since_print = 0
            #     print(f"FPS: {sum(fpss)/len(fpss)}")

            # Do things
            dt, events = self.update_globals(rdt)
            self.update_tutorial(dt, events)
            if self.queue_reset:
                new_alpha = self.shade_2.get_alpha() + 500 * dt
                self.shade_2.set_alpha(min(new_alpha, 160))
            for button in self.buttons:
                button.update(rdt, events)
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
            if self.submit_button.clicked:
                self.freeze_surf = self.screen.copy()
            self.draw_score()
            for button in self.buttons:
                button.draw(self.screen)
            self.draw_error_text(self.screen)
            self.draw_tutorial(self.screen)
            if self.shade_3.get_alpha() > 0:
                self.screen.blit(self.shade_3, (0, 0))
            self.update_screen()

            # Other things?
            if self.submit_button.clicked:
                self.error_message = ""
                status = self.submit_score()
                for button in self.buttons:
                    button.disabled = False
                if status == c.SCORE_RECEIVED:
                    return 0
                elif status == c.NO_CONNECT:
                    self.submit_button.clicked = False
                    self.error_message = "No Internet connection"
                elif status == c.TIMEOUT:
                    self.submit_button.clicked = False
                    self.error_message = "Server timed out"
            if self.retry_button.clicked:
                self.retry_button.clicked = False
                self.closing = True
                self.reset_sound.play()
            if self.closing:
                new_alpha = self.shade_3.get_alpha() + 1000 * dt
                self.shade_3.set_alpha(min(new_alpha, 255))
                if self.shade_3.get_alpha() == 255:
                    return 1
            else:
                new_alpha = self.shade_3.get_alpha() - 1000 * dt
                self.shade_3.set_alpha(max(new_alpha, 0))

            self.clock.tick(c.MAX_FPS)

    def update_globals(self, dt):
        events = pygame.event.get()
        if self.phase == c.GAME_PHASE and self.player.y < self.y_offset - 100:
            self.player.test_wings()
        if self.phase == c.GAME_PHASE and self.player_is_dead():
            self.queue_reset = True
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONUP and self.phase == c.GAME_PHASE:
                if event.button == 1: # 1 is left click
                    self.player.dash_toward(self.mouse_position(), 300)
                    self.aiming = False
                    self.aimingness = 0
            if event.type == pygame.MOUSEBUTTONDOWN and self.phase == c.GAME_PHASE and not self.player.cutting and not self.queue_reset:
                if event.button == 1:
                    self.shade_target_alpha = 100
                    self.aiming = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.phase == c.GAME_PHASE:
                    self.queue_reset = True
                if event.key == pygame.K_f:
                    self.player.flying = not self.player.flying
        return dt * min(self.slowdown, self.effect_slow), events

    def update_screen(self):
        pygame.display.flip()

    def player_is_dead(self):
        return self.player.y < self.y_offset - 50 and not self.player.flying and not self.player.has_wings

    def get_sprocket(self, container):
        try:
            port = get_server_port()
            if not port:
                return
            sprocket = Sprocket(c.SERVER_ADDR, port)
            container.append(sprocket)
        except Exception as e:
            print(e)

    def submit_score(self):
        name = self.name
        container = []
        threading.Thread(target=self.get_sprocket, args=(container,), daemon=True).start()
        age = 0
        while not container:
            dt = self.clock.tick(60)/1000
            age += dt
            if age > c.TIMEOUT_TIME:
                return c.TIMEOUT
            if threading.active_count() == 1 and not container:
                return c.NO_CONNECT
            self.screen.blit(self.freeze_surf, (0, 0))
            self.draw_score()
            for button in self.buttons:
                button.disabled = True
                button.update(dt, [])
                button.draw(self.screen)
            self.draw_loading_text(self.screen)
            self.update_globals(dt)
            pygame.display.flip()
        sprocket = container[0]
        sprocket.send(type="push", score=self.score(), name=name)
        result = []
        age = 0
        do_break = False
        while not do_break:
            dt = self.clock.tick(60)/1000
            age += dt
            self.update_globals(dt)
            if age > c.TIMEOUT_TIME:
                return c.TIMEOUT
            result += sprocket.get()
            for packet in result:
                if packet.has("success") and packet.success:
                    do_break = True
        return self.score_phase(sprocket)

    def draw_scoreboard(self, surface, scoreboard):
        size = 30
        font = pygame.font.Font(os.path.join(c.ASSETS_PATH, "no_continue.ttf"), size)
        scores = scoreboard.data
        spacing = int(1.25*size)
        x = int(c.WINDOW_WIDTH*0.55)
        y = int(c.WINDOW_HEIGHT - (size*10 + (spacing-size)*9))//2 + 50
        green = (60, 210, 100)
        shadow_offset = 3
        self.max_score = scores[9].score
        for item in scores[:10]:
            if item.name == self.name and item.score == self.score():
                color = green
                green = c.WHITE
            else:
                color = c.WHITE
            name = item.name[:5]
            space = ""
            width = 225
            text = f"{name}:"
            surfb = font.render(text, 1, c.BLACK)
            surf = font.render(text, 1, color)
            surface.blit(surfb, (x, y+shadow_offset))
            surface.blit(surf, (x, y))
            surf2 = font.render(f"{item.score}", 1, color)
            surf2b = font.render(f"{item.score}", 1, c.BLACK)
            surface.blit(surf2b, (x + width - surf2.get_width(), y+shadow_offset))
            surface.blit(surf2, (x + width - surf2.get_width(), y))

            y += spacing

    def score_phase(self, sprocket):
        age = 0
        alpha = 255
        self.freeze_surf = self.screen.copy().convert()
        sprocket.send(type="print")
        result = []
        has_result = False
        while alpha > 0 or not has_result:
            dt = self.clock.tick(60)/1000
            age += dt
            self.screen.fill(c.BLACK)
            alpha = max(0, 255 - age*900)
            self.freeze_surf.set_alpha(alpha)
            self.screen.blit(self.freeze_surf, (0, 0))
            self.update_globals(dt)

            pygame.display.flip()

            result += sprocket.get()
            for packet in result:
                if packet.has("scores"):
                    scoreboard = packet.scores
                    has_result = True
        shade = pygame.Surface(c.WINDOW_SIZE)
        shade.fill(c.BLACK)
        shade.set_alpha(255)
        age = 0
        back_button = Button((140, c.WINDOW_HEIGHT - 100), "back", (50, 50), visible=True)
        buttons = [back_button]
        while True:
            dt = self.clock.tick(60)/1000
            age += dt
            _, events = self.update_globals(dt)
            for button in buttons:
                button.update(dt, events)

            shade.set_alpha(255 - min(255, age*900))
            self.screen.blit(self.score_background, (0, 0))
            self.draw_scoreboard(self.screen, scoreboard)
            for button in buttons:
                button.draw(self.screen)
            self.screen.blit(shade, (0, 0))
            pygame.display.flip()

            if back_button.clicked:
                return c.SCORE_RECEIVED

def get_server_port():
    try:
        file = urllib.request.urlopen(c.SERVER_PORT_ADDR)
        port = int(file.readlines()[0])
        return port
    except:
        return None

if __name__=="__main__":
    Game()