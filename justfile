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

    # Generate 4-char hash from deck filenames
    hash=$(echo "{{deck1}}{{deck2}}" | md5sum | cut -c1-4)
    outdir="output/${hash}"

    echo "Creating matchup: ${hash}"
    mkdir -p "${outdir}"

    # Convert decks to dot
    {{python}} bin/txt_to_dot.py 1 "{{deck1}}" > "${outdir}/deck1.dot"
    {{python}} bin/txt_to_dot.py 2 "{{deck2}}" > "${outdir}/deck2.dot"

    # Create base game.dot (template + decks, unshuffled)
    {{python}} bin/rules-engine.py init "${outdir}"

    echo "  ${outdir}/deck1.dot"
    echo "  ${outdir}/deck2.dot"
    echo "  ${outdir}/game.dot"
    echo "Done. Use: just show ${hash}"

# Show game state and available actions
# Usage: just show fe69
show hash:
    {{python}} bin/rules-engine.py show "output/{{hash}}/game.dot"
