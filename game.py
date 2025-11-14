import pygame
import random
import math

# --- Constantes e Configurações (Layout Horizontal, Jogador Livre) ---
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
    "red": 100,
    "green": 500,
    "purple": 2000,
    "orange": 4000
}

# Spawn / movimento
ITEM_SPAWN_RATE = 30  
ITEM_FALL_SPEED = 8   
BULLET_SPEED = 20 
BULLET_WIDTH = 35 
BULLET_HEIGHT = 4 
SHOOT_COOLDOWN = 200 

# --- Inicialização do Pygame ---
pygame.init()
pygame.font.init()
pygame.mixer.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Monkey Runners")
clock = pygame.time.Clock() 
main_font = pygame.font.SysFont("Consolas", 18) 
title_font = pygame.font.SysFont("Consolas", 26, bold=True)

# --- Carregar Áudio ---
try:
    MUSIC_FILE = "musica.mp3" 
    VOLUME = 0.10 
    
    pygame.mixer.music.load(MUSIC_FILE)
    pygame.mixer.music.set_volume(VOLUME)
    pygame.mixer.music.play(-1) 
    print(f"Música {MUSIC_FILE} carregada e tocando a {VOLUME*100:.0f}%")
except pygame.error:
    print(f"AVISO: Não foi possível carregar o arquivo '{MUSIC_FILE}'. Verifique se ele existe.")


# --- Carregar Imagem do Jogador ---
player_width = 110  
player_height = 90 
player_image = None
try:
    player_image = pygame.image.load("monkey.png").convert_alpha()
    player_image = pygame.transform.scale(player_image, (player_width, player_height))
except pygame.error as e:
    print(f"ERRO: Não foi possível carregar 'monkey.png'. Usando quadrado azul. Detalhes: {e}")
    

# --- Carregar Imagens dos Balões (Inimigos) ---
ITEM_IMAGE_WIDTH = 60 # Largura dos balões
ITEM_IMAGE_HEIGHT = 80 # NOVO: Altura dos balões (aumentada)
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
    balloon_images = {} # Limpa as imagens para usar o fallback


