"""
Main game logic and entity classes for RL Space Adventure.
"""

import random
import pygame
from .config import *
from .rl_agent import RLAgent
from .rendering import Renderer


class GameEntity:
    """Base class for game entities with position."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def position(self):
        """Get position as tuple."""
        return (self.x, self.y)

    @position.setter
    def position(self, pos):
        """Set position from tuple."""
        self.x, self.y = pos


class Player(GameEntity):
    """Player spaceship entity."""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.fuel = 100.0

    def move(self, dx, dy):
        """Move player and consume fuel."""
        self.x = max(0, min(GRID_WIDTH - 1, self.x + dx))
        self.y = max(0, min(GRID_HEIGHT - 1, self.y + dy))
        self.fuel = max(0, self.fuel - 0.1)

    def refuel(self, amount):
        """Add fuel to player."""
        self.fuel = min(100, self.fuel + amount)


class Coin(GameEntity):
    """Coin/star collectible entity."""
    pass


class Enemy(GameEntity):
    """Enemy/asteroid entity."""

    def move_toward(self, target_x, target_y):
        """Move enemy toward target position."""
        dx = 1 if target_x > self.x else -1 if target_x < self.x else 0
        dy = 1 if target_y > self.y else -1 if target_y < self.y else 0

        self.x = max(0, min(GRID_WIDTH - 1, self.x + dx))
        self.y = max(0, min(GRID_HEIGHT - 1, self.y + dy))


class SpaceAdventureGame:
    """Main game class managing game state and logic."""

    def __init__(self):
        pygame.init()

        # Initialize display
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("RL Space Adventure")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)

        # Initialize components
        self.renderer = Renderer(self.screen, self.font)
        self.agent = RLAgent()

        # Game state
        self.player = Player(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.coins = []
        self.enemies = []
        self.score = 0
        self.manual_mode = False
        self.episode_count = 0

        # Initialize entities
        self._spawn_coins()
        self._spawn_enemies()

    def _spawn_coins(self):
        """Spawn initial coins."""
        self.coins = []
        for _ in range(MAX_COINS):
            self.coins.append(Coin(
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            ))

    def _spawn_enemies(self):
        """Spawn initial enemies."""
        self.enemies = []
        for _ in range(MAX_ENEMIES):
            self.enemies.append(Enemy(
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            ))

    def reset_episode(self):
        """Reset game state for new episode."""
        self.player = Player(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self._spawn_coins()
        self._spawn_enemies()
        self.episode_count += 1
        self.agent.decay_epsilon()

    def handle_input(self):
        """Handle user input events."""
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.renderer.button_rect.collidepoint(event.pos):
                    self.manual_mode = not self.manual_mode

    def get_manual_action(self):
        """Get action from manual player input."""
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_UP]:
            dx, dy = -1, 0
        elif keys[pygame.K_DOWN]:
            dx, dy = 1, 0
        elif keys[pygame.K_LEFT]:
            dx, dy = 0, -1
        elif keys[pygame.K_RIGHT]:
            dx, dy = 0, 1

        return ACTIONS.index((dx, dy)) if (dx, dy) in ACTIONS else 0, dx, dy

    def update_enemies(self):
        """Update enemy positions to chase player."""
        for enemy in self.enemies:
            if random.random() < 0.5:  # 50% chance to move each frame
                enemy.move_toward(self.player.x, self.player.y)

    def check_collisions(self):
        """
        Check for collisions and update game state.

        Returns:
            Reward for the current action
        """
        reward = FUEL_CONSUMPTION_REWARD

        # Check coin collection
        collected_coins = [coin for coin in self.coins if coin.position == self.player.position]
        if collected_coins:
            reward = COIN_COLLECTION_REWARD
            self.score += len(collected_coins)
            self.player.refuel(FUEL_RESTORE_PER_COIN * len(collected_coins))

            # Remove collected coins and spawn new ones
            self.coins = [coin for coin in self.coins if coin not in collected_coins]
            while len(self.coins) < MAX_COINS:
                new_coin = Coin(
                    random.randint(0, GRID_WIDTH - 1),
                    random.randint(0, GRID_HEIGHT - 1)
                )
                # Ensure no overlap with player or existing coins
                if (new_coin.position not in [coin.position for coin in self.coins] and
                    new_coin.position != self.player.position):
                    self.coins.append(new_coin)

        # Check enemy collision or fuel depletion
        enemy_collision = any(enemy.position == self.player.position for enemy in self.enemies)
        if enemy_collision or self.player.fuel <= 0:
            reward = ENEMY_COLLISION_REWARD if enemy_collision else FUEL_DEPLETION_REWARD
            self.reset_episode()

        return reward

    def update(self):
        """Update game state for one frame."""
        self.handle_input()

        # Get current state
        current_state = self.agent.get_state(
            self.player.position, self.player.fuel,
            [coin.position for coin in self.coins],
            [enemy.position for enemy in self.enemies]
        )

        # Choose and execute action
        if self.manual_mode:
            action_idx, dx, dy = self.get_manual_action()
        else:
            action_idx = self.agent.choose_action(current_state)
            dx, dy = ACTIONS[action_idx]

        # Move player if action is not stay
        if (dx, dy) != (0, 0):
            self.player.move(dx, dy)

        # Update enemies
        self.update_enemies()

        # Check collisions and get reward
        reward = self.check_collisions()

        # Update Q-learning if not manual mode or player made a move
        if not self.manual_mode or (dx, dy) != (0, 0):
            next_state = self.agent.get_state(
                self.player.position, self.player.fuel,
                [coin.position for coin in self.coins],
                [enemy.position for enemy in self.enemies]
            )
            self.agent.update_q_value(current_state, action_idx, reward, next_state)

    def render(self):
        """Render the current game state."""
        self.renderer.render_frame(
            self.player.position,
            [coin.position for coin in self.coins],
            [enemy.position for enemy in self.enemies],
            self.score, self.manual_mode, self.player.fuel, self.episode_count
        )

    def run(self):
        """Main synchronous game loop."""
        while True:
            self.update()
            self.render()
            self.clock.tick(FPS)

    async def run_async(self):
        """Main asynchronous game loop."""
        while True:
            self.update()
            self.render()
            self.clock.tick(FPS)
            await asyncio.sleep(1.0 / FPS)
