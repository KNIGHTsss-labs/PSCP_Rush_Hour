import pygame
import random

""" Basic Settings """
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 120

""" Colors """
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

""" Graphics Stuff """
icon_image = pygame.image.load("PSCP_Rush_Hour/Graphics/cats.jpg")
terrain_image = "PSCP_Rush_Hour/Graphics/floor.jpg"
player_image = "PSCP_Rush_Hour/Graphics/amongus.png"
roof_image = "PSCP_Rush_Hour/Graphics/roof.jpg"
obstacle_images_paths = [
    "PSCP_Rush_Hour/Graphics/cats.jpg",
    "PSCP_Rush_Hour/Graphics/cats.jpg",  # top-half hitbox
    "PSCP_Rush_Hour/Graphics/cats.jpg",
    "PSCP_Rush_Hour/Graphics/cats.jpg",  # hanging
    "PSCP_Rush_Hour/Graphics/cats.jpg"
]

pygame.init()

""" Screen Settings """
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
font = pygame.font.Font(None, 60)
pygame.display.set_icon(icon_image)
pygame.display.set_caption("PSCP Rush Hour")
clock = pygame.time.Clock()

""" Obstacle Pre-Set Settings """
num_obstacles = 5
obstacle_images = []
for path in obstacle_images_paths :
    image = pygame.image.load(path).convert_alpha()
    scaled_versions = {
        "small" : pygame.transform.scale(image, (80, 80)),
        "medium" : pygame.transform.scale(image, (70, 120)),
        "wide" : pygame.transform.scale(image, (120, 70))
    }
    obstacle_images.append(scaled_versions)

class Player :
    def __init__(self, image_path, x, y) :
        """ Player Settings """
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image_normal = pygame.transform.scale(self.original_image, (100, 100))
        self.sliding_height = 50
        self.image_slide = pygame.transform.scale(self.original_image, (100, self.sliding_height))
        self.start_x, self.start_y = x, y
        self.obstacle = self.image_normal.get_rect(midbottom=(x, y))
        self.normal_height = self.obstacle.height
        self.velocity = 0
        self.gravity = 2500
        self.jump_strength = -1000
        self.on_ground = True
        self.falling = False
        self.collision = False
        self.sliding = False

    def handle_input(self, keys) :
        """ Input Receiver """
        global game_started
        if not game_over :
            if keys[pygame.K_SPACE] and self.on_ground and not self.sliding :
                self.velocity = self.jump_strength
                self.on_ground = False
                game_started = True

            if keys[pygame.K_s] or keys[pygame.K_DOWN] :
                if not self.sliding and self.on_ground :
                    self.sliding = True
                    self.obstacle.height = self.sliding_height
                    self.obstacle.bottom = base.terrain.top
            else :
                if self.sliding :
                    self.sliding = False
                    self.obstacle.height = self.normal_height
                    self.obstacle.bottom = base.terrain.top

    def apply_gravity(self, floor, dt) :
        """ Jumping physics """
        self.velocity += self.gravity * dt
        self.obstacle.y += self.velocity * dt

        if not self.falling :
            if self.obstacle.bottom >= floor.top :
                self.obstacle.bottom = floor.top
                self.velocity = 0
                self.on_ground = True

        if self.collision :
            self.velocity = -1000
            self.collision = False
            self.falling = True

        if self.obstacle.top > SCREEN_HEIGHT :
            self.velocity = 0

    def reset(self) :
        """ Reset player """
        self.obstacle.midbottom = (self.start_x, self.start_y)
        self.velocity = 0
        self.on_ground = True
        self.falling = False
        self.collision = False
        self.sliding = False

    def create(self, surface) :
        """ Draw player """
        surface.blit(self.image_slide if self.sliding else self.image_normal, self.obstacle)

