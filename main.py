import pygame
import os
import random
import pyaudio
import numpy as np
import json
from button import Button

pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN])
pygame.display.set_caption("Flippy bird")

WHITE = (255, 255, 255)

#  AUDIO BULLSHIT
CHUNK = 1024  # Number of frames per buffer
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Number of audio channels (1 for mono, 2 for stereo)
RATE = 44100  # Sample rate (samples per second)
rms_threshold = 60

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

#  LOAD HIGHSCORE
try:
    highscore = json.load(open("highscore.json"))["highscore"]
except FileNotFoundError:
    print("No highscore file found, creating one...")
    highscore = 0

fps = 60
bg_x, fl_x = 0, 0
game_state = "menu"
voice_control = False

gravity = 0.65
new_highscore = False

BACKGROUND_IMAGE = pygame.image.load(os.path.join("assets", "background.png"))
BACKGROUND = pygame.transform.scale_by(BACKGROUND_IMAGE, 4.5)
FLOOR_IMAGE = pygame.image.load(os.path.join("assets", "floor.png"))
FLOOR = pygame.transform.scale_by(FLOOR_IMAGE, (7, 2))
del BACKGROUND_IMAGE, FLOOR_IMAGE  # Delete all unneeded images

# Load player sprite images
choose_player = random.randint(0, 3)
PLAYER_IMAGE = pygame.image.load(os.path.join("assets", f"player1.{choose_player}.png"))
PLAYER_IMAGE2 = pygame.image.load(os.path.join("assets", f"player2.{choose_player}.png"))

PLAYER_IMAGE = pygame.transform.scale_by(PLAYER_IMAGE, 4)  # Scale the image to 70x70 pixels
PLAYER_IMAGE2 = pygame.transform.scale_by(PLAYER_IMAGE2, 4)

PLAYER_IMAGES = [PLAYER_IMAGE, PLAYER_IMAGE2]  # Save images in an array to animate with
del PLAYER_IMAGE, PLAYER_IMAGE2  # Delete all unneeded images

OBSTACLE_IMAGE = pygame.image.load(os.path.join("assets", "obstacle.png"))
OBSTACLE = pygame.transform.scale_by(OBSTACLE_IMAGE, (4, 6))
del OBSTACLE_IMAGE

BACKGROUND_WIDTH = BACKGROUND.get_width()
FLOOR_WIDTH = FLOOR.get_width()
FLOOR_HEIGHT = FLOOR.get_height()

flap = pygame.mixer.Sound("assets/sounds/flap.wav")
hit = pygame.mixer.Sound("assets/sounds/hit.wav")
point = pygame.mixer.Sound("assets/sounds/pointSound.wav")
start = pygame.mixer.Sound("assets/sounds/start.wav")

flap.set_volume(0.5)
hit.set_volume(0.5)
point.set_volume(0.4)
start.set_volume(0.5)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image1 = OBSTACLE
        self.image2 = pygame.transform.rotate(OBSTACLE, 180)
        self.rect = self.image1.get_rect()
        self.rect2 = self.image2.get_rect()
        self.speed = [-4, 0]
        area = pygame.display.get_surface().get_rect()
        width, height = area.width, area.height
        self.rect.x = 2000
        self.rect2.x = 2000
        if voice_control:
            self.rect.y = random.randint(300, height - 300)
            self.rect2.bottom = self.rect.top - 250
        else:
            self.rect.y = random.randint(200, height - 200)
            self.rect2.bottom = self.rect.top - 200
        self.canScore = True

    def update(self):
        self.rect = self.image1.get_rect(center=self.rect.center)
        self.rect2 = self.image2.get_rect(center=self.rect2.center)
        self.rect = self.rect.move(self.speed)
        self.rect2 = self.rect2.move(self.speed)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.animation_time = 0
        self.current_sprite = 0
        self.image = PLAYER_IMAGES[self.current_sprite]
        self.rect = self.image.get_rect()
        self.maxSpeed = 12
        self.speed = [0, 0]
        area = pygame.display.get_surface().get_rect()
        self.width, self.height = area.width, area.height
        self.rect.center = (self.width / 2, self.height / 2)

    def update(self):
        self.animation_time += 1
        if self.animation_time == 10:
            self.current_sprite += 1
            self.animation_time = 0
        if self.current_sprite >= len(PLAYER_IMAGES):
            self.current_sprite = 0
        angle = -self.speed[1] * 4
        if angle > 90:
            angle = 90
        elif angle < -90:
            angle = -90
        self.image = pygame.transform.rotate(PLAYER_IMAGES[self.current_sprite], angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect = self.rect.move(self.speed)
        self.rect.left = clip(self.rect.left, 0, self.width)
        self.rect.right = clip(self.rect.right, 0, self.width)
        self.rect.top = clip(self.rect.top, 0, self.height)
        self.rect.bottom = clip(self.rect.bottom, 0, self.height - FLOOR_HEIGHT + 10)


def clip(val, minval, maxval):
    return min(max(val, minval), maxval)


def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)