# --- Variáveis do Jogo ---
player_rect = pygame.Rect(30, GAME_HEIGHT // 2 - player_height // 2, player_width, player_height) 
player_speed = 8 
items = [] 
bullets = [] 
item_spawn_timer = 0
last_shot_time = 0

# ----- VARIÁVEIS DE ESTADO -----
current_score = 0
score_vs_time = [(0.0, 0)]
start_time_ms = pygame.time.get_ticks()

stats_counts = {"red": 0, "green": 0, "purple": 0, "orange": 0}
stats_intervals = {"0-0.7s": 0, "0.7-1.4": 0, "1.4-2.0": 0, "2.0s+": 0} 
INTERVAL_KEYS = list(stats_intervals.keys())
INTERVAL_COLORS = {key: GRAPH_YELLOW for key in INTERVAL_KEYS}
last_collection_time = pygame.time.get_ticks() 
all_collection_intervals = []


# ----------------------------------------------------------------------
## Funções de Desenho
# ----------------------------------------------------------------------

def get_empirical_prob(item_type, current_counts):
    total_count = sum(current_counts.values())
    if total_count == 0:
        return 0.0
    return current_counts.get(item_type, 0) / float(total_count)


def draw_game(player, item_list, bullet_list, player_img):
    pygame.draw.rect(screen, LIGHT_BLUE, (0, 0, GAME_WIDTH, GAME_HEIGHT))
    
    if player_img:
        screen.blit(player_img, player.topleft)
    else:
        pygame.draw.rect(screen, PLAYER_COLOR, player)
    
    # Desenha os inimigos (agora com imagens de balões)
    for item in item_list:
        if item["image"]: 
            screen.blit(item["image"], item["rect"].topleft)
        else: 
            center = (int(item["rect"].centerx), int(item["rect"].centery))
            radius = int(item["rect"].width // 2)
            pygame.draw.circle(screen, item["color"], center, radius)

    for bullet in bullet_list:
        pygame.draw.rect(screen, BULLET_COLOR, bullet)
        
    score_text = title_font.render(f"PONTUAÇÃO: {current_score}", True, WHITE)
    screen.blit(score_text, (10, 10))


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

        label_text = main_font.render(str(item_type), True, WHITE) 
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
    graph_title_rect = graph_title_text.get_rect(center=(bounds_rect.centerx, bounds_rect.top + 20))
    surface.blit(graph_title_text, graph_title_rect)

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
    max_score_scaled = math.ceil(max(4000, max_score_raw) / Y_STEP) * Y_STEP

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
## Loop Principal do Jogo
# ----------------------------------------------------------------------
running = True
while running:
    elapsed_time_sec = (pygame.time.get_ticks() - start_time_ms) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.mixer.music.stop() 
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: 
                current_time = pygame.time.get_ticks()
                if current_time - last_shot_time > SHOOT_COOLDOWN:
                    bullet_rect = pygame.Rect(
                        player_rect.right, 
                        player_rect.centery - BULLET_HEIGHT // 2, 
                        BULLET_WIDTH, 
                        BULLET_HEIGHT
                    )
                    bullets.append(bullet_rect)
                    last_shot_time = current_time

    # --- Teclas (Controles Livres 4-direções) ---
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_UP]: 
        player_rect.y -= player_speed
    if keys[pygame.K_DOWN]: 
        player_rect.y += player_speed
        
    if keys[pygame.K_LEFT]: 
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT]: 
        player_rect.x += player_speed


    # --- Limites do jogador (Vertical e Horizontal) ---
    if player_rect.top < 0:
        player_rect.top = 0
    if player_rect.bottom > GAME_HEIGHT: 
        player_rect.bottom = GAME_HEIGHT
    
    if player_rect.left < 0:
        player_rect.left = 0
    if player_rect.right > GAME_WIDTH: 
        player_rect.right = GAME_WIDTH


    # --- Spawn de inimigos (Vem da Direita) ---
    item_spawn_timer += 1
    if item_spawn_timer >= ITEM_SPAWN_RATE:
        item_spawn_timer = 0
        item_type = random.choices(COLOR_TYPES, weights=[ITEM_PROBABILITIES[t] for t in COLOR_TYPES], k=1)[0]
        item_color = ITEM_COLORS[item_type]
        item_x = GAME_WIDTH + ITEM_IMAGE_WIDTH 
        item_y = random.randint(0, GAME_HEIGHT - ITEM_IMAGE_HEIGHT) # Usa a nova altura para o spawn
        
        # Cria o rect do item com o novo tamanho (largura, altura) da imagem
        new_item_rect = pygame.Rect(item_x, item_y, ITEM_IMAGE_WIDTH, ITEM_IMAGE_HEIGHT)
        items.append({"rect": new_item_rect, "color": item_color, "type": item_type, "image": balloon_images.get(item_type)})

    # Mover projéteis (Para Direita)
    for i in range(len(bullets) - 1, -1, -1):
        bullet = bullets[i]
        bullet.x += BULLET_SPEED 
        if bullet.left > GAME_WIDTH: 
            bullets.pop(i)

    # Mover inimigos (Para Esquerda)
    for i in range(len(items) - 1, -1, -1):
        item = items[i]
        item["rect"].x -= ITEM_FALL_SPEED 
        
        if item["rect"].right < 0:
            items.pop(i)
            continue

        # Colisão com JOGADOR 
        if player_rect.colliderect(item["rect"]):
            print("GAME OVER! Inimigo atingiu o jogador.")
            pygame.mixer.music.stop()
            running = False 
            items.pop(i) 
            continue

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

                current_time = pygame.time.get_ticks()
                interval_sec = (current_time - last_collection_time) / 1000.0
                last_collection_time = current_time
                all_collection_intervals.append(interval_sec)

                if interval_sec < 0.7:
                    stats_intervals["0-0.7s"] += 1
                elif interval_sec < 1.4:
                    stats_intervals["0.7-1.4"] += 1
                elif interval_sec < 2.0:
                    stats_intervals["1.4-2.0"] += 1
                elif interval_sec < 2.5: 
                    stats_intervals["2.0s+"] += 1 

                items.pop(i_idx)
                bullets.pop(b_idx)
                
                hit_detected = True
                break 
        
        if hit_detected:
            continue

    # --- Renderização ---
    screen.fill(BLACK) 
    draw_game(player_rect, items, bullets, player_image) 

    # --- Define os RECTs dos gráficos ---
    rect_grafico_1 = pygame.Rect(0, GAME_HEIGHT, GRAPH_WIDTH_PER_PLOT, GRAPH_HEIGHT)
    rect_grafico_2 = pygame.Rect(GRAPH_X_SPLIT_1, GAME_HEIGHT, GRAPH_WIDTH_PER_PLOT, GRAPH_HEIGHT)
    rect_grafico_3 = pygame.Rect(GRAPH_X_SPLIT_2, GAME_HEIGHT, GRAPH_WIDTH_PER_PLOT, GRAPH_HEIGHT)

    draw_histogram(screen, stats_counts, COLOR_TYPES, ITEM_COLORS,
                   "Contagem (Destruídos)", rect_grafico_1,
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
    clock.tick(60)

pygame.quit()