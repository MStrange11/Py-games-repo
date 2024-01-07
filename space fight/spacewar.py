import pygame
from pygame.locals import *
import random
import sys

import warnings

warnings.filterwarnings("ignore")

# Basics
pygame.init()
clock = pygame.time.Clock()

screen_width, screen_height = 800, 800
screen_center = (screen_width // 2, screen_height // 2)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.mouse.set_visible(False)


class Color():
    def __init__(self):
        self.white = (255, 255, 255)
        self.dark = (100, 100, 100)
        self.light = (170, 170, 170)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # self.image = pygame.Surface((100, 100))
        # self.image.fill((255, 255, 255))

        self.max_health = 1000
        self.health = self.max_health
        self.m = [screen_width//2, screen_height]

        self.health_data = Generate_text(self.m)

        self.image = pygame.transform.scale(pygame.image.load("src\\spaceship1.png"), (100, 100))
        self.rect = self.image.get_rect(center=(screen_width // 2, screen_height // 2))

    def update(self):
        global winner

        mouse = pygame.mouse.get_pos()

        # if csb_d != None and csb_d[0] <= mouse[0] <= csb_d[0] + csb_d[2] and csb_d[1] <= mouse[1] <= csb_d[1] + csb_d[3] :
        #     pygame.mouse.set_visible(True)

        if (reset_btn_detect[0] <= mouse[0] <= reset_btn_detect[0] + reset_btn_detect[2] and reset_btn_detect[1] <= mouse[1] <= reset_btn_detect[1] + reset_btn_detect[3] or
                user_name_input_rect[0] <= mouse[0] <= user_name_input_rect[0] + user_name_input_rect[2] and user_name_input_rect[1] <= mouse[1] <= user_name_input_rect[1] + user_name_input_rect[3]):
            pygame.mouse.set_visible(True)
        else:
            pygame.mouse.set_visible(False)

        if winner:
            self.rect.y -= 1
            self.image = pygame.transform.scale(pygame.image.load("src\\spaceship" + str(ship_num) + ".png"), (100, 100))
            pygame.mouse.set_visible(True)

        elif self.health > 0:
            self.rect.center = mouse
            self.m = list(mouse)
            self.image = pygame.transform.scale(pygame.image.load("src\\spaceship" + str(ship_num) + ".png"), (100, 100))

            health_data = tuple((self.m[0] - 30, self.m[1] + 50))
            self.health_data.render_text(f"{self.health}/{self.max_health}", health_data, Color().white)
        else:
            pygame.mouse.set_visible(True)
            self.image = pygame.transform.scale(pygame.image.load("src\\explode.png"), (100, 100))

        health_bar = tuple((self.m[0] - 50, self.m[1] + 70))
        h_ratio = self.health / self.max_health
        if pygame.sprite.spritecollide(self, enemy_group, False) and self.health > 0:
            self.health -= 2
            # print(h_ratio)

        pygame.draw.rect(screen, (200, 20, 20), (health_bar, [100, 5]))
        pygame.draw.rect(screen, (20, 200, 20), (health_bar, [100 * h_ratio, 5]))

    def create_bullet(self, weapon_name="bullet.png", size = (20,20)):

        if "bullet.png" == weapon_name:
            global bullet_count
            bullet_count += 1
            bullet_group.add(Bullet(self.rect.x + 100 - 5, self.rect.y + 50, weapon_name, size))
            return Bullet(self.rect.x+5, self.rect.y+50, weapon_name, size)

        return Bullet(self.rect.x+50, self.rect.y+50, weapon_name, size)


class Enemy_h_text(pygame.sprite.Sprite):
    def __init__(self, xy, damage_get):
        super().__init__()

        text = Generate_text(xy).render_text("-" + str(damage_get), None, Color().white)
        self.text = text
        self.xy = xy
        self.speedY = 2

    def update(self):
        newxy = list(self.xy)
        newxy[1] -= self.speedY
        self.xy = tuple(newxy)

        screen.blit(self.text, self.xy)

        if self.xy[1] <= 0:
            # print("text deleted")
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.health = 100

        self.spwaningX_range = (50, screen_width - 70 - 50)
        self.spwaningY_range = (70, screen_height // 2 - 70)

        enemyX = random.randint(self.spwaningX_range[0], self.spwaningX_range[1])
        enemyY = random.randint(self.spwaningY_range[0], self.spwaningY_range[1])

        self.X_speed = random.randint(1, 5)
        self.Y_speed = random.randint(-1, 1)

        self.image = pygame.transform.scale(pygame.image.load("src\\enemy2.png"), (70, 70))
        self.rect = self.image.get_rect(center=(enemyX, enemyY))
        # print("enemy spawn")

    def update(self, missile, damage_get):
        global enemy_Killed

        if self.rect.right > screen_width:
            self.X_speed *= -1
        elif self.rect.left < 0:
            self.X_speed *= -1

        if self.rect.top < self.spwaningY_range[0]:
            self.Y_speed *= -1
        elif self.rect.top > self.spwaningY_range[1]:
            self.Y_speed *= -1

        self.rect.move_ip(self.X_speed, self.Y_speed)

        if pygame.sprite.spritecollide(self, missile, True):

            Enemy_h_text_group.add(Enemy_h_text(self.rect.midtop, damage_get))

            # print("got hit, text created")

            self.health -= damage_get
            # print("target hit", "health remaining: ", self.health)
            if self.health <= 0:
                enemy_Killed += 1
                # print("enemy killed", enemy_Killed)
                self.kill()

def add_enemies():
    global wave_lvl, ship_num , bullet_damage, missile_damage

    if not len(enemy_group) and wave_lvl <= 5 and player.health > 0:
        wave_lvl += 1
        print("wave_lvl", wave_lvl, "ship_num", ship_num)
        for e in range(min(32, (2 ** wave_lvl))):
            enemy_group.add(Enemy())

    if not len(enemy_group) and ship_num < 3 and wave_lvl >= 6 and not winner:
        ship_num += 1
        wave_lvl = 0

        if ship_num == 2:
            bullet_damage *= 1.5
            missile_damage = 40
        elif ship_num == 3:
            bullet_damage *= 2
            missile_damage = 60


missile_damage = 30
bullet_damage = 10


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, weapon_name, size):
        super().__init__()

        self.image = pygame.transform.scale(pygame.image.load(f"src\\{weapon_name}"), size)
        self.rect = self.image.get_rect(center=(pos_x, pos_y))

    def update(self):
        global bullet_count
        self.rect.y -= 5

        if self.rect.y <= 0 - 50:
            self.kill()
            # print("bullet destroyed", bullet_count)


class Generate_text():
    def __init__(self, xy=(0, 0)):
        self.xy = xy
        self.font1 = pygame.font.SysFont('freesanbold.ttf', 20)
        self.font2 = pygame.font.SysFont('chalkduster.ttf', 20)

    def render_text(self, text, dest, color, bg=None):
        Text = self.font1.render(text, True, color, bg)
        dest = dest if dest else self.xy
        screen.blit(Text, dest)
        return Text


class Button():
    def __init__(self):
        self.btn_size = (70, 30)

    def generate_btn(self, text, color, position: tuple = None, size=None, bg=Color().dark):
        self.btn_size = size if size else self.btn_size

        rect = (position + self.btn_size) if position else (screen_width // 2, screen_height // 2) + self.btn_size
        pygame.draw.rect(screen, bg, rect, 0, 5)
        self.rect = Rect(rect)
        rect = list(rect)
        rect[0] += 10
        rect[1] += 10
        text = Generate_text().render_text(text, tuple(rect), color)
        self.rect.w = max(100, text.get_width() + 10)
        return self.rect

max_fps, min_fps = 0, float('inf')

def show_fps():
    global max_fps, min_fps

    fps = clock.get_fps()
    rounded_fps = round(fps, 1)

    Player_name.render_text(f"FPS: {rounded_fps}", (screen_width - 100, 10), (255, 255, 255), (0, 0, 50))

    max_fps = max(max_fps, rounded_fps)

    if min_fps == 0 or rounded_fps > 0:
        min_fps = min(min_fps, rounded_fps)

    Player_name.render_text(f"Max FPS: {max_fps}", (screen_width - 100, 25), (255, 255, 255), (0, 0, 50))
    Player_name.render_text(f"Min FPS: {min_fps}", (screen_width - 100, 40), (255, 255, 255), (0, 0, 50))


player = Player()
player_group = pygame.sprite.Group()
player_group.add(player)

winner = False

ship_num = 1
max_ship_num = 3

bullet_group = pygame.sprite.Group()
bullet_count = 0
bullet_firing = False

last_print_time = 0
bullet_firing_delay = 100

missile_group = pygame.sprite.Group()
missile_count = 0

Enemy_h_text_group = pygame.sprite.Group()

enemy_group = pygame.sprite.Group()
enemy_Killed = 0
wave_lvl = 0

spawn_delay = 2
last_wave_created_time = 0

bg_img = pygame.image.load("src\\space_bg.jpg")
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height * 1.8))
print(bg_img.get_size())

change_ship_btn = Button()
csb_d = None

reset_btn = Button()
reset_btn_detect = None

Player_name = Generate_text()
Bullet_fire = Generate_text()
Enemy_killed = Generate_text()
Wave_level = Generate_text()
enemy_remaining = Generate_text()

user_name_input_rect = pygame.Rect(20, screen_height - 20 - 10, 10, 20)
user_name = ""
write = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):  # Fix the event type here
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            if user_name_input_rect.collidepoint(event.pos) and not player.health <= 0:
                write = True
            else:
                write = False

            if csb_d != None and csb_d.collidepoint(event.pos):
                ship_num += 1
                if ship_num > max_ship_num:
                    ship_num = 1
            elif reset_btn_detect.collidepoint(event.pos) and player.health <= 0:
                wave_lvl = 0
                player.health = player.max_health

            elif reset_btn_detect.collidepoint(event.pos) and winner:
                wave_lvl = 0
                ship_num = 1
                missile_damage = 30
                bullet_damage = 10
                player.health = player.max_health
                winner = not winner

        if event.type == KEYDOWN:
            if event.key == K_s:
                enemy_group.add(Enemy())

            if event.key == K_5:
                bullet_firing = True


            if event.key == K_SPACE and not write and len(bullet_group) <= 5:
                missile_group.add(player.create_bullet("missile.png", (50,50) ) )
                missile_count += 1

            if event.key == K_BACKSPACE:
                if write:
                    user_name = user_name[:-1]
            else:
                if write:
                    user_name += event.unicode

        if event.type == KEYUP:
            if event.key == K_5:
                bullet_firing = False

    if bullet_firing:
        current_time = pygame.time.get_ticks()
        if current_time - last_print_time >= bullet_firing_delay:
            bullet_group.add(player.create_bullet())
            bullet_count += 1
            last_print_time = current_time

    screen.fill((0, 0, 0))
    screen.blit(bg_img, (0, 0))

    missile_group.draw(screen)
    bullet_group.draw(screen)
    player_group.draw(screen)

    enemy_group.draw(screen)
    missile_group.update()
    bullet_group.update()

    Enemy_h_text_group.update()

    pygame.draw.rect(screen, Color().white, user_name_input_rect)

    text2 = Generate_text().render_text(user_name, (user_name_input_rect.x + 5, user_name_input_rect.y + 5), (0, 0, 0))
    user_name_input_rect.w = max(100, text2.get_width() + 10)

    Player_name.render_text("Player name: " + user_name, (10, 10), (255, 255, 255), (0, 0, 50))
    Bullet_fire.render_text("Bullet fire: " + str(bullet_count), (10, 25), (255, 255, 255), (0, 0, 50))
    Enemy_killed.render_text("Enemy killed: " + str(enemy_Killed), (10, 40), (255, 255, 255), (0, 0, 50))
    Wave_level.render_text("Ship level: " + str(ship_num), (10, 55), (255, 255, 255), (0, 0, 50))
    Wave_level.render_text("Wave level: " + str(wave_lvl), (10, 70), (255, 255, 255), (0, 0, 50))
    enemy_remaining.render_text("enemy remaining: " + str(len(enemy_group)), (10, 85), (255, 255, 255), (0, 0, 50))

    show_fps()

    # csb_d = change_ship_btn.generate_btn("Change Ship", Color().white, (screen_width - 110, screen_height - 40), (100, 30))
    reset_btn_detect = reset_btn.generate_btn("Restart", Color().white, (screen_width - 185, screen_height - 40))


    add_enemies()

    if wave_lvl >= 6 and ship_num >= 3:
        game_won = pygame.transform.scale(pygame.image.load("src\\winner.png"), (500, 500))
        game_won.set_alpha(255 * 0.95)
        game_won_rect = game_won.get_rect(center=screen_center)  # Get the rect with the center at screen_center
        screen.blit(game_won, game_won_rect.topleft)  # Blit the image using the top-left corner of the rect

        winner = True
        enemy_group.empty()

    if not write:
        player_group.update()

    if player.health <= 0:
        game_over = pygame.transform.scale(pygame.image.load("src\\game-over.png"), (500, 500))
        game_over.set_alpha(255 * 0.95)
        game_over_rect = game_over.get_rect(center=screen_center)  # Get the rect with the center at screen_center
        screen.blit(game_over, game_over_rect.topleft)  # Blit the image using the top-left corner of the rect

        arrow = pygame.transform.scale(pygame.image.load("src\\right-arrow.png"), (60, 60))
        screen.blit(arrow, (screen_width - 240, screen_height - 65))

        enemy_group.empty()
    else:
        enemy_group.update(bullet_group, bullet_damage)
        enemy_group.update(missile_group, missile_damage)

    pygame.display.flip()
    clock.tick(60)
