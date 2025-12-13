class ParallaxBackground:
    def __init__(self, screen_width, screen_height, image_files, speeds):
        self.width = screen_width
        self.height = screen_height
        self.layers = []
        
        for idx, filename in enumerate(image_files):
            try:
                # Otimização: .convert() para fundos opacos (camada 0) é mais rápido
                if idx == 0:
                    img = pygame.image.load(filename).convert()
                else:
                    img = pygame.image.load(filename).convert_alpha()
                    
                img = pygame.transform.scale(img, (screen_width, screen_height))
                
                self.layers.append({
                    "image": img,
                    "speed_factor": speeds[idx],
                    "x": 0.0 # Float para precisão
                })
                print(f"Camada {idx+1} carregada: {filename}")
            except pygame.error:
                print(f"Placeholder criado para {filename}")
                surf = pygame.Surface((screen_width, screen_height))
                color_val = (50 + idx * 20) % 255
                surf.fill((color_val, 100, 200))
                if idx > 0: surf.set_colorkey((0,0,0)); surf.set_alpha(150)
                self.layers.append({"image": surf, "speed_factor": speeds[idx], "x": 0.0})

    def update(self, game_speed, dt):
        """Agora recebe dt para garantir movimento suave no tempo"""
        for layer in self.layers:
            # ALTERAÇÃO AQUI: Removemos o "* dt"
            # Agora ele vai mover uma fração direta da velocidade do jogo a cada loop.
            move_amount = (game_speed * layer["speed_factor"])
            
            layer["x"] -= move_amount
            
            # Mantemos o loop suave
            if layer["x"] <= -self.width:
                layer["x"] += self.width

    def draw(self, screen):
        for layer in self.layers:
            # ALTERAÇÃO AQUI: Troque round() por int() para estabilidade
            x_pos = int(layer["x"])
            
            screen.blit(layer["image"], (x_pos, 0))
            if x_pos < 0:
                screen.blit(layer["image"], (x_pos + self.width, 0))

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
SCORE_TO_BOSS = 200000

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
BULLET_HEIGHT = 8
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

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), vsync=1)
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

# -- Carregar som estorando balão ---
try:
    POP_SOUND_FILE = "estorar_balao.wav"
    pop_sound = pygame.mixer.Sound(POP_SOUND_FILE)
    pop_sound.set_volume(0.1)
    print(f"Efeito sonoro {POP_SOUND_FILE} carregado.")
except pygame.error:
    print(f"AVISO: Não foi possível carregar o arquivo '{POP_SOUND_FILE}'.")

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

# --- Carregar Imagem do Projétil ---
bullet_img = None
try:
    # Tente carregar a imagem 'projetil.png'
    bullet_img = pygame.image.load("projetil.png").convert_alpha()
    # Redimensiona para o tamanho exato definido nas configurações (35x4)
    # Se quiser o projetil maior, altere BULLET_WIDTH e BULLET_HEIGHT lá em cima nas constantes
    bullet_img = pygame.transform.scale(bullet_img, (BULLET_WIDTH, BULLET_HEIGHT))
    print("Imagem do projétil carregada.")
