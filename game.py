import pygame
import random
import math 

# --- Constantes e Configurações (AJUSTADAS PARA 1920x1080) ---
SCREEN_WIDTH = 1920 
SCREEN_HEIGHT = 1080
GAME_WIDTH = 960    
GRAPH_WIDTH = 960 

# --- Divisão da área de gráficos (Dividida em 3 partes iguais) ---
GRAPH_HEIGHT_PER_PLOT = SCREEN_HEIGHT // 3 # 1080 / 3 = 360
GRAPH_Y_SPLIT_1 = GRAPH_HEIGHT_PER_PLOT
GRAPH_Y_SPLIT_2 = GRAPH_HEIGHT_PER_PLOT * 2 

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
PLAYER_COLOR = (0, 100, 255) # Cor para o jogador (quadrado azul)
GRAPH_YELLOW = (255, 215, 0)
THEORETICAL_COLOR = (255, 0, 0) # Cor para a linha teórica
SCORE_POINT_COLOR = (0, 255, 255) # Cor dos pontos do Scatter Plot

# --- CONFIGURAÇÕES DE PROBABILIDADE E PONTUAÇÃO ---
NEW_COLOR_NAME = "orange"
NEW_COLOR_RGB = (255, 165, 0) 

ITEM_COLORS = { # Essas cores serão usadas para desenhar os itens
    "red": (255, 50, 50),
    "green": (50, 255, 50),
    "purple": (150, 50, 255),
    NEW_COLOR_NAME: NEW_COLOR_RGB
}
COLOR_TYPES = list(ITEM_COLORS.keys()) 

ITEM_PROBABILITIES = {
    "red": 0.50,
    "green": 0.25,
    "purple": 0.125,
    "orange": 0.125
}

ITEM_SCORES = {
    "red": 10,
    "green": 20,
    "purple": 40,
    "orange": 40
}

# --- Inicialização do Pygame ---
pygame.init()
pygame.font.init() 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jogo Estatístico - Formas Geométricas")
clock = pygame.time.Clock()
main_font = pygame.font.SysFont("Consolas", 30) 
title_font = pygame.font.SysFont("Consolas", 40, bold=True) 

