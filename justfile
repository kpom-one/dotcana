# Dotcana - Lorcana game state engine

set shell := ["bash", "-uc"]

# Use venv python
python := ".venv/bin/python"

# Show available commands
default:
    @just --list

# Set up development environment
setup:
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install networkx pydot
    @echo "Environment ready. Dependencies installed."

# Clear all output
clear:
    rm -rf output/*
    @echo "Cleared output/"

# Create a matchup from two deck files
# Usage: just match data/decks/bs01.txt data/decks/rp01.txt
match deck1 deck2:
    #!/usr/bin/env bash
    set -euo pipefail

    # rules-engine generates hash from deck contents and returns it
    hash=$({{python}} bin/rules-engine.py init "{{deck1}}" "{{deck2}}")

    echo "Created matchup: ${hash}"
    echo "  output/${hash}/deck1.txt"
    echo "  output/${hash}/deck2.txt"
    echo "  output/${hash}/game.dot"
    echo "Done. Use: just show ${hash}"

# Show game state and available actions
# Usage: just show fe69
show hash:
    {{python}} bin/rules-engine.py show "output/{{hash}}/game.dot"
