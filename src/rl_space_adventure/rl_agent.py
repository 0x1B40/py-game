"""
Reinforcement Learning agent implementation using Q-learning.
"""

import numpy as np
import random
from .config import *


class RLAgent:
    """Q-Learning agent for the space adventure game."""

    def __init__(self):
        # Initialize Q-table with state space dimensions
        # State: (player_x, player_y, fuel_bin, coin_dx, coin_dy, enemy_dx, enemy_dy)
        self.q_table = np.zeros((STATE_BINS, STATE_BINS, FUEL_BINS,
                                STATE_BINS, STATE_BINS, STATE_BINS, STATE_BINS,
                                len(ACTIONS)))
        self.epsilon = EPSILON_START

    def discretize(self, value, max_value, bins):
        """Discretize a continuous value into bins."""
        return min(bins - 1, int(value / max_value * bins))

    def get_state(self, player_pos, fuel, coins, enemies):
        """
        Convert game state to discrete representation.

        Args:
            player_pos: (x, y) tuple for player position
            fuel: Current fuel level (0-100)
            coins: List of coin positions
            enemies: List of enemy positions

        Returns:
            Tuple representing the discrete state
        """
        px, py = player_pos

        # Find nearest coin and enemy
        coin = min(coins, key=lambda c: abs(c[0] - px) + abs(c[1] - py)) if coins else [px, py]
        enemy = min(enemies, key=lambda e: abs(e[0] - px) + abs(e[1] - py)) if enemies else [px, py]

        cx, cy = coin
        ex, ey = enemy

        # Discretize all components
        px = self.discretize(px, GRID_WIDTH, STATE_BINS)
        py = self.discretize(py, GRID_HEIGHT, STATE_BINS)
        fuel_bin = self.discretize(fuel, 100, FUEL_BINS)
        cdx = self.discretize(cx - px, GRID_WIDTH, STATE_BINS)
        cdy = self.discretize(cy - py, GRID_HEIGHT, STATE_BINS)
        edx = self.discretize(ex - px, GRID_WIDTH, STATE_BINS)
        edy = self.discretize(ey - py, GRID_HEIGHT, STATE_BINS)

        return (px, py, fuel_bin, cdx, cdy, edx, edy)

    def choose_action(self, state):
        """
        Choose an action using epsilon-greedy policy.

        Args:
            state: Current discrete state

        Returns:
            Index of chosen action
        """
        if random.random() < self.epsilon:
            return random.randint(0, len(ACTIONS) - 1)
        return np.argmax(self.q_table[state])

    def update_q_value(self, state, action, reward, next_state):
        """
        Update Q-value using Q-learning update rule.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
        """
        current_q = self.q_table[state][action]
        next_max_q = np.max(self.q_table[next_state])
        self.q_table[state][action] = current_q + ALPHA * (reward + GAMMA * next_max_q - current_q)

    def decay_epsilon(self):
        """Decay exploration rate."""
        self.epsilon = max(EPSILON_END, self.epsilon * EPSILON_DECAY)
