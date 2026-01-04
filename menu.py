import pygame

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
GREEN_HOVER = (0, 200, 0)
BLUE_HOVER = (0, 0, 200) 
RED_HOVER = (200, 0, 0)

def draw_text_with_outline(surface, font, text, center, text_color, outline_color=(0,0,0), offset=2):
    text_surface = font.render(text, True, text_color)
    outline_surface = font.render(text, True, outline_color)
    cx, cy = center
    for dx, dy in [(-offset, 0), (offset, 0), (0, -offset), (0, offset)]:
        rect_o = outline_surface.get_rect(center=(cx + dx, cy + dy))
        surface.blit(outline_surface, rect_o)
    rect_t = text_surface.get_rect(center=center)
    surface.blit(text_surface, rect_t)

def show_menu(screen, screen_width, screen_height, title_font, main_font, background_image=None):
    clock = pygame.time.Clock()
    
    # Inicializa Joysticks se necessário
    if not pygame.joystick.get_init():
        pygame.joystick.init()
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    for joy in joysticks:
        if not joy.get_init():
            joy.init()

    button_width, button_height = 246, 217
    button_2p_width, button_2p_height = 300, 120
    spacing = 100
    center_y = screen_height // 2

    # Opções do menu
    menu_options = [
        {
            "rect": pygame.Rect((screen_width // 2) - (button_width // 2), center_y - button_height + spacing, button_width, button_height),
            "action": "PLAY",
            "color_selected": GREEN_HOVER
        },
        {
            "rect": pygame.Rect((screen_width // 2) - (button_2p_width // 2), center_y + spacing, button_2p_width, button_2p_height),
            "action": "PLAY_2P",
            "color_selected": BLUE_HOVER
        }
    ]

    selected_index = 0

    # Carregamento de Imagens (Sem try/except para mostrar erro se faltar arquivo)
    # Certifique-se que estes arquivos existem na pasta source/
    try:
        ace_bloon_img = pygame.image.load("source/ace_bloon.png").convert_alpha()
        ace_bloon_img = pygame.transform.smoothscale(ace_bloon_img, (340, 325))
    except FileNotFoundError:
        print("AVISO: 'source/ace_bloon.png' não encontrado.")
        ace_bloon_img = None

    try:
        red_ace_bloon_img = pygame.image.load("source/red_ace_monkey.png").convert_alpha()
        red_ace_bloon_img = pygame.transform.smoothscale(red_ace_bloon_img, (340, 325))
    except FileNotFoundError:
        print("AVISO: 'source/red_ace_monkey.png' não encontrado.")
        red_ace_bloon_img = None

    # Imagens dos Botões
    try:
        p_def = pygame.image.load("source/botao_jogar_1.png").convert_alpha()
        p_def = pygame.transform.smoothscale(p_def, (button_width, button_height))
        
        p_hov = pygame.image.load("source/botao_jogar_2.png").convert_alpha()
        p_hov = pygame.transform.smoothscale(p_hov, (button_width, button_height))
        
        two_p_img = pygame.image.load("source/dois_jogadores_botao1.png").convert_alpha()
        two_p_img = pygame.transform.smoothscale(two_p_img, (button_2p_width, button_2p_height))
    except FileNotFoundError as e:
        print(f"ERRO CRÍTICO: Imagem de botão faltando: {e}")
        p_def = None
        p_hov = None
        two_p_img = None

    last_input_time = 0
    
    while True:
        now = pygame.time.get_ticks()
        m_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            
            # Mouse motion
            if event.type == pygame.MOUSEMOTION:
                for i, opt in enumerate(menu_options):
                    if opt["rect"].collidepoint(m_pos): selected_index = i
            
            # Click
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if menu_options[selected_index]["rect"].collidepoint(m_pos):
                    return menu_options[selected_index]["action"]
            
            # Teclado
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w]: selected_index = (selected_index - 1) % len(menu_options)
                elif event.key in [pygame.K_DOWN, pygame.K_s]: selected_index = (selected_index + 1) % len(menu_options)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER]: return menu_options[selected_index]["action"]
            
            # Joystick Botões
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button in [0, 1, 2, 7]: return menu_options[selected_index]["action"]
            
            # Joystick D-PAD
            if event.type == pygame.JOYHATMOTION:
                if event.value[1] == 1: selected_index = (selected_index - 1) % len(menu_options)
                elif event.value[1] == -1: selected_index = (selected_index + 1) % len(menu_options)

        # Joystick Analógico (com delay para não pular muito rápido)
        if now - last_input_time > 200:
            for joy in joysticks:
                try:
                    ay = joy.get_axis(1)
                    if abs(ay) > 0.5:
                        selected_index = (selected_index + (1 if ay > 0 else -1)) % len(menu_options)
                        last_input_time = now
                except: pass

        # Desenho
        if background_image: screen.blit(background_image, (0,0))
        else: screen.fill(GRAY)

        draw_text_with_outline(screen, title_font, "MONKEY RUNNERS", (screen_width // 2, (screen_height // 3) - 50), WHITE, BLACK)

        # Desenha imagens decorativas se existirem
        if ace_bloon_img: screen.blit(ace_bloon_img, (100, screen_height - ace_bloon_img.get_height() - 150))
        if red_ace_bloon_img: screen.blit(red_ace_bloon_img, (screen_width - red_ace_bloon_img.get_width() - 50, screen_height - red_ace_bloon_img.get_height() - 150))

        # Botão 1 Jogador
        is_play = (selected_index == 0)
        p_rect = menu_options[0]["rect"]
        
        if p_def and p_hov:
            if is_play: screen.blit(p_hov, p_rect.topleft)
            else: screen.blit(p_def, p_rect.topleft)
        else:
            # Fallback se não tiver imagem
            c = menu_options[0]["color_selected"] if is_play else BLACK
            pygame.draw.rect(screen, c, p_rect, border_radius=10)
            screen.blit(main_font.render("1 JOGADOR", True, WHITE), p_rect.center)

        # Botão 2 Jogadores
        is_two = (selected_index == 1)
        two_rect = menu_options[1]["rect"]
        
        if two_p_img:
            if is_two:
                t_copy = two_p_img.copy()
                t_copy.set_alpha(160) # Efeito visual de seleção
                screen.blit(t_copy, two_rect.topleft)
            else:
                screen.blit(two_p_img, two_rect.topleft)
        else:
            # Fallback
            c = menu_options[1]["color_selected"] if is_two else BLACK
            pygame.draw.rect(screen, c, two_rect, border_radius=10)
            screen.blit(main_font.render("2 JOGADORES", True, WHITE), two_rect.center)

        pygame.display.flip()
        clock.tick(30)