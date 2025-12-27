#!/usr/bin/env python3
"""
Demo script showing the in-memory game API.

Plays a random game using MemoryStore - much faster than file I/O.
"""
import time
import sys
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.lorcana.game_api import GameSession

def main():
    if len(sys.argv) < 2:
        print("Usage: demo-game-api.py <initial_state_path>")
        print("Example: demo-game-api.py output/b013/b123456.0123456.ab")
        sys.exit(1)

    initial_path = sys.argv[1]

    print(f"Loading initial state from {initial_path}...")
    t0 = time.time()
    session = GameSession.from_file(initial_path)
    t1 = time.time()
    print(f"Loaded in {(t1-t0)*1000:.1f}ms\n")

    print("Playing random game until completion...")
    t2 = time.time()
    final_path = session.play_until_game_over()
    t3 = time.time()
    print(f"Game completed in {(t3-t2)*1000:.1f}ms")
    print(f"Total time: {(t3-t0)*1000:.1f}ms\n")

    print(f"Final path: {final_path}")
    print(f"Winner: {session.get_winner()}")
    print(f"Game over: {session.is_game_over()}")

    # Show actions taken
    action_count = final_path.count('/') if final_path else 0
    print(f"Actions taken: {action_count}")
    if action_count > 0:
        avg_time = (t3-t2) / action_count * 1000
        print(f"Average time per action: {avg_time:.1f}ms")

if __name__ == "__main__":
    main()
