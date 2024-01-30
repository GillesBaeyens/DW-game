import pygame
import os
import random

pygame.display.set_caption("Budget Geometry Dash")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (11, 150, 191)

fps = 60
bg_x, fl_x = 0, 0

gravity = 0.5

BACKGROUND_IMAGE = pygame.image.load(os.path.join("assets", "background.png"))
BACKGROUND = pygame.transform.scale_by(BACKGROUND_IMAGE, 0.3)
FLOOR_IMAGE = pygame.image.load(os.path.join("assets", "floor.png"))
FLOOR = pygame.transform.scale_by(FLOOR_IMAGE, 0.5)
PLAYER_IMAGE = pygame.image.load(os.path.join("assets", "player.png"))
PLAYER = pygame.transform.scale(PLAYER_IMAGE, (80, 60))   # Scale the image to 70x70 pixels
OBSTACLE_IMAGE = pygame.image.load(os.path.join("assets", "obstacle.png"))
OBSTACLE = OBSTACLE_IMAGE

BACKGROUND_WIDTH = BACKGROUND.get_width()
FLOOR_WIDTH = FLOOR.get_width()
FLOOR_HEIGHT = FLOOR.get_height()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = OBSTACLE
        self.rect = self.image.get_rect()
        self.speed = [-4, 0]
        area = pygame.display.get_surface().get_rect()
        self.width, self.height = area.width, area.height
        self.rect.center = (900, random.randint(0, self.height))

    def update(self):
        rdm = random.randint(0, 1)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect = self.rect.move(self.speed)


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
        angle = -self.speed[1] * 5
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
        self.rect.bottom = clip(self.rect.bottom, 0, self.height)


def clip(val, minval, maxval):
    return min(max(val, minval), maxval)


class Main(object):
    def __init__(self):
        pygame.init()
        size = (self.width, self.height) = (800, 600)
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
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
            self.screen.blit(obstacle.image, obstacle.rect)
        pygame.display.update()

    def generate_obstacles(self):
        self.obstacles.append(Obstacle())
    def event_loop(self):
        player = self.player
        friction = 1
        clock = pygame.time.Clock()
        run = True
        counter = 0
        while run:
            clock.tick(fps)
            counter += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and player.speed[1] > -player.maxSpeed:
                        player.speed[1] = -player.maxSpeed

                elif event.type == pygame.KEYUP:
                    friction = 0.99
            player.speed = [friction * s for s in player.speed]
            player.speed[1] += gravity
            if counter == 60:
                self.generate_obstacles()
                counter = 0
            player.update()
            for obstacle in self.obstacles:
                obstacle.update()
            self.draw_window()

        pygame.quit()


if __name__ == "__main__":
    app = Main()
    app.event_loop()