def quit_game():
    json.dump({"highscore": highscore}, open("highscore.json", "w"))

    pygame.quit()
    quit()


class Main(object):
    def __init__(self):
        self.score = 0
        self.width, self.height = 1280, 720
        self.screen = pygame.display.set_mode((1280, 720))
        self.player = Player()
        self.obstacle = Obstacle()
        self.obstacles = []
        self.screen.blit(self.player.image, (self.width / 2, self.height / 2))
        self.background()
        self.clock = pygame.time.Clock()

    def background(self):
        global bg_x
        bg_speed = 0.5
        bg_x -= bg_speed
        if bg_x <= -BACKGROUND_WIDTH:
            bg_x = 0
        self.screen.blit(BACKGROUND, (bg_x, 0))
        self.screen.blit(BACKGROUND, (bg_x + BACKGROUND_WIDTH, 0))

    def floor(self):
        global fl_x
        fl_speed = 3
        fl_x -= fl_speed
        if fl_x <= -FLOOR_WIDTH:
            fl_x = 0
        self.screen.blit(FLOOR, (fl_x, self.height - FLOOR_HEIGHT))
        self.screen.blit(FLOOR, (fl_x + FLOOR_WIDTH, self.height - FLOOR_HEIGHT))

    def draw_window(self):
        self.background()
        self.floor()

        self.screen.blit(self.player.image, self.player.rect)

        for obstacle in self.obstacles:
            self.screen.blit(obstacle.image1, obstacle.rect)
            self.screen.blit(obstacle.image2, obstacle.rect2)

        score_text = get_font(30).render("Score: {}".format(self.score), True, WHITE)
        fps_text = get_font(30).render("FPS: {}".format(int(self.clock.get_fps())), True, WHITE)

        self.screen.blit(fps_text, (10, 40))
        self.screen.blit(score_text, (10, 10))

        pygame.display.update()

    def generate_obstacles(self):
        self.obstacles.append(Obstacle())

    def pre_game(self):
        global game_state, bg_x, voice_control, rms_threshold
        while game_state == "pre_game":
            self.screen.blit(BACKGROUND, (0, 0))

            # Reset player and background
            self.player = Player()
            bg_x = 0

            for obstacle in self.obstacles:
                self.obstacles.remove(obstacle)

            if voice_control:
                jump_to_start_text = get_font(100).render("TALK TO START", True, "#d9243c")
            else:
                jump_to_start_text = get_font(100).render("JUMP TO START", True, "#d9243c")
            jump_to_start_rect = jump_to_start_text.get_rect(center=(self.width / 2, self.height / 2 - 200))

            self.screen.blit(jump_to_start_text, jump_to_start_rect)
            self.screen.blit(self.player.image, self.player.rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()

                if not voice_control:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                            game_state = "play"
                            self.player.speed[1] = -self.player.maxSpeed
                            self.play()

            if voice_control:
                data = stream.read(CHUNK)
                audio_signal = np.frombuffer(data, dtype=np.int16)

                # Calculate RMS (Root Mean Square) as an estimate of loudness
                rms = np.sqrt(abs(np.mean(np.square(audio_signal))))

                if rms > rms_threshold:
                    start.play()
                    game_state = "play"
                    self.play()

            self.player.update()
            pygame.display.update()

        del self

    def game_over(self):
        global game_state, highscore, new_highscore
        while game_state == "game_over":
            if self.score > highscore:
                new_highscore = True
                highscore = self.score

            menu_mouse_pos = pygame.mouse.get_pos()

            game_over_text = get_font(100).render("GAME OVER", True, "#d9243c")
            game_over_rect = game_over_text.get_rect(center=(self.width / 2, self.height / 2 - 200))

            restart_button = Button(image=None, pos=(self.width / 2, self.height / 2),
                                    text_input="RESTART", font=get_font(75), base_color="#d7fcd4",
                                    hovering_color="White")
            menu_button = Button(image=None, pos=(self.width / 2, self.height / 2 + 100),
                                 text_input="MAIN MENU", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

            if new_highscore:
                highscore_text = get_font(50).render("NEW HIGHSCORE: {}".format(highscore), True, "#d9243c")
            else:
                highscore_text = get_font(50).render("Highscore: {}".format(highscore), True, WHITE)
            highscore_rect = highscore_text.get_rect(center=(self.width / 2, self.height / 2 + 200))

            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(highscore_text, highscore_rect)

            for button in [restart_button, menu_button]:
                button.changeColor(menu_mouse_pos)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.checkForInput(menu_mouse_pos):
                        game_state = "pre_game"
                        self.pre_game()
                    if menu_button.checkForInput(menu_mouse_pos):
                        game_state = "menu"
                        self.main_menu()

            self.player.update()
            pygame.display.update()
        del self

    def play(self):
        global game_state, voice_control, rms_threshold
        player = self.player
        friction = 1
        counter = 0
        self.score = 0
        while game_state == "play":
            self.clock.tick(fps)
            counter += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()

                if not voice_control:
                    if event.type == pygame.KEYDOWN:
                        if (event.key == pygame.K_UP or event.key == pygame.K_SPACE
                                and player.speed[1] > -player.maxSpeed):
                            flap.play()
                            player.speed[1] = -12
                        elif event.type == pygame.KEYUP:
                            friction = 0.99

            if voice_control:
                data = stream.read(CHUNK)
                audio_signal = np.frombuffer(data, dtype=np.int16)

                # Calculate RMS (Root Mean Square) as an estimate of loudness
                rms = np.sqrt(abs(np.mean(np.square(audio_signal))))

                if rms > rms_threshold and player.speed[1] > -player.maxSpeed:
                    flap.play()
                    player.speed[1] = -12

            for obstacle in self.obstacles:
                if player.rect.colliderect(obstacle.rect) or player.rect.colliderect(obstacle.rect2):
                    game_state = "game_over"
                    hit.play()
                    self.game_over()

            if player.rect.bottom >= self.height - FLOOR_HEIGHT:
                game_state = "game_over"
                hit.play()
                self.game_over()

            player.speed = [friction * s for s in player.speed]
            player.speed[1] += gravity

            for obstacle in self.obstacles:
                if obstacle.canScore and obstacle.rect.right < player.rect.left:
                    obstacle.canScore = False
                    self.score += 1
                    point.play()

            if counter == 120:
                self.generate_obstacles()
                counter = 0

            for obstacle in self.obstacles:
                obstacle.update()

            player.update()
            self.draw_window()

    def main_menu(self):
        global game_state, voice_control
        while game_state == "menu":
            self.screen.blit(BACKGROUND, (0, 0))

            menu_mouse_pos = pygame.mouse.get_pos()

            menu_text = get_font(100).render("MAIN MENU", True, "#b68f40")
            menu_rect = menu_text.get_rect(center=(self.width / 2, self.height / 2 - 200))

            play_button = Button(image=None, pos=(self.width / 2, self.height / 2),
                                          text_input="PLAY", font=get_font(75), base_color="#d7fcd4",
                                          hovering_color="White")
            if voice_control:
                voice_button = Button(image=None, pos=(self.width / 2, self.height / 2 + 100),
                                      text_input="VOICE CONTROLS: ON", font=get_font(75), base_color="#d7fcd4",
                                      hovering_color="White")
            else:
                voice_button = Button(image=None, pos=(self.width / 2, self.height / 2 + 100),
                                      text_input="VOICE CONTROLS: OFF", font=get_font(75), base_color="#d7fcd4",
                                      hovering_color="White")
            quit_button = Button(image=None, pos=(self.width / 2, self.height / 2 + 200),
                                 text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

            self.screen.blit(menu_text, menu_rect)

            for button in [play_button, voice_button, quit_button]:
                button.changeColor(menu_mouse_pos)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.checkForInput(menu_mouse_pos):
                        start.play()
                        game_state = "pre_game"
                        self.pre_game()

                    if voice_button.checkForInput(menu_mouse_pos):
                        if voice_control:
                            voice_control = False
                        else:
                            voice_control = True

                    if quit_button.checkForInput(menu_mouse_pos):
                        quit_game()

            pygame.display.update()
        del self


if __name__ == "__main__":
    app = Main()
    app.main_menu()
