import random
import sys
import pygame as pg

pg.init()
pg.display.set_caption('Key Finder')
tile_width = tile_height = 40
clock = pg.time.Clock()
FPS = 30

music_volume = 1
pg.mixer.music.load('assets/music.mp3')
pg.mixer.music.play()
pg.mixer.music.set_volume(music_volume)
attack_sound = pg.mixer.Sound('assets/attack.mp3')
bonus_sound = pg.mixer.Sound('assets/bonus.mp3')
key_sound = pg.mixer.Sound('assets/key.mp3')
step_sound = pg.mixer.Sound('assets/step.mp3')

score = 100
boxes_cnt = 0
is_key = False
is_door = False

all_sprites = pg.sprite.Group()
tiles_group = pg.sprite.Group()
player_group = pg.sprite.Group()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)


def terminate():
    pg.quit()
    sys.exit()


def size(filename):
    filename = "levels/" + filename
    with open(filename, 'r') as level:
        level_map = [line.strip() for line in level]
    width = max(map(len, level_map))
    height = len(level_map)
    return width * tile_width, height * tile_height


map_list = ['map.txt', 'map2.txt', 'map3.txt', 'map4.txt']
current_map = random.choice(map_list)
game_screen = pg.display.set_mode(size(current_map))
player_image = pg.transform.scale(pg.image.load('assets/player.gif').convert_alpha(), (tile_width, tile_height))
player_image_rotate = pg.transform.flip(player_image, True, False)


def load_image(name, color_key=None):
    try:
        image = pg.image.load('assets/' + name).convert()
    except pg.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at(size(current_map))
        image.set_colorkey(color_key)
    else:
        image = image.convert
    return image


box_sprites = ['box1', 'box2', 'box3', 'box4', 'box5']

tile_images = {
    'box1': pg.transform.scale(pg.image.load('assets/box1.jpg'), (tile_width, tile_height)),
    'box2': pg.transform.scale(pg.image.load('assets/box2.jpg'), (tile_width, tile_height)),
    'box3': pg.transform.scale(pg.image.load('assets/box3.jpg'), (tile_width, tile_height)),
    'box4': pg.transform.scale(pg.image.load('assets/box4.jpg'), (tile_width, tile_height)),
    'box5': pg.transform.scale(pg.image.load('assets/box5.jpg'), (tile_width, tile_height)),
    'empty': pg.transform.scale(pg.image.load('assets/floor.png'), (tile_width, tile_height)),
    'bonus': pg.transform.scale(pg.image.load('assets/bonus_floor.png'), (tile_width, tile_height)),
    'player_floor': pg.transform.scale(pg.image.load('assets/player_floor.png'), (tile_width, tile_height)),
    'floor_with_key': pg.transform.scale(pg.image.load('assets/floor_with_key.png'), (tile_width, tile_height)),
    'door': pg.transform.scale(pg.image.load('assets/door.png'), (tile_width, tile_height)),
    'door_opened': pg.transform.scale(pg.image.load('assets/door_opened.png'), (tile_width, tile_height)),
    'wall': pg.transform.scale(pg.image.load('assets/wall.png'), (tile_width, tile_height))
}


