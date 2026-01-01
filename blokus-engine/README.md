# Blokus Game Engine

Moteur de jeu Python pour Blokus.

## Installation

```bash
cd blokus-engine
pip install -e ".[dev]"
```

## Usage

```python
from blokus import Game, Piece

game = Game(num_players=4)
# Jouer un coup...
```

## Tests

```bash
pytest tests/ -v
```
