import pygame
import sys
import os

# Add the directory containing 'ballistic_range' to sys.path
# to allow running this script directly as 'python ballistic_range/main.py'
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from ballistic_range.constants import *
from ballistic_range.levels import LEVELS
from ballistic_range.game import Level

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Trebuchet Tactics: Castle Siege")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 24)
    small_font = pygame.font.SysFont("Arial", 18)

    current_level_idx = 0
    total_score = 0

    def load_level(idx, prev_color=TREBUCHET_WOOD):
        if idx < len(LEVELS):
            lvl = Level(LEVELS[idx], font, small_font, level_idx=idx)
            lvl.trebuchet_color = prev_color
            return lvl
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
                prev_color = current_level.trebuchet_color
                current_level_idx += 1
                current_level = load_level(current_level_idx, prev_color)
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
