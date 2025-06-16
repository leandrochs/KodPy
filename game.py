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
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FLOOR_HEIGHT = 20
FLOOR_Y_POSITION = WINDOW_HEIGHT - FLOOR_HEIGHT
FLOOR_WIDTH = 10000
PLAYER_INITIAL_X = 100
PLAYER_INITIAL_Y = 500
PLAYER_MOVEMENT_SPEED = 3
GRAVITY_FORCE = 0.5
PLAYER_JUMP_FORCE = -10
PLAYER_MAX_HEALTH = 5
WORLD_SCROLL_LIMIT = WINDOW_WIDTH * 0.7
PLATFORM_MIN_X_SPACING = 200
PLATFORM_MAX_X_SPACING = 400
PLATFORM_MIN_Y_POSITION = 400
PLATFORM_MAX_Y_POSITION = 500
PLATFORM_MIN_WIDTH = 100
PLATFORM_MAX_WIDTH = 200
ENEMY_MIN_X_SPACING = 300
ENEMY_MAX_X_SPACING = 500
ENEMY_MIN_Y_POSITION = 200
ENEMY_MAX_Y_POSITION = 500
SPIDER_PATROL_RANGE = 100
SPIDER_MOVEMENT_SPEED = 2
BEE_PATROL_RANGE = 80
BEE_MOVEMENT_SPEED = 1.5
ANIMATION_FRAME_INTERVAL = 10
HURT_ANIMATION_DURATION = 30
INVINCIBILITY_DURATION = 60
MENU_TITLE_Y_POSITION = 70
MENU_SUBTITLE_Y_POSITION = MENU_TITLE_Y_POSITION + 40
MENU_BUTTON_START_Y = 200
MENU_BUTTON_Y_OFFSET = 150
SCREEN_LEFT_LIMIT = 10
HEAD_TEXT_X = 10
HEAD_TEXT_Y = 10
GAME_OVER_MESSAGE_Y = WINDOW_HEIGHT // 3
SCORE_DISPLAY_Y = GAME_OVER_MESSAGE_Y + 50
RESTART_PROMPT_Y = SCORE_DISPLAY_Y + 50

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

# === Game Logic ===
def update():
    global current_game_state, world_offset, score
    if current_game_state == GAME_STATES["PLAYING"]:
        player.update()
        if player.x > WORLD_SCROLL_LIMIT:
            world_offset += player.x - WORLD_SCROLL_LIMIT
            player.x = WORLD_SCROLL_LIMIT
        for enemy in enemies:
            enemy.update()
            enemy_screen_x = enemy.x - world_offset
            if not enemy.passed and player.x > enemy_screen_x + enemy.width:
                score += 1
                enemy.passed = True
        check_player_enemy_collisions()
        generate_world()

# === Rendering ===
def draw():
    screen.clear()
    if current_game_state == GAME_STATES["MENU"]:
        draw_menu()
    elif current_game_state == GAME_STATES["PLAYING"]:
        draw_playing_state()
    elif current_game_state == GAME_STATES["GAME_OVER"]:
        draw_game_over_screen()

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

# === Game Initialization ===
def start_background_music():
    global is_music_enabled
    if is_music_enabled:
        music.play('bg_music')
        music.set_volume(0.3)

# === Player Module ===
class Player(Actor):
    def __init__(self):
        super().__init__('player_idle/player_idle1', (PLAYER_INITIAL_X, PLAYER_INITIAL_Y))
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_on_ground = False
        self.animation_frame = 0
        self.animation_timer = 0
        self.is_hurt = False
        self.hurt_timer = 0
        self.health = PLAYER_MAX_HEALTH
        self.invincible = False
        self.invincibility_timer = 0

    def update(self):
        self.move()
        self.animate()

    def move(self):
        self.velocity_x = 0
        if keyboard.left:
            self.velocity_x = -PLAYER_MOVEMENT_SPEED
            if self.left < SCREEN_LEFT_LIMIT:
                self.velocity_x = 0
        if keyboard.right:
            self.velocity_x = PLAYER_MOVEMENT_SPEED
        self.x += self.velocity_x

        if not self.is_on_ground:
            self.velocity_y += GRAVITY_FORCE
        else:
            self.velocity_y = 0
            if keyboard.space:
                self.velocity_y = PLAYER_JUMP_FORCE
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

        base_ground_y = FLOOR_Y_POSITION - self.height / 2
        if self.y > base_ground_y:
            self.y = base_ground_y
            self.velocity_y = 0
            self.is_on_ground = True

    def animate(self):
        if self.is_hurt:
            self.image = 'player_idle/player_hurt'
            self.hurt_timer += 1
            if self.hurt_timer > HURT_ANIMATION_DURATION:
                self.is_hurt = False
                self.hurt_timer = 0
            return

        self.animation_timer += 1
        if self.animation_timer > ANIMATION_FRAME_INTERVAL:
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
        if self.animation_timer > ANIMATION_FRAME_INTERVAL:
            self.animation_frame = (self.animation_frame + 1) % 2
            self.animation_timer = 0
        self.image = f'{self.sprite_prefix}{self.animation_frame + 1}'

