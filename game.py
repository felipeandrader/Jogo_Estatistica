import pygame
import random
import math
import menu

pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.joystick.init()

SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
GAME_HEIGHT = int(SCREEN_HEIGHT * 0.70)
GRAPH_HEIGHT = SCREEN_HEIGHT - GAME_HEIGHT
GAME_WIDTH = SCREEN_WIDTH
GRAPH_AREA_WIDTH = SCREEN_WIDTH
GRAPH_WIDTH_PER_PLOT = GRAPH_AREA_WIDTH // 3
GRAPH_X_SPLIT_1 = GRAPH_WIDTH_PER_PLOT
GRAPH_X_SPLIT_2 = GRAPH_WIDTH_PER_PLOT * 2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
LIGHT_BLUE = (135, 206, 250)
PLAYER_COLOR = (0, 100, 255)
BULLET_COLOR = (10, 10, 10)
GRAPH_YELLOW = (255, 215, 0)
SCORE_POINT_COLOR = (0, 255, 255)
FITTING_COLOR = (255, 0, 0)

SCORE_TO_BOSS = 20000

NEW_COLOR_NAME = "orange"
NEW_COLOR_RGB = (255, 165, 0)

ITEM_COLORS = {
    "red": (255, 50, 50),
    "green": (50, 255, 50),
    "purple": (150, 50, 255),
    NEW_COLOR_NAME: NEW_COLOR_RGB
}
COLOR_TYPES = list(ITEM_COLORS.keys())

ITEM_PROBABILITIES = {
    "red": 0.40,
    "green": 0.25,
    "purple": 0.20,
    "orange": 0.15
}

ITEM_SCORES = {
    "red": 200,
    "green": 400,
    "purple": 800,
    "orange": 1600
}

ITEM_SPAWN_RATE = 30
ITEM_INITIAL_SPEED = 8
ITEM_SPEED_INCREASE = 1.5
ITEM_SPEED_INTERVAL = 15.0

BULLET_SPEED = 20
BULLET_WIDTH = 35
BULLET_HEIGHT = 8
SHOOT_COOLDOWN = 200
PLAYER_MAX_VELOCITY = 600
BOSS_IMAGE_WIDTH = 125
BOSS_IMAGE_HEIGHT = 76

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), vsync=1)
pygame.display.set_caption("Monkey Runners")
clock = pygame.time.Clock()

try:
    title_font = pygame.font.Font("source/LuckiestGuy-Regular.ttf", 64)
    second_font = pygame.font.Font("source/LuckiestGuy-Regular.ttf", 26)
except:
    print("AVISO: Fonte 'LuckiestGuy-Regular.ttf' não encontrada em 'source/'. Usando Arial.")
    title_font = pygame.font.SysFont("Arial", 64, bold=True)
    second_font = pygame.font.SysFont("Arial", 26, bold=True)
main_font = pygame.font.SysFont("Consolas", 18)

joysticks = []
JOYSTICK_DEADZONE = 0.1
for i in range(pygame.joystick.get_count()):
    joy = pygame.joystick.Joystick(i)
    joy.init()
    joysticks.append(joy)

try:
    pygame.mixer.music.load("source/musica.mp3")
    pygame.mixer.music.set_volume(0.05)
except Exception as e:
    print(f"AVISO: Música não carregada: {e}")

try:
    hit_sound = pygame.mixer.Sound("source/som_de_hit.wav")
    hit_sound.set_volume(0.1)
except Exception as e:
    print(f"AVISO: Som de hit não carregado: {e}")
    hit_sound = None

try:
    pop_sound = pygame.mixer.Sound("source/estorar_balao.wav")
    pop_sound.set_volume(0.1)
except Exception as e:
    print(f"AVISO: Som de estouro não carregado: {e}")
    pop_sound = None

