import pygame
import os
import sys

# Ensure parent directory is in sys.path for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from ballistic_range.constants import BLACK, GRAY, DARK_GRAY, WHITE, BLUE

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, label, initial_val=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val if initial_val is not None else min_val
        self.label = label
        self.handle_rect = pygame.Rect(x, y, 10, h)
        self.update_handle()
        self.dragging = False
        self.touched = False

    def update_handle(self):
        pos = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.centerx = self.rect.x + pos * self.rect.width

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self.touched = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                rel_x = max(0, min(event.pos[0] - self.rect.x, self.rect.width))
                self.val = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
                self.update_handle()
                return True
        return False

    def draw(self, screen, font):
        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, BLUE, self.handle_rect)

        txt = font.render(f"{self.label}: {self.val:.1f}", True, BLACK)
        screen.blit(txt, (self.rect.x, self.rect.y - 25))

class Button:
    def __init__(self, x, y, w, h, text, color=GRAY):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.enabled = True

    def handle_event(self, event):
        if self.enabled and event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen, font):
        color = self.color if self.enabled else DARK_GRAY
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        txt = font.render(self.text, True, BLACK)
        txt_rect = txt.get_rect(center=self.rect.center)
        screen.blit(txt, txt_rect)