# --- Variáveis do Jogo ---
player_size = 80 
player_rect = pygame.Rect(GAME_WIDTH // 2 - player_size // 2, SCREEN_HEIGHT - 90, player_size, player_size)
player_speed = 10 
items = [] 
item_spawn_timer = 0
ITEM_SPAWN_RATE = 30 

# ----- VARIÁVEIS DE ESTADO -----

# Variáveis do Scatter Plot
current_score = 0
score_vs_time = [(0.0, 0)] 
start_time_ms = pygame.time.get_ticks()

# 1. Estatísticas de Contagem (Histograma 1: Distribuição Discreta)
stats_counts = {
    "red": 0,
    "green": 0,
    "purple": 0,
    "orange": 0 
}

# 2. Estatísticas de Intervalo (Histograma 3: Distribuição Contínua (Intervalos))
stats_intervals = {
    "0-0.7s": 0,
    "0.7-1.4s": 0,
    "1.4-2.0s": 0,
    "2.0s- 2.5s": 0,
}
INTERVAL_KEYS = list(stats_intervals.keys())
INTERVAL_COLORS = {key: GRAPH_YELLOW for key in INTERVAL_KEYS}
last_collection_time = pygame.time.get_ticks() 
all_collection_intervals = [] # Para calcular a média e adaptar o fitting

# --- Funções Estatísticas e de Desenho ---

# Fitting para o Gráfico 1 (Distribuição Discreta)
def get_theoretical_prob(item_type):
    return ITEM_PROBABILITIES.get(item_type, 0.0) 

# Fitting para o Gráfico 3 (Distribuição Contínua - Exponencial ADAPTATIVA)
def get_theoretical_interval_prob(interval_key):
    # Calcula a taxa (lambda) adaptativamente com base nos intervalos observados
    if not all_collection_intervals:
        RATE_LAMBDA = 1.0 # Valor padrão se não houver dados
    else:
        mean_interval = sum(all_collection_intervals) / len(all_collection_intervals)
        RATE_LAMBDA = 1.0 / mean_interval if mean_interval > 0 else 1.0 # Taxa = 1 / Média

    # Definindo os limites do intervalo em segundos
    if interval_key == "0-0.7s":
        t1, t2 = 0.0, 0.7
    elif interval_key == "0.7-1.4s":
        t1, t2 = 0.7, 1.4
    elif interval_key == "1.4-2.0s":
        t1, t2 = 1.4, 2.0
    elif interval_key == "2.0s- 2.5s":
        t1, t2 = 2.0, 2.5
    else:
        return 0.0
        
    # Função de Sobrevivência (1 - CDF) para distribuição Exponencial
    # S(t) = e^(-lambda * t)
    def survival_function(t):
        try:
            return math.exp(-RATE_LAMBDA * t)
        except OverflowError:
            return 0.0

    # Probabilidade de cair no intervalo [t1, t2] é S(t1) - S(t2)
    prob = survival_function(t1) - survival_function(t2)
    return prob

def draw_game(player, item_list):
    """Desenha a área do jogo (lado esquerdo) e a pontuação."""
    pygame.draw.rect(screen, GRAY, (0, 0, GAME_WIDTH, SCREEN_HEIGHT))
    
    # Desenha o jogador como um quadrado azul
    pygame.draw.rect(screen, PLAYER_COLOR, player)

    for item in item_list:
        # Desenha o item como um círculo colorido
        pygame.draw.circle(screen, item["color"], item["rect"].center, item["rect"].width // 2)

    score_text = title_font.render(f"PONTUAÇÃO: {current_score}", True, WHITE)
    screen.blit(score_text, (20, 20))

def draw_histogram(
    surface, data_dict, data_keys, data_colors, title, bounds_rect, theoretical_prob_func=None 
):
    graph_x_start = bounds_rect.left + 80
    graph_y_bottom = bounds_rect.bottom - 80 
    
    title_text = title_font.render(title, True, WHITE)
    title_x = bounds_rect.left + (bounds_rect.width - title_text.get_width()) // 2
    title_y = bounds_rect.top + 30
    surface.blit(title_text, (title_x, title_y))

    total_count = sum(data_dict.values()) 
    max_val = max(data_dict.values())
    if max_val == 0: max_val = 1 
        
    max_bar_height = bounds_rect.height - 180 
    total_width_available = bounds_rect.width - 160 
    
    if len(data_keys) == 0: return 
    
    bar_width = total_width_available / (len(data_keys) * 1.5 + 0.5) 
    bar_spacing = bar_width * 0.5
    
    theoretical_line_points = []
    
    for i, item_type in enumerate(data_keys):
        count = data_dict[item_type]
        color = data_colors[item_type]
        
        bar_height = (count / max_val) * max_bar_height
        bar_x = graph_x_start + (i * (bar_width + bar_spacing))
        bar_y = graph_y_bottom - bar_height
        
        bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(surface, color, bar_rect)
        
        label_text = main_font.render(str(item_type), True, WHITE)
        label_x = bar_x + (bar_width - label_text.get_width()) // 2
        surface.blit(label_text, (label_x, graph_y_bottom + 10))
        
        if total_count > 0: 
            prob_emp = (count / total_count) * 100
            count_label = f"{prob_emp:.1f}% ({count})"
        else: 
            count_label = str(count)
            
        count_text = main_font.render(count_label, True, WHITE)
        count_x = bar_x + (bar_width - count_text.get_width()) // 2
        surface.blit(count_text, (count_x, bar_y - 35))
        
        # Lógica para desenhar o fitting teórico
        if theoretical_prob_func is not None and total_count > 0:
            prob_theoretical = theoretical_prob_func(item_type)
            
            theoretical_count_val = prob_theoretical * total_count
            theoretical_height = (theoretical_count_val / max_val) * max_bar_height
            
            theoretical_y = graph_y_bottom - theoretical_height
            theoretical_x = bar_x + bar_width // 2
            
            theoretical_line_points.append((theoretical_x, theoretical_y))

    if len(theoretical_line_points) >= 2:
        pygame.draw.lines(surface, THEORETICAL_COLOR, False, theoretical_line_points, 5)
        
        legend_text = main_font.render("Prob. Teórica", True, THEORETICAL_COLOR)
        legend_y = bounds_rect.top + max_bar_height + 120
        surface.blit(legend_text, (graph_x_start - 50, legend_y)) 

def draw_scatter_plot(surface, data_points, bounds_rect):
    """Desenha um gráfico de dispersão (Scatter Plot) de tempo x pontuação."""
    
    surface.fill(GRAY, bounds_rect) 
    
    title_text = title_font.render("Pontuação x Tempo (Série Temporal)", True, WHITE)
    title_x = bounds_rect.left + (bounds_rect.width - title_text.get_width()) // 2
    title_y = bounds_rect.top + 30
    surface.blit(title_text, (title_x, title_y))

    MARGIN = 50
    PLOT_AREA = pygame.Rect(
        bounds_rect.left + MARGIN,
        bounds_rect.top + MARGIN + 40,
        bounds_rect.width - 2 * MARGIN,
        bounds_rect.height - 2 * MARGIN - 40
    )
    
    # Desenha os eixos
    pygame.draw.line(surface, WHITE, PLOT_AREA.bottomleft, PLOT_AREA.topleft, 2) 
    pygame.draw.line(surface, WHITE, PLOT_AREA.bottomleft, PLOT_AREA.bottomright, 2) 
    
    if not data_points or len(data_points) < 2:
        empty_text = main_font.render("Coletando dados...", True, WHITE)
        surface.blit(empty_text, (PLOT_AREA.left + 50, PLOT_AREA.top + 50))
        return

    # Encontra os valores máximos para escala
    times = [p[0] for p in data_points]
    scores = [p[1] for p in data_points]
    
    max_time = times[-1] if times else 1 
    max_score = max(scores) if scores else 1 
    
    if max_score < 40: max_score = 40 
    if max_time < 1: max_time = 1
    
    # Desenha os Pontos e a Linha (Scatter Plot & Conexão)
    scaled_points = []
    
    for time, score in data_points:
        # Normalização e Escala
        x_norm = time / max_time
        y_norm = score / max_score
        
        # Converte para coordenadas de tela
        screen_x = PLOT_AREA.left + int(x_norm * PLOT_AREA.width)
        screen_y = PLOT_AREA.bottom - int(y_norm * PLOT_AREA.height) 
        
        scaled_points.append((screen_x, screen_y))
        
        # Desenha o ponto (círculo)
        pygame.draw.circle(surface, SCORE_POINT_COLOR, (screen_x, screen_y), 5)
        
    # Desenha a linha conectando os pontos
    if len(scaled_points) >= 2:
        pygame.draw.lines(surface, SCORE_POINT_COLOR, False, scaled_points, 3)

    # --- Rótulos dos Eixos (simplificados) ---
    
    # Rótulo X (Tempo)
    label_x_max = main_font.render(f"{max_time:.1f}s", True, WHITE)
    surface.blit(label_x_max, (PLOT_AREA.right - label_x_max.get_width(), PLOT_AREA.bottom + 10))
    label_x_title = main_font.render("Tempo (s)", True, WHITE)
    surface.blit(label_x_title, (PLOT_AREA.right - 150, PLOT_AREA.bottom + 40))

    # Rótulo Y (Pontuação)
    label_y_max = main_font.render(str(int(max_score)), True, WHITE)
    surface.blit(label_y_max, (PLOT_AREA.left - label_y_max.get_width() - 5, PLOT_AREA.top))
    label_y_title = main_font.render("Score", True, WHITE)
    surface.blit(label_y_title, (PLOT_AREA.left - 20, PLOT_AREA.top - 30))


# --- Loop Principal do Jogo ---
running = True

while running:
    # --- 1. Eventos (Input) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Checa teclas pressionadas para movimento
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_rect.x += player_speed

    # Limita o jogador à área do jogo (lado esquerdo)
    if player_rect.left < 0:
        player_rect.left = 0
    if player_rect.right > GAME_WIDTH:
        player_rect.right = GAME_WIDTH

    # --- 2. Lógica do Jogo (Update) ---
    
    # Spawns de novos itens
    item_spawn_timer += 1
    if item_spawn_timer >= ITEM_SPAWN_RATE:
        item_spawn_timer = 0
        
        # LÓGICA DE PROBABILIDADE PONDERADA (PESOS)
        item_type = random.choices(
            COLOR_TYPES,
            weights=[ITEM_PROBABILITIES[t] for t in COLOR_TYPES],
            k=1
        )[0]

        item_color = ITEM_COLORS[item_type] 
        item_size_spawn = 50 
        item_x = random.randint(0, GAME_WIDTH - item_size_spawn)
        new_item_rect = pygame.Rect(item_x, -item_size_spawn, item_size_spawn, item_size_spawn)
        items.append({"rect": new_item_rect, "color": item_color, "type": item_type})

    # Mover e checar colisão dos itens
    for i in range(len(items) - 1, -1, -1):
        item = items[i]
        item["rect"].y += 6 
        
        if item["rect"].top > SCREEN_HEIGHT:
            items.pop(i)
            continue 

        if player_rect.colliderect(item["rect"]):
            
            item_type = item["type"]
            
            # --- 1. ATUALIZA PONTUAÇÃO (PONDERADA) ---
            current_score += ITEM_SCORES[item_type]
            
            # --- 2. REGISTRA PONTO NO SCATTER PLOT ---
            elapsed_time_sec = (pygame.time.get_ticks() - start_time_ms) / 1000.0
            score_vs_time.append((elapsed_time_sec, current_score))

            # --- 3. ATUALIZA GRÁFICO DE CONTAGEM (DISTRIBUIÇÃO DISCRETA) ---
            stats_counts[item_type] += 1
            
            # --- 4. ATUALIZA GRÁFICO DE INTERVALO (DISTRIBUIÇÃO CONTÍNUA) ---
            current_time = pygame.time.get_ticks()
            interval_sec = (current_time - last_collection_time) / 1000.0
            last_collection_time = current_time 
            
            all_collection_intervals.append(interval_sec) # Armazena para cálculo adaptativo

            if interval_sec < 0.7:
                stats_intervals["0-0.7s"] += 1
            elif interval_sec < 1.4:
                stats_intervals["0.7-1.4s"] += 1
            elif interval_sec < 2.0:
                stats_intervals["1.4-2.0s"] += 1
            elif interval_sec < 2.5:
                stats_intervals["2.0s- 2.5s"] += 1
            
            # --- 5. Remove o item ---
            items.pop(i)
            
    # --- 3. Desenho (Render) ---
    
    screen.fill(BLACK)
    
    # --- Lado Esquerdo: Jogo ---
    draw_game(player_rect, items)
    
    # --- Lado Direito: Gráficos (3 PARTES) ---
    
    rect_grafico_1 = pygame.Rect(GAME_WIDTH, 0, GRAPH_WIDTH, GRAPH_HEIGHT_PER_PLOT) # TOPO (360px)
    rect_grafico_2 = pygame.Rect(GAME_WIDTH, GRAPH_Y_SPLIT_1, GRAPH_WIDTH, GRAPH_HEIGHT_PER_PLOT) # MEIO (360px)
    rect_grafico_3 = pygame.Rect(GAME_WIDTH, GRAPH_Y_SPLIT_2, GRAPH_WIDTH, GRAPH_HEIGHT_PER_PLOT) # BASE (360px)

    # Gráfico 1 (TOPO): Contagem (Distribuição Ponderada) - Fitting Teórico (Discreto)
    draw_histogram(
        screen,
        stats_counts, 
        COLOR_TYPES, 
        ITEM_COLORS, 
        "Contagem (Freq. Ponderada)", 
        rect_grafico_1,
        theoretical_prob_func=get_theoretical_prob 
    )
    
    # Gráfico 2 (MEIO): Pontuação x Tempo (Série Temporal / Scatter Plot)
    draw_scatter_plot(
        screen,
        score_vs_time, 
        rect_grafico_2 
    )

    # Gráfico 3 (BASE): Intervalo de Coleta (Histograma Contínuo) - Fitting Teórico (Exponencial Adaptativo)
    draw_histogram(
        screen,
        stats_intervals, 
        INTERVAL_KEYS, 
        INTERVAL_COLORS, 
        "Intervalo de Coleta (Freq. Contínua)", 
        rect_grafico_3,
        theoretical_prob_func=get_theoretical_interval_prob 
    )

    # Linhas divisórias
    pygame.draw.line(screen, WHITE, (GAME_WIDTH, 0), (GAME_WIDTH, SCREEN_HEIGHT), 5) # Vertical
    pygame.draw.line(screen, WHITE, (GAME_WIDTH, GRAPH_Y_SPLIT_1), (SCREEN_WIDTH, GRAPH_Y_SPLIT_1), 5) # Horizontal 1
    pygame.draw.line(screen, WHITE, (GAME_WIDTH, GRAPH_Y_SPLIT_2), (SCREEN_WIDTH, GRAPH_Y_SPLIT_2), 5) # Horizontal 2

    # Atualiza a tela
    pygame.display.flip()
    
    # Controla o FPS
    clock.tick(60)

# --- Fim ---
pygame.quit()
