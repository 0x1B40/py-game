import pygame
import numpy as np
import asyncio
import platform
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 30
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10
MAX_COINS = 3
MAX_ENEMIES = 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 100)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
GRAY = (100, 100, 100)
LIGHT_GRAY = (150, 150, 150)

# Q-Learning parameters
ALPHA = 0.1
GAMMA = 0.95
EPSILON_START = 0.2
EPSILON_END = 0.01
EPSILON_DECAY = 0.995
ACTIONS = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
STATE_BINS = 4
FUEL_BINS = 4

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RL Space Adventure")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

# Q-table
q_table = np.zeros((STATE_BINS, STATE_BINS, FUEL_BINS, STATE_BINS, STATE_BINS, STATE_BINS, STATE_BINS, len(ACTIONS)))

def discretize(value, max_value, bins):
    return min(bins - 1, int(value / max_value * bins))

def get_state(player_pos, fuel, coins, enemies):
    px, py = player_pos
    coin = min(coins, key=lambda c: abs(c[0] - px) + abs(c[1] - py)) if coins else [px, py]
    enemy = min(enemies, key=lambda e: abs(e[0] - px) + abs(e[1] - py)) if enemies else [px, py]
    cx, cy = coin
    ex, ey = enemy
    px = discretize(px, GRID_WIDTH, STATE_BINS)
    py = discretize(py, GRID_HEIGHT, STATE_BINS)
    fuel_bin = discretize(fuel, 100, FUEL_BINS)
    cdx = discretize(cx - px, GRID_WIDTH, STATE_BINS)
    cdy = discretize(cy - py, GRID_HEIGHT, STATE_BINS)
    edx = discretize(ex - px, GRID_WIDTH, STATE_BINS)
    edy = discretize(ey - py, GRID_HEIGHT, STATE_BINS)
    return (px, py, fuel_bin, cdx, cdy, edx, edy)

def choose_action(state, epsilon):
    if random.random() < epsilon:
        return random.randint(0, len(ACTIONS) - 1)
    return np.argmax(q_table[state])

def update_q_table(state, action, reward, next_state):
    current_q = q_table[state][action]
    next_max_q = np.max(q_table[next_state])
    q_table[state][action] = current_q + ALPHA * (reward + GAMMA * next_max_q - current_q)

