from pgzero.actor import Actor
from pygame import Rect
from random import randint, choice

# Type hints for Pygame Zero
screen: any  # type: ignore
keyboard: any  # type: ignore
mouse: any  # type: ignore
music: any  # type: ignore
sounds: any  # type: ignore

# === Game Configuration ===
WIDTH = 800
HEIGHT = 600

GAME_STATES = {
    "MENU": "menu",
    "PLAYING": "playing",
    "GAME_OVER": "game_over"
}

# === Global Variables ===
current_game_state = GAME_STATES["MENU"]
is_music_enabled = True
is_sound_enabled = True
world_offset = 0
last_platform_x = 0
last_enemy_x = 500
score = 0

# === Player Module ===
class Player(Actor):
    def __init__(self):
        super().__init__('player_idle/player_idle1', (100, 500))
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_on_ground = False
        self.animation_frame = 0
        self.animation_timer = 0
        self.is_hurt = False
        self.hurt_timer = 0
        self.health = 5
        self.invincible = False
        self.invincibility_timer = 0

    def update(self):
        self.move()
        self.animate()

    def move(self):
        self.velocity_x = 0
        if keyboard.left:
            self.velocity_x = -3
            if self.left < 10:
                self.velocity_x = 0
        if keyboard.right:
            self.velocity_x = 3
        self.x += self.velocity_x

        if not self.is_on_ground:
            self.velocity_y += 0.5  # Gravity
        else:
            self.velocity_y = 0
            if keyboard.space:
                self.velocity_y = -10
                if is_sound_enabled:
                    sounds.jump.play()
                self.is_on_ground = False

        self.y += self.velocity_y
        self.check_ground()

    def check_ground(self):
        self.is_on_ground = False
        for platform in platforms:
            original_x = platform.rectangle.x
            platform.rectangle.x -= world_offset
            if self.colliderect(platform.rectangle) and self.velocity_y >= 0:
                if self.bottom >= platform.rectangle.top and self.bottom <= platform.rectangle.top + 10:
                    self.y = platform.rectangle.top - self.height / 2
                    self.velocity_y = 0
                    self.is_on_ground = True
            platform.rectangle.x = original_x

        base_ground_y = 580 - self.height / 2
        if self.y > base_ground_y:
            self.y = base_ground_y
            self.velocity_y = 0
            self.is_on_ground = True

    def animate(self):
        if self.is_hurt:
            self.image = 'player_idle/player_hurt'
            self.hurt_timer += 1
            if self.hurt_timer > 30:  # 0.5 seconds
                self.is_hurt = False
                self.hurt_timer = 0
            return

        self.animation_timer += 1
        if self.animation_timer > 10:
            self.animation_frame = (self.animation_frame + 1) % 2
            self.animation_timer = 0
        if self.velocity_x != 0:
            self.image = f'player_walk/player_walk{self.animation_frame + 1}'
        else:
            self.image = f'player_idle/player_idle{self.animation_frame + 1}'

# === Platform Module ===
class Platform:
    def __init__(self, x, y, width, height):
        self.rectangle = Rect((x, y), (width, height))
        self.color = (100, 100, 100)

    def draw(self):
        screen.draw.filled_rect(self.rectangle, self.color)

# === Enemy Module ===
class Enemy(Actor):
    def __init__(self, sprite_prefix, x, y):
        super().__init__(f'{sprite_prefix}1', (x, y))
        self.sprite_prefix = sprite_prefix
        self.animation_frame = 0
        self.animation_timer = 0
        self.passed = False

    def animate(self):
        self.animation_timer += 1
        if self.animation_timer > 10:
            self.animation_frame = (self.animation_frame + 1) % 2
            self.animation_timer = 0
        self.image = f'{self.sprite_prefix}{self.animation_frame + 1}'

class Spider(Enemy):
    def __init__(self, x, y):
        super().__init__('enemy/spider/enemy_walk', x, y)
        self.movement_speed = 2
        self.left_limit = x - 100
        self.right_limit = x + 100

    def update(self):
        self.x += self.movement_speed
        if self.x < self.left_limit or self.x > self.right_limit:
            self.movement_speed *= -1
        self.animate()

class Bee(Enemy):
    def __init__(self, x, y):
        super().__init__('enemy/bee/bee_fly', x, y)
        self.movement_speed = 1.5
        self.upper_limit = y - 80
        self.lower_limit = y + 80

    def update(self):
        self.y += self.movement_speed
        if self.y < self.upper_limit or self.y > self.lower_limit:
            self.movement_speed *= -1
        self.animate()

# === Game Objects ===
player = Player()
platforms = [Platform(0, 580, 10000, 20)]
enemies = []
start_button = Actor('menu/start_btn.png', (400, 200))
sound_button = Actor('menu/sound_on_btn', (400, 350))
exit_button = Actor('menu/exit_btn', (400, 500))

