def ending_screen(efficiency_score, additional_lines):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Transport Game - Ending Screen")
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(WHITE)
        draw_city(screen, additional_lines)

        # Display efficiency score
        score_text = font.render("Efficiency Score: {:.2f}".format(efficiency_score), True, BLACK)
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(score_text, score_rect)

        # Display cleaned up grid with bus animation
        for x in range(50, 550, 50):
            pygame.draw.line(screen, BLACK, (x, 50), (x, 550), 2)
            pygame.draw.line(screen, BLACK, (50, x), (550, x), 2)

        pygame.draw.circle(screen, RED, (300, 300), 10)
        pygame.display.update()
        clock.tick(FPS)