class Tile(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        global box_sprites
        if tile_type == 'box' or \
                tile_type == 'box_with_key' or \
                tile_type == 'box_with_bonus':
            self.current_box = random.choice(box_sprites)
            self.image = tile_images[self.current_box]
        else:
            self.image = tile_images[tile_type]
        self.rect = self.image.get_rect()
        self.tile_type = tile_type
        self.rect.x = tile_width * pos_x
        self.rect.y = tile_height * pos_y
        tiles_group.add(self)


def load_level(filename):
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    max_width = max(map(len, level_map))

    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Player(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos_x, tile_height * pos_y
        self.direction = "up"
        player_group.add(self)

    def update(self, to_x, to_y, direction):
        if self.rect.x + to_x != size(current_map)[0] and self.rect.x + to_x != -tile_width \
                and self.rect.y + to_y != size(current_map)[1] and self.rect.y + to_y != -tile_height:
            self.rect.x += to_x
            self.rect.y += to_y
            self.direction = direction

            global score
            for wall in tiles_group:
                if wall.tile_type == 'box' \
                        or wall.tile_type == 'box_with_key' \
                        or wall.tile_type == 'box_with_bonus' \
                        or wall.tile_type == 'door' \
                        or wall.tile_type == 'door_opened' \
                        or wall.tile_type == 'wall'\
                        or wall.tile_type == 'floor_with_key':
                    if self.rect.colliderect(wall.rect):
                        self.rect.x -= to_x
                        self.rect.y -= to_y
                        score += 1

    def broke_block(self):
        to_x = to_y = 0
        if self.direction == 'right':
            to_x = tile_width
        elif self.direction == 'left':
            to_x = -tile_width
        elif self.direction == 'up':
            to_y = -tile_height
        elif self.direction == 'down':
            to_y = tile_height

        self.rect.x += to_x
        self.rect.y += to_y

        global boxes_cnt
        global is_key
        global is_door
        for wall in tiles_group:
            if wall.tile_type == 'box':
                if self.rect.colliderect(wall.rect):
                    attack_sound.play()
                    wall.image = tile_images['empty']
                    wall.tile_type = "empty"
                    self.rect.x -= to_x
                    self.rect.y -= to_y
                    boxes_cnt -= 1
                    return

            if wall.tile_type == 'box_with_key':
                if self.rect.colliderect(wall.rect):
                    attack_sound.play()
                    wall.image = tile_images['floor_with_key']
                    wall.tile_type = "floor_with_key"
                    self.rect.x -= to_x
                    self.rect.y -= to_y
                    boxes_cnt -= 1
                    return

            if wall.tile_type == 'floor_with_key':
                if self.rect.colliderect(wall.rect):
                    key_sound.play()
                    wall.image = tile_images['empty']
                    wall.tile_type = "empty"
                    self.rect.x -= to_x
                    self.rect.y -= to_y
                    is_key = True
                    Tile('door_opened', door_coords[0], door_coords[1])
                    return

            if wall.tile_type == 'box_with_bonus':
                if self.rect.colliderect(wall.rect):
                    bonus_sound.play()
                    attack_sound.play()
                    wall.image = tile_images['bonus']
                    wall.tile_type = "empty"
                    self.rect.x -= to_x
                    self.rect.y -= to_y
                    boxes_cnt -= 1
                    add_points()
                    return

            if wall.tile_type == 'door':
                if self.rect.colliderect(wall.rect):
                    self.rect.x -= to_x
                    self.rect.y -= to_y
                    is_door = True
                    return

        self.rect.x -= to_x
        self.rect.y -= to_y


door_coords = 0, 0


def generate_level(level):
    new_player = None
    x = None
    y = None
    global boxes_cnt
    global door_coords
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('box', x, y)
                boxes_cnt += 1
            elif level[y][x] == '$':
                Tile('box_with_key', x, y)
                boxes_cnt += 1
            elif level[y][x] == '%':
                Tile('door', x, y)
                door_coords = x, y
            elif level[y][x] == '*':
                Tile('box_with_bonus', x, y)
                boxes_cnt += 1
            elif level[y][x] == '&':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('player_floor', x, y)
                new_player = Player(x, y)

    return new_player, x, y


player, level_x, level_y = generate_level(load_level('levels/' + current_map))


def generate_map():
    restart_map = current_map
    while restart_map == current_map:
        restart_map = random.choice(map_list)
    return restart_map


def restart_game():
    global player, level_x, level_y, score,\
        boxes_cnt, is_key, is_door, tiles_group,\
        player_group, all_sprites
    score = 100
    boxes_cnt = 0
    player = None
    is_key = False
    is_door = False
    tiles_group = pg.sprite.Group()
    player_group = pg.sprite.Group()
    all_sprites = pg.sprite.Group()
    player, level_x, level_y = generate_level(load_level('levels/' + generate_map()))
    game_process()


def add_points():
    global score
    points_added = random.randint(3, 15)
    score += points_added


def draw_text(surf, text, text_size, x, y):
    font = pg.font.Font(None, text_size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    pg.draw.rect(game_screen, BLACK, text_rect)
    surf.blit(text_surface, text_rect)


def start_process():
    intro_text = ["Key Finder",
                  "",
                  "Правила игры:",
                  "Вам необходимо найти ключ в одном из ящиков.",
                  "С каждым ходом количество очков уменьшается на единицу,",
                  "поэтому старайтесь выбирать оптимальный маршрут до того или иного",
                  "ящика, когда проверяете свою интуицию.",
                  "Если пол загорелся зеленым, то Вы заработали от 3 до 15 дополнительных очков."
                  "",
                  "Управление:",
                  "Стрелочки - перемещение",
                  "Пробел - сломать ящик и войти в дверь",
                  "n - сделать музыку тише, m - громче"
                  "",
                  "Для начала игры нажмите пробел."]

    menu_bg = load_image('menu_bg.png', 1)
    menu_bg = pg.transform.scale(menu_bg, size(current_map))
    game_screen.blit(menu_bg, (0, 0))
    font = pg.font.Font(None, 24)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, BLACK)
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        text_bg = (intro_rect[0] - 5, intro_rect[1] - 5, intro_rect[2] + 10, intro_rect[3] + 10)
        pg.draw.rect(game_screen, WHITE, text_bg)
        game_screen.blit(string_rendered, intro_rect)

    menu_running = True
    global music_volume
    global all_sprites

    all_sprites = pg.sprite.Group()

    while menu_running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    menu_running = False
                    game_process()

                elif event.key == pg.K_n:
                    if music_volume > 0:
                        music_volume -= 0.1
                elif event.key == pg.K_m:
                    if music_volume < 1:
                        music_volume += 0.1

        pg.mixer.music.set_volume(music_volume)
        all_sprites.draw(game_screen)
        all_sprites.update()
        pg.display.flip()
        draw_text(game_screen, 'Громкость музыки: ' + str(int(music_volume * 100)) + '%',
                  24, 100, size(current_map)[1] - 25)
        clock.tick(FPS)


class Firework(pg.sprite.Sprite):

    def __init__(self, win_flag, *group):
        super().__init__(*group)

        self.len = random.randint(1, 4)

        self.image = pg.Surface((self.len, self.len))
        if win_flag:
            pg.draw.circle(self.image, GREEN, (self.len // 2, self.len // 2), self.len // 2)
        else:
            pg.draw.circle(self.image, RED, (self.len // 2, self.len // 2), self.len // 2)
        self.rect = self.image.get_rect()
        self.x = self.rect.x = random.randrange(size(current_map)[0])
        self.y = self.rect.y = random.randrange(size(current_map)[1])

    def update(self):
        self.x += 0.05
        self.y += 0.1 * (self.len // 2)
        self.rect.x = self.x % size(current_map)[0]
        self.rect.y = self.y % size(current_map)[1]


is_win = True


def finish_process():
    global boxes_cnt, is_win
    win_text = ["Поздравляю! Вы победили!",
                "Количество очков:" + str(score),
                "Осталось коробок:" + str(boxes_cnt)]
    lose_text = ["К сожалению, вы проиграли :("]
    if is_key and is_door:
        current_text = win_text
        is_win = True
    else:
        current_text = lose_text
        is_win = False
    finish_bg = load_image('menu_bg.png', 1)
    finish_bg = pg.transform.scale(finish_bg, size(current_map))
    game_screen.blit(finish_bg, (0, 0))
    font = pg.font.Font(None, 24)
    text_coord = 50
    for line in current_text:
        string_rendered = font.render(line, True, BLACK)
        finish_rect = string_rendered.get_rect()
        text_coord += size(current_map)[0] / 10
        finish_rect.top = text_coord + 50
        finish_rect.x = text_coord + 80
        text_coord += finish_rect.height
        text_bg = (finish_rect[0] - 5, finish_rect[1] - 5, finish_rect[2] + 10, finish_rect[3] + 10)
        pg.draw.rect(game_screen, WHITE, text_bg)
        game_screen.blit(string_rendered, finish_rect)

    finish_running = True

    global music_volume
    global all_sprites
    all_sprites = pg.sprite.Group()

    for _ in range(70):
        Firework(is_win, all_sprites)

    while finish_running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    finish_running = False
                    restart_game()

                elif event.key == pg.K_n:
                    if music_volume > 0:
                        music_volume -= 0.1
                elif event.key == pg.K_m:
                    if music_volume < 1:
                        music_volume += 0.1

        all_sprites.draw(game_screen)
        all_sprites.update()
        pg.mixer.music.set_volume(music_volume)
        pg.display.flip()
        draw_text(game_screen, 'Громкость музыки: ' + str(int(music_volume * 100)) + '%',
                  24, 100, size(current_map)[1] - 25)

        clock.tick(FPS)


def game_process():

    running = True
    global score
    global is_door
    global music_volume

    while running:
        for event in pg.event.get():
            if score <= 0:
                finish_process()
            if event.type == pg.QUIT:
                running = False
                terminate()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT or event.key == pg.K_a:
                    step_sound.play()
                    player.update(-tile_width, 0, 'left')
                    player.image = player_image_rotate
                    score -= 1
                    is_door = False
                elif event.key == pg.K_RIGHT or event.key == pg.K_d:
                    step_sound.play()
                    player.update(tile_width, 0, 'right')
                    player.image = player_image
                    score -= 1
                    is_door = False
                elif event.key == pg.K_UP or event.key == pg.K_w:
                    step_sound.play()
                    player.update(0, -tile_height, 'up')
                    score -= 1
                    is_door = False
                elif event.key == pg.K_DOWN or event.key == pg.K_s:
                    step_sound.play()
                    player.update(0, tile_height, 'down')
                    score -= 1
                    is_door = False

                elif event.key == pg.K_n:
                    if music_volume > 0:
                        music_volume -= 0.1
                elif event.key == pg.K_m:
                    if music_volume < 1:
                        music_volume += 0.1

                elif event.key == pg.K_SPACE:
                    player.broke_block()
                    if is_door and is_key:
                        finish_process()

        pg.mixer.music.set_volume(music_volume)
        tiles_group.draw(game_screen)
        player_group.draw(game_screen)
        draw_text(game_screen, 'Очки: ' + str(score), 24, 50, 10)
        draw_text(game_screen, 'Громкость музыки: ' + str(int(music_volume * 100)) + '%',
                  24, 100, size(current_map)[1] - 25)
        draw_text(game_screen, 'Ящиков на поле:' + str(boxes_cnt), 24, size(current_map)[0] - 100, 10)
        if is_door and not is_key:
            draw_text(game_screen, 'Сначала найди ключ!', 24, size(current_map)[0] / 2, 10)
        if is_key:
            draw_text(game_screen, 'Ключ найден! Беги к двери!', 24, size(current_map)[0] / 2, 10)
        pg.display.flip()
        clock.tick(FPS)

    pg.quit()


start_process()
