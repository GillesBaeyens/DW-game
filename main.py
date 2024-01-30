import pygame
import os
import random
from button import Button

pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.init()
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN])
pygame.display.set_caption("Flippy bird")

WHITE = (255, 255, 255)

fps = 60
bg_x, fl_x = 0, 0
game_state = "menu"

gravity = 0.65

BACKGROUND_IMAGE = pygame.image.load(os.path.join("assets", "background.png"))
BACKGROUND = pygame.transform.scale_by(BACKGROUND_IMAGE, 4.5)
FLOOR_IMAGE = pygame.image.load(os.path.join("assets", "floor.png"))
FLOOR = pygame.transform.scale_by(FLOOR_IMAGE, (7, 2))
del BACKGROUND_IMAGE, FLOOR_IMAGE  # Delete all unneeded images

# Load player sprite images
choose_player = random.randint(0, 3)
PLAYER_IMAGE = pygame.image.load(os.path.join("assets", f"player1.{choose_player}.png"))
PLAYER_IMAGE2 = pygame.image.load(os.path.join("assets", f"player2.{choose_player}.png"))

PLAYER_IMAGE = pygame.transform.scale_by(PLAYER_IMAGE, 4)   # Scale the image to 70x70 pixels
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

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image1 = OBSTACLE
        self.image2 = pygame.transform.rotate(OBSTACLE, 180)
        self.rect = self.image1.get_rect()
        self.rect2 = self.image2.get_rect()
        self.speed = [-4, 0]
        area = pygame.display.get_surface().get_rect()
        self.width, self.height = area.width, area.height
        self.rect.x = 2000
        self.rect2.x = 2000
        self.rect.y = random.randint(200, self.height - 200)
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
        self.setup_background()

    def setup_background(self):
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
        self.setup_background()
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
        global game_state
        while game_state == "pre_game":
            self.screen.blit(BACKGROUND, (0, 0))

            self.player = Player()

            for obstacle in self.obstacles:
                self.obstacles.remove(obstacle)

            JUMP_TO_START_TEXT = get_font(150).render("JUMP TO START", True, "#ffffff")

            JUMP_TO_START_RECT = JUMP_TO_START_TEXT.get_rect(center=(self.width / 2, self.height / 2 - 200))

            self.screen.blit(JUMP_TO_START_TEXT, JUMP_TO_START_RECT)
            self.screen.blit(self.player.image, self.player.rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                        game_state = "play"
                        self.player.speed[1] = -self.player.maxSpeed
                        self.play()

            self.player.update()
            pygame.display.update()
        del self

    def game_over(self):
        global game_state
        while game_state == "game_over":

            MENU_MOUSE_POS = pygame.mouse.get_pos()

            GAME_OVER_TEXT = get_font(100).render("GAME OVER", True, "#d9243c")
            GAME_OVER_RECT = GAME_OVER_TEXT.get_rect(center=(self.width / 2, self.height / 2 - 200))

            RESTART_BUTTON = Button(image=None, pos=(self.width / 2, self.height / 2),
                                    text_input="RESTART", font=get_font(75), base_color="#d7fcd4",
                                    hovering_color="White")
            QUIT_BUTTON = Button(image=None, pos=(self.width / 2, self.height / 2 + 100),
                                 text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

            self.screen.blit(GAME_OVER_TEXT, GAME_OVER_RECT)

            for button in [RESTART_BUTTON, QUIT_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if RESTART_BUTTON.checkForInput(MENU_MOUSE_POS):
                        game_state = "pre_game"
                        self.pre_game()
                    if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        quit_game()

            self.player.update()
            pygame.display.update()
        del self

    def play(self):
        global game_state
        player = self.player
        friction = 1
        self.clock = pygame.time.Clock()
        counter = 0
        self.score = 0
        while game_state == "play":
            self.clock.tick(fps)
            counter += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state = "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_SPACE and player.speed[1] > -player.maxSpeed:
                        player.speed[1] = -player.maxSpeed
                        flap.play()
                elif event.type == pygame.KEYUP:
                    friction = 0.99

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
            player.update()
            for obstacle in self.obstacles:
                obstacle.update()
            self.draw_window()

    def main_menu(self):
        global game_state
        while game_state == "menu":
            self.screen.blit(BACKGROUND, (0, 0))

            MENU_MOUSE_POS = pygame.mouse.get_pos()

            MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")

            MENU_RECT = MENU_TEXT.get_rect(center=(self.width / 2, self.height / 2 - 200))

            PLAY_BUTTON = Button(image=None, pos=(self.width / 2, self.height / 2),
                                 text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
            QUIT_BUTTON = Button(image=None, pos=(self.width / 2, self.height / 2 + 100),
                                 text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

            self.screen.blit(MENU_TEXT, MENU_RECT)

            for button in [PLAY_BUTTON, QUIT_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                        game_state = "pre_game"
                        self.pre_game()
                    if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        quit_game()
            pygame.display.update()
        del self

if __name__ == "__main__":
    app = Main()
    app.main_menu()
