"""
Unit tests for the RL Agent module.
"""

import pytest
import numpy as np
from src.rl_space_adventure.rl_agent import RLAgent
from src.rl_space_adventure.config import *


class TestRLAgent:
    """Test cases for the RLAgent class."""

    def test_initialization(self):
        """Test agent initializes with correct Q-table shape."""
        agent = RLAgent()
        expected_shape = (STATE_BINS, STATE_BINS, FUEL_BINS,
                         STATE_BINS, STATE_BINS, STATE_BINS, STATE_BINS,
                         len(ACTIONS))
        assert agent.q_table.shape == expected_shape
        assert agent.epsilon == EPSILON_START

    def test_discretize(self):
        """Test value discretization."""
        agent = RLAgent()

        # Test boundary values
        assert agent.discretize(0, 100, 4) == 0
        assert agent.discretize(99, 100, 4) == 3
        assert agent.discretize(100, 100, 4) == 3  # Should cap at max

    def test_get_state(self):
        """Test state representation generation."""
        agent = RLAgent()

        player_pos = (5, 5)
        fuel = 75.0
        coins = [(3, 3), (7, 7)]
        enemies = [(2, 2)]

        state = agent.get_state(player_pos, fuel, coins, enemies)

        # Should return 7-tuple
        assert len(state) == 7
        assert all(isinstance(x, int) for x in state)

    def test_choose_action_exploration(self):
        """Test action selection includes exploration."""
        agent = RLAgent()
        state = (0, 0, 0, 0, 0, 0, 0)

        # With high exploration, should occasionally choose different actions
        actions = set()
        for _ in range(100):
            actions.add(agent.choose_action(state))

        assert len(actions) > 1  # Should explore different actions

    def test_q_value_update(self):
        """Test Q-value updates correctly."""
        agent = RLAgent()
        state = (0, 0, 0, 0, 0, 0, 0)
        next_state = (0, 1, 0, 0, 0, 0, 0)
        action = 0
        reward = 10.0

        old_q = agent.q_table[state][action]
        agent.update_q_value(state, action, reward, next_state)
        new_q = agent.q_table[state][action]

        assert new_q != old_q  # Q-value should change

    def test_epsilon_decay(self):
        """Test exploration rate decay."""
        agent = RLAgent()
        initial_epsilon = agent.epsilon

        agent.decay_epsilon()
        decayed_epsilon = agent.epsilon

        assert decayed_epsilon < initial_epsilon
        assert decayed_epsilon >= EPSILON_END
