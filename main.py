import pygame
import os
import sys
import time

pygame.init()
pygame.mixer.init()

FPS = 60
TILE_SIZE = 65
WIDTH = 21 * TILE_SIZE
HEIGHT = 12 * TILE_SIZE
MAX_LVL = 2
HEIGHT_JUMP = 18
GRAVITY = 12
SPEED = 5
BLACK = pygame.Color('black')
DARK_GREY = (40, 40, 40)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mount Road")
lvl = 1
hero = None
clock = pygame.time.Clock()
l_check = 0

start_sound = pygame.mixer.Sound("data/sounds/start.wav")
main_sound = pygame.mixer.Sound("data/sounds/main.wav")
lvl_completed_sound = pygame.mixer.Sound("data/sounds/lvl_completed.wav")
game_over_sound = pygame.mixer.Sound("data/sounds/game_over.mp3")
game_over_sound.set_volume(0.25)
finish_sound = pygame.mixer.Sound("data/sounds/finish.wav")
finish_sound.set_volume(0.25)

sign_group = pygame.sprite.Group()
bash_group = pygame.sprite.Group()
tree_group = pygame.sprite.Group()
stone_group = pygame.sprite.Group()
house_group = pygame.sprite.Group()
hero_group = pygame.sprite.Group()
tile_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
flag_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
group_lst = [tree_group, stone_group, house_group, sign_group,
             spike_group, hero_group, tile_group, flag_group, bash_group]