def draw_sprite(surface, color, pos, shape, size):
    x, y = pos[0] * GRID_SIZE + GRID_SIZE // 2, pos[1] * GRID_SIZE + GRID_SIZE // 2
    if shape == "spaceship":
        pygame.draw.polygon(surface, color, [
            (x, y - size), (x - size, y + size), (x + size, y + size)
        ])
        pygame.draw.circle(surface, WHITE, (x, y - size // 2), size // 4)
    elif shape == "star":
        points = []
        for i in range(8):
            angle = i * math.pi / 4
            r = size if i % 2 == 0 else size // 2
            points.append((x + r * math.cos(angle), y + r * math.sin(angle)))
        pygame.draw.polygon(surface, color, points)
    elif shape == "asteroid":
        pygame.draw.circle(surface, color, (x, y), size)
        pygame.draw.circle(surface, BLACK, (x - size // 4, y - size // 4), size // 4)

def draw_background(surface):
    for y in range(HEIGHT):
        color = (0, 0, max(50, 255 - y // 2))
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))

async def main():
    # Game state
    player_pos = [GRID_WIDTH // 2, GRID_HEIGHT // 2]
    fuel = 100.0
    coins = [[random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)] for _ in range(MAX_COINS)]
    enemies = [[random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)] for _ in range(MAX_ENEMIES)]
    score = 0
    manual_mode = False
    epsilon = EPSILON_START
    episode_count = 0

    # Button properties
    button_rect = pygame.Rect(10, 160, 150, 40)
    button_text = font.render("Toggle Mode", True, WHITE)

    def reset_positions():
        nonlocal player_pos, fuel, coins, enemies, episode_count
        player_pos = [GRID_WIDTH // 2, GRID_HEIGHT // 2]
        fuel = 100.0
        coins = [[random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)] for _ in range(MAX_COINS)]
        enemies = [[random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)] for _ in range(MAX_ENEMIES)]
        episode_count += 1

    def update_loop():
        nonlocal player_pos, fuel, coins, enemies, score, manual_mode, epsilon, episode_count
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    manual_mode = not manual_mode

        # Get state
        state = get_state(player_pos, fuel, coins, enemies)

        # Choose action
        dx, dy = 0, 0
        if manual_mode:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                dx, dy = -1, 0
            elif keys[pygame.K_DOWN]:
                dx, dy = 1, 0
            elif keys[pygame.K_LEFT]:
                dx, dy = 0, -1
            elif keys[pygame.K_RIGHT]:
                dx, dy = 0, 1
            action_idx = ACTIONS.index((dx, dy)) if (dx, dy) in ACTIONS else 0
        else:
            action_idx = choose_action(state, epsilon)
            dx, dy = ACTIONS[action_idx]

        # Update player position
        new_x = max(0, min(GRID_WIDTH - 1, player_pos[0] + dx))
        new_y = max(0, min(GRID_HEIGHT - 1, player_pos[1] + dy))
        player_pos = [new_x, new_y]

        # Update fuel
        fuel = max(0, fuel - 0.1)
        reward = -0.1

        # Check collisions
        collected = [c for c in coins if c == player_pos]
        if collected:
            reward = 20
            score += len(collected)
            fuel = min(100, fuel + 5 * len(collected))
            coins = [c for c in coins if c != player_pos]
            while len(coins) < MAX_COINS:
                new_coin = [random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)]
                if new_coin not in coins and new_coin != player_pos:
                    coins.append(new_coin)

        hit = [e for e in enemies if e == player_pos]
        if hit or fuel <= 0:
            reward = -50 if hit else -100
            reset_positions()
            epsilon = max(EPSILON_END, epsilon * EPSILON_DECAY)

        # Update enemies
        for i, enemy in enumerate(enemies):
            if random.random() < 0.5:
                ex, ey = enemy
                dx = 1 if player_pos[0] > ex else -1 if player_pos[0] < ex else 0
                dy = 1 if player_pos[1] > ey else -1 if player_pos[1] < ey else 0
                new_ex = max(0, min(GRID_WIDTH - 1, ex + dx))
                new_ey = max(0, min(GRID_HEIGHT - 1, ey + dy))
                enemies[i] = [new_ex, new_ey]

        # Update Q-table
        if not manual_mode or (dx, dy) != (0, 0):
            next_state = get_state(player_pos, fuel, coins, enemies)
            update_q_table(state, action_idx, reward, next_state)

        # Draw
        draw_background(screen)
        draw_sprite(screen, BLUE, player_pos, "spaceship", GRID_SIZE // 2)
        for coin in coins:
            draw_sprite(screen, YELLOW, coin, "star", GRID_SIZE // 3)
        for enemy in enemies:
            draw_sprite(screen, RED, enemy, "asteroid", GRID_SIZE // 2)
        
        # Draw HUD
        score_text = font.render(f"Score: {score}", True, WHITE)
        mode_text = font.render(f"Mode: {'Manual' if manual_mode else 'RL'}", True, WHITE)
        fuel_text = font.render(f"Fuel: {int(fuel)}%", True, WHITE)
        episode_text = font.render(f"Episode: {episode_count}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(mode_text, (10, 40))
        screen.blit(fuel_text, (10, 70))
        screen.blit(episode_text, (10, 100))
        
        # Fuel bar
        pygame.draw.rect(screen, GREEN, (10, 130, int(fuel * 1.8), 20))
        pygame.draw.rect(screen, WHITE, (10, 130, 180, 20), 2)
        
        # Draw button
        mouse_pos = pygame.mouse.get_pos()
        button_color = LIGHT_GRAY if button_rect.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, button_color, button_rect)
        pygame.draw.rect(screen, WHITE, button_rect, 2)
        text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, text_rect)
        
        pygame.display.flip()

    def setup():
        pass

    setup()
    while True:
        update_loop()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())