except pygame.error:
    print("AVISO: 'projetil.png' não encontrado. Usando retângulo padrão.")
    bullet_img = None

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
    
    # Player 1
    players_list.append({
        "rect": pygame.Rect(30, GAME_HEIGHT // 3, player_width, player_height),
        "id": 0,
        "color": PLAYER_COLOR,
        "joy_id": p1_controller_id,
        "last_shot_time": 0  # <--- NOVO: Cada um tem seu tempo
    })

    # Player 2
    if num_players == 2:
        players_list.append({
            "rect": pygame.Rect(30, (GAME_HEIGHT // 3) * 2, player_width, player_height),
            "id": 1,
            "color": (255, 50, 50),
            "joy_id": p2_controller_id,
            "last_shot_time": 0 # <--- NOVO
        })

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

    # Aumente este valor se ainda achar lento (ex: 5.0, 10.0, etc)
    PARALLAX_SPEED_MULTIPLIER = 0.2

    # --- CONFIGURAÇÃO DO PARALLAX ---
    bg_files = [
        "forest_sky.png",      # Fundo total (Céu/Estrelas)
        "forest_short.png",   # Nuvens distantes
        "forest_mountain.png",# Montanhas longe
        "forest_moon.png",  # Prédios/Cidade
        "forest_mid.png",  # Árvores fundo
        "forest_long.png", # Arbustos perto
        "forest_back.png"      # Chão onde o macaco pisa (Transparente em cima)
    ]
    
    # Velocidades: O céu (0.1) é lento, o chão (1.0) acompanha a velocidade dos itens
    bg_speeds = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0]
    
    # Cria o objeto Parallax
    parallax_bg = ParallaxBackground(SCREEN_WIDTH, SCREEN_HEIGHT, bg_files, bg_speeds)

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
        parallax_bg.update(current_item_speed * PARALLAX_SPEED_MULTIPLIER, dt)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            # --- TIRO (JOYSTICK) ---
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 2: # Botão X (geralmente)
                    triggered_joy_id = event.joy
                    firing_player = None
                    # Descobre quem apertou o botão
                    for p in players_list:
                        if p["joy_id"] == triggered_joy_id:
                            firing_player = p; break
                    
                    # Verifica o tempo DESTE jogador específico
                    if firing_player and (current_time_ticks - firing_player["last_shot_time"] > SHOOT_COOLDOWN):
                        bullet_rect = pygame.Rect(firing_player["rect"].right, firing_player["rect"].centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT)
                        bullets.append(bullet_rect)
                        
                        # Atualiza o tempo só DESTE jogador
                        firing_player["last_shot_time"] = current_time_ticks
                        

            # --- TIRO (TECLADO) ---
            if event.type == pygame.KEYDOWN:
                firing_player = None
                
                # Player 1 (Espaço)
                if event.key == pygame.K_SPACE:
                    firing_player = next((p for p in players_list if p["id"] == 0), None)

                # Player 2 (Enter)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    firing_player = next((p for p in players_list if p["id"] == 1), None)

                # Verifica o tempo DESTE jogador específico
                if firing_player and (current_time_ticks - firing_player["last_shot_time"] > SHOOT_COOLDOWN):
                    bullet_rect = pygame.Rect(firing_player["rect"].right, firing_player["rect"].centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT)
                    bullets.append(bullet_rect)
                    
                    # Atualiza o tempo só DESTE jogador
                    firing_player["last_shot_time"] = current_time_ticks
                    

        # --- MOVIMENTAÇÃO ---
        keys = pygame.key.get_pressed()

        for p in players_list:
            move_x = 0.0
            move_y = 0.0
            
            # --- PLAYER 1: Usa WASD ---
            if p["id"] == 0:
                if keys[pygame.K_w]: move_y -= 1.0
                if keys[pygame.K_s]: move_y += 1.0
                if keys[pygame.K_a]: move_x -= 1.0
                if keys[pygame.K_d]: move_x += 1.0
                # Opcional: Se estiver SOZINHO (1 jogador), P1 também pode usar setas
                if num_players == 1:
                    if keys[pygame.K_UP]: move_y -= 1.0
                    if keys[pygame.K_DOWN]: move_y += 1.0
                    if keys[pygame.K_LEFT]: move_x -= 1.0
                    if keys[pygame.K_RIGHT]: move_x += 1.0

            # --- PLAYER 2: Usa SETINHAS ---
            elif p["id"] == 1:
                if keys[pygame.K_UP]: move_y -= 1.0
                if keys[pygame.K_DOWN]: move_y += 1.0
                if keys[pygame.K_LEFT]: move_x -= 1.0
                if keys[pygame.K_RIGHT]: move_x += 1.0

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

                    # Toca som de acerto (se disponível)
                    try:
                        pop_sound.play()
                    except Exception:
                        pass

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
        screen.fill(BLACK) # Limpa a tela

        # Desenha o Parallax (Fundo)
        parallax_bg.draw(screen)

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

        # Desenho das Balas
        for b in bullets:
            if bullet_img:
                # Se a imagem existe, desenha ela na posição do retângulo
                screen.blit(bullet_img, b.topleft)
            else:
                # Se a imagem falhou ao carregar, desenha o retângulo antigo
                pygame.draw.rect(screen, BULLET_COLOR, b)

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

# Constantes do Boss
BOSS_MAX_HP = 5
BOSS_MOVE_SPEED = 40  # Pixels por segundo (movimento para esquerda)
BOSS_ORBIT_RADIUS = 120  # Raio da órbita dos balões
BOSS_ORBIT_SPEED = 1.5  # Velocidade angular (radianos por segundo)
BOSS_DANGER_ZONE = 180  # Distância X do jogador onde o boss causa game over
BOSS_VICTORY_BONUS = 10000  # Pontuação por derrotar o boss

# Partículas para efeitos visuais épicos
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
        self.vy += 200 * dt  # Gravidade
        self.lifetime -= dt
        return self.lifetime > 0
    
    def draw(self, surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
        # Desenha círculo com fade
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)

def create_explosion_particles(x, y, color, count=15):
    """Cria partículas de explosão"""
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(100, 300)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed - 100  # Impulso para cima
        lifetime = random.uniform(0.3, 0.8)
        size = random.randint(3, 8)
        particles.append(Particle(x, y, color, (vx, vy), lifetime, size))
    return particles

def create_hit_particles(x, y, count=8):
    """Cria partículas de impacto (amarelas/laranjas)"""
    particles = []
    colors = [(255, 255, 0), (255, 200, 0), (255, 150, 0), (255, 100, 0)]
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, 150)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        lifetime = random.uniform(0.2, 0.5)
        size = random.randint(2, 5)
        particles.append(Particle(x, y, random.choice(colors), (vx, vy), lifetime, size))
    return particles

def draw_boss_health_bar(surface, boss_hp, max_hp, boss_center_x, boss_center_y):
    """Desenha uma barra de vida épica acima do boss"""
    bar_width = 150
    bar_height = 16
    bar_x = boss_center_x - bar_width // 2
    bar_y = boss_center_y - BOSS_IMAGE_HEIGHT // 2 - 40
    
    # Fundo da barra (preto com borda)
    pygame.draw.rect(surface, (30, 30, 30), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
    pygame.draw.rect(surface, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height))
    
    # Vida atual (gradiente de vermelho para verde)
    hp_ratio = boss_hp / max_hp
    fill_width = int(bar_width * hp_ratio)
    
    # Cor baseada na vida restante
    if hp_ratio > 0.6:
        bar_color = (50, 255, 50)  # Verde
    elif hp_ratio > 0.3:
        bar_color = (255, 200, 0)  # Amarelo
    else:
        bar_color = (255, 50, 50)  # Vermelho
    
    if fill_width > 0:
        pygame.draw.rect(surface, bar_color, (bar_x, bar_y, fill_width, bar_height))
    
    # Borda
    pygame.draw.rect(surface, WHITE, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 2)
    
    # Texto HP
    hp_text = main_font.render(f"BOSS: {boss_hp}/{max_hp}", True, WHITE)
    surface.blit(hp_text, (bar_x + bar_width // 2 - hp_text.get_width() // 2, bar_y - 22))

def draw_warning_overlay(surface, boss_x, danger_threshold):
    """Desenha overlay de perigo quando o boss está perto"""
    if boss_x < danger_threshold + 200:
        # Calcula intensidade do warning
        intensity = max(0, 1 - (boss_x - danger_threshold) / 200)
        alpha = int(50 * intensity)
        
        # Flash vermelho nas bordas
        warning_surf = pygame.Surface((SCREEN_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(warning_surf, (255, 0, 0, alpha), (0, 0, 30, GAME_HEIGHT))
        pygame.draw.rect(warning_surf, (255, 0, 0, alpha), (SCREEN_WIDTH - 30, 0, 30, GAME_HEIGHT))
        pygame.draw.rect(warning_surf, (255, 0, 0, alpha), (0, 0, SCREEN_WIDTH, 30))
        pygame.draw.rect(warning_surf, (255, 0, 0, alpha), (0, GAME_HEIGHT - 30, SCREEN_WIDTH, 30))
        surface.blit(warning_surf, (0, 0))

def run_game_boss(screen, num_players=1):
    global current_score, player_lives, joysticks

    # --- CONFIGURAÇÃO DO BOSS ---
    boss_hp = BOSS_MAX_HP
    boss_center_x = float(SCREEN_WIDTH - 200)  # Posição X inicial (direita da tela)
    boss_center_y = float(GAME_HEIGHT // 2)    # Centro vertical
    boss_hit_flash_until = 0  # Timer para flash quando leva dano
    boss_defeated = False
    victory_animation_timer = 0
    
    # Screen shake
    screen_shake_until = 0
    screen_shake_intensity = 0
    
    # Partículas
    particles = []
    
    # Aura do boss (círculos pulsantes)
    aura_pulse = 0.0

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
                         "id": 0, "color": PLAYER_COLOR, "joy_id": p1_controller_id,
                         "last_shot_time": 0})
    # Player 2
    if num_players == 2:
        players_list.append({"rect": pygame.Rect(100, (GAME_HEIGHT // 3) * 2, player_width, player_height), 
                             "id": 1, "color": (255, 50, 50), "joy_id": p2_controller_id,
                             "last_shot_time": 0})

    bullets = []
    pos_hit_until_ms = 0
    
    # Configuração da Animação de Explosão (Boss)
    EXPLOSION_ANIMATION_SPEED = 0.35 

    player_frame_index = 0
    player_last_frame_update = pygame.time.get_ticks()
    PLAYER_ANIMATION_SPEED_MS = 100
    PLAYER_ANIMATION_SEQUENCE = [1, 0, 2, 0]

    start_time_ms = pygame.time.get_ticks()
    last_collection_time_boss = start_time_ms

    # --- BALÕES ORBITANDO O BOSS ---
    # Cada balão tem um ângulo de órbita que aumenta continuamente
    NUM_ORBITING_BALLOONS = 8
    orbit_angle_offset = 0.0  # Ângulo global que incrementa para rotação
    
    balloons_around_boss = []
    for i in range(NUM_ORBITING_BALLOONS):
        chosen_type = random.choice(COLOR_TYPES)
        angle = (2 * math.pi / NUM_ORBITING_BALLOONS) * i  # Distribuição uniforme
        
        balloons_around_boss.append({
            "type": chosen_type, 
            "image": balloon_images.get(chosen_type), 
            "rect": pygame.Rect(0, 0, ITEM_IMAGE_WIDTH, ITEM_IMAGE_HEIGHT),
            "orbit_angle": angle,  # Ângulo individual na órbita
            "orbit_radius": BOSS_ORBIT_RADIUS + random.randint(-20, 20),  # Variação no raio
            "orbit_speed_mult": 1.0 + random.uniform(-0.2, 0.2),  # Variação na velocidade
            "exploding": False, 
            "explosion_frame_index": 0.0
        })

    # Função para respawnar balões
    def spawn_new_balloon():
        chosen_type = random.choice(COLOR_TYPES)
        # Spawna do lado oposto (atrás do boss)
        angle = random.uniform(0, 2 * math.pi)
        return {
            "type": chosen_type, 
            "image": balloon_images.get(chosen_type), 
            "rect": pygame.Rect(0, 0, ITEM_IMAGE_WIDTH, ITEM_IMAGE_HEIGHT),
            "orbit_angle": angle,
            "orbit_radius": BOSS_ORBIT_RADIUS + random.randint(-20, 20),
            "orbit_speed_mult": 1.0 + random.uniform(-0.2, 0.2),
            "exploding": False, 
            "explosion_frame_index": 0.0
        }

    balloon_respawn_timer = 0
    BALLOON_RESPAWN_INTERVAL = 2.0  # Segundos para respawnar balões

    global boss_stats_counts, boss_stats_intervals, boss_score_vs_time, boss_snapshot_elapsed
    stats_counts_local = boss_stats_counts.copy() if boss_stats_counts else {k: 0 for k in COLOR_TYPES}
    stats_intervals_local = boss_stats_intervals.copy() if boss_stats_intervals else {"0-0.7s": 0, "0.7-1.4": 0, "1.4-2.0": 0, "2.0s+": 0}
    score_vs_time_local = boss_score_vs_time.copy() if boss_score_vs_time else [(0.0, current_score)]
    snapshot_elapsed = boss_snapshot_elapsed

    # --- PARALLAX PARA O BOSS ---
    bg_files = [
        "forest_sky.png", "forest_short.png", "forest_mountain.png",
        "forest_moon.png", "forest_mid.png", "forest_long.png", "forest_back.png"
    ]
    bg_speeds = [0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0]
    parallax_bg = ParallaxBackground(SCREEN_WIDTH, SCREEN_HEIGHT, bg_files, bg_speeds)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        current_time_ticks = pygame.time.get_ticks()
        elapsed_time_sec = (current_time_ticks - start_time_ms) / 1000.0

        # --- ANIMAÇÃO DE VITÓRIA ---
        if boss_defeated:
            victory_animation_timer += dt
            if victory_animation_timer > 3.0:  # 3 segundos de celebração
                pygame.mixer.music.stop()
                return "GAME_OVER"  # Volta ao menu (poderia ser "VICTORY" se quiser diferenciar)
            
            # Adiciona partículas de celebração
            if random.random() < 0.3:
                px = random.randint(100, SCREEN_WIDTH - 100)
                py = random.randint(50, GAME_HEIGHT - 50)
                particles.extend(create_explosion_particles(px, py, random.choice([(255, 215, 0), (50, 255, 50), (50, 200, 255)]), 5))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"

            # --- TIRO (JOYSTICK) ---
            if event.type == pygame.JOYBUTTONDOWN and event.button == 2:
                triggered_joy_id = event.joy
                shooter = next((p for p in players_list if p["joy_id"] == triggered_joy_id), None)
                if shooter and (current_time_ticks - shooter["last_shot_time"] > SHOOT_COOLDOWN):
                    bullets.append(pygame.Rect(shooter["rect"].right, shooter["rect"].centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT))
                    shooter["last_shot_time"] = current_time_ticks

            # --- TIRO (TECLADO) ---
            if event.type == pygame.KEYDOWN:
                firing_player = None
                
                if event.key == pygame.K_SPACE:
                    firing_player = players_list[0] 
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if num_players == 1:
                        firing_player = players_list[0]
                    elif num_players == 2:
                        firing_player = next((p for p in players_list if p["id"] == 1), None)

                if firing_player and (current_time_ticks - firing_player["last_shot_time"] > SHOOT_COOLDOWN):
                    bullets.append(pygame.Rect(firing_player["rect"].right, firing_player["rect"].centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT))
                    firing_player["last_shot_time"] = current_time_ticks

        # --- MOVIMENTAÇÃO JOGADORES ---
        keys = pygame.key.get_pressed()
        for p in players_list:
            move_x, move_y = 0.0, 0.0
            
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
                    if abs(joy.get_axis(0)) > JOYSTICK_DEADZONE: move_x += joy.get_axis(0)
                    if abs(joy.get_axis(1)) > JOYSTICK_DEADZONE: move_y += joy.get_axis(1)
                except: pass

            length = math.hypot(move_x, move_y)
            if length > 1: move_x /= length; move_y /= length
            p["rect"].x += move_x * PLAYER_MAX_VELOCITY * dt
            p["rect"].y += move_y * PLAYER_MAX_VELOCITY * dt
            
            if p["rect"].top < 0: p["rect"].top = 0
            if p["rect"].bottom > GAME_HEIGHT: p["rect"].bottom = GAME_HEIGHT
            if p["rect"].left < 0: p["rect"].left = 0
            if p["rect"].right > GAME_WIDTH: p["rect"].right = GAME_WIDTH

        if not boss_defeated:
            # --- MOVIMENTO DO BOSS PARA ESQUERDA ---
            boss_center_x -= BOSS_MOVE_SPEED * dt
            
            # Movimento vertical sinusoidal para ficar mais dinâmico
            boss_center_y = GAME_HEIGHT // 2 + math.sin(elapsed_time_sec * 0.8) * 80
            
            # Atualiza parallax com velocidade do boss
            parallax_bg.update(BOSS_MOVE_SPEED * 0.1, dt)
            
            # --- VERIFICAÇÃO: BOSS CHEGOU NO JOGADOR ---
            if boss_center_x <= BOSS_DANGER_ZONE:
                pygame.mixer.music.stop()
                return "GAME_OVER"

            # --- ATUALIZAÇÃO DA ÓRBITA DOS BALÕES ---
            orbit_angle_offset += BOSS_ORBIT_SPEED * dt
            aura_pulse += dt * 3  # Para efeito visual

            # Atualiza posição dos balões em órbita
            for i in range(len(balloons_around_boss) - 1, -1, -1):
                b = balloons_around_boss[i]
                
                if b["exploding"]:
                    b["explosion_frame_index"] += EXPLOSION_ANIMATION_SPEED
                    anim_frames = explosion_animations.get(b["type"], [])
                    max_frames = len(anim_frames) if anim_frames else 0
                    if max_frames == 0 or b["explosion_frame_index"] >= max_frames:
                        balloons_around_boss.pop(i)
                    continue
                
                # Calcula posição orbital
                current_angle = b["orbit_angle"] + orbit_angle_offset * b["orbit_speed_mult"]
                b["rect"].centerx = int(boss_center_x + math.cos(current_angle) * b["orbit_radius"])
                b["rect"].centery = int(boss_center_y + math.sin(current_angle) * b["orbit_radius"])

            # Respawn de balões
            balloon_respawn_timer += dt
            if balloon_respawn_timer >= BALLOON_RESPAWN_INTERVAL:
                balloon_respawn_timer = 0
                # Mantém pelo menos 4 balões orbitando
                active_balloons = len([b for b in balloons_around_boss if not b["exploding"]])
                if active_balloons < 4:
                    balloons_around_boss.append(spawn_new_balloon())

        # --- COLISÃO BALAS ---
        for i in range(len(bullets) - 1, -1, -1):
            bullets[i].x += BULLET_SPEED
            if bullets[i].left > SCREEN_WIDTH: 
                bullets.pop(i)
                continue
            
            hit = False
            
            # Colisão com balões orbitantes
            for bi in range(len(balloons_around_boss) - 1, -1, -1):
                b = balloons_around_boss[bi]
                if b["exploding"]: continue

                if bullets[i].colliderect(b["rect"]):
                    current_score += ITEM_SCORES.get(b["type"], 0)
                    stats_counts_local[b["type"]] += 1
                    
                    interval = (current_time_ticks - last_collection_time_boss) / 1000.0
                    last_collection_time_boss = current_time_ticks
                    if interval < 0.7: stats_intervals_local["0-0.7s"] += 1
                    elif interval < 1.4: stats_intervals_local["0.7-1.4"] += 1
                    elif interval < 2.0: stats_intervals_local["1.4-2.0"] += 1
                    else: stats_intervals_local["2.0s+"] += 1

                    score_vs_time_local.append((snapshot_elapsed + elapsed_time_sec, current_score))

                    try: pop_sound.play()
                    except: pass
                    
                    # Partículas de explosão
                    particles.extend(create_explosion_particles(b["rect"].centerx, b["rect"].centery, ITEM_COLORS.get(b["type"], WHITE)))
                    
                    if b["type"] in explosion_animations and explosion_animations[b["type"]]:
                        b["exploding"] = True
                        b["explosion_frame_index"] = 0.0
                    else:
                        balloons_around_boss.pop(bi)

                    bullets.pop(i)
                    hit = True
                    break
            
            if hit: continue
            
            # --- COLISÃO COM O BOSS ---
            if not boss_defeated and i < len(bullets):
                boss_hitbox = pygame.Rect(
                    int(boss_center_x - BOSS_IMAGE_WIDTH // 2),
                    int(boss_center_y - BOSS_IMAGE_HEIGHT // 2),
                    BOSS_IMAGE_WIDTH, BOSS_IMAGE_HEIGHT
                )
                
                if bullets[i].colliderect(boss_hitbox):
                    boss_hp -= 1
                    current_score += 500  # Pontos por acertar o boss
                    score_vs_time_local.append((snapshot_elapsed + elapsed_time_sec, current_score))
                    
                    boss_hit_flash_until = current_time_ticks + 200
                    screen_shake_until = current_time_ticks + 150
                    screen_shake_intensity = 8
                    
                    try: hit_sound.play()
                    except: pass
                    
                    # Partículas épicas de impacto
                    particles.extend(create_hit_particles(int(boss_center_x), int(boss_center_y), 15))
                    
                    bullets.pop(i)
                    
                    # Boss derrotado!
                    if boss_hp <= 0:
                        boss_defeated = True
                        current_score += BOSS_VICTORY_BONUS
                        score_vs_time_local.append((snapshot_elapsed + elapsed_time_sec, current_score))
                        
                        # MEGA explosão de vitória
                        for _ in range(5):
                            px = int(boss_center_x + random.randint(-50, 50))
                            py = int(boss_center_y + random.randint(-50, 50))
                            particles.extend(create_explosion_particles(px, py, random.choice([(255, 50, 50), (255, 200, 0), (255, 100, 0)]), 20))
                        
                        screen_shake_until = current_time_ticks + 500
                        screen_shake_intensity = 15

        # --- COLISÃO JOGADOR COM BALÕES ---
        if current_time_ticks >= pos_hit_until_ms:
            for bi in range(len(balloons_around_boss) - 1, -1, -1):
                b = balloons_around_boss[bi]
                if b["exploding"]: continue

                hit_p = False
                for p in players_list:
                    if p["rect"].colliderect(b["rect"]):
                        try: hit_sound.play()
                        except: pass
                        player_lives -= 1
                        pos_hit_until_ms = current_time_ticks + 1000
                        
                        particles.extend(create_hit_particles(b["rect"].centerx, b["rect"].centery))
                        balloons_around_boss.pop(bi)
                        hit_p = True
                        break
                if hit_p:
                    if player_lives <= 0:
                        pygame.mixer.music.stop()
                        return "GAME_OVER"
                    break

        # --- ATUALIZAÇÃO DAS PARTÍCULAS ---
        particles = [p for p in particles if p.update(dt)]

        # --- RENDER ---
        if (current_time_ticks - player_last_frame_update > PLAYER_ANIMATION_SPEED_MS):
            player_last_frame_update = current_time_ticks
            player_frame_index = (player_frame_index + 1) % len(PLAYER_ANIMATION_SEQUENCE)

        # Screen shake offset
        shake_offset_x, shake_offset_y = 0, 0
        if current_time_ticks < screen_shake_until:
            shake_offset_x = random.randint(-screen_shake_intensity, screen_shake_intensity)
            shake_offset_y = random.randint(-screen_shake_intensity, screen_shake_intensity)

        screen.fill(BLACK)
        
        # Desenha parallax (com shake)
        parallax_bg.draw(screen)
        
        # Warning overlay quando boss está perto
        draw_warning_overlay(screen, boss_center_x, BOSS_DANGER_ZONE)
        
        frame_idx = PLAYER_ANIMATION_SEQUENCE[player_frame_index]

        # Desenha jogadores
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
            
            draw_pos = (p["rect"].left + shake_offset_x, p["rect"].top + shake_offset_y)
            
            if current_time_ticks < pos_hit_until_ms:
                if (current_time_ticks // 150) % 2 == 0:
                    if draw_img: screen.blit(draw_img, draw_pos)
                    else: pygame.draw.rect(screen, p["color"], p["rect"].move(shake_offset_x, shake_offset_y))
            else:
                if draw_img: screen.blit(draw_img, draw_pos)
                else: pygame.draw.rect(screen, p["color"], p["rect"].move(shake_offset_x, shake_offset_y))

        # Desenha balas
        for b in bullets:
            if bullet_img:
                screen.blit(bullet_img, (b.left + shake_offset_x, b.top + shake_offset_y))
            else:
                pygame.draw.rect(screen, BULLET_COLOR, b.move(shake_offset_x, shake_offset_y))

        if not boss_defeated:
            boss_draw_x = int(boss_center_x + shake_offset_x)
            boss_draw_y = int(boss_center_y + shake_offset_y)
            
            # Aura pulsante ao redor do boss
            aura_size = int(BOSS_ORBIT_RADIUS + 30 + math.sin(aura_pulse) * 10)
            aura_alpha = int(50 + math.sin(aura_pulse * 2) * 30)
            aura_color = (255, 100, 100) if boss_hp <= 2 else (100, 100, 255)
            
            # Desenha múltiplos círculos de aura
            for i in range(3):
                radius = aura_size - i * 15
                if radius > 0:
                    pygame.draw.circle(screen, aura_color, (boss_draw_x, boss_draw_y), radius, 2)
            
            # Desenha balões orbitantes
            for b in balloons_around_boss:
                draw_x = b["rect"].left + shake_offset_x
                draw_y = b["rect"].top + shake_offset_y
                
                if b.get("exploding", False):
                    frame_index = int(b["explosion_frame_index"])
                    anim_frames = explosion_animations.get(b["type"], [])
                    if anim_frames and 0 <= frame_index < len(anim_frames):
                        img = anim_frames[frame_index]
                        center_x, center_y = b["rect"].center
                        explosion_rect = img.get_rect()
                        explosion_rect.center = (center_x + shake_offset_x, center_y + shake_offset_y)
                        screen.blit(img, explosion_rect.topleft)
                elif b["image"]: 
                    screen.blit(b["image"], (draw_x, draw_y))
                else: 
                    pygame.draw.circle(screen, ITEM_COLORS.get(b["type"], WHITE), 
                                       (b["rect"].centerx + shake_offset_x, b["rect"].centery + shake_offset_y), 
                                       ITEM_IMAGE_WIDTH // 2)
            
            # Desenha o boss (com flash quando leva dano)
            if boss_sprite:
                boss_img = boss_sprite.copy()
                if current_time_ticks < boss_hit_flash_until:
                    # Flash branco quando leva dano
                    boss_img.fill((255, 255, 255), special_flags=pygame.BLEND_ADD)
                
                boss_rect_draw = boss_img.get_rect(center=(boss_draw_x, boss_draw_y))
                screen.blit(boss_img, boss_rect_draw.topleft)
            else:
                # Fallback: desenha círculo
                color = (255, 255, 255) if current_time_ticks < boss_hit_flash_until else (200, 50, 50)
                pygame.draw.circle(screen, color, (boss_draw_x, boss_draw_y), BOSS_IMAGE_WIDTH // 2)
            
            # Barra de vida do boss
            draw_boss_health_bar(screen, boss_hp, BOSS_MAX_HP, boss_draw_x, boss_draw_y)

        # Desenha partículas
        for p in particles:
            p.draw(screen)

        # HUD
        screen.blit(second_font.render(f"PONTUAÇÃO: {current_score}", True, WHITE), (10, 10))
        
        if boss_defeated:
            # Texto de vitória pulsante
            victory_scale = 1.0 + math.sin(victory_animation_timer * 5) * 0.1
            victory_text = title_font.render("VITÓRIA!", True, (255, 215, 0))
            vt_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, GAME_HEIGHT // 2))
            screen.blit(victory_text, vt_rect)
            
            bonus_text = second_font.render(f"+{BOSS_VICTORY_BONUS} PONTOS!", True, (50, 255, 50))
            bt_rect = bonus_text.get_rect(center=(SCREEN_WIDTH // 2, GAME_HEIGHT // 2 + 60))
            screen.blit(bonus_text, bt_rect)
        else:
            screen.blit(second_font.render("DERROTE O BOSS!", True, (255, 100, 100)), (10, 45))
        
        draw_player_lives(screen, player_lives)

        # Gráficos
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