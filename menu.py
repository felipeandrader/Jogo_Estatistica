import pygame

# --- Cores (pode adicionar mais) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
GREEN_HOVER = (0, 200, 0)
RED_HOVER = (200, 0, 0)

def draw_text_with_outline(surface, font, text, center, text_color, outline_color=(0,0,0), offset=2):
    """Desenha `text` com contorno: 4 passadas na cor de contorno e, por fim, o texto na cor principal.
    `center` é a coordenada central onde o texto deve ficar alinhado.
    """
    text_surface = font.render(text, True, text_color)
    outline_surface = font.render(text, True, outline_color)

    # Posições (esquerda, direita, cima, baixo) conforme a lógica do .txt
    cx, cy = center
    for dx, dy in [(-offset, 0), (offset, 0), (0, -offset), (0, offset)]:
        rect_o = outline_surface.get_rect(center=(cx + dx, cy + dy))
        surface.blit(outline_surface, rect_o)

    rect_t = text_surface.get_rect(center=center)
    surface.blit(text_surface, rect_t)

def show_menu(screen, screen_width, screen_height, title_font, main_font, background_image=None):
    """
    Mostra a tela de menu e retorna a ação do jogador ("PLAY" ou "QUIT").
    Se `background_image` for fornecida, ela será desenhada como background abaixo
    dos elementos do menu.
    """
    clock = pygame.time.Clock()

    # --- Configuração dos Botões ---
    button_width = 246
    button_height = 217
    
    play_button_rect = pygame.Rect(
        (screen_width // 2) - (button_width // 2), 
        (screen_height // 2) - 50, 
        button_width, 
        button_height
    )
    
    # Carrega sprites do botão JOGAR
    try:
        play_btn_img_default = pygame.image.load("botao_jogar_1.png").convert_alpha()
        play_btn_img_default = pygame.transform.smoothscale(play_btn_img_default, (button_width, button_height))
    except pygame.error:
        play_btn_img_default = None
    try:
        play_btn_img_hover = pygame.image.load("botao_jogar_2.png").convert_alpha()
        play_btn_img_hover = pygame.transform.smoothscale(play_btn_img_hover, (button_width, button_height))
    except pygame.error:
        play_btn_img_hover = None

    menu_running = True
    while menu_running:
        mouse_pos = pygame.mouse.get_pos()
        
        # --- Verificação de Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(mouse_pos):
                    return "PLAY" # Inicia o jogo

        # --- Desenho ---
        # Desenha background se fornecido, caso contrário pinta o fundo com GRAY
        if background_image:
            try:
                screen.blit(background_image, (0, 0))
            except Exception:
                screen.fill(GRAY)
        else:
            screen.fill(GRAY)
        
        # Título com contorno preto para melhor legibilidade
        title_offset_y = -50
        title_center = (screen_width // 2, (screen_height // 3) + title_offset_y)
        draw_text_with_outline(
            screen,
            title_font,
            "MONKEY RUNNERS",
            title_center,
            WHITE,  # cor principal do título
            BLACK,         # contorno preto
            offset=2
        )

        # Cores de Hover / Sprites
        play_hover = play_button_rect.collidepoint(mouse_pos)

        # Botão Jogar com sprites
        if play_hover and play_btn_img_hover:
            screen.blit(play_btn_img_hover, play_button_rect.topleft)
        elif play_btn_img_default:
            screen.blit(play_btn_img_default, play_button_rect.topleft)
        else:
            # Fallback se imagens não carregarem
            play_color = GREEN_HOVER if play_hover else BLACK
            pygame.draw.rect(screen, play_color, play_button_rect)
            play_text = main_font.render("JOGAR", True, WHITE)
            play_text_rect = play_text.get_rect(center=play_button_rect.center)
            screen.blit(play_text, play_text_rect)
        
        pygame.display.flip()
        clock.tick(15) # Menu não precisa de 60fps