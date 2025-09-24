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
    "PSCP_Rush_Hour/Graphics/obstacle.jpg",  # top-half hitbox
    "PSCP_Rush_Hour/Graphics/cats.jpg",
    "PSCP_Rush_Hour/Graphics/cats.jpg",  # hanging
    "PSCP_Rush_Hour/Graphics/cats.jpg"
]

# NEW: optional graphics for gun and bullet (fallback handled later)
gun_image_path = "PSCP_Rush_Hour/Graphics/gun.jpg"
bullet_image_path = "PSCP_Rush_Hour/Graphics/fireball.png"

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
        "small" : pygame.transform.scale(image, (100, 100)),
        "medium" : pygame.transform.scale(image, (100, 160)),
        "wide" : pygame.transform.scale(image, (175, 125)),
        "hanging" :pygame.transform.scale(image, (125, 330))
    }
    obstacle_images.append(scaled_versions)

class Player :
    def __init__(self, image_path, x, y) :
        """ Player Settings """
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image_normal = pygame.transform.scale(self.original_image, (100, 200))
        self.sliding_height = 80
        self.image_slide = pygame.transform.scale(self.original_image, (175, self.sliding_height))
        self.start_x, self.start_y = x, y
        self.obstacle = self.image_normal.get_rect(midbottom=(x, y))
        self.normal_height = self.obstacle.height
        self.velocity = 0
        self.gravity = 2500
        self.jump_strength = -1100
        self.on_ground = True
        self.falling = False
        self.collision = False
        self.sliding = False

        # NEW: gun state
        self.has_gun = False
        self.fire_cooldown = 0.0   # seconds remaining until next shot allowed
        self.fire_rate = 0.25      # seconds between shots
        # optional: show ammo count later

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

            # NEW: shooting input (K_f)
            if self.has_gun and keys[pygame.K_f] and self.fire_cooldown <= 0 and not game_over:
                # spawn a bullet
                bx = self.obstacle.right + 10
                by = self.obstacle.centery
                bullets.append(Bullet(bx, by))
                self.fire_cooldown = self.fire_rate

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
            self.velocity = -1200
            self.collision = False
            self.falling = True

        if self.obstacle.top > SCREEN_HEIGHT :
            self.velocity = 0

        # NEW: cooldown update
        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt
            if self.fire_cooldown < 0:
                self.fire_cooldown = 0

    def pickup_gun(self) :
        self.has_gun = True

    def reset(self) :
        """ Reset player """
        self.obstacle.midbottom = (self.start_x, self.start_y)
        self.velocity = 0
        self.on_ground = True
        self.falling = False
        self.collision = False
        self.sliding = False
        # reset gun
        self.has_gun = False
        self.fire_cooldown = 0

    def create(self, surface) :
        """ Draw player """
        surface.blit(self.image_slide if self.sliding else self.image_normal, self.obstacle)
        # Optional: draw a small gun icon above player when has_gun
        if self.has_gun:
            # draw a small rectangle or icon to indicate gun
            try:
                g_img = pygame.transform.scale(gun_image, (40, 20))
                g_rect = g_img.get_rect(midbottom=(self.obstacle.centerx, self.obstacle.top - 10))
                surface.blit(g_img, g_rect)
            except Exception:
                # fallback simple rect
                rect = pygame.Rect(0,0,40,10)
                rect.midbottom = (self.obstacle.centerx, self.obstacle.top - 10)
                pygame.draw.rect(surface, BLACK, rect)

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
        if self.type in [0, 1] :
            self.width, self.height = 100, 160
            self.image = obstacle_images[self.type]["medium"]
        elif self.type == 3 :
            self.width, self.height = 175, 125
            self.image = obstacle_images[self.type]["wide"]
        elif self.type == 2 :
            self.width, self.height = 100, 330
            self.image = obstacle_images[self.type]["hanging"]
        else :
            self.width, self.height = 100, 100
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
            new_x = max(SCREEN_WIDTH, max_x) + random.randint(550, 700)
            self.reset(new_x, base.terrain.top)

    def create(self, surface) :
        """ Draw Obstacle """
        if self.active:
            surface.blit(self.image, self.obstacle)

    def hitbox(self) :
        """ Obstacle Hitbox """
        if self.top_half_hitbox :
            return pygame.Rect(self.obstacle.x, self.obstacle.y, self.obstacle.width, self.obstacle.height // 2)
        return self.obstacle

# NEW: Bullet class
class Bullet:
    def __init__(self, x, y):
        self.speed = 1300   # pixels per second
        self.image = None
        # try load image, fallback to simple rect
        try:
            img = pygame.image.load(bullet_image_path).convert_alpha()
            self.image = pygame.transform.scale(img, (20, 20))
            self.rect = self.image.get_rect(center=(x, y))
        except Exception:
            self.image = None
            self.rect = pygame.Rect(0,0,12,6)
            self.rect.center = (x, y)

        self.active = True

    def move(self, dt):
        if not game_over:
            self.rect.x += int(self.speed * dt)
        if self.rect.left > SCREEN_WIDTH + 50:
            self.active = False

    def create(self, surface):
        if self.image:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surface, BLACK, self.rect)

