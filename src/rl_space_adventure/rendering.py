"""
Rendering and display functions for RL Space Adventure.
"""

import pygame
import math
from .config import *


class Renderer:
    """Handles all rendering operations for the game."""

    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.button_rect = pygame.Rect(10, 160, 150, 40)
        self.button_text = font.render("Toggle Mode", True, WHITE)

    def draw_sprite(self, color, pos, shape, size):
        """Draw a game sprite at the specified position."""
        x, y = pos[0] * GRID_SIZE + GRID_SIZE // 2, pos[1] * GRID_SIZE + GRID_SIZE // 2

        if shape == "spaceship":
            # Draw spaceship as triangle with circle
            pygame.draw.polygon(self.screen, color, [
                (x, y - size), (x - size, y + size), (x + size, y + size)
            ])
            pygame.draw.circle(self.screen, WHITE, (x, y - size // 2), size // 4)
        elif shape == "star":
            # Draw star as 8-pointed polygon
            points = []
            for i in range(8):
                angle = i * math.pi / 4
                r = size if i % 2 == 0 else size // 2
                points.append((x + r * math.cos(angle), y + r * math.sin(angle)))
            pygame.draw.polygon(self.screen, color, points)
        elif shape == "asteroid":
            # Draw asteroid as circle with crater
            pygame.draw.circle(self.screen, color, (x, y), size)
            pygame.draw.circle(self.screen, BLACK, (x - size // 4, y - size // 4), size // 4)

    def draw_background(self):
        """Draw the space background with gradient."""
        for y in range(HEIGHT):
            color = (0, 0, max(50, 255 - y // 2))
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))

    def draw_hud(self, score, manual_mode, fuel, episode_count):
        """Draw the heads-up display with game information."""
        score_text = self.font.render(f"Score: {score}", True, WHITE)
        mode_text = self.font.render(f"Mode: {'Manual' if manual_mode else 'RL'}", True, WHITE)
        fuel_text = self.font.render(f"Fuel: {int(fuel)}%", True, WHITE)
        episode_text = self.font.render(f"Episode: {episode_count}", True, WHITE)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(mode_text, (10, 40))
        self.screen.blit(fuel_text, (10, 70))
        self.screen.blit(episode_text, (10, 100))

        # Fuel bar
        pygame.draw.rect(self.screen, GREEN, (10, 130, int(fuel * 1.8), 20))
        pygame.draw.rect(self.screen, WHITE, (10, 130, 180, 20), 2)

    def draw_button(self):
        """Draw the mode toggle button."""
        mouse_pos = pygame.mouse.get_pos()
        button_color = LIGHT_GRAY if self.button_rect.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(self.screen, button_color, self.button_rect)
        pygame.draw.rect(self.screen, WHITE, self.button_rect, 2)
        text_rect = self.button_text.get_rect(center=self.button_rect.center)
        self.screen.blit(self.button_text, text_rect)

    def draw_game_objects(self, player_pos, coins, enemies):
        """Draw all game objects."""
        # Draw player
        self.draw_sprite(BLUE, player_pos, "spaceship", GRID_SIZE // 2)

        # Draw coins
        for coin in coins:
            self.draw_sprite(YELLOW, coin, "star", GRID_SIZE // 3)

        # Draw enemies
        for enemy in enemies:
            self.draw_sprite(RED, enemy, "asteroid", GRID_SIZE // 2)

    def render_frame(self, player_pos, coins, enemies, score, manual_mode, fuel, episode_count):
        """Render a complete game frame."""
        self.draw_background()
        self.draw_game_objects(player_pos, coins, enemies)
        self.draw_hud(score, manual_mode, fuel, episode_count)
        self.draw_button()
        pygame.display.flip()
