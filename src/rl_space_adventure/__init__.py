"""
RL Space Adventure - A Pygame-based reinforcement learning game.

This package contains a space-themed game where players control a spaceship
to collect stars while avoiding asteroids. The game features both manual
control and an AI agent that learns using Q-learning.
"""

from .game import SpaceAdventureGame
from .config import *
from .rl_agent import RLAgent
from .rendering import Renderer

__version__ = "1.0.0"
__author__ = "RL Space Adventure Team"
__description__ = "Reinforcement learning space adventure game built with Pygame"
