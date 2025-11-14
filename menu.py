import pygame

# --- Cores (pode adicionar mais) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
GREEN_HOVER = (0, 200, 0)
RED_HOVER = (200, 0, 0)

def show_menu(screen, screen_width, screen_height, title_font, main_font):
    """
    Mostra a tela de menu e retorna a ação do jogador ("PLAY" ou "QUIT").
    """
    clock = pygame.time.Clock()

    # --- Configuração dos Botões ---
    button_width = 300
    button_height = 80
    
    play_button_rect = pygame.Rect(
        (screen_width // 2) - (button_width // 2), 
        (screen_height // 2) - 50, 
        button_width, 
        button_height
    )
    
    quit_button_rect = pygame.Rect(
        (screen_width // 2) - (button_width // 2), 
        (screen_height // 2) + 60, 
        button_width, 
        button_height
    )

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
                if quit_button_rect.collidepoint(mouse_pos):
                    return "QUIT" # Fecha tudo

        # --- Desenho ---
        screen.fill(GRAY)
        
        # Título
        title_text = title_font.render("MONKEY RUNNERS", True, WHITE)
        title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 3))
        screen.blit(title_text, title_rect)

        # Cores de Hover
        play_color = GREEN_HOVER if play_button_rect.collidepoint(mouse_pos) else BLACK
        quit_color = RED_HOVER if quit_button_rect.collidepoint(mouse_pos) else BLACK
        
        # Botão Jogar
        pygame.draw.rect(screen, play_color, play_button_rect)
        play_text = main_font.render("JOGAR", True, WHITE)
        play_text_rect = play_text.get_rect(center=play_button_rect.center)
        screen.blit(play_text, play_text_rect)
        
        # Botão Sair
        pygame.draw.rect(screen, quit_color, quit_button_rect)
        quit_text = main_font.render("SAIR", True, WHITE)
        quit_text_rect = quit_text.get_rect(center=quit_button_rect.center)
        screen.blit(quit_text, quit_text_rect)

        pygame.display.flip()
        clock.tick(15) # Menu não precisa de 60fps