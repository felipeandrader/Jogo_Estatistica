import pygame
import random
import math
import menu  # Assume que existe um arquivo 'menu.py' para a tela inicial

# --- Constantes e Configurações ---
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768

# --- LAYOUT ---
GAME_HEIGHT = int(SCREEN_HEIGHT * 0.70)
GRAPH_HEIGHT = SCREEN_HEIGHT - GAME_HEIGHT
GAME_WIDTH = SCREEN_WIDTH
GRAPH_AREA_WIDTH = SCREEN_WIDTH

GRAPH_WIDTH_PER_PLOT = GRAPH_AREA_WIDTH // 3
GRAPH_X_SPLIT_1 = GRAPH_WIDTH_PER_PLOT
GRAPH_X_SPLIT_2 = GRAPH_WIDTH_PER_PLOT * 2

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
LIGHT_BLUE = (135, 206, 250)
PLAYER_COLOR = (0, 100, 255)
BULLET_COLOR = (10, 10, 10)
GRAPH_YELLOW = (255, 215, 0)
FITTING_COLOR = (255, 0, 0)
SCORE_POINT_COLOR = (0, 255, 255)

# SCORE TO UNLOCK BOSS FIGHT
SCORE_TO_BOSS = 200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

# --- CONFIGURAÇÕES DE PROBABILIDADE E PONTUAÇÃO ---
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

# Spawn / movimento
ITEM_SPAWN_RATE = 30
ITEM_INITIAL_SPEED = 8
# VALORES DE DIFICULDADE
ITEM_SPEED_INCREASE = 1.5
ITEM_SPEED_INTERVAL = 15.0  # Aumento de velocidade a cada 15 segundos

BULLET_SPEED = 20
BULLET_WIDTH = 35
BULLET_HEIGHT = 4
SHOOT_COOLDOWN = 200

# Velocidade do jogador em pixels por segundo
PLAYER_MAX_VELOCITY = 600

# Tamanho da imagem do boss
BOSS_IMAGE_WIDTH = 125
BOSS_IMAGE_HEIGHT = 76

# --- Inicialização do Pygame ---
pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.joystick.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Monkey Runners")
clock = pygame.time.Clock()
main_font = pygame.font.SysFont("Consolas", 18)
# Tenta carregar a fonte, se não der usa a padrão
try:
    title_font = pygame.font.Font("LuckiestGuy-Regular.ttf", 64)
    second_font = pygame.font.Font("LuckiestGuy-Regular.ttf", 26)
except:
    title_font = pygame.font.SysFont("Arial", 64, bold=True)
    second_font = pygame.font.SysFont("Arial", 26, bold=True)

# --- Configuração dos Joysticks Globais ---
joysticks = []
JOYSTICK_DEADZONE = 0.1

for i in range(pygame.joystick.get_count()):
    joy = pygame.joystick.Joystick(i)
    joy.init()
    joysticks.append(joy)
    print(f"Controle {i} detectado: {joy.get_name()}")

if not joysticks:
    print("Nenhum controle detectado. Usando teclado.")

# --- Carregar Áudio ---
try:
    MUSIC_FILE = "musica.mp3"
    VOLUME = 0.05
    pygame.mixer.music.load(MUSIC_FILE)
    pygame.mixer.music.set_volume(VOLUME)
    print(f"Música {MUSIC_FILE} carregada.")
except pygame.error:
    print(f"AVISO: Não foi possível carregar o arquivo '{MUSIC_FILE}'.")

# -- Carregar Som ---
try:
    HIT_SOUND_FILE = "som_de_hit.wav"
    hit_sound = pygame.mixer.Sound(HIT_SOUND_FILE)
    hit_sound.set_volume(0.1)
    print(f"Efeito sonoro {HIT_SOUND_FILE} carregado.")
except pygame.error:
    print(f"AVISO: Não foi possível carregar o arquivo '{HIT_SOUND_FILE}'.")

