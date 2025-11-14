import pygame
import random
import math
import menu # Assume que existe um arquivo 'menu.py' para a tela inicial

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

# NOVO: Valores de pontuação menores e menos exorbitantes
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
ITEM_SPEED_INTERVAL = 15.0 # ALTERADO: Aumento de velocidade a cada 15 segundos
 
BULLET_SPEED = 20 
BULLET_WIDTH = 35 
BULLET_HEIGHT = 4 
SHOOT_COOLDOWN = 200 

# Velocidade do jogador em pixels por segundo (para movimento fluido)
PLAYER_MAX_VELOCITY = 400 

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

        # RÓTULO DO EIXO X: Mostra a contagem numérica no gráfico de "Contagem"
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
    
    # NOVO: Ajuste de escala para os novos valores de pontuação (max single score 1600, usa 2000 como base)
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
# --- FUNÇÃO PRINCIPAL DO JOGO (STATE: GAME) ---
# ----------------------------------------------------------------------

# Defina a variável global current_score no topo do script principal
global current_score
current_score = 0

# Variáveis do Joystick (mantidas fora do loop principal, mas inicializadas dentro do main/run_game)
joystick_x = 0.0
joystick_y = 0.0

def run_game(screen):
    
    # Variáveis de Controle de Dificuldade
    current_item_speed = ITEM_INITIAL_SPEED
    last_speed_increase_time = pygame.time.get_ticks()

    # Variáveis do Jogo
    player_rect = pygame.Rect(30, GAME_HEIGHT // 2 - player_height // 2, player_width, player_height) 
    items = [] 
    bullets = [] 
    item_spawn_timer = 0
    last_shot_time = 0

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
        # Verifica o tempo decorrido desde o último aumento (em segundos)
        if (current_time_ticks - last_speed_increase_time) / 1000.0 >= ITEM_SPEED_INTERVAL:
            current_item_speed += ITEM_SPEED_INCREASE
            last_speed_increase_time = current_time_ticks
            print(f"Dificuldade Aumentada! Velocidade atual: {current_item_speed:.2f}")


        # Resetar os valores do joystick a cada frame
        global joystick, joystick_x, joystick_y, JOYSTICK_DEADZONE
        joystick_x = 0.0
        joystick_y = 0.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop() 
                return "QUIT" 
            
            # --- EVENTOS DE CONTROLE ---
            if joystick:
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis == 0: 
                        joystick_x = event.value
                    elif event.axis == 1: 
                        joystick_y = event.value
                
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0: 
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

        # Leitura do Joystick
        if joystick:
            if abs(joystick_x) > JOYSTICK_DEADZONE:
                move_x += joystick_x
            if abs(joystick_y) > JOYSTICK_DEADZONE:
                move_y += joystick_y

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


        # --- Spawn de inimigos (Vem da Direita) ---
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

        # Mover inimigos (USANDO A VELOCIDADE ATUALIZADA current_item_speed)
        for i in range(len(items) - 1, -1, -1):
            item = items[i]
            item["rect"].x -= current_item_speed 
            
            if item["rect"].right < 0:
                items.pop(i)
                continue

            # Colisão com JOGADOR 
            if player_rect.colliderect(item["rect"]):
                print("GAME OVER! Inimigo atingiu o jogador.")
                pygame.mixer.music.stop()
                items.pop(i) 
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

        draw_game(player_rect, items, bullets, current_player_img)
        
        score_text = title_font.render(f"PONTUAÇÃO: {current_score}", True, WHITE)
        screen.blit(score_text, (10, 10))


        # --- Define os RECTs dos gráficos ---
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
# --- LOOP PRINCIPAL DA APLICAÇÃO (GERENCIADOR DE ESTADO) ---
# ----------------------------------------------------------------------

def main():
    # Garante que o joystick esteja inicializado globalmente para toda a aplicação
    global joystick
    
    current_state = "MENU"
    
    while True:
        if current_state == "MENU":
            # Assume que menu.show_menu existe e retorna "PLAY" ou "QUIT"
            result = menu.show_menu(screen, SCREEN_WIDTH, SCREEN_HEIGHT, title_font, main_font)
            if result == "PLAY":
                current_state = "GAME"
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
            elif result == "QUIT":
                break 

    pygame.quit()

if __name__ == "__main__":
    main()