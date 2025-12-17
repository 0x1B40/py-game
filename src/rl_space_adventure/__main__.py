"""
Main entry point for RL Space Adventure game.
"""

import asyncio
import platform
from .game import SpaceAdventureGame


async def main():
    """Run the game asynchronously."""
    game = SpaceAdventureGame()
    await game.run_async()


def main_sync():
    """Run the game synchronously."""
    game = SpaceAdventureGame()
    game.run()


if __name__ == "__main__":
    if platform.system() == "Emscripten":
        # For web deployment
        asyncio.ensure_future(main())
    else:
        # For desktop
        main_sync()