# --- Carregar background do menu ---
try:
    MENU_BG_FILE = "menu_.png"
    menu_bg = pygame.image.load(MENU_BG_FILE).convert()
    menu_bg = pygame.transform.scale(menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    print(f"Background {MENU_BG_FILE} carregado.")
except pygame.error:
    menu_bg = None
    print(f"AVISO: Não foi possível carregar '{MENU_BG_FILE}'.")


# --- Carregar Imagem dos Jogadores ---
player_width = 110
player_height = 90

# Player 1 (MACACO)
p1_animation_frames = []
p1_filenames = ["macaco1.png", "macaco2.png", "macaco3.png"]

try:
    for filename in p1_filenames:
        image = pygame.image.load(filename).convert_alpha()
        image = pygame.transform.scale(image, (player_width, player_height))
        p1_animation_frames.append(image)
    print(f"Animação do Player 1 (Macaco) carregada.")
except pygame.error as e:
    print(f"ERRO P1: Não foi possível carregar 'macaco*.png'. Detalhes: {e}")
    p1_animation_frames = []

# Player 2 (MAMACO)
p2_animation_frames = []
p2_filenames = ["mamaco1.png", "mamaco2.png", "mamaco3.png"]

try:
    for filename in p2_filenames:
        image = pygame.image.load(filename).convert_alpha()
        image = pygame.transform.scale(image, (player_width, player_height))
        p2_animation_frames.append(image)
    print(f"Animação do Player 2 (Mamaco) carregada.")
except pygame.error as e:
    print(f"ERRO P2: Não foi possível carregar 'mamaco*.png'. Usando fallback. Detalhes: {e}")
    p2_animation_frames = []


# --- Carregar Imagens dos Balões (Inimigos) ---
ITEM_IMAGE_WIDTH = 60  # Tamanho do balão NORMAL
ITEM_IMAGE_HEIGHT = 80 # Tamanho do balão NORMAL

# --- NOVAS VARIÁVEIS INDEPENDENTES PARA A EXPLOSÃO ---
EXPLOSION_WIDTH = 120  # Tamanho da explosão (maior que o balão)
EXPLOSION_HEIGHT = 120 # Tamanho da explosão

balloon_images = {}
try:
    balloon_images["red"] = pygame.image.load("balaovermelho.png").convert_alpha()
    balloon_images["red"] = pygame.transform.scale(balloon_images["red"], (ITEM_IMAGE_WIDTH, ITEM_IMAGE_HEIGHT))

    balloon_images["green"] = pygame.image.load("balaoverde.png").convert_alpha()
    balloon_images["green"] = pygame.transform.scale(balloon_images["green"], (ITEM_IMAGE_WIDTH, ITEM_IMAGE_HEIGHT))

    balloon_images["purple"] = pygame.image.load("balaoroxo.png").convert_alpha()
    balloon_images["purple"] = pygame.transform.scale(balloon_images["purple"], (ITEM_IMAGE_WIDTH, ITEM_IMAGE_HEIGHT))

    balloon_images["orange"] = pygame.image.load("balaoamarelo.png").convert_alpha()
    balloon_images["orange"] = pygame.transform.scale(balloon_images["orange"], (ITEM_IMAGE_WIDTH, ITEM_IMAGE_HEIGHT))
    print("Todas as imagens de balões foram carregadas com sucesso.")

except pygame.error as e:
    print(f"ERRO: Não foi possível carregar uma ou mais imagens de balões. Usando círculos. Detalhes: {e}")
    balloon_images = {}

# --- Carregar Imagens da Explosão (Animação) ---
explosion_animations = {}

# Animação para balão AMARELO
yellow_explosion_frames = []
yellow_filenames = ["amarelo1.png", "amarelo2.png", "amarelo3.png", "amarelo4.png"]
try:
    for filename in yellow_filenames:
        image = pygame.image.load(filename).convert_alpha()
        image = pygame.transform.scale(image, (EXPLOSION_WIDTH, EXPLOSION_HEIGHT))
        yellow_explosion_frames.append(image)
    explosion_animations["orange"] = yellow_explosion_frames
except pygame.error:
    explosion_animations["orange"] = []

# Animação para balão VERMELHO
red_explosion_frames = []
red_filenames = ["vermelho1.png", "vermelho2.png", "vermelho3.png", "vermelho4.png"]
try:
    for filename in red_filenames:
        image = pygame.image.load(filename).convert_alpha()
        image = pygame.transform.scale(image, (EXPLOSION_WIDTH, EXPLOSION_HEIGHT))
        red_explosion_frames.append(image)
    explosion_animations["red"] = red_explosion_frames
except pygame.error:
    explosion_animations["red"] = []

# Animação para balão ROXO
purple_explosion_frames = []
purple_filenames = ["roxo1.png", "roxo2.png", "roxo3.png", "roxo4.png"]
try:
    for filename in purple_filenames:
        image = pygame.image.load(filename).convert_alpha()
        image = pygame.transform.scale(image, (EXPLOSION_WIDTH, EXPLOSION_HEIGHT))
        purple_explosion_frames.append(image)
    explosion_animations["purple"] = purple_explosion_frames
except pygame.error:
    explosion_animations["purple"] = []

# Animação para balão VERDE
green_explosion_frames = []
green_filenames = ["verde1.png", "verde2.png", "verde3.png", "verde4.png"]
try:
    for filename in green_filenames:
        image = pygame.image.load(filename).convert_alpha()
        image = pygame.transform.scale(image, (EXPLOSION_WIDTH, EXPLOSION_HEIGHT))
        green_explosion_frames.append(image)
    explosion_animations["green"] = green_explosion_frames
except pygame.error:
    explosion_animations["green"] = []


# Carregar bloon_death_green - imagem do boss
try:
    boss_sprite = pygame.image.load("balaoboss.png").convert_alpha()
    boss_sprite = pygame.transform.scale(boss_sprite, (BOSS_IMAGE_WIDTH, BOSS_IMAGE_HEIGHT))
    print("Imagem do boss carregada com sucesso.")
except pygame.error as e:
    print(f"ERRO: Não foi possível carregar a imagem do boss. Usando círculo. Detalhes: {e}")
    boss_sprite = None

# Carregar vida_do_jogador - imagem da vida do jogador
try:
    life_sprite = pygame.image.load("vida_do_jogador.png").convert_alpha()
    life_sprite = pygame.transform.scale(life_sprite, (64, 64))
    print("Imagem da vida do jogador carregada com sucesso.")
except pygame.error as e:
    print(f"ERRO: Não foi possível carregar a imagem da vida do jogador. Usando quadrado vermelho. Detalhes: {e}")
    life_sprite = None

# ----------------------------------------------------------------------
## Funções de Desenho
# ----------------------------------------------------------------------

def get_empirical_prob(item_type, current_counts):
    total_count = sum(current_counts.values())
    if total_count == 0:
        return 0.0
    return current_counts.get(item_type, 0) / float(total_count)

def draw_histogram(surface, data_dict, data_keys, data_colors, title, bounds_rect, expected_prob_func=None):
    pygame.draw.rect(screen, GRAY, bounds_rect)

    graph_x_start = bounds_rect.left + 30
    graph_y_bottom = bounds_rect.bottom - 30

    title_text = second_font.render(title, True, WHITE)
    surface.blit(title_text, (bounds_rect.left + (bounds_rect.width - title_text.get_width()) // 2, bounds_rect.top + 10))

    total_count = sum(data_dict.values())
    max_bar_height = bounds_rect.height - 100
    total_width_available = bounds_rect.width - 60

    if not data_keys:
        return

    max_obs_count = max(data_dict.values()) if data_dict.values() else 1
    if max_obs_count == 0:
        max_obs_count = 1

    expected_counts = {}
    max_expected_count = 0
    if expected_prob_func and total_count > 0:
        for item_type in data_keys:
            prob_expected = expected_prob_func(item_type)
            expected_count_val = prob_expected * total_count
            expected_counts[item_type] = expected_count_val

        if expected_counts:
            max_expected_count = max(expected_counts.values())

    max_val = max(max_obs_count, max_expected_count)
    if max_val == 0:
        max_val = 1

    bar_width = int(total_width_available / (len(data_keys) * 1.5 + 0.5))
    bar_spacing = int(bar_width * 0.5)
    fitting_line_points = []

    for i, item_type in enumerate(data_keys):
        count = data_dict.get(item_type, 0)
        color = data_colors.get(item_type, WHITE)

        bar_height = int((count / max_val) * max_bar_height)
        bar_x = int(graph_x_start + (i * (bar_width + bar_spacing)))
        bar_y = int(graph_y_bottom - bar_height)

        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, color, bar_rect)

        if title == "Contagem":
            label_display = str(count)
        else:
            label_display = item_type

        label_text = main_font.render(label_display, True, WHITE)
        surface.blit(label_text, (bar_x + (bar_width - label_text.get_width()) // 2, graph_y_bottom + 5))

        if total_count > 0:
            prob_emp = (count / total_count) * 100
            count_label = f"{prob_emp:.0f}%"
        else:
            count_label = str(count)

        count_text = main_font.render(count_label, True, WHITE)
        surface.blit(count_text, (bar_x + (bar_width - count_text.get_width()) // 2, bar_y - 25))

        if expected_prob_func and total_count > 0:
            expected_count_val = expected_counts.get(item_type, 0)

            expected_height = int((expected_count_val / max_val) * max_bar_height)
            expected_y = graph_y_bottom - expected_height
            expected_x = bar_x + bar_width // 2
            fitting_line_points.append((int(expected_x), int(expected_y)))

    if len(fitting_line_points) >= 2:
        pygame.draw.lines(surface, FITTING_COLOR, False, fitting_line_points, 3)


def draw_scatter_plot(surface, data_points, bounds_rect, elapsed_time):
    pygame.draw.rect(screen, GRAY, bounds_rect) 
    
    graph_title_text = second_font.render("Pontuação x Tempo", True, WHITE)
    surface.blit(graph_title_text, (bounds_rect.left + (bounds_rect.width - graph_title_text.get_width()) // 2, bounds_rect.top + 20))

    MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, MARGIN_BOTTOM = 60, 30, 50, 50
    PLOT_AREA = pygame.Rect(bounds_rect.left + MARGIN_LEFT, bounds_rect.top + MARGIN_TOP,
                            bounds_rect.width - (MARGIN_LEFT + MARGIN_RIGHT),
                            bounds_rect.height - (MARGIN_TOP + MARGIN_BOTTOM))

    pygame.draw.line(surface, WHITE, PLOT_AREA.bottomleft, PLOT_AREA.topleft, 2)
    pygame.draw.line(surface, WHITE, PLOT_AREA.bottomleft, PLOT_AREA.bottomright, 2)

    if not data_points or len(data_points) < 2:
        empty_text = main_font.render("Destruindo inimigos...", True, WHITE)
        surface.blit(empty_text, (PLOT_AREA.left + 50, PLOT_AREA.top + 50))
        time_label = main_font.render(f"{elapsed_time:.1f}s", True, WHITE)
        time_label_rect = time_label.get_rect(midright=(PLOT_AREA.right, PLOT_AREA.bottom + 10))
        surface.blit(time_label, time_label_rect)
        return

    times = [p[0] for p in data_points]
    scores = [p[1] for p in data_points]
    max_time_raw = times[-1] if times else 1
    max_score_raw = max(scores) if scores else 1

    max_time_to_scale = max(max_time_raw, elapsed_time)

    max_time_scaled = math.ceil(max(10, max_time_to_scale) / 10) * 10
    Y_STEP = 2000
    max_score_scaled = math.ceil(max(2000, max_score_raw) / Y_STEP) * Y_STEP

    scaled_points = []
    for time_val, score_val in data_points:
        x_norm = time_val / max_time_scaled
        y_norm = score_val / max_score_scaled
        screen_x = PLOT_AREA.left + int(x_norm * PLOT_AREA.width)
        screen_y = PLOT_AREA.bottom - int(y_norm * PLOT_AREA.height)
        screen_x = max(PLOT_AREA.left, min(screen_x, PLOT_AREA.right))
        screen_y = max(PLOT_AREA.top, min(screen_y, PLOT_AREA.bottom))
        scaled_points.append((screen_x, screen_y))
        pygame.draw.circle(surface, SCORE_POINT_COLOR, (screen_x, screen_y), 3)

    if len(scaled_points) >= 2:
        pygame.draw.lines(surface, SCORE_POINT_COLOR, False, scaled_points, 2)

    if scaled_points:
        last_point_x, last_point_y = scaled_points[-1]
        current_score_value = data_points[-1][1]
        score_label = main_font.render(str(current_score_value), True, WHITE)
        label_x = last_point_x + 10
        label_y = last_point_y - 20
        if label_x + score_label.get_width() > PLOT_AREA.right:
            label_x = last_point_x - score_label.get_width() - 10
        surface.blit(score_label, (label_x, label_y))

    time_label = main_font.render(f"{elapsed_time:.1f}s", True, WHITE)
    time_label_rect = time_label.get_rect(midright=(PLOT_AREA.right, PLOT_AREA.bottom + 10))
    surface.blit(time_label, time_label_rect)

# ----------------------------------------------------------------------
# --- HUD/UTILS ---
# ----------------------------------------------------------------------

def draw_player_lives(surface, lives):
    size = 20
    spacing = 20
    margin = 5
    offset_x = 50
    total_width = size * lives + spacing * max(0, lives - 1)
    start_x = SCREEN_WIDTH - offset_x - margin - total_width
    y = margin
    for i in range(lives):
        if life_sprite:
            surface.blit(life_sprite, (start_x + i * (size + spacing), y))
        else:
            rect = pygame.Rect(start_x + i * (size + spacing), y, size, size)
            pygame.draw.rect(surface, (220, 50, 50), rect)

# --- FUNÇÃO PRINCIPAL DO JOGO (STATE: GAME) ---
# ----------------------------------------------------------------------

global current_score
current_score = 0
boss_stats_counts = None
boss_stats_intervals = None
boss_score_vs_time = None
boss_snapshot_elapsed = 0.0

global player_lives
player_lives = 3

player_rect = pygame.Rect(30, GAME_HEIGHT // 2 - player_height // 2, player_width, player_height)

def run_game(screen, num_players=1):
    # Variáveis de Controle de Dificuldade e Jogo
    current_item_speed = ITEM_INITIAL_SPEED
    last_speed_increase_time = pygame.time.get_ticks()
    items = []
    bullets = []
    item_spawn_timer = 0
    last_shot_time = 0
    pos_hit_until_ms = 0
    
    # --- CONFIGURAÇÃO DA ANIMAÇÃO DE EXPLOSÃO ---
    EXPLOSION_ANIMATION_SPEED = 0.35 # Quanto maior, mais rápido

    # --- LÓGICA DE CONTROLES FLEXÍVEL ---
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

    # Configuração dos Retângulos dos Jogadores
    players_list = []
    p1_rect = pygame.Rect(30, GAME_HEIGHT // 3, player_width, player_height)
    players_list.append({"rect": p1_rect, "id": 0, "color": PLAYER_COLOR, "joy_id": p1_controller_id})

    if num_players == 2:
        p2_rect = pygame.Rect(30, (GAME_HEIGHT // 3) * 2, player_width, player_height)
        players_list.append({"rect": p2_rect, "id": 1, "color": (255, 50, 50), "joy_id": p2_controller_id})

    # Variáveis de Animação e Estado
    player_frame_index = 0
    player_last_frame_update = pygame.time.get_ticks()
    PLAYER_ANIMATION_SPEED_MS = 100
    PLAYER_ANIMATION_SEQUENCE = [1, 0, 2, 0]

    global current_score
    current_score = 0
    score_vs_time = [(0.0, 0)]
    start_time_ms = pygame.time.get_ticks()
    global player_lives

    stats_counts = {"red": 0, "green": 0, "purple": 0, "orange": 0}
    stats_intervals = {"0-0.7s": 0, "0.7-1.4": 0, "1.4-2.0": 0, "2.0s+": 0}
    INTERVAL_KEYS = list(stats_intervals.keys())
    INTERVAL_COLORS = {key: GRAPH_YELLOW for key in INTERVAL_KEYS}
    last_collection_time = pygame.time.get_ticks()

    # --- Loop Principal ---
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        current_time_ticks = pygame.time.get_ticks()
        elapsed_time_sec = (current_time_ticks - start_time_ms) / 1000.0

        # Dificuldade
        global ITEM_SPEED_INTERVAL, ITEM_SPEED_INCREASE
        if (current_time_ticks - last_speed_increase_time) / 1000.0 >= ITEM_SPEED_INTERVAL:
            current_item_speed += ITEM_SPEED_INCREASE
            last_speed_increase_time = current_time_ticks
            print(f"Dificuldade Aumentada! Velocidade: {current_item_speed:.2f}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return "QUIT"

            # --- TIRO (JOYSTICK) ---
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 2: # Botão X (geralmente)
                    triggered_joy_id = event.joy
                    shooter = None
                    for p in players_list:
                        if p["joy_id"] == triggered_joy_id:
                            shooter = p; break
                    
                    if shooter and (current_time_ticks - last_shot_time > SHOOT_COOLDOWN):
                        bullet_rect = pygame.Rect(shooter["rect"].right, shooter["rect"].centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT)
                        bullets.append(bullet_rect)
                        last_shot_time = current_time_ticks

            # --- TIRO (TECLADO) ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if current_time_ticks - last_shot_time > SHOOT_COOLDOWN:
                        p1 = players_list[0]
                        bullet_rect = pygame.Rect(p1["rect"].right, p1["rect"].centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT)
                        bullets.append(bullet_rect)
                        last_shot_time = current_time_ticks

        # --- MOVIMENTAÇÃO ---
        keys = pygame.key.get_pressed()

        for p in players_list:
            move_x = 0.0
            move_y = 0.0
            
            # 1. Movimento via Teclado (Só Player 1)
            if p["id"] == 0:
                if keys[pygame.K_UP] or keys[pygame.K_w]: move_y -= 1.0
                if keys[pygame.K_DOWN] or keys[pygame.K_s]: move_y += 1.0
                if keys[pygame.K_LEFT] or keys[pygame.K_a]: move_x -= 1.0
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move_x += 1.0
            
            # 2. Movimento via Joystick
            if p["joy_id"] is not None and p["joy_id"] < len(joysticks):
                try:
                    joy = joysticks[p["joy_id"]]
                    axis_x = joy.get_axis(0)
                    axis_y = joy.get_axis(1)
                    if abs(axis_x) > JOYSTICK_DEADZONE: move_x += axis_x
                    if abs(axis_y) > JOYSTICK_DEADZONE: move_y += axis_y
                except:
                    pass

            length = math.hypot(move_x, move_y)
            if length > 1: move_x /= length; move_y /= length

            p["rect"].x += move_x * PLAYER_MAX_VELOCITY * dt
            p["rect"].y += move_y * PLAYER_MAX_VELOCITY * dt

            # Limites
            if p["rect"].top < 0: p["rect"].top = 0
            if p["rect"].bottom > GAME_HEIGHT: p["rect"].bottom = GAME_HEIGHT
            if p["rect"].left < 0: p["rect"].left = 0
            if p["rect"].right > GAME_WIDTH: p["rect"].right = GAME_WIDTH

        # --- SPAWN (ITEMS) ---
        item_spawn_timer += 1
        if item_spawn_timer >= ITEM_SPAWN_RATE:
            item_spawn_timer = 0
            item_type = random.choices(COLOR_TYPES, weights=[ITEM_PROBABILITIES[t] for t in COLOR_TYPES], k=1)[0]
            # Adiciona variáveis de explosão no dicionário
            items.append({
                "rect": pygame.Rect(GAME_WIDTH + ITEM_IMAGE_WIDTH, random.randint(0, GAME_HEIGHT - ITEM_IMAGE_HEIGHT), ITEM_IMAGE_WIDTH, ITEM_IMAGE_HEIGHT), 
                "color": ITEM_COLORS[item_type], 
                "type": item_type, 
                "image": balloon_images.get(item_type),
                "exploding": False, # Estado inicial
                "explosion_frame_index": 0.0 # Frame inicial
            })

        for i in range(len(bullets) - 1, -1, -1):
            bullets[i].x += BULLET_SPEED
            if bullets[i].left > GAME_WIDTH: bullets.pop(i)

        for i in range(len(items) - 1, -1, -1):
            item = items[i]

            # --- LÓGICA DE EXPLOSÃO (ATUALIZAÇÃO) ---
            if item["exploding"]:
                item["explosion_frame_index"] += EXPLOSION_ANIMATION_SPEED
                
                # Seleciona a animação correta para saber o tamanho máximo
                anim_frames = explosion_animations.get(item["type"], [])
                max_frames = len(anim_frames) if anim_frames else 0
                
                # Se a animação acabou ou não existe, remove o item
                if max_frames == 0 or item["explosion_frame_index"] >= max_frames:
                    items.pop(i)
                continue # Pula o movimento se estiver explodindo

            item["rect"].x -= current_item_speed
            if item["rect"].right < 0:
                items.pop(i); continue

            # Colisão Jogador
            if current_time_ticks >= pos_hit_until_ms:
                hit = False
                for p in players_list:
                    if p["rect"].colliderect(item["rect"]):
                        hit_sound.play(); player_lives -= 1; pos_hit_until_ms = current_time_ticks + 1000; hit = True
                        print(f"Player {p['id']+1} hit!"); break
                if hit:
                    items.pop(i)
                    if player_lives <= 0: pygame.mixer.music.stop(); return "GAME_OVER"
                    continue

        # Colisão Bala-Inimigo
        for b_idx in range(len(bullets) - 1, -1, -1):
            hit = False
            for i_idx in range(len(items) - 1, -1, -1):
                # Ignora se já estiver explodindo
                if items[i_idx]["exploding"]:
                    continue

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

                    # --- GATILHO DA EXPLOSÃO ---
                    # Verifica se existe animação para este tipo, senão remove logo
                    if item_type in explosion_animations and explosion_animations[item_type]:
                        items[i_idx]["exploding"] = True
                        items[i_idx]["explosion_frame_index"] = 0.0
                    else:
                        items.pop(i_idx) # Sem animação, remove direto

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

        # Animação Jogador
        if (current_time_ticks - player_last_frame_update > PLAYER_ANIMATION_SPEED_MS):
            player_last_frame_update = current_time_ticks
            player_frame_index = (player_frame_index + 1) % len(PLAYER_ANIMATION_SEQUENCE)

        # --- Renderização ---
        screen.fill(BLACK)
        pygame.draw.rect(screen, LIGHT_BLUE, (0, 0, GAME_WIDTH, GAME_HEIGHT))

        # Índice do frame atual
        frame_idx = PLAYER_ANIMATION_SEQUENCE[player_frame_index]
        
        for p in players_list:
            draw_img = None
            
            # Se for Player 1 (ID 0) -> Usa Macaco
            if p["id"] == 0:
                if p1_animation_frames:
                    draw_img = p1_animation_frames[frame_idx]
            
            # Se for Player 2 (ID 1) -> Usa Mamaco
            elif p["id"] == 1:
                if p2_animation_frames:
                    draw_img = p2_animation_frames[frame_idx]
                else:
                    # Fallback: Se não tem mamaco, usa macaco pintado de vermelho
                    if p1_animation_frames:
                        draw_img = p1_animation_frames[frame_idx].copy()
                        draw_img.fill((255, 100, 100), special_flags=pygame.BLEND_MULT)
            
            # Efeito de piscar ao levar dano
            if current_time_ticks < pos_hit_until_ms:
                 if (current_time_ticks // 150) % 2 == 0: 
                     if draw_img: screen.blit(draw_img, p["rect"].topleft)
                     else: pygame.draw.rect(screen, p["color"], p["rect"])
            else:
                if draw_img: screen.blit(draw_img, p["rect"].topleft)
                else: pygame.draw.rect(screen, p["color"], p["rect"])

        # DESENHO DOS ITENS COM SUPORTE A EXPLOSÃO
        for item in items:
            # Se estiver explodindo, desenha o frame da explosão
            if item.get("exploding", False):
                frame_index = int(item["explosion_frame_index"])
                anim_frames = explosion_animations.get(item["type"], [])
                
                if anim_frames and 0 <= frame_index < len(anim_frames):
                    img = anim_frames[frame_index]
                    # Centraliza a explosão no balão original
                    center_x, center_y = item["rect"].center
                    explosion_rect = img.get_rect()
                    explosion_rect.center = (center_x, center_y)
                    screen.blit(img, explosion_rect.topleft)
            # Se não, desenha o balão normal
            elif item["image"]: 
                screen.blit(item["image"], item["rect"].topleft)
            else: 
                pygame.draw.circle(screen, item["color"], item["rect"].center, item["rect"].width // 2)

        for b in bullets: pygame.draw.rect(screen, BULLET_COLOR, b)

        screen.blit(second_font.render(f"PONTUAÇÃO: {current_score}", True, WHITE), (10, 10))
        draw_player_lives(screen, player_lives)

        # Gráficos
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
# ----------------------------------------------------------------------
# --- CENA DO BOSS (PREPARAÇÃO) ---
# ----------------------------------------------------------------------

boss_rect = pygame.Rect(962, 262, BOSS_IMAGE_WIDTH, BOSS_IMAGE_HEIGHT)

def run_game_boss(screen, num_players=1):
    global current_score, player_lives, joysticks

    # --- LÓGICA DE CONTROLES (Igual à run_game) ---
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
    # Player 1
    players_list.append({"rect": pygame.Rect(100, GAME_HEIGHT // 3, player_width, player_height), 
                         "id": 0, "color": PLAYER_COLOR, "joy_id": p1_controller_id})
    # Player 2
    if num_players == 2:
        players_list.append({"rect": pygame.Rect(100, (GAME_HEIGHT // 3) * 2, player_width, player_height), 
                             "id": 1, "color": (255, 50, 50), "joy_id": p2_controller_id})

    items = []
    bullets = []
    last_shot_time = 0
    pos_hit_until_ms = 0
    
    # Configuração da Animação de Explosão (Boss)
    EXPLOSION_ANIMATION_SPEED = 0.35 

    player_frame_index = 0
    player_last_frame_update = pygame.time.get_ticks()
    PLAYER_ANIMATION_SPEED_MS = 100
    PLAYER_ANIMATION_SEQUENCE = [1, 0, 2, 0]

    start_time_ms = pygame.time.get_ticks()
    last_collection_time_boss = start_time_ms

    # Configuração do Boss (Hexágono)
    boss_center_x, boss_center_y = boss_rect.center
    radius_x = boss_rect.width // 2 + 100
    radius_y = boss_rect.height // 2 + 100
    hexagon_points = [(int(boss_center_x + radius_x * math.cos(math.radians(a))), int(boss_center_y + radius_y * math.sin(math.radians(a)))) for a in [0, 60, 120, 180, 240, 300]]
    BOSS_BALLOON_SPEED = 160

    balloons_around_boss = []
    for i, (cx, cy) in enumerate(hexagon_points):
        chosen_type = random.choice(COLOR_TYPES)
        # Adiciona variáveis de explosão nos balões do boss
        balloons_around_boss.append({
            "type": chosen_type, 
            "image": balloon_images.get(chosen_type), 
            "rect": balloon_images.get(chosen_type).get_rect(center=(cx, cy)) if balloon_images.get(chosen_type) else pygame.Rect(cx, cy, ITEM_IMAGE_WIDTH, ITEM_IMAGE_HEIGHT), 
            "target_idx": (i + 1) % 6,
            "exploding": False, 
            "explosion_frame_index": 0.0
        })

    global boss_stats_counts, boss_stats_intervals, boss_score_vs_time, boss_snapshot_elapsed
    stats_counts_local = boss_stats_counts.copy() if boss_stats_counts else {k: 0 for k in COLOR_TYPES}
    stats_intervals_local = boss_stats_intervals.copy() if boss_stats_intervals else {"0-0.7s": 0, "0.7-1.4": 0, "1.4-2.0": 0, "2.0s+": 0}
    score_vs_time_local = boss_score_vs_time.copy() if boss_score_vs_time else [(0.0, current_score)]
    snapshot_elapsed = boss_snapshot_elapsed

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        current_time_ticks = pygame.time.get_ticks()
        elapsed_time_sec = (current_time_ticks - start_time_ms) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"

            # Tiro Joystick (Mapeado pelo joy_id)
            if event.type == pygame.JOYBUTTONDOWN and event.button == 2:
                triggered_joy_id = event.joy
                shooter = next((p for p in players_list if p["joy_id"] == triggered_joy_id), None)
                if shooter and (current_time_ticks - last_shot_time > SHOOT_COOLDOWN):
                    bullets.append(pygame.Rect(shooter["rect"].right, shooter["rect"].centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT))
                    last_shot_time = current_time_ticks

            # Tiro Teclado (Sempre P1)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if current_time_ticks - last_shot_time > SHOOT_COOLDOWN:
                    bullets.append(pygame.Rect(players_list[0]["rect"].right, players_list[0]["rect"].centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT))
                    last_shot_time = current_time_ticks

        # Movimento
        keys = pygame.key.get_pressed()
        for p in players_list:
            move_x, move_y = 0.0, 0.0
            
            # Teclado (Só P1)
            if p["id"] == 0:
                if keys[pygame.K_UP] or keys[pygame.K_w]: move_y -= 1.0
                if keys[pygame.K_DOWN] or keys[pygame.K_s]: move_y += 1.0
                if keys[pygame.K_LEFT] or keys[pygame.K_a]: move_x -= 1.0
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move_x += 1.0

            # Joystick
            if p["joy_id"] is not None and p["joy_id"] < len(joysticks):
                try:
                    joy = joysticks[p["joy_id"]]
                    if abs(joy.get_axis(0)) > JOYSTICK_DEADZONE: move_x += joy.get_axis(0)
                    if abs(joy.get_axis(1)) > JOYSTICK_DEADZONE: move_y += joy.get_axis(1)
                except: pass

            length = math.hypot(move_x, move_y)
            if length > 1: move_x /= length; move_y /= length
            p["rect"].x += move_x * PLAYER_MAX_VELOCITY * dt
            p["rect"].y += move_y * PLAYER_MAX_VELOCITY * dt
            
            # Limites
            if p["rect"].top < 0: p["rect"].top = 0
            if p["rect"].bottom > GAME_HEIGHT: p["rect"].bottom = GAME_HEIGHT
            if p["rect"].left < 0: p["rect"].left = 0
            if p["rect"].right > GAME_WIDTH: p["rect"].right = GAME_WIDTH

        # Lógica Boss (Giro)
        for i in range(len(balloons_around_boss) - 1, -1, -1):
            b = balloons_around_boss[i]
            
            # --- LÓGICA DE EXPLOSÃO (Boss) ---
            if b["exploding"]:
                b["explosion_frame_index"] += EXPLOSION_ANIMATION_SPEED
                anim_frames = explosion_animations.get(b["type"], [])
                max_frames = len(anim_frames) if anim_frames else 0
                if max_frames == 0 or b["explosion_frame_index"] >= max_frames:
                    balloons_around_boss.pop(i)
                continue # Se está explodindo, não gira mais

            tx, ty = hexagon_points[b["target_idx"]]
            cx, cy = b["rect"].center
            dx, dy = tx - cx, ty - cy
            dist = math.hypot(dx, dy)
            step = BOSS_BALLOON_SPEED * dt
            if dist <= max(4.0, step * 1.25):
                b["rect"].center = (tx, ty)
                b["target_idx"] = (b["target_idx"] + 1) % 6
            else:
                b["rect"].center = (int(cx + (dx/dist)*step), int(cy + (dy/dist)*step))

        # Balas -> Balões Boss
        for i in range(len(bullets) - 1, -1, -1):
            bullets[i].x += BULLET_SPEED
            if bullets[i].left > GAME_WIDTH: bullets.pop(i); continue
            
            hit = False
            for bi in range(len(balloons_around_boss) - 1, -1, -1):
                b = balloons_around_boss[bi]
                
                # Ignora se já estiver explodindo
                if b["exploding"]: continue

                if bullets[i].colliderect(b["rect"]):
                    # b = balloons_around_boss.pop(bi) <-- Não removemos mais direto
                    current_score += ITEM_SCORES.get(b["type"], 0)
                    stats_counts_local[b["type"]] += 1
                    
                    interval = (current_time_ticks - last_collection_time_boss) / 1000.0
                    last_collection_time_boss = current_time_ticks
                    if interval < 0.7: stats_intervals_local["0-0.7s"] += 1
                    elif interval < 1.4: stats_intervals_local["0.7-1.4"] += 1
                    elif interval < 2.0: stats_intervals_local["1.4-2.0"] += 1
                    else: stats_intervals_local["2.0s+"] += 1

                    score_vs_time_local.append((snapshot_elapsed + elapsed_time_sec, current_score))
                    
                    # --- GATILHO EXPLOSÃO (Boss) ---
                    if b["type"] in explosion_animations and explosion_animations[b["type"]]:
                        b["exploding"] = True
                        b["explosion_frame_index"] = 0.0
                    else:
                        balloons_around_boss.pop(bi)

                    bullets.pop(i); hit = True; break
            if hit: continue

        # Colisão Jogador -> Balões Boss
        if current_time_ticks >= pos_hit_until_ms:
            for bi in range(len(balloons_around_boss) - 1, -1, -1):
                b = balloons_around_boss[bi]
                # Se está explodindo, não causa dano
                if b["exploding"]: continue

                hit_p = False
                for p in players_list:
                    if p["rect"].colliderect(b["rect"]):
                        hit_sound.play(); player_lives -= 1; pos_hit_until_ms = current_time_ticks + 1000
                        balloons_around_boss.pop(bi); hit_p = True; break
                if hit_p:
                    if player_lives <= 0: pygame.mixer.music.stop(); return "GAME_OVER"
                    break

        # Render
        if (current_time_ticks - player_last_frame_update > PLAYER_ANIMATION_SPEED_MS):
            player_last_frame_update = current_time_ticks
            player_frame_index = (player_frame_index + 1) % len(PLAYER_ANIMATION_SEQUENCE)

        screen.fill(BLACK)
        pygame.draw.rect(screen, LIGHT_BLUE, (0, 0, GAME_WIDTH, GAME_HEIGHT))
        
        # Índice do frame atual
        frame_idx = PLAYER_ANIMATION_SEQUENCE[player_frame_index]

        for p in players_list:
            draw_img = None
            
            # Se for Player 1 (ID 0) -> Usa Macaco
            if p["id"] == 0:
                if p1_animation_frames:
                    draw_img = p1_animation_frames[frame_idx]
            
            # Se for Player 2 (ID 1) -> Usa Mamaco
            elif p["id"] == 1:
                if p2_animation_frames:
                    draw_img = p2_animation_frames[frame_idx]
                else:
                    # Fallback: Se não tem mamaco, usa macaco pintado de vermelho
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

        for b in bullets: pygame.draw.rect(screen, BULLET_COLOR, b)
        pygame.draw.rect(screen, (200, 50, 50), boss_rect, width=4)
        
        # DESENHO DOS BALÕES DO BOSS COM EXPLOSÃO
        for b in balloons_around_boss:
            if b.get("exploding", False):
                frame_index = int(b["explosion_frame_index"])
                anim_frames = explosion_animations.get(b["type"], [])
                if anim_frames and 0 <= frame_index < len(anim_frames):
                    img = anim_frames[frame_index]
                    center_x, center_y = b["rect"].center
                    explosion_rect = img.get_rect()
                    explosion_rect.center = (center_x, center_y)
                    screen.blit(img, explosion_rect.topleft)
            elif b["image"]: 
                screen.blit(b["image"], b["rect"].topleft)
            else: 
                pygame.draw.circle(screen, ITEM_COLORS.get(b["type"], WHITE), b["rect"].center, ITEM_IMAGE_WIDTH // 2)
        
        if boss_sprite: screen.blit(boss_sprite, boss_rect.topleft)

        screen.blit(second_font.render(f"PONTUAÇÃO: {current_score}", True, WHITE), (10, 10))
        screen.blit(second_font.render("CENA DO BOSS - Prepare-se!", True, WHITE), (10, 45))
        draw_player_lives(screen, player_lives)

        rect1 = pygame.Rect(0, GAME_HEIGHT, GRAPH_WIDTH_PER_PLOT, GRAPH_HEIGHT)
        rect2 = pygame.Rect(GRAPH_X_SPLIT_1, GAME_HEIGHT, GRAPH_WIDTH_PER_PLOT, GRAPH_HEIGHT)
        rect3 = pygame.Rect(GRAPH_X_SPLIT_2, GAME_HEIGHT, GRAPH_WIDTH_PER_PLOT, GRAPH_HEIGHT)
        draw_histogram(screen, stats_counts_local, COLOR_TYPES, ITEM_COLORS, "Contagem", rect1, lambda t: get_empirical_prob(t, stats_counts_local))
        draw_scatter_plot(screen, score_vs_time_local, rect2, snapshot_elapsed + elapsed_time_sec)
        draw_histogram(screen, stats_intervals_local, list(stats_intervals_local.keys()), {k: GRAPH_YELLOW for k in stats_intervals_local}, "Intervalo de Destruição", rect3, lambda k: get_empirical_prob(k, stats_intervals_local))

        pygame.draw.line(screen, WHITE, (0, GAME_HEIGHT), (SCREEN_WIDTH, GAME_HEIGHT), 3)
        pygame.draw.line(screen, WHITE, (GRAPH_X_SPLIT_1, GAME_HEIGHT), (GRAPH_X_SPLIT_1, SCREEN_HEIGHT), 3)
        pygame.draw.line(screen, WHITE, (GRAPH_X_SPLIT_2, GAME_HEIGHT), (GRAPH_X_SPLIT_2, SCREEN_HEIGHT), 3)
        pygame.display.flip()
# ----------------------------------------------------------------------
# --- LOOP PRINCIPAL DA APLICAÇÃO ---
# ----------------------------------------------------------------------

def main():
    global joysticks
    global player_lives

    current_state = "MENU"
    selected_num_players = 1 # Padrão

    while True:
        if current_state == "MENU":
            result = menu.show_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT, title_font, main_font, menu_bg)
            if result == "PLAY":
                current_state = "GAME"
                selected_num_players = 1
                player_lives = 3
                try: pygame.mixer.music.play(-1)
                except: pass
            
            elif result == "PLAY_2P":
                current_state = "GAME"
                selected_num_players = 2
                player_lives = 3 
                try: pygame.mixer.music.play(-1)
                except: pass

            elif result == "QUIT":
                break

        elif current_state == "GAME":
            result = run_game(screen, num_players=selected_num_players)
            
            if result == "GAME_OVER":
                print(f"Fim de Jogo. Pontuação Final: {current_score}")
                current_state = "MENU"
            elif result == "BOSS_FIGHT":
                current_state = "BOSS"
            elif result == "QUIT":
                break

        elif current_state == "BOSS":
            result = run_game_boss(screen, num_players=selected_num_players)

            if result == "GAME_OVER":
                print(f"Fim de Jogo. Pontuação Final: {current_score}")
                current_state = "MENU"
            elif result == "QUIT":
                break
    pygame.quit()

if __name__ == "__main__":
    main()