class Obstacle :
    def __init__(self, x, terrain_top) :
        """ Obstacle Settings """
        self.type = random.randint(0, 4)
        self.hanging = self.type == 2
        self.top_half_hitbox = self.type == 1
        self.speed = 600
        self.active = True
        self.reset(x, terrain_top)

    def reset(self, x, terrain_top) :
        """ Reset Obstacle """
        if self.type in [0, 1, 2] :
            self.width, self.height = 70, 120
            self.image = obstacle_images[self.type]["medium"]
        elif self.type == 3 :
            self.width, self.height = 120, 70
            self.image = obstacle_images[self.type]["wide"]
        else :
            self.width, self.height = 80, 80
            self.image = obstacle_images[self.type]["small"]

        if self.hanging :
            self.obstacle = self.image.get_rect(midtop=(x, above.roof.bottom))
        else :
            self.obstacle = self.image.get_rect(midbottom=(x, terrain_top))

    def move(self, dt) :
        """ Move Obstacle """
        if not game_over and self.active and game_started :
            self.obstacle.x -= self.speed * dt

        if self.obstacle.right < 0 :
            self.type = random.randint(0, 4)
            self.hanging = self.type == 2
            self.top_half_hitbox = self.type == 1
            max_x = max(obs.obstacle.right for obs in obstacles)
            new_x = max(SCREEN_WIDTH, max_x) + random.randint(400, 700)
            self.reset(new_x, base.terrain.top)

    def create(self, surface) :
        """ Draw Obstacle """
        surface.blit(self.image, self.obstacle)

    def hitbox(self) :
        """ Obstacle Hitbox """
        if self.top_half_hitbox :
            return pygame.Rect(self.obstacle.x, self.obstacle.y, self.obstacle.width, self.obstacle.height // 2)
        return self.obstacle

class Roof :
    def __init__(self, image_path, x, y) :
        """ Roof Settings """
        original_image = pygame.image.load(image_path).convert_alpha()
        self.texture = pygame.transform.scale(original_image, (SCREEN_WIDTH // 4, 200))
        self.roof = self.texture.get_rect(topleft=(x, y))

    def create(self, surface) :
        surface.blit(self.texture, self.roof)

class Terrain :
    def __init__(self, image_path, x, y) :
        """ Terrain Settings """
        original_image = pygame.image.load(image_path).convert_alpha()
        self.texture = pygame.transform.scale(original_image, (SCREEN_WIDTH * 3, SCREEN_HEIGHT - y))
        self.terrain = self.texture.get_rect(topleft=(x, y))

    def create(self, surface) :
        surface.blit(self.texture, self.terrain)

""" Game Settings """
above = Roof(roof_image, 100, 0)
base = Terrain(terrain_image, -1000, 575)
player = Player(player_image, 100, base.terrain.top)
game_over = False
game_started = False
score = 0

obstacles = []
x = 1100
for _ in range(num_obstacles) :
    obstacles.append(Obstacle(x, base.terrain.top))
    x += random.randint(400, 700)

def reset_game() :
    """ Reset all game stats """
    global game_over, game_started, score
    player.reset()
    x = 1100
    for obs in obstacles :
        obs.type = random.randint(0, 4)
        obs.hanging = obs.type == 2
        obs.top_half_hitbox = obs.type == 1
        obs.reset(x, base.terrain.top)
        obs.active = True
        x += random.randint(400, 700)
    random.shuffle(obstacles)
    game_over = False
    game_started = False
    score = 0

""" Main Attraction """
running = True
while running :
    dt = clock.tick(FPS) / 1000
    keys = pygame.key.get_pressed()

    for event in pygame.event.get() :
        if event.type == pygame.QUIT :
            running = False

    if game_started and not game_over :
        score += dt * 100

    if game_over and keys[pygame.K_ESCAPE] :
        reset_game()

    player.handle_input(keys)
    player.apply_gravity(base.terrain, dt)

    screen.fill(WHITE)
    above.create(screen)
    base.create(screen)
    player.create(screen)

    for obs in obstacles :
        if obs.obstacle.right > 0 :
            obs.move(dt)
            obs.create(screen)

            if player.obstacle.colliderect(obs.hitbox()) and not game_over :
                game_over = True
                for ob in obstacles :
                    ob.active = False
                player.collision = True

    score_text = font.render(f"Score  : {str(int(score)).zfill(5)}", True, BLACK)
    screen.blit(score_text, (1050, 50))

    pygame.display.flip()

pygame.quit()