class Spider(Enemy):
    def __init__(self, x, y):
        super().__init__('enemy/spider/enemy_walk', x, y)
        self.movement_speed = SPIDER_MOVEMENT_SPEED
        self.left_limit = x - SPIDER_PATROL_RANGE
        self.right_limit = x + SPIDER_PATROL_RANGE

    def update(self):
        self.x += self.movement_speed
        if self.x < self.left_limit or self.x > self.right_limit:
            self.movement_speed *= -1
        self.animate()

class Bee(Enemy):
    def __init__(self, x, y):
        super().__init__('enemy/bee/bee_fly', x, y)
        self.movement_speed = BEE_MOVEMENT_SPEED
        self.upper_limit = y - BEE_PATROL_RANGE
        self.lower_limit = y + BEE_PATROL_RANGE

    def update(self):
        self.y += self.movement_speed
        if self.y < self.upper_limit or self.y > self.lower_limit:
            self.movement_speed *= -1
        self.animate()

# === Game Objects ===
player = Player()
platforms = [Platform(0, FLOOR_Y_POSITION, FLOOR_WIDTH, FLOOR_HEIGHT)]
enemies = []
start_button = Actor('menu/start_btn.png', (WINDOW_WIDTH // 2, MENU_BUTTON_START_Y))
sound_button = Actor('menu/sound_on_btn', (WINDOW_WIDTH // 2, MENU_BUTTON_START_Y + MENU_BUTTON_Y_OFFSET))
exit_button = Actor('menu/exit_btn', (WINDOW_WIDTH // 2, MENU_BUTTON_START_Y + 2 * MENU_BUTTON_Y_OFFSET))

# === World Generation ===
def generate_world():
    global last_platform_x, last_enemy_x
    # floor
    for platform in platforms:
        if platform.rectangle.y == FLOOR_Y_POSITION and platform.rectangle.height == FLOOR_HEIGHT:
            if platform.rectangle.right < world_offset + WINDOW_WIDTH:
                platforms.append(Platform(platform.rectangle.right, FLOOR_Y_POSITION, FLOOR_WIDTH, FLOOR_HEIGHT))

    # floating platforms
    while last_platform_x < world_offset + WINDOW_WIDTH * 2:
        x = last_platform_x + randint(PLATFORM_MIN_X_SPACING, PLATFORM_MAX_X_SPACING)
        y = randint(PLATFORM_MIN_Y_POSITION, PLATFORM_MAX_Y_POSITION)
        width = randint(PLATFORM_MIN_WIDTH, PLATFORM_MAX_WIDTH)
        platforms.append(Platform(x, y, width, FLOOR_HEIGHT))
        last_platform_x = x + width

    # enemies
    while last_enemy_x < world_offset + WINDOW_WIDTH * 1.5:
        x = last_enemy_x + randint(ENEMY_MIN_X_SPACING, ENEMY_MAX_X_SPACING)
        enemy_type = choice([Spider, Bee])
        y = FLOOR_Y_POSITION if enemy_type == Spider else randint(ENEMY_MIN_Y_POSITION, ENEMY_MAX_Y_POSITION)
        enemies.append(enemy_type(x, y))
        last_enemy_x = x

    # Clean
    platforms[:] = [p for p in platforms if p.rectangle.right > world_offset or (p.rectangle.height == FLOOR_HEIGHT and p.rectangle.y == FLOOR_Y_POSITION)]
    enemies[:] = [e for e in enemies if e.x + e.width > world_offset]

def check_player_enemy_collisions():
    global current_game_state
    if player.invincible:
        player.invincibility_timer += 1
        if player.invincibility_timer > INVINCIBILITY_DURATION:
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

def draw_menu():
    screen.draw.text("KodPy", center=(WINDOW_WIDTH // 2, MENU_TITLE_Y_POSITION), fontsize=80, color="white")
    screen.draw.text("Platformer Game", center=(WINDOW_WIDTH // 2, MENU_SUBTITLE_Y_POSITION), fontsize=30, color="gray")
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
    screen.draw.text(f"Health: {player.health} Score: {score}", (HEAD_TEXT_X, HEAD_TEXT_Y), color="white", fontsize=30)

def draw_game_over_screen():
    screen.draw.text("GAME OVER", center=(WINDOW_WIDTH // 2, GAME_OVER_MESSAGE_Y), fontsize=80, color="red")
    screen.draw.text(f"Score: {score}", center=(WINDOW_WIDTH // 2, SCORE_DISPLAY_Y), fontsize=50, color="white")
    screen.draw.text("Click to return to menu", center=(WINDOW_WIDTH // 2, RESTART_PROMPT_Y), fontsize=40, color="white")

# === Game State Management ===
def reset_game_state():
    global world_offset, score, last_platform_x, last_enemy_x
    player.x, player.y = PLAYER_INITIAL_X, PLAYER_INITIAL_Y
    player.health = PLAYER_MAX_HEALTH
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
    platforms.append(Platform(0, FLOOR_Y_POSITION, FLOOR_WIDTH, FLOOR_HEIGHT))
    start_background_music()

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

# === Game Initialization ===
start_background_music()