import pygame

# --- Cores ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
GREEN_HOVER = (0, 200, 0)
BLUE_HOVER = (0, 0, 200) 
RED_HOVER = (200, 0, 0)
HIGHLIGHT_BORDER = (255, 255, 0) # Cor da borda quando selecionado

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
    Mostra a tela de menu navegável por Mouse, Teclado e Controle.
    Retorna: "PLAY", "PLAY_2P" ou "QUIT".
    """
    clock = pygame.time.Clock()

    # --- Inicialização de Joysticks no Menu ---
    # Garante que os controles sejam reconhecidos mesmo se plugados agora
    if not pygame.joystick.get_init():
        pygame.joystick.init()
    
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    for joy in joysticks:
        if not joy.get_init():
            joy.init()

    screen_height = 768

    # --- Configuração dos Botões ---
    button_width = 246
    button_height = 217
    spacing = 100
    center_y = screen_height // 2

    # Ajuste do tamanho do botão de 2 Jogadores
    button_2p_width = 300
    button_2p_height = 120

    # Criamos uma lista de dicionários (removendo o botão SAIR)
    menu_options = [
        {
            "rect": pygame.Rect((screen_width // 2) - (button_width // 2), center_y - button_height + spacing, button_width, button_height),
            "label": "1 JOGADOR",
            "action": "PLAY",
            "color_selected": GREEN_HOVER
        },
        {
            "rect": pygame.Rect((screen_width // 2) - (button_2p_width // 2), center_y + spacing, button_2p_width, button_2p_height),
            "label": "2 JOGADORES",
            "action": "PLAY_2P",
            "color_selected": BLUE_HOVER
        }
    ]

    selected_index = 0 # Qual opção está selecionada atualmente
    
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

    # Carrega sprite do botão 2 Jogadores
    try:
        two_players_img = pygame.image.load("dois_jogadores_botao1.png").convert_alpha()
        two_players_img = pygame.transform.smoothscale(two_players_img, (button_2p_width, button_2p_height))
    except pygame.error:
        two_players_img = None

    last_input_time = 0
    INPUT_COOLDOWN = 200 

    menu_running = True
    while menu_running:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        
        # --- Verificação de Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
                
            # --- MOUSE ---
            # Se mover o mouse, seleciona o botão sob ele
            if event.type == pygame.MOUSEMOTION:
                for i, option in enumerate(menu_options):
                    if option["rect"].collidepoint(mouse_pos):
                        selected_index = i

            # Clique do Mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Botão esquerdo
                    if menu_options[selected_index]["rect"].collidepoint(mouse_pos):
                        return menu_options[selected_index]["action"]

            # --- TECLADO ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    selected_index = (selected_index - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    selected_index = (selected_index + 1) % len(menu_options)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER]:
                    return menu_options[selected_index]["action"]

            # --- JOYSTICK (BOTÕES e D-PAD) ---
            if event.type == pygame.JOYBUTTONDOWN:
                # Botão 0 (A/X), Botão 7 (Start) geralmente confirmam
                if event.button in [0, 1, 2, 7]: 
                    return menu_options[selected_index]["action"]
            
            if event.type == pygame.JOYHATMOTION:
                hat_x, hat_y = event.value
                if hat_y == 1: # Cima
                    selected_index = (selected_index - 1) % len(menu_options)
                elif hat_y == -1: # Baixo
                    selected_index = (selected_index + 1) % len(menu_options)

        # --- JOYSTICK (ANALÓGICO) ---
        # Verificação fora do loop de eventos para controle contínuo com delay
        if current_time - last_input_time > INPUT_COOLDOWN:
            moved = False
            for joy in joysticks:
                try:
                    axis_y = joy.get_axis(1) # Eixo vertical
                    if axis_y < -0.5: # Cima
                        selected_index = (selected_index - 1) % len(menu_options)
                        moved = True
                    elif axis_y > 0.5: # Baixo
                        selected_index = (selected_index + 1) % len(menu_options)
                        moved = True
                except:
                    pass
            
            if moved:
                last_input_time = current_time

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

        # Desenhar Botão 2 Jogadores com sprite e efeito de hover (opacidade reduzida)
        two_rect = menu_options[1]["rect"]
        two_hover = two_rect.collidepoint(mouse_pos)
        if two_players_img:
            if two_hover:
                try:
                    temp_img = two_players_img.copy()
                    temp_img.set_alpha(160)  # opacidade reduzida no hover
                    screen.blit(temp_img, two_rect.topleft)
                except Exception:
                    screen.blit(two_players_img, two_rect.topleft)
            else:
                screen.blit(two_players_img, two_rect.topleft)
        else:
            # Fallback se imagem não carregou
            color = BLUE_HOVER if (selected_index == 1) else BLACK
            if selected_index == 1:
                pygame.draw.rect(screen, WHITE, two_rect.inflate(6, 6), border_radius=10)
            pygame.draw.rect(screen, color, two_rect, border_radius=10)
            text_surf = main_font.render("2 JOGADORES", True, WHITE)
            text_rect = text_surf.get_rect(center=two_rect.center)
            screen.blit(text_surf, text_rect)

        # Botão Jogar com sprites (default e hover)
        play_rect = menu_options[0]["rect"]
        play_hover = play_rect.collidepoint(mouse_pos)
        if play_hover and play_btn_img_hover:
            screen.blit(play_btn_img_hover, play_rect.topleft)
        elif play_btn_img_default:
            screen.blit(play_btn_img_default, play_rect.topleft)
        else:
            # Fallback se imagens não carregarem
            play_text = main_font.render("1 JOGADOR", True, WHITE)
            play_text_rect = play_text.get_rect(center=play_rect.center)
            screen.blit(play_text, play_text_rect)
        
        pygame.display.flip()
        clock.tick(30)