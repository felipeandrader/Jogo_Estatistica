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
SCORE_TO_BOSS = 200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000

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
title_font = pygame.font.SysFont("Consolas", 26, bold=True)

# --- Configuração do Joystick Global ---
joystick = None
JOYSTICK_DEADZONE = 0.1

if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Controle detectado: {joystick.get_name()}")
else:
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


# --- Carregar Imagem do Jogador ---
player_width = 110
player_height = 90
player_animation_frames = []
player_filenames = ["macaco1.png", "macaco2.png", "macaco3.png"]

try:
    for filename in player_filenames:
        image = pygame.image.load(filename).convert_alpha()
        image = pygame.transform.scale(image, (player_width, player_height))
        player_animation_frames.append(image)
    print(f"Animação do jogador carregada ({len(player_animation_frames)} frames).")
except pygame.error as e:
    print(f"ERRO: Não foi possível carregar a animação 'macaco*.png'. Usando quadrado azul. Detalhes: {e}")
    player_animation_frames = []


# --- Carregar Imagens dos Balões (Inimigos) ---
ITEM_IMAGE_WIDTH = 60
ITEM_IMAGE_HEIGHT = 80
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


def draw_game(player, item_list, bullet_list, player_img, pos_hit_until_ms=0, current_time_ticks=None):
    pygame.draw.rect(screen, LIGHT_BLUE, (0, 0, GAME_WIDTH, GAME_HEIGHT))

    # Efeito de piscar durante a janela pos-hit
    if player_img:
        pos_hit_active = False
        if current_time_ticks is not None and current_time_ticks < pos_hit_until_ms:
            pos_hit_active = True

        if pos_hit_active:
            BLINK_INTERVAL_MS = 150
            ALPHA_LOW = 80
            ALPHA_HIGH = 160
            try:
                phase = (current_time_ticks // BLINK_INTERVAL_MS) % 2
                alpha_val = ALPHA_LOW if phase == 0 else ALPHA_HIGH
                temp_img = player_img.copy()
                temp_img.set_alpha(int(alpha_val))
                screen.blit(temp_img, player.topleft)
            except Exception:
                screen.blit(player_img, player.topleft)
        else:
            screen.blit(player_img, player.topleft)
    else:
        pygame.draw.rect(screen, PLAYER_COLOR, player)

    for item in item_list:
        if item["image"]:
            screen.blit(item["image"], item["rect"].topleft)
        else:
            center = (int(item["rect"].centerx), int(item["rect"].centery))
            radius = int(item["rect"].width // 2)
            pygame.draw.circle(screen, item["color"], center, radius)

    for bullet in bullet_list:
        pygame.draw.rect(screen, BULLET_COLOR, bullet)


def draw_histogram(surface, data_dict, data_keys, data_colors, title, bounds_rect, expected_prob_func=None):
    pygame.draw.rect(screen, GRAY, bounds_rect)

    graph_x_start = bounds_rect.left + 30
    graph_y_bottom = bounds_rect.bottom - 30

    title_text = title_font.render(title, True, WHITE)
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

    graph_title_text = title_font.render("Pontuação x Tempo", True, WHITE)
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

def run_game(screen):
    # Variáveis de Controle de Dificuldade
    current_item_speed = ITEM_INITIAL_SPEED
    last_speed_increase_time = pygame.time.get_ticks()

    # Variáveis do Jogo
    items = []
    bullets = []
    item_spawn_timer = 0
    last_shot_time = 0
    pos_hit_until_ms = 0

    # Variáveis de Animação
    player_frame_index = 0
    player_last_frame_update = pygame.time.get_ticks()
    PLAYER_ANIMATION_SPEED_MS = 100
    PLAYER_ANIMATION_SEQUENCE = [1, 0, 2, 0]

    # Variáveis de Estado
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
    all_collection_intervals = []

    # --- Loop Principal do Jogo ---
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        current_time_ticks = pygame.time.get_ticks()
        elapsed_time_sec = (current_time_ticks - start_time_ms) / 1000.0

        # --- LÓGICA DE AUMENTO DE VELOCIDADE (DIFICULDADE) ---
        global ITEM_SPEED_INTERVAL, ITEM_SPEED_INCREASE
        if (current_time_ticks - last_speed_increase_time) / 1000.0 >= ITEM_SPEED_INTERVAL:
            current_item_speed += ITEM_SPEED_INCREASE
            last_speed_increase_time = current_time_ticks
            print(f"Dificuldade Aumentada! Velocidade atual: {current_item_speed:.2f}")

        # NOTA: Não resetamos mais joystick_x/y aqui. Lemos direto no movimento.

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return "QUIT"

            # --- EVENTOS DE BOTÕES (TIRO) ---
            if joystick:
                if event.type == pygame.JOYBUTTONDOWN:
                    # ALTERADO DE 0 (A) PARA 2 (X)
                    if event.button == 2:
                        if current_time_ticks - last_shot_time > SHOOT_COOLDOWN:
                            bullet_rect = pygame.Rect(player_rect.right, player_rect.centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT)
                            bullets.append(bullet_rect)
                            last_shot_time = current_time_ticks

            # --- EVENTOS DE TECLADO (DISPARO) ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if current_time_ticks - last_shot_time > SHOOT_COOLDOWN:
                        bullet_rect = pygame.Rect(player_rect.right, player_rect.centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT)
                        bullets.append(bullet_rect)
                        last_shot_time = current_time_ticks

        # --- Aplicação do Movimento (Teclado e Controle Fluido) ---
        keys = pygame.key.get_pressed()

        move_x = 0.0
        move_y = 0.0

        # Leitura do teclado
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y -= 1.0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y += 1.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x += 1.0

        # --- CORREÇÃO DO CONTROLE: Leitura direta dos eixos (Polling) ---
        if joystick:
            axis_x = joystick.get_axis(0)  # Horizontal
            axis_y = joystick.get_axis(1)  # Vertical

            if abs(axis_x) > JOYSTICK_DEADZONE:
                move_x += axis_x
            if abs(axis_y) > JOYSTICK_DEADZONE:
                move_y += axis_y

        # Normalizar vetor para evitar que diagonais sejam mais rápidas
        length = math.hypot(move_x, move_y)
        if length > 0:
            if length > 1: # Se magnitude > 1, normaliza
                move_x /= length
                move_y /= length

        # Aplicação do movimento fluido (dt-based)
        player_rect.x += move_x * PLAYER_MAX_VELOCITY * dt
        player_rect.y += move_y * PLAYER_MAX_VELOCITY * dt

        # --- Limites do jogador (Vertical e Horizontal) ---
        if player_rect.top < 0:
            player_rect.top = 0
        if player_rect.bottom > GAME_HEIGHT:
            player_rect.bottom = GAME_HEIGHT
        if player_rect.left < 0:
            player_rect.left = 0
        if player_rect.right > GAME_WIDTH:
            player_rect.right = GAME_WIDTH

        # --- Spawn de inimigos ---
        item_spawn_timer += 1
        if item_spawn_timer >= ITEM_SPAWN_RATE:
            item_spawn_timer = 0
            item_type = random.choices(COLOR_TYPES, weights=[ITEM_PROBABILITIES[t] for t in COLOR_TYPES], k=1)[0]
            item_color = ITEM_COLORS[item_type]

            item_x = GAME_WIDTH + ITEM_IMAGE_WIDTH
            item_y = random.randint(0, GAME_HEIGHT - ITEM_IMAGE_HEIGHT)

            new_item_rect = pygame.Rect(item_x, item_y, ITEM_IMAGE_WIDTH, ITEM_IMAGE_HEIGHT)
            items.append({"rect": new_item_rect, "color": item_color, "type": item_type, "image": balloon_images.get(item_type)})

        # Mover projéteis
        for i in range(len(bullets) - 1, -1, -1):
            bullet = bullets[i]
            bullet.x += BULLET_SPEED
            if bullet.left > GAME_WIDTH:
                bullets.pop(i)

        # Mover inimigos
        for i in range(len(items) - 1, -1, -1):
            item = items[i]
            item["rect"].x -= current_item_speed

            if item["rect"].right < 0:
                items.pop(i)
                continue

            # Colisão com JOGADOR
            if player_rect.colliderect(item["rect"]):
                if current_time_ticks < pos_hit_until_ms:
                    continue

                hit_sound.play()
                items.pop(i)
                player_lives -= 1
                pos_hit_until_ms = current_time_ticks + 1000
                print(f"Jogador atingido! Vidas restantes: {player_lives}")
                if player_lives <= 0:
                    print("GAME OVER! Vidas esgotadas.")
                    pygame.mixer.music.stop()
                    return "GAME_OVER"

        # Colisão PROJÉTIL-INIMIGO
        for b_idx in range(len(bullets) - 1, -1, -1):
            bullet = bullets[b_idx]
            hit_detected = False

            for i_idx in range(len(items) - 1, -1, -1):
                item = items[i_idx]

                if bullet.colliderect(item["rect"]):
                    item_type = item["type"]
                    current_score += ITEM_SCORES[item_type]

                    score_vs_time.append((elapsed_time_sec, current_score))
                    stats_counts[item_type] += 1

                    interval_sec = (current_time_ticks - last_collection_time) / 1000.0
                    last_collection_time = current_time_ticks
                    all_collection_intervals.append(interval_sec)

                    if interval_sec < 0.7:
                        stats_intervals["0-0.7s"] += 1
                    elif interval_sec < 1.4:
                        stats_intervals["0.7-1.4"] += 1
                    elif interval_sec < 2.0:
                        stats_intervals["1.4-2.0"] += 1
                    else:
                        stats_intervals["2.0s+"] += 1

                    items.pop(i_idx)
                    bullets.pop(b_idx)

                    hit_detected = True
                    break

            if hit_detected:
                continue

        if current_score >= SCORE_TO_BOSS:
            print(f"BOSS FIGHT DESBLOQUEADA! Pontuação: {current_score}")
            pygame.mixer.music.stop()
            global boss_stats_counts, boss_stats_intervals, boss_score_vs_time, boss_snapshot_elapsed
            boss_stats_counts = stats_counts.copy()
            boss_stats_intervals = stats_intervals.copy()
            boss_score_vs_time = score_vs_time.copy()
            boss_snapshot_elapsed = elapsed_time_sec
            return "BOSS_FIGHT"

        # --- Atualização da Animação do Player ---
        if player_animation_frames:
            if current_time_ticks - player_last_frame_update > PLAYER_ANIMATION_SPEED_MS:
                player_last_frame_update = current_time_ticks
                player_frame_index = (player_frame_index + 1) % len(PLAYER_ANIMATION_SEQUENCE)

        # --- Renderização ---
        screen.fill(BLACK)

        current_player_img = None
        if player_animation_frames:
            actual_frame_index = PLAYER_ANIMATION_SEQUENCE[player_frame_index]
            current_player_img = player_animation_frames[actual_frame_index]

        draw_game(player_rect, items, bullets, current_player_img, pos_hit_until_ms, current_time_ticks)

        score_text = title_font.render(f"PONTUAÇÃO: {current_score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        draw_player_lives(screen, player_lives)

        # --- Gráficos ---
        rect_grafico_1 = pygame.Rect(0, GAME_HEIGHT, GRAPH_WIDTH_PER_PLOT, GRAPH_HEIGHT)
        rect_grafico_2 = pygame.Rect(GRAPH_X_SPLIT_1, GAME_HEIGHT, GRAPH_WIDTH_PER_PLOT, GRAPH_HEIGHT)
        rect_grafico_3 = pygame.Rect(GRAPH_X_SPLIT_2, GAME_HEIGHT, GRAPH_WIDTH_PER_PLOT, GRAPH_HEIGHT)

        draw_histogram(screen, stats_counts, COLOR_TYPES, ITEM_COLORS,
                       "Contagem", rect_grafico_1,
                       expected_prob_func=lambda t: get_empirical_prob(t, stats_counts))

        draw_scatter_plot(screen, score_vs_time, rect_grafico_2, elapsed_time_sec)

        draw_histogram(screen, stats_intervals, INTERVAL_KEYS, INTERVAL_COLORS,
                       "Intervalo de Destruição", rect_grafico_3,
                       expected_prob_func=lambda k: get_empirical_prob(k, stats_intervals))

        # --- Divisórias ---
        pygame.draw.line(screen, WHITE, (0, GAME_HEIGHT), (SCREEN_WIDTH, GAME_HEIGHT), 3)
        pygame.draw.line(screen, WHITE, (GRAPH_X_SPLIT_1, GAME_HEIGHT), (GRAPH_X_SPLIT_1, SCREEN_HEIGHT), 3)
        pygame.draw.line(screen, WHITE, (GRAPH_X_SPLIT_2, GAME_HEIGHT), (GRAPH_X_SPLIT_2, SCREEN_HEIGHT), 3)

        pygame.display.flip()


# ----------------------------------------------------------------------
# --- CENA DO BOSS (PREPARAÇÃO) ---
# ----------------------------------------------------------------------

boss_rect = pygame.Rect(962, 262, BOSS_IMAGE_WIDTH, BOSS_IMAGE_HEIGHT)

def run_game_boss(screen):
    global current_score
    global player_lives

    items = []  # não haverá novos itens
    bullets = []
    last_shot_time = 0
    pos_hit_until_ms = 0

    player_frame_index = 0
    player_last_frame_update = pygame.time.get_ticks()
    PLAYER_ANIMATION_SPEED_MS = 100
    PLAYER_ANIMATION_SEQUENCE = [1, 0, 2, 0]

    start_time_ms = pygame.time.get_ticks()
    last_collection_time_boss = start_time_ms

    # Configura balões ao redor do boss
    boss_center_x, boss_center_y = boss_rect.center
    radius_x = boss_rect.width // 2 + 100
    radius_y = boss_rect.height // 2 + 100
    angles_deg = [0, 60, 120, 180, 240, 300]

    hexagon_points = []
    for ang in angles_deg:
        rad = math.radians(ang)
        cx = int(boss_center_x + radius_x * math.cos(rad))
        cy = int(boss_center_y + radius_y * math.sin(rad))
        hexagon_points.append((cx, cy))

    BOSS_BALLOON_SPEED = 160

    balloons_around_boss = []
    for i, (cx, cy) in enumerate(hexagon_points):
        chosen_type = random.choice(COLOR_TYPES)
        sprite = balloon_images.get(chosen_type)
        if sprite:
            rect = sprite.get_rect(center=(cx, cy))
        else:
            rect = pygame.Rect(cx - ITEM_IMAGE_WIDTH // 2, cy - ITEM_IMAGE_HEIGHT // 2, ITEM_IMAGE_WIDTH, ITEM_IMAGE_HEIGHT)
        target_idx = (i + 1) % len(hexagon_points)  # sentido horário
        balloons_around_boss.append({
            "type": chosen_type,
            "image": sprite,
            "rect": rect,
            "target_idx": target_idx
        })

    global boss_stats_counts, boss_stats_intervals, boss_score_vs_time, boss_snapshot_elapsed
    if boss_stats_counts is None:
        stats_counts_local = {k: 0 for k in COLOR_TYPES}
    else:
        stats_counts_local = boss_stats_counts.copy()

    if boss_stats_intervals is None:
        stats_intervals_local = {"0-0.7s": 0, "0.7-1.4": 0, "1.4-2.0": 0, "2.0s+": 0}
    else:
        stats_intervals_local = boss_stats_intervals.copy()

    if boss_score_vs_time is None:
        score_vs_time_local = [(0.0, current_score)]
    else:
        score_vs_time_local = boss_score_vs_time.copy()

    snapshot_elapsed = boss_snapshot_elapsed

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        current_time_ticks = pygame.time.get_ticks()
        elapsed_time_sec = (current_time_ticks - start_time_ms) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if joystick:
                if event.type == pygame.JOYBUTTONDOWN:
                    # ALTERADO DE 0 (A) PARA 2 (X)
                    if event.button == 2:
                        if current_time_ticks - last_shot_time > SHOOT_COOLDOWN:
                            bullet_rect = pygame.Rect(player_rect.right, player_rect.centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT)
                            bullets.append(bullet_rect)
                            last_shot_time = current_time_ticks

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if current_time_ticks - last_shot_time > SHOOT_COOLDOWN:
                        bullet_rect = pygame.Rect(player_rect.right, player_rect.centery - BULLET_HEIGHT // 2, BULLET_WIDTH, BULLET_HEIGHT)
                        bullets.append(bullet_rect)
                        last_shot_time = current_time_ticks

        # Movimento do jogador
        keys = pygame.key.get_pressed()
        move_x = 0.0
        move_y = 0.0
        if keys[pygame.K_UP] or keys[pygame.K_w]: move_y -= 1.0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: move_y += 1.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: move_x -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: move_x += 1.0

        # --- CORREÇÃO DO CONTROLE: Leitura direta dos eixos (Polling) ---
        if joystick:
            axis_x = joystick.get_axis(0)
            axis_y = joystick.get_axis(1)

            if abs(axis_x) > JOYSTICK_DEADZONE:
                move_x += axis_x
            if abs(axis_y) > JOYSTICK_DEADZONE:
                move_y += axis_y

        # Normalização
        length = math.hypot(move_x, move_y)
        if length > 0:
            if length > 1:
                move_x /= length
                move_y /= length

        player_rect.x += move_x * PLAYER_MAX_VELOCITY * dt
        player_rect.y += move_y * PLAYER_MAX_VELOCITY * dt

        # Limites do jogador
        if player_rect.top < 0: player_rect.top = 0
        if player_rect.bottom > GAME_HEIGHT: player_rect.bottom = GAME_HEIGHT
        if player_rect.left < 0: player_rect.left = 0
        if player_rect.right > GAME_WIDTH: player_rect.right = GAME_WIDTH

        # Movimento rotatório dos balões
        for b in balloons_around_boss:
            tx, ty = hexagon_points[b["target_idx"]]
            cx, cy = b["rect"].center
            dx = tx - cx
            dy = ty - cy
            dist = math.hypot(dx, dy)
            step = BOSS_BALLOON_SPEED * dt
            if dist <= max(4.0, step * 1.25):
                b["rect"].center = (tx, ty)
                b["target_idx"] = (b["target_idx"] + 1) % len(hexagon_points)
            else:
                nx = dx / dist if dist != 0 else 0
                ny = dy / dist if dist != 0 else 0
                cx += nx * step
                cy += ny * step
                b["rect"].center = (int(cx), int(cy))

        # Mover Balas
        for i in range(len(bullets) - 1, -1, -1):
            bullet = bullets[i]
            bullet.x += BULLET_SPEED
            if bullet.left > GAME_WIDTH:
                bullets.pop(i)
                continue

            # Colisão PROJÉTIL - BALÕES DO BOSS
            hit = False
            for bi in range(len(balloons_around_boss) - 1, -1, -1):
                b = balloons_around_boss[bi]
                if bullet.colliderect(b["rect"]):
                    b_type = b.get("type")
                    current_score += ITEM_SCORES.get(b_type, 0)

                    try:
                        stats_counts_local[b_type] = stats_counts_local.get(b_type, 0) + 1
                    except Exception:
                        pass

                    interval_sec = (current_time_ticks - last_collection_time_boss) / 1000.0
                    last_collection_time_boss = current_time_ticks
                    if interval_sec < 0.7:
                        stats_intervals_local["0-0.7s"] = stats_intervals_local.get("0-0.7s", 0) + 1
                    elif interval_sec < 1.4:
                        stats_intervals_local["0.7-1.4"] = stats_intervals_local.get("0.7-1.4", 0) + 1
                    elif interval_sec < 2.0:
                        stats_intervals_local["1.4-2.0"] = stats_intervals_local.get("1.4-2.0", 0) + 1
                    else:
                        stats_intervals_local["2.0s+"] = stats_intervals_local.get("2.0s+", 0) + 1

                    score_time = snapshot_elapsed + elapsed_time_sec
                    score_vs_time_local.append((score_time, current_score))

                    balloons_around_boss.pop(bi)
                    bullets.pop(i)
                    hit = True
                    break
            if hit:
                continue

        # Animação player
        if player_animation_frames:
            if current_time_ticks - player_last_frame_update > PLAYER_ANIMATION_SPEED_MS:
                player_last_frame_update = current_time_ticks
                player_frame_index = (player_frame_index + 1) % len(PLAYER_ANIMATION_SEQUENCE)

        # Colisão jogador - balões boss
        for bi in range(len(balloons_around_boss) - 1, -1, -1):
            b = balloons_around_boss[bi]
            if player_rect.colliderect(b["rect"]):
                if current_time_ticks < pos_hit_until_ms:
                    continue

                hit_sound.play()
                balloons_around_boss.pop(bi)
                player_lives -= 1
                pos_hit_until_ms = current_time_ticks + 1000
                print(f"Jogador atingido pelo boss! Vidas restantes: {player_lives}")
                if player_lives <= 0:
                    print("GAME OVER! Vidas esgotadas na cena do boss.")
                    pygame.mixer.music.stop()
                    return "GAME_OVER"

        # Renderização
        screen.fill(BLACK)
        current_player_img = None
        if player_animation_frames:
            actual_frame_index = PLAYER_ANIMATION_SEQUENCE[player_frame_index]
            current_player_img = player_animation_frames[actual_frame_index]

        draw_game(player_rect, items, bullets, current_player_img, pos_hit_until_ms, current_time_ticks)

        pygame.draw.rect(screen, (200, 50, 50), boss_rect, width=4)
        for b in balloons_around_boss:
            if b["image"]:
                screen.blit(b["image"], b["rect"].topleft)
            else:
                center = b["rect"].center
                pygame.draw.circle(screen, ITEM_COLORS.get(b["type"], WHITE), center, ITEM_IMAGE_WIDTH // 2)

        if boss_sprite:
            screen.blit(boss_sprite, boss_rect.topleft)

        score_text = title_font.render(f"PONTUAÇÃO: {current_score}", True, WHITE)
        boss_text = title_font.render("CENA DO BOSS - Prepare-se!", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(boss_text, (10, 45))
        draw_player_lives(screen, player_lives)

        rect_grafico_1 = pygame.Rect(0, GAME_HEIGHT, GRAPH_WIDTH_PER_PLOT, GRAPH_HEIGHT)
        rect_grafico_2 = pygame.Rect(GRAPH_X_SPLIT_1, GAME_HEIGHT, GRAPH_WIDTH_PER_PLOT, GRAPH_HEIGHT)
        rect_grafico_3 = pygame.Rect(GRAPH_X_SPLIT_2, GAME_HEIGHT, GRAPH_WIDTH_PER_PLOT, GRAPH_HEIGHT)

        INTERVAL_KEYS_LOCAL = list(stats_intervals_local.keys())
        INTERVAL_COLORS_LOCAL = {key: GRAPH_YELLOW for key in INTERVAL_KEYS_LOCAL}

        draw_histogram(screen, stats_counts_local, COLOR_TYPES, ITEM_COLORS,
                "Contagem", rect_grafico_1,
                expected_prob_func=lambda t: get_empirical_prob(t, stats_counts_local))

        draw_scatter_plot(screen, score_vs_time_local, rect_grafico_2, snapshot_elapsed + elapsed_time_sec)

        draw_histogram(screen, stats_intervals_local, INTERVAL_KEYS_LOCAL, INTERVAL_COLORS_LOCAL,
                "Intervalo de Destruição", rect_grafico_3,
                expected_prob_func=lambda k: get_empirical_prob(k, stats_intervals_local))

        pygame.draw.line(screen, WHITE, (0, GAME_HEIGHT), (SCREEN_WIDTH, GAME_HEIGHT), 3)
        pygame.draw.line(screen, WHITE, (GRAPH_X_SPLIT_1, GAME_HEIGHT), (GRAPH_X_SPLIT_1, SCREEN_HEIGHT), 3)
        pygame.draw.line(screen, WHITE, (GRAPH_X_SPLIT_2, GAME_HEIGHT), (GRAPH_X_SPLIT_2, SCREEN_HEIGHT), 3)

        pygame.display.flip()

# ----------------------------------------------------------------------
# --- LOOP PRINCIPAL DA APLICAÇÃO ---
# ----------------------------------------------------------------------

def main():
    global joystick
    global player_lives

    current_state = "MENU"

    while True:
        if current_state == "MENU":
            # Assume que menu.show_menu existe e retorna "PLAY" ou "QUIT"
            result = menu.show_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT, title_font, main_font)
            if result == "PLAY":
                current_state = "GAME"
                player_lives = 3
                try:
                    pygame.mixer.music.play(-1)
                except pygame.error:
                    print("Não foi possível tocar a música.")
            elif result == "QUIT":
                break

        elif current_state == "GAME":
            result = run_game(screen)
            if result == "GAME_OVER":
                final_score = current_score
                print(f"Fim de Jogo. Pontuação Final: {final_score}")
                current_state = "MENU"

            elif result == "BOSS_FIGHT":
                current_state = "BOSS"

            elif result == "QUIT":
                break

        elif current_state == "BOSS":
            result = run_game_boss(screen)

            if result == "GAME_OVER":
                final_score = current_score
                print(f"Fim de Jogo. Pontuação Final: {final_score}")
                current_state = "MENU"

            elif result == "QUIT":
                break
    pygame.quit()

if __name__ == "__main__":
    main()