try:
    menu_bg = pygame.image.load("source/menu_.png").convert()
    menu_bg = pygame.transform.scale(menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    menu_bg = None

player_width = 110
player_height = 90
p1_animation_frames = []
p1_filenames = ["source/macaco1.png", "source/macaco2.png", "source/macaco3.png"]

try:
    for filename in p1_filenames:
        image = pygame.image.load(filename).convert_alpha()
        image = pygame.transform.scale(image, (player_width, player_height))
        p1_animation_frames.append(image)
except:
    print("AVISO: Imagens do macaco P1 não encontradas.")
    p1_animation_frames = []

p2_animation_frames = []
p2_filenames = ["source/mamaco1.png", "source/mamaco2.png", "source/mamaco3.png"]

try:
    for filename in p2_filenames:
        image = pygame.image.load(filename).convert_alpha()
        image = pygame.transform.scale(image, (player_width, player_height))
        p2_animation_frames.append(image)
except:
    print("AVISO: Imagens do mamaco P2 não encontradas.")
    p2_animation_frames = []

ITEM_IMAGE_WIDTH = 60
ITEM_IMAGE_HEIGHT = 80
EXPLOSION_WIDTH = 120
EXPLOSION_HEIGHT = 120

balloon_images = {}
try:
    balloon_images["red"] = pygame.image.load("source/balaovermelho.png").convert_alpha()
    balloon_images["red"] = pygame.transform.scale(balloon_images["red"], (ITEM_IMAGE_WIDTH, ITEM_IMAGE_HEIGHT))
    balloon_images["green"] = pygame.image.load("source/balaoverde.png").convert_alpha()
    balloon_images["green"] = pygame.transform.scale(balloon_images["green"], (ITEM_IMAGE_WIDTH, ITEM_IMAGE_HEIGHT))
    balloon_images["purple"] = pygame.image.load("source/balaoroxo.png").convert_alpha()
    balloon_images["purple"] = pygame.transform.scale(balloon_images["purple"], (ITEM_IMAGE_WIDTH, ITEM_IMAGE_HEIGHT))
    balloon_images["orange"] = pygame.image.load("source/balaoamarelo.png").convert_alpha()
    balloon_images["orange"] = pygame.transform.scale(balloon_images["orange"], (ITEM_IMAGE_WIDTH, ITEM_IMAGE_HEIGHT))
except Exception as e:
    print(f"AVISO: Falha ao carregar balões: {e}")
    balloon_images = {}

explosion_animations = {}
def load_explosion(color_key, filenames):
    frames = []
    try:
        for f in filenames:
            img = pygame.image.load(f).convert_alpha()
            img = pygame.transform.scale(img, (EXPLOSION_WIDTH, EXPLOSION_HEIGHT))
            frames.append(img)
        explosion_animations[color_key] = frames
    except:
        explosion_animations[color_key] = []

load_explosion("orange", ["source/amarelo1.png", "source/amarelo2.png", "source/amarelo3.png", "source/amarelo4.png"])
load_explosion("red", ["source/vermelho1.png", "source/vermelho2.png", "source/vermelho3.png", "source/vermelho4.png"])
load_explosion("purple", ["source/roxo1.png", "source/roxo2.png", "source/roxo3.png", "source/roxo4.png"])
load_explosion("green", ["source/verde1.png", "source/verde2.png", "source/verde3.png", "source/verde4.png"])

try:
    boss_sprite = pygame.image.load("source/balaoboss.png").convert_alpha()
    boss_sprite = pygame.transform.scale(boss_sprite, (BOSS_IMAGE_WIDTH, BOSS_IMAGE_HEIGHT))
except:
    boss_sprite = None

try:
    life_sprite = pygame.image.load("source/vida_do_jogador.png").convert_alpha()
    life_sprite = pygame.transform.scale(life_sprite, (64, 64))
except:
    life_sprite = None

bullet_img = None
try:
    bullet_img = pygame.image.load("source/projetil.png").convert_alpha()
    bullet_img = pygame.transform.scale(bullet_img, (BULLET_WIDTH, BULLET_HEIGHT))
except:
    bullet_img = None

class ParallaxBackground:
    def __init__(self, screen_width, screen_height, image_files, speeds):
        self.width = screen_width
        self.height = screen_height
        self.layers = []
        for idx, filename in enumerate(image_files):
            try:
                if idx == 0:
                    img = pygame.image.load(filename).convert()
                else:
                    img = pygame.image.load(filename).convert_alpha()
                img = pygame.transform.scale(img, (screen_width, screen_height))
                self.layers.append({
                    "image": img,
                    "speed_factor": speeds[idx],
                    "x": 0.0
                })
            except pygame.error:
                surf = pygame.Surface((screen_width, screen_height))
                color_val = (50 + idx * 20) % 255
                surf.fill((color_val, 100, 200))
                if idx > 0: surf.set_colorkey((0,0,0)); surf.set_alpha(150)
                self.layers.append({"image": surf, "speed_factor": speeds[idx], "x": 0.0})

    def update(self, game_speed, dt):
        for layer in self.layers:
            move_amount = (game_speed * layer["speed_factor"])
            layer["x"] -= move_amount
            if layer["x"] <= -self.width:
                layer["x"] += self.width

    def draw(self, screen):
        for layer in self.layers:
            x_pos = int(layer["x"])
            screen.blit(layer["image"], (x_pos, 0))
            if x_pos < 0:
                screen.blit(layer["image"], (x_pos + self.width, 0))

def get_empirical_prob(item_type, current_counts):
    total = sum(current_counts.values())
    return current_counts.get(item_type, 0) / float(total) if total > 0 else 0.0

def draw_histogram(surface, data_dict, data_keys, data_colors, title, bounds_rect, expected_prob_func=None):
    pygame.draw.rect(screen, GRAY, bounds_rect)
    graph_x_start = bounds_rect.left + 30
    graph_y_bottom = bounds_rect.bottom - 30
    title_text = second_font.render(title, True, WHITE)
    surface.blit(title_text, (bounds_rect.left + (bounds_rect.width - title_text.get_width()) // 2, bounds_rect.top + 10))
    total_count = sum(data_dict.values())
    if not data_keys: return
    max_obs_count = max(data_dict.values()) if data_dict.values() else 1
    max_val = max_obs_count
    bar_width = int((bounds_rect.width - 60) / (len(data_keys) * 1.5 + 0.5))
    bar_spacing = int(bar_width * 0.5)
    for i, item_type in enumerate(data_keys):
        count = data_dict.get(item_type, 0)
        color = data_colors.get(item_type, WHITE)
        bar_height = int((count / max_val) * (bounds_rect.height - 100)) if max_val > 0 else 0
        bar_x = int(graph_x_start + (i * (bar_width + bar_spacing)))
        bar_y = int(graph_y_bottom - bar_height)
        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, color, bar_rect)
        if title == "Contagem": label_display = str(count)
        else: label_display = item_type
        label_text = main_font.render(label_display, True, WHITE)
        surface.blit(label_text, (bar_x + (bar_width - label_text.get_width()) // 2, graph_y_bottom + 5))
        if total_count > 0:
            prob_emp = (count / total_count) * 100
            count_label = f"{prob_emp:.0f}%"
        else:
            count_label = str(count)
        count_text = main_font.render(count_label, True, WHITE)
        surface.blit(count_text, (bar_x + (bar_width - count_text.get_width()) // 2, bar_y - 25))

def draw_scatter_plot(surface, data_points, bounds_rect, elapsed_time):
    pygame.draw.rect(screen, GRAY, bounds_rect) 
    title = second_font.render("Pontuação x Tempo", True, WHITE)
    surface.blit(title, (bounds_rect.left + (bounds_rect.width - title.get_width()) // 2, bounds_rect.top + 20))
    plot = pygame.Rect(bounds_rect.left + 60, bounds_rect.top + 50, bounds_rect.width - 90, bounds_rect.height - 100)
    pygame.draw.line(surface, WHITE, plot.bottomleft, plot.topleft, 2)
    pygame.draw.line(surface, WHITE, plot.bottomleft, plot.bottomright, 2)
    if len(data_points) < 2: return
    max_t = max(data_points[-1][0], elapsed_time, 1)
    max_s = max([p[1] for p in data_points] + [2000])
    scaled = []
    for t, s in data_points:
        sx = plot.left + int((t / max_t) * plot.width)
        sy = plot.bottom - int((s / max_s) * plot.height)
        scaled.append((sx, sy))
        pygame.draw.circle(surface, SCORE_POINT_COLOR, (sx, sy), 3)
    if len(scaled) >= 2: pygame.draw.lines(surface, SCORE_POINT_COLOR, False, scaled, 2)

def draw_player_lives(surface, lives):
    size = 20
    spacing = 20
    margin = 5
    offset_x = 50
    total_width = size * lives + spacing * max(0, lives - 1)
    for i in range(lives):
        if life_sprite: surface.blit(life_sprite, (SCREEN_WIDTH - 50 - 5 - (20 * lives + 20 * (lives-1)) + i * 40, 5))
        else: pygame.draw.rect(surface, (220, 50, 50), (SCREEN_WIDTH - 100 + i * 25, 5, 20, 20))

class Particle:
    def __init__(self, x, y, color, velocity, lifetime, size=4):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
    
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 200 * dt
        self.lifetime -= dt
        return self.lifetime > 0
    
    def draw(self, surface):
        size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)

def create_explosion_particles(x, y, color, count=15):
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(100, 300)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed - 100
        lifetime = random.uniform(0.3, 0.8)
        size = random.randint(3, 8)
        particles.append(Particle(x, y, color, (vx, vy), lifetime, size))
    return particles

current_score = 0
boss_stats_counts = None
boss_stats_intervals = None
boss_score_vs_time = None
boss_snapshot_elapsed = 0.0
player_lives = 3

def run_game(screen, num_players=1):
    current_item_speed = ITEM_INITIAL_SPEED
    last_speed_increase_time = pygame.time.get_ticks()
    items = []
    bullets = []
    item_spawn_timer = 0
    pos_hit_until_ms = 0
    EXPLOSION_ANIMATION_SPEED = 0.35
    p1_controller_id = None
    p2_controller_id = None
    
    if len(joysticks) >= 1:
        if num_players == 1:
            p1_controller_id = 0
        elif num_players == 2:
            if len(joysticks) == 1:
                p1_controller_id = None; p2_controller_id = 0
            else:
                p1_controller_id = 0; p2_controller_id = 1

    players_list = []
    players_list.append({
        "rect": pygame.Rect(30, GAME_HEIGHT // 3, player_width, player_height),
        "id": 0, "color": PLAYER_COLOR, "joy_id": p1_controller_id, "last_shot_time": 0
    })

    if num_players == 2:
        players_list.append({
            "rect": pygame.Rect(30, (GAME_HEIGHT // 3) * 2, player_width, player_height),
            "id": 1, "color": (255, 50, 50), "joy_id": p2_controller_id, "last_shot_time": 0
        })

    player_frame_index = 0
    player_last_frame_update = pygame.time.get_ticks()
    PLAYER_ANIMATION_SPEED_MS = 100
    PLAYER_ANIMATION_SEQUENCE = [1, 0, 2, 0]

    global current_score, player_lives, ITEM_SPEED_INTERVAL, ITEM_SPEED_INCREASE
    current_score = 0
    score_vs_time = [(0.0, 0)]
    start_time_ms = pygame.time.get_ticks()
    stats_counts = {"red": 0, "green": 0, "purple": 0, "orange": 0}
    stats_intervals = {"0-0.7s": 0, "0.7-1.4": 0, "1.4-2.0": 0, "2.0s+": 0}
    INTERVAL_KEYS = list(stats_intervals.keys())
    INTERVAL_COLORS = {key: GRAPH_YELLOW for key in INTERVAL_KEYS}
    last_collection_time = pygame.time.get_ticks()
    PARALLAX_SPEED_MULTIPLIER = 0.2

    bg_files = [
        "source/forest_sky.png", "source/forest_short.png", "source/forest_mountain.png",
        "source/forest_moon.png", "source/forest_mid.png", "source/forest_long.png", "source/forest_back.png"
    ]
    bg_speeds = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0]
    parallax_bg = ParallaxBackground(SCREEN_WIDTH, SCREEN_HEIGHT, bg_files, bg_speeds)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        current_time_ticks = pygame.time.get_ticks()
        elapsed_time_sec = (current_time_ticks - start_time_ms) / 1000.0

        if (current_time_ticks - last_speed_increase_time) / 1000.0 >= ITEM_SPEED_INTERVAL:
            current_item_speed += ITEM_SPEED_INCREASE
            last_speed_increase_time = current_time_ticks
            
        parallax_bg.update(current_item_speed * PARALLAX_SPEED_MULTIPLIER, dt)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 2:
                    triggered_joy_id = event.joy
                    firing_player = None
                    for p in players_list:
                        if p["joy_id"] == triggered_joy_id:
                            firing_player = p; break
                    if firing_player and (current_time_ticks - firing_player["last_shot_time"] > SHOOT_COOLDOWN):
                        bullet_rect = pygame.Rect(firing_player["rect"].right, firing_player["rect"].centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT)
                        bullets.append(bullet_rect)
                        firing_player["last_shot_time"] = current_time_ticks
            if event.type == pygame.KEYDOWN:
                firing_player = None
                if event.key == pygame.K_SPACE:
                    firing_player = next((p for p in players_list if p["id"] == 0), None)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    firing_player = next((p for p in players_list if p["id"] == 1), None)
                if firing_player and (current_time_ticks - firing_player["last_shot_time"] > SHOOT_COOLDOWN):
                    bullet_rect = pygame.Rect(firing_player["rect"].right, firing_player["rect"].centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT)
                    bullets.append(bullet_rect)
                    firing_player["last_shot_time"] = current_time_ticks

        keys = pygame.key.get_pressed()
        for p in players_list:
            move_x = 0.0
            move_y = 0.0
            if p["id"] == 0:
                if keys[pygame.K_w]: move_y -= 1.0
                if keys[pygame.K_s]: move_y += 1.0
                if keys[pygame.K_a]: move_x -= 1.0
                if keys[pygame.K_d]: move_x += 1.0
                if num_players == 1:
                    if keys[pygame.K_UP]: move_y -= 1.0
                    if keys[pygame.K_DOWN]: move_y += 1.0
                    if keys[pygame.K_LEFT]: move_x -= 1.0
                    if keys[pygame.K_RIGHT]: move_x += 1.0
            elif p["id"] == 1:
                if keys[pygame.K_UP]: move_y -= 1.0
                if keys[pygame.K_DOWN]: move_y += 1.0
                if keys[pygame.K_LEFT]: move_x -= 1.0
                if keys[pygame.K_RIGHT]: move_x += 1.0
            
            if p["joy_id"] is not None and p["joy_id"] < len(joysticks):
                try:
                    joy = joysticks[p["joy_id"]]
                    axis_x = joy.get_axis(0)
                    axis_y = joy.get_axis(1)
                    if abs(axis_x) > JOYSTICK_DEADZONE: move_x += axis_x
                    if abs(axis_y) > JOYSTICK_DEADZONE: move_y += axis_y
                except: pass

            length = math.hypot(move_x, move_y)
            if length > 1: move_x /= length; move_y /= length
            p["rect"].x += move_x * PLAYER_MAX_VELOCITY * dt
            p["rect"].y += move_y * PLAYER_MAX_VELOCITY * dt
            if p["rect"].top < 0: p["rect"].top = 0
            if p["rect"].bottom > GAME_HEIGHT: p["rect"].bottom = GAME_HEIGHT
            if p["rect"].left < 0: p["rect"].left = 0
            if p["rect"].right > GAME_WIDTH: p["rect"].right = GAME_WIDTH

        item_spawn_timer += 1
        if item_spawn_timer >= ITEM_SPAWN_RATE:
            item_spawn_timer = 0
            item_type = random.choices(COLOR_TYPES, weights=[ITEM_PROBABILITIES[t] for t in COLOR_TYPES], k=1)[0]
            items.append({
                "rect": pygame.Rect(GAME_WIDTH + ITEM_IMAGE_WIDTH, random.randint(0, GAME_HEIGHT - ITEM_IMAGE_HEIGHT), ITEM_IMAGE_WIDTH, ITEM_IMAGE_HEIGHT), 
                "color": ITEM_COLORS[item_type], 
                "type": item_type, 
                "image": balloon_images.get(item_type),
                "exploding": False, 
                "explosion_frame_index": 0.0
            })

        for i in range(len(bullets) - 1, -1, -1):
            bullets[i].x += BULLET_SPEED
            if bullets[i].left > GAME_WIDTH: bullets.pop(i)

        for i in range(len(items) - 1, -1, -1):
            item = items[i]
            if item["exploding"]:
                item["explosion_frame_index"] += EXPLOSION_ANIMATION_SPEED
                anim_frames = explosion_animations.get(item["type"], [])
                max_frames = len(anim_frames) if anim_frames else 0
                if max_frames == 0 or item["explosion_frame_index"] >= max_frames:
                    items.pop(i)
                continue

            item["rect"].x -= current_item_speed
            if item["rect"].right < 0:
                items.pop(i); continue

            if current_time_ticks >= pos_hit_until_ms:
                hit = False
                for p in players_list:
                    if p["rect"].colliderect(item["rect"]):
                        if hit_sound: hit_sound.play()
                        player_lives -= 1; pos_hit_until_ms = current_time_ticks + 1000; hit = True
                        break
                if hit:
                    items.pop(i)
                    if player_lives <= 0: pygame.mixer.music.stop(); return "GAME_OVER"
                    continue

        for b_idx in range(len(bullets) - 1, -1, -1):
            hit = False
            for i_idx in range(len(items) - 1, -1, -1):
                if items[i_idx]["exploding"]: continue
                if bullets[b_idx].colliderect(items[i_idx]["rect"]):
                    item_type = items[i_idx]["type"]
                    current_score += ITEM_SCORES[item_type]
                    score_vs_time.append((elapsed_time_sec, current_score))
                    stats_counts[item_type] += 1
                    interval = (current_time_ticks - last_collection_time) / 1000.0
                    last_collection_time = current_time_ticks
                    if interval < 0.7: stats_intervals["0-0.7s"] += 1
                    elif interval < 1.4: stats_intervals["0.7-1.4"] += 1
                    elif interval < 2.0: stats_intervals["1.4-2.0"] += 1
                    else: stats_intervals["2.0s+"] += 1
                    if pop_sound: pop_sound.play()
                    if item_type in explosion_animations and explosion_animations[item_type]:
                        items[i_idx]["exploding"] = True
                        items[i_idx]["explosion_frame_index"] = 0.0
                    else:
                        items.pop(i_idx)
                    bullets.pop(b_idx); hit = True; break
            if hit: continue

        if current_score >= SCORE_TO_BOSS:
            pygame.mixer.music.stop()
            global boss_stats_counts, boss_stats_intervals, boss_score_vs_time, boss_snapshot_elapsed
            boss_stats_counts = stats_counts.copy()
            boss_stats_intervals = stats_intervals.copy()
            boss_score_vs_time = score_vs_time.copy()
            boss_snapshot_elapsed = elapsed_time_sec
            return "BOSS_FIGHT"

        if (current_time_ticks - player_last_frame_update > PLAYER_ANIMATION_SPEED_MS):
            player_last_frame_update = current_time_ticks
            player_frame_index = (player_frame_index + 1) % len(PLAYER_ANIMATION_SEQUENCE)

        screen.fill(BLACK)
        parallax_bg.draw(screen)
        frame_idx = PLAYER_ANIMATION_SEQUENCE[player_frame_index]
        for p in players_list:
            draw_img = None
            if p["id"] == 0:
                if p1_animation_frames: draw_img = p1_animation_frames[frame_idx]
            elif p["id"] == 1:
                if p2_animation_frames: draw_img = p2_animation_frames[frame_idx]
                else:
                    if p1_animation_frames:
                        draw_img = p1_animation_frames[frame_idx].copy()
                        draw_img.fill((255, 100, 100), special_flags=pygame.BLEND_MULT)
            
            if current_time_ticks < pos_hit_until_ms:
                 if (current_time_ticks // 150) % 2 == 0: 
                     if draw_img: screen.blit(draw_img, p["rect"].topleft)
                     else: pygame.draw.rect(screen, p["color"], p["rect"])
            else:
                if draw_img: screen.blit(draw_img, p["rect"].topleft)
                else: pygame.draw.rect(screen, p["color"], p["rect"])

        for item in items:
            if item.get("exploding", False):
                frame_index = int(item["explosion_frame_index"])
                anim_frames = explosion_animations.get(item["type"], [])
                if anim_frames and 0 <= frame_index < len(anim_frames):
                    img = anim_frames[frame_index]
                    center_x, center_y = item["rect"].center
                    explosion_rect = img.get_rect()
                    explosion_rect.center = (center_x, center_y)
                    screen.blit(img, explosion_rect.topleft)
            elif item["image"]: 
                screen.blit(item["image"], item["rect"].topleft)
            else: 
                pygame.draw.circle(screen, item["color"], item["rect"].center, item["rect"].width // 2)

        for b in bullets:
            if bullet_img: screen.blit(bullet_img, b.topleft)
            else: pygame.draw.rect(screen, BULLET_COLOR, b)

        screen.blit(second_font.render(f"PONTUAÇÃO: {current_score}", True, WHITE), (10, 10))
        draw_player_lives(screen, player_lives)
        rect1 = pygame.Rect(0, GAME_HEIGHT, GRAPH_WIDTH_PER_PLOT, GRAPH_HEIGHT)
        rect2 = pygame.Rect(GRAPH_X_SPLIT_1, GAME_HEIGHT, GRAPH_WIDTH_PER_PLOT, GRAPH_HEIGHT)
        rect3 = pygame.Rect(GRAPH_X_SPLIT_2, GAME_HEIGHT, GRAPH_WIDTH_PER_PLOT, GRAPH_HEIGHT)
        draw_histogram(screen, stats_counts, COLOR_TYPES, ITEM_COLORS, "Contagem", rect1, lambda t: get_empirical_prob(t, stats_counts))
        draw_scatter_plot(screen, score_vs_time, rect2, elapsed_time_sec)
        draw_histogram(screen, stats_intervals, INTERVAL_KEYS, INTERVAL_COLORS, "Intervalo de Destruição", rect3, lambda k: get_empirical_prob(k, stats_intervals))
        pygame.draw.line(screen, WHITE, (0, GAME_HEIGHT), (SCREEN_WIDTH, GAME_HEIGHT), 3)
        pygame.draw.line(screen, WHITE, (GRAPH_X_SPLIT_1, GAME_HEIGHT), (GRAPH_X_SPLIT_1, SCREEN_HEIGHT), 3)
        pygame.draw.line(screen, WHITE, (GRAPH_X_SPLIT_2, GAME_HEIGHT), (GRAPH_X_SPLIT_2, SCREEN_HEIGHT), 3)
        pygame.display.flip()

BOSS_MAX_HP = 50
BOSS_MOVE_SPEED = 40
BOSS_ORBIT_RADIUS = 120
BOSS_ORBIT_SPEED = 1.5

def run_game_boss(screen, num_players=1):
    global current_score, player_lives
    bullets = []
    start_time_ms = pygame.time.get_ticks()
    
    players = []
    p1_joy = 0 if len(joysticks) > 0 else None
    players.append({"rect": pygame.Rect(100, GAME_HEIGHT // 3, player_width, player_height), "id": 0, "joy_id": p1_joy, "last_shot_time": 0, "color": PLAYER_COLOR})
    
    if num_players == 2:
        p2_joy = 1 if len(joysticks) > 1 else None
        players.append({"rect": pygame.Rect(100, (GAME_HEIGHT // 3) * 2, player_width, player_height), "id": 1, "joy_id": p2_joy, "last_shot_time": 0, "color": (255, 50, 50)})

    boss_rect = pygame.Rect(962, 262, BOSS_IMAGE_WIDTH, BOSS_IMAGE_HEIGHT)
    boss_hp = BOSS_MAX_HP
    boss_defeated = False
    victory_animation_timer = 0
    particles = []
    
    balloons = []
    hexagon = [(int(boss_rect.centerx + 150 * math.cos(math.radians(a))), int(boss_rect.centery + 150 * math.sin(math.radians(a)))) for a in [0, 60, 120, 180, 240, 300]]
    for i, pt in enumerate(hexagon):
        t = random.choice(COLOR_TYPES)
        balloons.append({"type": t, "rect": pygame.Rect(0, 0, 60, 80), "target": (i + 1) % 6, "exploding": False, "frame": 0.0})
        balloons[-1]["rect"].center = pt

    last_anim = pygame.time.get_ticks()
    anim_idx = 0

    while True:
        dt = clock.tick(60) / 1000.0
        current_time_ticks = pygame.time.get_ticks()
        now = current_time_ticks

        if boss_defeated:
            victory_animation_timer += dt
            if victory_animation_timer > 3.0:
                pygame.mixer.music.stop()
                return "GAME_OVER"
            if random.random() < 0.3:
                px = random.randint(100, SCREEN_WIDTH - 100)
                py = random.randint(50, GAME_HEIGHT - 50)
                particles.extend(create_explosion_particles(px, py, random.choice([(255, 215, 0), (50, 255, 50), (50, 200, 255)]), 5))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if not boss_defeated:
                if event.type == pygame.JOYBUTTONDOWN and event.button == 2:
                    triggered_joy_id = event.joy
                    shooter = next((p for p in players if p["joy_id"] == triggered_joy_id), None)
                    if shooter and (current_time_ticks - shooter["last_shot_time"] > SHOOT_COOLDOWN):
                        bullets.append(pygame.Rect(shooter["rect"].right, shooter["rect"].centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT))
                        shooter["last_shot_time"] = current_time_ticks
                
                if event.type == pygame.KEYDOWN:
                    firing_player = None
                    if event.key == pygame.K_SPACE:
                        firing_player = players[0] 
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        if num_players == 1: firing_player = players[0]
                        elif num_players == 2: firing_player = next((p for p in players if p["id"] == 1), None)

                    if firing_player and (current_time_ticks - firing_player["last_shot_time"] > SHOOT_COOLDOWN):
                        bullets.append(pygame.Rect(firing_player["rect"].right, firing_player["rect"].centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT))
                        firing_player["last_shot_time"] = current_time_ticks

        keys = pygame.key.get_pressed()
        for p in players:
            mx, my = 0, 0
            if p["id"] == 0:
                if keys[pygame.K_w]: my -= 1
                if keys[pygame.K_s]: my += 1
            else:
                if keys[pygame.K_UP]: my -= 1
                if keys[pygame.K_DOWN]: my += 1
            p["rect"].y += my * PLAYER_MAX_VELOCITY * dt
            p["rect"].clamp_ip(pygame.Rect(0, 0, GAME_WIDTH, GAME_HEIGHT))

        for b in balloons:
            if b["exploding"]:
                b["frame"] += 0.35
                if b["frame"] >= 4: balloons.remove(b)
                continue
            if len(hexagon) > 0:
                tx, ty = hexagon[b["target"]]
                cx, cy = b["rect"].center
                dx, dy = tx - cx, ty - cy
                dist = math.hypot(dx, dy)
                if dist < 5: b["target"] = (b["target"] + 1) % 6
                else:
                    b["rect"].x += (dx/dist) * 160 * dt
                    b["rect"].y += (dy/dist) * 160 * dt

        for blt in bullets[:]:
            blt.x += BULLET_SPEED
            if blt.left > SCREEN_WIDTH: bullets.remove(blt)
            
            if not boss_defeated and blt.colliderect(boss_rect):
                boss_hp -= 1
                bullets.remove(blt)
                if boss_hp <= 0:
                    boss_defeated = True
                    current_score += 10000
                continue

            for b in balloons:
                if not b["exploding"] and blt.colliderect(b["rect"]):
                    b["exploding"] = True
                    current_score += 500
                    if blt in bullets: bullets.remove(blt)

        for p in particles[:]:
            if not p.update(dt): particles.remove(p)

        screen.fill(BLACK)
        pygame.draw.rect(screen, LIGHT_BLUE, (0, 0, GAME_WIDTH, GAME_HEIGHT))
        if boss_sprite and not boss_defeated: screen.blit(boss_sprite, boss_rect)
        elif not boss_defeated: pygame.draw.rect(screen, (100, 0, 100), boss_rect)

        for p in players:
            pygame.draw.rect(screen, p["color"], p["rect"])

        for b in balloons:
            if b["exploding"]:
                frames = explosion_animations.get(b["type"], [])
                if frames: screen.blit(frames[min(int(b["frame"]), len(frames)-1)], b["rect"])
            else: screen.blit(balloon_images[b["type"]], b["rect"])
            
        for blt in bullets: pygame.draw.rect(screen, BULLET_COLOR, blt)
        for p in particles: p.draw(screen)

        if not boss_defeated:
             hp_text = main_font.render(f"BOSS HP: {boss_hp}", True, BLACK)
             screen.blit(hp_text, (boss_rect.centerx - 40, boss_rect.top - 20))
        
        pygame.display.flip()

def main():
    global joysticks, player_lives
    current_state = "MENU"
    selected_num_players = 1
    
    while True:
        if current_state == "MENU":
            result = menu.show_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT, title_font, main_font, menu_bg)
            if result == "PLAY":
                current_state = "GAME"; selected_num_players = 1; player_lives = 3
                try: pygame.mixer.music.play(-1)
                except: pass
            elif result == "PLAY_2P":
                current_state = "GAME"; selected_num_players = 2; player_lives = 3
                try: pygame.mixer.music.play(-1)
                except: pass
            elif result == "QUIT": break
        
        elif current_state == "GAME":
            result = run_game(screen, num_players=selected_num_players)
            if result == "GAME_OVER": current_state = "MENU"
            elif result == "BOSS_FIGHT": current_state = "BOSS"
            elif result == "QUIT": break
            
        elif current_state == "BOSS":
            result = run_game_boss(screen, num_players=selected_num_players)
            if result == "GAME_OVER": current_state = "MENU"
            elif result == "QUIT": break
            
    pygame.quit()

if __name__ == "__main__":
    main()