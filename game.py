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