def load_image(name, directory=None, colorkey=None):
    if directory is not None:
        fullname = os.path.join(f'data/{directory}', name)
    else:
        fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):  # загрузка карты
    filename = "levels/" + filename
    with open(filename, 'r', encoding="UTF-8") as lvlFile:
        level_map = [line.strip() for line in lvlFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def create_level(level):  # создание уровня
    global hero
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == "&":
                hero = Hero(x, y)
            elif level[y][x] == "f":
                Flag(x, y)
            elif level[y][x] == "@":
                House(x, y)
            elif level[y][x] == 'ш':
                Spike(x, y)
            elif level[y][x] in "yо":
                Sign(level[y][x], x, y)
            elif level[y][x] in "йёк":
                Stone(level[y][x], x, y)
            elif level[y][x] in "вгджзи":
                Tree(level[y][x], x, y)
            elif level[y][x] in "лмнп":
                Bush(level[y][x], x, y)
            elif level[y][x] != ".":
                Tile(level[y][x], x, y)


def level_up():  # новый уровень
    global lvl
    global BACKGROUND
    if lvl != MAX_LVL:
        lvl += 1
    BACKGROUND = pygame.transform.scale(load_image(f"background_{lvl}.png"), (WIDTH, HEIGHT))
    return


def start_screen():  # начальный экран
    start_sound.play(-1)
    start_sound.set_volume(0.5)
    fon = pygame.transform.scale(load_image('startscreen.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    press_font = pygame.font.Font(None, 30)
    main_font = pygame.font.Font(None, 100)
    press_txt = press_font.render('press any button', True, DARK_GREY)
    screen.blit(press_txt, (WIDTH // 2 - press_txt.get_width() // 2, 130))
    main_txt = main_font.render('Mount Road', True, DARK_GREY)
    screen.blit(main_txt, (WIDTH // 2 - main_txt.get_width() // 2, 70))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                start_sound.stop()
                return
        clock.tick(FPS)
        pygame.display.flip()


def lvl_completed():  # уровень пройден
    main_sound.stop()
    lvl_completed_sound.play()
    lvl_completed_sound.set_volume(0.15)
    all_sprites.draw(screen)
    completed = pygame.font.Font(None, 100)
    c_text = completed.render(f'Level {lvl} completed', True, BLACK)
    screen.blit(c_text, (WIDTH // 2 - c_text.get_width() // 2, 150))
    pressed = pygame.font.Font(None, 40)
    p1_text = pressed.render('press 1 - to go to next level', True, DARK_GREY)
    p2_text = pressed.render('press 2 - to go to menu', True, DARK_GREY)
    screen.blit(p1_text, (WIDTH // 2 - p1_text.get_width() // 2, 280))
    screen.blit(p2_text, (WIDTH // 2 - p2_text.get_width() // 2, 330))
    times = pygame.font.Font(None, 55)
    t_text = times.render(f"Time: {minutes}.{seconds}", True, BLACK)
    screen.blit(t_text, (WIDTH // 2 - t_text.get_width() // 2, 230))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if lvl == MAX_LVL:
                    finish_screen()
                    return
                else:
                    for sprite in all_sprites:
                        sprite.kill()
                    if event.key == pygame.K_1:
                        level_up()
                        create_level(load_level(f"lvl{lvl}.txt"))
                        main_sound.play()
                        main_sound.set_volume(0.5)
                        global time_start
                        time_start = time.time()
                        return
                    elif event.key == pygame.K_2:
                        level_up()
                        menu()
                        return
        clock.tick(FPS)
        pygame.display.flip()


def menu():
    global lvl
    global time_start
    main_sound.stop()
    start_sound.play()
    start_sound.set_volume(0.3)
    fon = pygame.transform.scale(load_image(f'background_{lvl}.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    press_font = pygame.font.Font(None, 50)
    main_font = pygame.font.Font(None, 100)
    menu = main_font.render('Menu', True, BLACK)
    lvl1_txt = press_font.render('Level 1', True, DARK_GREY)
    lvl2_txt = press_font.render('Level 2', True, DARK_GREY)
    lvl_1 = pygame.transform.scale(load_image('lvl_1.png'), (454, 366))
    if lvl != 2:
        lvl_2 = pygame.transform.scale(load_image("lvl_2_locked.png"), (454, 366))
    else:
        lvl_2 = pygame.transform.scale(load_image('lvl_2.png'), (454, 366))
    screen.blit(menu, ((WIDTH // 1.75) - menu.get_width(), 95))
    screen.blit(lvl1_txt, (((WIDTH // 1.75) - menu.get_width()) - lvl1_txt.get_width() - 150, 200))
    screen.blit(lvl2_txt, ((WIDTH // 1.75) + 150, 200))
    screen.blit(lvl_1, (((WIDTH // 1.75) - menu.get_width()) - lvl1_txt.get_width() - 330, 255))
    screen.blit(lvl_2, ((WIDTH // 1.75) - 30, 255))
    click_area_1 = pygame.Rect(((WIDTH // 1.75) - menu.get_width()) - lvl1_txt.get_width() - 330, 255, 454, 366)
    click_area_2 = pygame.Rect((WIDTH // 1.75) - 30, 255, 454, 366)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if click_area_1.collidepoint(event.pos):
                    start_sound.stop()
                    main_sound.play(-1)
                    main_sound.set_volume(0.25)
                    create_level(load_level(f"lvl{1}.txt"))
                    time_start = time.time()
                    return
                elif click_area_2.collidepoint(event.pos) and lvl == 2:
                    start_sound.stop()
                    main_sound.play(-1)
                    main_sound.set_volume(0.25)
                    create_level(load_level(f"lvl{2}.txt"))
                    time_start = time.time()
                    return
        clock.tick(FPS)
        pygame.display.flip()


def game_over():  # смерть игрока
    global lvl
    game_over_sound.play()
    game_over_sound.set_volume(0.15)
    all_sprites.draw(screen)
    press_font = pygame.font.Font(None, 40)
    lost = pygame.font.Font(None, 100)
    main_txt = lost.render('Game Over', True, BLACK)
    replay = press_font.render('press 1 - to restart this level', True, DARK_GREY)
    to_menu = press_font.render('press 2 - go to menu', True, DARK_GREY)
    screen.blit(main_txt, (WIDTH // 2 - main_txt.get_width() // 2, 250))
    screen.blit(replay, (WIDTH // 2 - replay.get_width() // 2, 320))
    screen.blit(to_menu, (WIDTH // 2 - to_menu.get_width() // 2, 360))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    for sprite in all_sprites:
                        sprite.kill()
                    create_level(load_level(f"lvl{lvl}.txt"))
                    global time_start
                    time_start = time.time()
                    return
                elif event.key == pygame.K_2:
                    for sprite in all_sprites:
                        sprite.kill()
                    menu()
                    return
        clock.tick(FPS)
        pygame.display.flip()


def finish_screen():  # конечный экран
    main_sound.stop()
    finish_sound.play()
    finish_sound.set_volume(0.15)
    fon = pygame.transform.scale(load_image('finishscreen.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    game = pygame.font.Font(None, 100)
    small_game = pygame.font.Font(None, 50)
    pass_game = game.render("Congratulations!", True, BLACK)
    passing = small_game.render("You've passed the game!", True, DARK_GREY)
    screen.blit(pass_game, (WIDTH // 2 - pass_game.get_width() // 2, HEIGHT // 2 - 200))
    screen.blit(passing, (WIDTH // 2 - passing.get_width() // 2, HEIGHT // 2 - 130))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                for sprite in all_sprites:
                    sprite.kill()
                pygame.quit()
                sys.exit()
        clock.tick(FPS)
        pygame.display.flip()


class Sign(pygame.sprite.Sprite):
    def __init__(self, sign_type, x, y):
        super().__init__(sign_group, all_sprites)
        self.image = pygame.transform.scale(load_image(f"{sign_type}.png", "objects/Signs"), (35, 48))
        self.rect = self.image.get_rect()
        self.rect.bottom = (y + 1) * TILE_SIZE + 1
        self.rect.left = x * TILE_SIZE + 10


class Bush(pygame.sprite.Sprite):
    def __init__(self, bash_type, x, y):
        super().__init__(bash_group, all_sprites)
        self.size_x = TILE_SIZE * 2
        self.size_y = TILE_SIZE * 1
        if bash_type == "п":
            self.size_x = TILE_SIZE * 1.5
            self.size_y = 32
        self.image = pygame.transform.scale(load_image(f"{bash_type}.png", "objects/Bushes"),
                                            (self.size_x, self.size_y))
        self.rect = self.image.get_rect()
        self.rect.bottom = (y + 1) * TILE_SIZE
        self.rect.left = x * TILE_SIZE + 3


class Tree(pygame.sprite.Sprite):
    def __init__(self, tree_type, x, y):
        super().__init__(tree_group, all_sprites)
        self.image = pygame.transform.scale(load_image(f"{tree_type}.png", "objects/Trees"),
                                            (TILE_SIZE * 2, TILE_SIZE * 3))
        self.rect = self.image.get_rect()
        self.rect.bottom = (y + 1) * TILE_SIZE + 1
        self.rect.left = x * TILE_SIZE
        if tree_type == "д":
            self.rect.left -= 35
        else:
            self.rect.left -= 18


class Stone(pygame.sprite.Sprite):
    def __init__(self, stone_type, x, y):
        super().__init__(stone_group, all_sprites)
        self.image = pygame.transform.scale(load_image(f"{stone_type}.png", "objects/Stones"),
                                            (TILE_SIZE * 2, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.bottom = (y + 1) * TILE_SIZE + 2
        self.rect.left = x * TILE_SIZE + 10


class House(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(house_group, all_sprites)
        self.image = pygame.transform.scale(load_image("@.png", "objects"),
                                            (TILE_SIZE * 3, TILE_SIZE * 3))
        self.rect = self.image.get_rect()
        self.rect.bottom = (y + 1) * TILE_SIZE + 1
        self.rect.left = x * TILE_SIZE


class Tile(pygame.sprite.Sprite):  # блоки
    def __init__(self, tile_type, x, y):
        super().__init__(tile_group, all_sprites)
        self.image = pygame.transform.scale(load_image(f"{tile_type}.png", "tileset"),
                                            (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect().move(TILE_SIZE * x, TILE_SIZE * y)


class Flag(pygame.sprite.Sprite):  # финишный флаг
    def __init__(self, x, y):
        super().__init__(flag_group, all_sprites)
        self.image = pygame.transform.scale(load_image("f.png", "objects"), (48, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.bottom = (y + 1) * TILE_SIZE
        self.rect.left = x * TILE_SIZE + 10


class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(spike_group, all_sprites)
        self.image = pygame.transform.scale(load_image('spike_3.png', 'objects/spikes'),
                                            (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.bottom = (y + 1) * TILE_SIZE
        self.rect.left = x * TILE_SIZE


class Camera:
    def __init__(self):
        self.dx = 0

    def apply(self, subject):
        subject.rect.x += self.dx

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w - WIDTH // 2)


class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(hero_group, all_sprites)
        self.is_jump = False
        self.height_jump = HEIGHT_JUMP
        self.new_state = ["idle"]

        self.idle_state = []
        self.idle_count = 0
        for i in range(1, 8):
            self.idle_state.append(load_image(f"idle{i}.png", 'hero/idle'))

        self.run_state = self.jump_state = []
        self.run_count = 1
        self.jump_count = 0
        for i in range(1, 9):
            self.run_state.append(load_image(f"run{i}.png", 'hero/run'))

        self.death_state = []
        self.death_count = 1
        for i in range(1, 6):
            self.death_state.append(load_image(f'death{i}.png', 'hero/death'))

        self.curr_image = 0
        self.image = self.idle_state[self.idle_count]
        self.rect = load_image(f'hero.png', 'hero').get_rect()
        self.rect.left = x * TILE_SIZE
        self.rect.bottom = (y + 1) * TILE_SIZE

    def get_state(self, buttons):
        keys = pygame.key.get_pressed()
        states = []
        if (buttons["space"] and pygame.sprite.spritecollideany(self, tile_group)) or self.is_jump:
            states.append("jump")
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            states.append("right")
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            states.append("left")
        if len(states) == 0:
            states.append("idle")
        return states

    def update(self, buttons):

        if not self.on_screen():
            self.kill()
            game_over()
        if self.on_finish():
            self.kill()
            lvl_completed()

        self.rect.bottom += 1
        curr_state = self.get_state(buttons)
        self.rect.bottom -= 1

        if curr_state != self.new_state:
            self.idle_count = 0
            self.jump_count = 0
            self.run_count = 1
            self.curr_image = 0
            self.new_state = curr_state

        global l_check

        if self.on_spikes():
            if 'left' in curr_state:
                l_check = 1
            curr_state = ['death']
            self.death()

        if "idle" in curr_state:
            self.idle(curr_state)

        elif "jump" in curr_state:
            self.is_jump = True
            self.jump(curr_state)

        elif 'left' in curr_state or 'right' in curr_state:
            self.run(curr_state)

        if not self.is_jump:
            self.rect.bottom += GRAVITY
            if pygame.sprite.spritecollideany(self, tile_group):
                self.rect.bottom -= self.rect.bottom % TILE_SIZE

    def idle(self, curr_state):
        self.idle_count = (self.idle_count + 1) % 10
        if self.idle_count == 9:
            self.curr_image = (self.curr_image + 1) % len(self.idle_state)
            self.image = pygame.transform.flip(self.idle_state[self.curr_image], "left" in curr_state, 0)

    def run(self, curr_state):
        if "right" in curr_state:
            self.rect.x += SPEED * 1.2
            if pygame.sprite.spritecollideany(self, tile_group):
                self.rect.x -= SPEED * 1.2
            self.run_count = (self.run_count + 1) % 7
            if self.run_count == 6:
                self.curr_image = (self.curr_image + 1) % len(self.run_state)
                self.image = self.run_state[self.curr_image]

        elif "left" in curr_state:
            self.rect.x -= SPEED * 1.2
            if pygame.sprite.spritecollideany(self, tile_group):
                self.rect.x += SPEED * 1.2
            self.run_count = (self.run_count + 1) % 7
            if self.run_count == 6:
                self.curr_image = (self.curr_image + 1) % len(self.run_state)
                self.image = pygame.transform.flip(self.run_state[self.curr_image], True, False)

    def jump(self, curr_state):
        self.rect.y -= self.height_jump
        self.height_jump -= 1

        if pygame.sprite.spritecollideany(self, tile_group):
            if self.height_jump < 0:
                self.rect.bottom -= self.rect.bottom % TILE_SIZE
                self.height_jump = HEIGHT_JUMP
                self.is_jump = False
            elif self.height_jump > 0:
                self.rect.bottom += self.height_jump
                self.height_jump = 0

        if "right" in curr_state:
            self.rect.x += SPEED
            if pygame.sprite.spritecollideany(self, tile_group):
                self.rect.x -= SPEED

        elif "left" in curr_state:
            self.rect.x -= SPEED
            if pygame.sprite.spritecollideany(self, tile_group):
                self.rect.x += SPEED

        self.jump_count = (self.jump_count + 1) % 6
        if self.jump_count == 5:
            self.curr_image = (self.curr_image + 1) % len(self.jump_state)
            self.image = pygame.transform.flip(self.jump_state[self.curr_image], "left" in curr_state, False)

    def death(self):
        global l_check
        if self.death_count < 5:
            self.death_count += 0.2
        else:
            self.kill()
            game_over()
        if isinstance(int(self.death_count), int):
            self.image = self.death_state[int(self.death_count) - 1]
        if l_check == 1:
            self.image = pygame.transform.flip(self.image, True, False)
            l_check = 0

    def collide_mask_check(self, sprite, sprite_group):
        curr_mask = pygame.mask.from_surface(sprite.image)
        for item in sprite_group:
            less_image = pygame.transform.scale(item.image, (TILE_SIZE, TILE_SIZE * 0.5))
            sprite_mask = pygame.mask.from_surface(less_image)
            offset = (item.rect.x - sprite.rect.x + 1, item.rect.y - sprite.rect.y + 40)
            if curr_mask.overlap(sprite_mask, offset):
                return True
        return False

    def on_screen(self):
        if self.rect.y <= HEIGHT:
            return True
        return False

    def on_spikes(self):
        if self.collide_mask_check(self, spike_group):
            return True
        return False

    def on_finish(self):
        if self.collide_mask_check(self, flag_group):
            return True
        return False


BACKGROUND = pygame.transform.scale(load_image(f"background_{lvl}.png"), (WIDTH, HEIGHT))
camera = Camera()
start_screen()
if __name__ == '__main__':
    menu()
    running = True
    time_start = time.time()  # начало
    while running:
        keys = {"space": False}
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    keys["space"] = True
        screen.blit(BACKGROUND, (0, 0))
        time_now = time.time()
        minutes = str(int((time_now - time_start) // 60))
        seconds = u'%.2f' % ((time_now - time_start) % 60)
        time_font = pygame.font.Font(None, 30)
        time_txt = time_font.render(f"{minutes}.{seconds}", True, (0, 0, 0))
        hero_group.update(keys)
        camera.update(hero)
        for sprite in all_sprites:
            camera.apply(sprite)
        for group in group_lst:
            group.draw(screen)
        screen.blit(time_txt, (10, 5))
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()