# NEW: Gun pickup item
class GunPickup:
    def __init__(self, x, terrain_top):
        self.speed = 600
        self.active = True
        self.width = 50
        self.height = 30
        self.x = x
        self.y = terrain_top - 100  # float a bit above ground
        # try load image:
        try:
            img = pygame.image.load(gun_image_path).convert_alpha()
            self.image = pygame.transform.scale(img, (50, 30))
            self.rect = self.image.get_rect(center=(x, self.y))
        except Exception:
            self.image = None
            self.rect = pygame.Rect(0,0,self.width,self.height)
            self.rect.center = (x, self.y)

    def move(self, dt):
        if not game_over and self.active and game_started:
            self.rect.x -= int(self.speed * dt)
        if self.rect.right < 0:
            # respawn to right side
            max_x = max([o.obstacle.right for o in obstacles] + [SCREEN_WIDTH])
            new_x = max(SCREEN_WIDTH, max_x) + random.randint(800, 1200)
            self.reset(new_x, base.terrain.top)

    def reset(self, x, terrain_top):
        self.rect.center = (x, terrain_top - 100)
        self.active = True

    def create(self, surface):
        if self.active:
            if self.image:
                surface.blit(self.image, self.rect)
            else:
                pygame.draw.rect(surface, (200,50,50), self.rect)

class Roof :
    def __init__(self, image_path, x, y) :
        """ Roof Settings """
        original_image = pygame.image.load(image_path).convert_alpha()
        self.texture = pygame.transform.scale(original_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.roof = self.texture.get_rect(topleft=(x, y))

    def create(self, surface) :
        surface.blit(self.texture, self.roof)

class Terrain :
    def __init__(self, image_path, x, y) :
        """ Terrain Settings """
        original_image = pygame.image.load(image_path).convert_alpha()
        self.texture = pygame.transform.scale(original_image, (SCREEN_WIDTH * 2, SCREEN_HEIGHT))
        self.terrain = self.texture.get_rect(topleft=(x, y))
        self.active = True
        self.speed = 600
 
    def move(self, dt) :
        """ Move Terrain """
        if not game_over and self.active and game_started :
            self.terrain.x -= self.speed * dt

        if self.terrain.right < SCREEN_WIDTH // 2 :
            self.reset(SCREEN_WIDTH, 650)

    def reset(self, x, terrain_topright) :
        self.terrain = self.texture.get_rect(topleft=(x, terrain_topright))

    def create(self, surface) :
        surface.blit(self.texture, self.terrain)

""" Game Settings """
above = Roof(roof_image, 0, -675)
base = Terrain(terrain_image, 0, 650)
player = Player(player_image, 100, base.terrain.top)
game_over = False
game_started = False
score = 0

obstacles = []
x = 1100
for _ in range(num_obstacles) :
    obstacles.append(Obstacle(x, base.terrain.top))
    x += random.randint(550, 700)

# NEW: bullets list and gun pickups
bullets = []
gun_pickups = []
# spawn one initial gun pickup a bit after obstacles
gun_spawn_x = SCREEN_WIDTH + 1400
gun_pickups.append(GunPickup(gun_spawn_x, base.terrain.top))

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
        x += random.randint(550, 700)
    base.active = True
    random.shuffle(obstacles)
    # reset pickups & bullets
    bullets.clear()
    for i, gp in enumerate(gun_pickups):
        gp.reset(SCREEN_WIDTH + 800 + i * 600, base.terrain.top)
    game_over = False
    game_started = False
    score = 0

""" Main Attraction """
running = True
# Try load gun and bullet asset (optional)
try:
    gun_image = pygame.image.load(gun_image_path).convert_alpha()
except Exception:
    gun_image = None

try:
    bullet_image = pygame.image.load(bullet_image_path).convert_alpha()
except Exception:
    bullet_image = None

while running :
    dt = clock.tick(FPS) / 1000
    keys = pygame.key.get_pressed()

    for event in pygame.event.get() :
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE] :
            running = False

    if game_started and not game_over :
        score += dt * 100

    if game_over and keys[pygame.K_r] :
        reset_game()

    player.handle_input(keys)
    player.apply_gravity(base.terrain, dt)

    # move and create terrain & roof
    screen.fill(WHITE)
    above.create(screen)
    base.create(screen)
    base.move(dt)

    # update obstacles
    for obs in obstacles :
        if obs.active and obs.obstacle.right > 0 :
            obs.move(dt)
            obs.create(screen)

            if player.obstacle.colliderect(obs.hitbox()) and not game_over :
                game_over = True
                for ob in obstacles :
                    ob.active = False
                base.active = False
                player.collision = True

    # NEW: gun pickups update & collision with player
    for gp in gun_pickups:
        if gp.active:
            gp.move(dt)
            gp.create(screen)
            if player.obstacle.colliderect(gp.rect) and not game_over:
                player.pickup_gun()
                gp.active = False

    # NEW: update bullets
    for b in bullets:
        if b.active:
            b.move(dt)
            b.create(screen)
            # check collision with obstacles
            for obs in obstacles:
                if obs.active and b.rect.colliderect(obs.hitbox()):
                    # hit: deactivate obstacle and bullet
                    obs.active = False
                    b.active = False
                    # optional: add points
                    score += 100

    # cleanup bullets (remove inactive)
    bullets = [b for b in bullets if b.active]

    player.create(screen)

    score_text = font.render(f"Score : {str(int(score)).zfill(5)}", True, WHITE)
    screen.blit(score_text, (1050, 50))

    # Hint text for shooting
    hint = "Press F to shoot (if you picked up a gun)"
    hint_text = font.render(hint, True, WHITE)
    screen.blit(hint_text, (50, 50))

    pygame.display.flip()

pygame.quit()