# === World Generation ===
def generate_world():
    global last_platform_x, last_enemy_x
    # Extend base floor
    for platform in platforms:
        if platform.rectangle.y == 580 and platform.rectangle.height == 20:
            if platform.rectangle.right < world_offset + WIDTH:
                platforms.append(Platform(platform.rectangle.right, 580, 10000, 20))

    # Generate floating platforms
    while last_platform_x < world_offset + WIDTH * 2:
        x = last_platform_x + randint(200, 400)
        y = randint(400, 500)
        width = randint(100, 200)
        platforms.append(Platform(x, y, width, 20))
        last_platform_x = x + width

    # Generate enemies
    while last_enemy_x < world_offset + WIDTH * 1.5:
        x = last_enemy_x + randint(300, 500)
        enemy_type = choice([Spider, Bee])
        y = 580 if enemy_type == Spider else randint(200, 500)
        enemies.append(enemy_type(x, y))
        last_enemy_x = x

    # Clean up off-screen objects
    platforms[:] = [p for p in platforms if p.rectangle.right > world_offset or (p.rectangle.height == 20 and p.rectangle.y == 580)]
    enemies[:] = [e for e in enemies if e.x + e.width > world_offset]

# === Game Logic ===
def update():
    global current_game_state, world_offset, score
    if current_game_state == GAME_STATES["PLAYING"]:
        player.update()
        if player.x > WIDTH * 0.7:
            world_offset += player.x - WIDTH * 0.7
            player.x = WIDTH * 0.7
        for enemy in enemies:
            enemy.update()
            enemy_screen_x = enemy.x - world_offset
            if not enemy.passed and player.x > enemy_screen_x + enemy.width:
                score += 1
                enemy.passed = True
        check_player_enemy_collisions()
        generate_world()

def check_player_enemy_collisions():
    global current_game_state
    if player.invincible:
        player.invincibility_timer += 1
        if player.invincibility_timer > 60:
            player.invincible = False
            player.invincibility_timer = 0
        return

    for enemy in enemies:
        original_x = enemy.x
        enemy.x -= world_offset
        if player.colliderect(enemy) and not player.invincible:
            player.health -= 1
            player.is_hurt = True
            player.invincible = True
            if is_sound_enabled:
                sounds.hit.play()
            if player.health <= 0:
                current_game_state = GAME_STATES["GAME_OVER"]
                music.stop()
            enemy.x = original_x
            break
        enemy.x = original_x

# === Rendering ===
def draw():
    screen.clear()
    if current_game_state == GAME_STATES["MENU"]:
        draw_menu()
    elif current_game_state == GAME_STATES["PLAYING"]:
        draw_playing_state()
    elif current_game_state == GAME_STATES["GAME_OVER"]:
        draw_game_over_screen()

def draw_menu():
    screen.draw.text("KodPy", center=(400, 70), fontsize=80, color="white")
    screen.draw.text("Platformer Game", center=(400, 110), fontsize=30, color="gray")
    start_button.draw()
    sound_button.draw()
    exit_button.draw()

def draw_playing_state():
    screen.fill((50, 50, 100))
    for platform in platforms:
        platform.rectangle.x -= world_offset
        platform.draw()
        platform.rectangle.x += world_offset
    for enemy in enemies:
        enemy.x -= world_offset
        enemy.draw()
        enemy.x += world_offset
    player.draw()
    screen.draw.text(f"Health: {player.health} Score: {score}", (10, 10), color="white", fontsize=30)

def draw_game_over_screen():
    screen.draw.text("GAME OVER", center=(400, 200), fontsize=80, color="red")
    screen.draw.text(f"Score: {score}", center=(400, 250), fontsize=50, color="white")
    screen.draw.text("Click to return to menu", center=(400, 300), fontsize=40, color="white")

# === Input Handling ===
def on_mouse_down(pos):
    global current_game_state, is_music_enabled
    if current_game_state == GAME_STATES["MENU"]:
        if start_button.collidepoint(pos):
            current_game_state = GAME_STATES["PLAYING"]
            if is_music_enabled:
                music.play('bg_music')
                music.set_volume(0.3)
        elif sound_button.collidepoint(pos):
            toggle_music_and_sound()
        elif exit_button.collidepoint(pos):
            quit()
    elif current_game_state == GAME_STATES["GAME_OVER"]:
        current_game_state = GAME_STATES["MENU"]
        reset_game_state()

# === Game State Management ===
def reset_game_state():
    global world_offset, score, last_platform_x, last_enemy_x
    player.x, player.y = 100, 500
    player.health = 5
    player.invincible = False
    player.invincibility_timer = 0
    player.is_hurt = False
    player.hurt_timer = 0
    world_offset = 0
    score = 0
    last_platform_x = 0
    last_enemy_x = 500
    platforms.clear()
    enemies.clear()
    platforms.append(Platform(0, 580, 10000, 20))
    initialize_game()

def toggle_music_and_sound():
    global is_music_enabled, is_sound_enabled
    is_music_enabled = not is_music_enabled
    is_sound_enabled = is_music_enabled
    if is_music_enabled:
        music.play('bg_music')
        music.set_volume(0.3)
        sound_button.image = 'menu/sound_on_btn'
    else:
        music.stop()
        sound_button.image = 'menu/sound_off_btn'

def initialize_game():
    global is_music_enabled
    if is_music_enabled:
        music.play('bg_music')
        music.set_volume(0.3)

# === Game Initialization ===
initialize_game()