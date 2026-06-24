import pygame
import sys
import os

# Add parent directory to sys.path to allow running this script directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ballistic_range.constants import *
from ballistic_range.levels import LEVELS
from ballistic_range.game import Level

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ballistic Range - Physics Prediction Game")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 24)
    small_font = pygame.font.SysFont("Arial", 18)

    current_level_idx = 0
    total_score = 0

    def load_level(idx):
        if idx < len(LEVELS):
            return Level(LEVELS[idx], font, small_font)
        return None

    current_level = load_level(current_level_idx)
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            result = current_level.handle_event(event)
            if result == "NEXT":
                total_score += current_level.score
                current_level_idx += 1
                current_level = load_level(current_level_idx)
                if current_level is None:
                    # End of game
                    print(f"Game Over! Total Score: {total_score:.1f}")
                    running = False

        if current_level:
            current_level.update(dt)

        screen.fill(WHITE)
        if current_level:
            current_level.draw(screen)

            # Global UI
            score_txt = font.render(f"Total Score: {total_score:.1f}", True, BLACK)
            screen.blit(score_txt, (10, 10))
            lvl_txt = font.render(f"Level: {current_level_idx + 1}/{len(LEVELS)}", True, BLACK)
            screen.blit(lvl_txt, (10, 40))
        else:
            # Should not happen if load_level is correct
            msg = font.render("Thanks for playing!", True, BLACK)
            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
