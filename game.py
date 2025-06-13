from pgzero.actor import Actor
from pygame import Rect
from random import randint

screen: any  # type: ignore
keyboard: any  # type: ignore
mouse: any  # type: ignore
music: any  # type: ignore
sounds: any  # type: ignore

WIDTH = 800
HEIGHT = 600
is_music_enabled = True
is_sound_enabled = True
class Player(Actor):
    def __init__(self):
        super().__init__('player_idle/player_idle1', (100, 500))
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_on_ground  = False
        self.animation_frame = 0
        self.animation_timer = 0
        self.is_hurt = False
        self.hurt_timer = 0


    def update(self):
        self.move()
        self.animate()

    def move(self):
        self.velocity_x = 0
        if keyboard.left:
            self.velocity_x = -3
        if keyboard.right:
            self.velocity_x = 3
        self.x += self.velocity_x

        if not self.is_on_ground :
            self.velocity_y += 0.5  # gravidade
        else:
            self.velocity_y = 0
            if keyboard.space:
                self.velocity_y = -10
                if is_sound_enabled:
                    sounds.jump.play()
                self.is_on_ground  = False

        self.y += self.velocity_y
        self.check_ground()

    def check_ground(self):
        self.is_on_ground  = False
        for platform in platforms:
            if self.colliderect(platform.rectangle) and self.velocity_y >= 0:
                self.y = platform.rectangle.top - self.height / 2
                self.is_on_ground  = True

    def animate(self):
        if self.is_hurt:
            self.image = 'player_idle/player_hurt'
            self.hurt_timer += 1
            if self.hurt_timer > 30:  # meio segundo
                self.is_hurt = False
                self.hurt_timer = 0
            return  # não anima andando enquanto está machucado

        self.animation_timer += 1
        if self.animation_timer > 10:
            self.animation_frame = (self.animation_frame + 1) % 2
            self.animation_timer = 0
        if self.velocity_x != 0:
            self.image = f'player_walk/player_walk{self.animation_frame + 1}'
        else:
            self.image = f'player_idle/player_idle{self.animation_frame + 1}'


class Platform:
    def __init__(self, x, y, width, height):
        self.rectangle = Rect((x, y), (width, height))

    def draw(self):
        screen.draw.filled_rect(self.rectangle, (100, 100, 100))
class Enemy(Actor):
    def __init__(self, sprite_prefix, x, y):
        super().__init__(f'{sprite_prefix}1', (x, y))
        self.sprite_prefix = sprite_prefix
        self.animation_frame = 0
        self.animation_timer = 0

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

player.health = 3
player.invincible = False
player.invincibility_timer = 0


def check_player_enemy_collisions():
    global game_state
    if player.invincible:
        player.invincibility_timer += 1
        if player.invincibility_timer > 60:
            player.invincible = False
            player.invincibility_timer = 0
        return

    for enemy in enemies:
        if player.colliderect(enemy):
            player.health -= 1
            player.is_hurt = True
            player.invincible = True
            player.invincibility_timer = 0
            if is_sound_enabled:
                sounds.hit.play()
            print(f"Player hit! Health: {player.health}")
            if player.health <= 0:
                print("Game Over")
                game_state = "game_over"
                music.stop()
            return

start_button = Actor('menu/start_btn.png', (400, 200))
sound_button = Actor('menu/sound_on_btn', (400, 350))
exit_button = Actor('menu/exit_btn', (400, 500))
def update():
    global game_state
    if game_state == "playing":
        player.update()
        for enemy in enemies:
            enemy.update()
        check_player_enemy_collisions()

def draw():
    screen.clear()
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_game_screen()
    elif game_state == "game_over":
        draw_game_over_screen()

def draw_menu():
    screen.draw.text("KodPy", center=(400, 70), fontsize=80, color="white")
    screen.draw.text("Platformer Game", center=(400, 110), fontsize=30, color="gray")
    start_button.draw()
    sound_button.draw()
    exit_button.draw()
def draw_game_screen():
    for platform in platforms:
        platform.draw()
    for enemy in enemies:
        enemy.draw()
    player.draw()
    screen.draw.text(f"Health: {player.health}", (10, 10), color="white", fontsize=30)


def reset_game_state():
    player.x, player.y = 100, 500
    player.health = 3
    player.invincible = False
    player.invincibility_timer = 0
    player.is_hurt = False
    player.hurt_timer = 0
    for enemy in enemies:
        if isinstance(enemy, Spider):
            enemy.x = 500
        elif isinstance(enemy, Bee):
            enemy.y = 300
    if is_music_enabled:
        music.play('bg_music')
        music.set_volume(0.3)


def toggle_music_and_sound():
    global is_music_enabled, is_sound_enabled
    is_music_enabled = not is_music_enabled
    is_sound_enabled = is_music_enabled
    if not is_music_enabled:
        music.stop()
        sound_button.image = 'menu/sound_off_btn'
    else:
        music.play('bg_music')
        music.set_volume(0.3)
        sound_button.image = 'menu/sound_on_btn'


if is_music_enabled:
    music.play('bg_music')
    music.set_volume(0.3)

def draw_game_over_screen():
    screen.draw.text("GAME OVER", center=(400, 200), fontsize=80, color="red")
    screen.draw.text("Clique para voltar ao menu", center=(400, 300), fontsize=40, color="white")
