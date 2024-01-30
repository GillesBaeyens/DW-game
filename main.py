import pygame
import os
import random

pygame.display.set_caption("Budget Geometry Dash")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (11, 150, 191)

fps = 60
bg_x, fl_x = 0, 0
game_state = "menu"

gravity = 0.65

BACKGROUND_IMAGE = pygame.image.load(os.path.join("assets", "background.png"))
BACKGROUND = pygame.transform.scale_by(BACKGROUND_IMAGE, 7)
FLOOR_IMAGE = pygame.image.load(os.path.join("assets", "floor.png"))
FLOOR = pygame.transform.scale_by(FLOOR_IMAGE, (7, 2))
PLAYER_IMAGE = pygame.image.load(os.path.join("assets", "player.png"))
PLAYER = pygame.transform.scale_by(PLAYER_IMAGE, 2)   # Scale the image to 70x70 pixels
OBSTACLE_IMAGE = pygame.image.load(os.path.join("assets", "obstacle.png"))
OBSTACLE = pygame.transform.scale_by(OBSTACLE_IMAGE, (4, 6))

BACKGROUND_WIDTH = BACKGROUND.get_width()
FLOOR_WIDTH = FLOOR.get_width()
FLOOR_HEIGHT = FLOOR.get_height()


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

    def update(self):
        self.rect = self.image1.get_rect(center=self.rect.center)
        self.rect2 = self.image2.get_rect(center=self.rect2.center)
        self.rect = self.rect.move(self.speed)
        self.rect2 = self.rect2.move(self.speed)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = PLAYER
        self.rect = self.image.get_rect()
        self.maxSpeed = 12
        self.speed = [0, 0]
        area = pygame.display.get_surface().get_rect()
        self.width, self.height = area.width, area.height
        self.rect.center = (self.width / 2, self.height / 2)

    def update(self):
        angle = -self.speed[1] * 4
        if angle > 90:
            angle = 90
        elif angle < -90:
            angle = -90
        self.image = pygame.transform.rotate(PLAYER, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect = self.rect.move(self.speed)
        self.rect.left = clip(self.rect.left, 0, self.width)
        self.rect.right = clip(self.rect.right, 0, self.width)
        self.rect.top = clip(self.rect.top, 0, self.height)
        self.rect.bottom = clip(self.rect.bottom, 0, self.height - FLOOR_HEIGHT + 10)


def clip(val, minval, maxval):
    return min(max(val, minval), maxval)


class Main(object):
    def __init__(self):
        self.width, self.height = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
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
        pygame.display.update()

    def generate_obstacles(self):
        self.obstacles.append(Obstacle())
    def event_loop(self):
        player = self.player
        friction = 1
        clock = pygame.time.Clock()
        counter = 0
        while game_state == "play":
            clock.tick(fps)
            counter += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state = "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and player.speed[1] > -player.maxSpeed:
                        player.speed[1] = -player.maxSpeed
                elif event.type == pygame.KEYUP:
                    friction = 0.99

            for obstacle in self.obstacles:
                if player.rect.colliderect(obstacle.rect) or player.rect.colliderect(obstacle.rect2):
                    self.main_menu()
                    game_state = "menu"
            if player.rect.bottom >= self.height - FLOOR_HEIGHT:
                self.main_menu()
                game_state = "menu"

            player.speed = [friction * s for s in player.speed]
            player.speed[1] += gravity
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
                    game_state = "quit"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                        game_state = "play"
                        self.play()
                    if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        game_state = "quit"
            pygame.display.update()



if __name__ == "__main__":
    app = Main()
    app.event_loop()
