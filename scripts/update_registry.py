#!/usr/bin/env python3
"""
Update the model registry with a new trained model.

This script adds or updates a model entry in blokus-engine/models/registry.json
to make it available for the web interface.
"""

import json
import argparse
from pathlib import Path
from typing import Optional


def update_registry(
    registry_path: Path,
    model_id: str,
    name: str,
    description: str,
    model_path: str,
    board_size: int,
    num_players: int = 2,
    algorithm: str = "DQN",
    level: str = "expert",
    style: str = "efficace",
    tags: Optional[list[str]] = None,
    enabled: bool = True,
) -> None:
    """
    Add or update a model entry in registry.json.
    
    Args:
        registry_path: Path to registry.json
        model_id: Unique identifier for the model
        name: Display name
        description: Human-readable description
        model_path: Relative path to model.pt (from models/ directory)
        board_size: Board size (14 for Duo, 20 for Standard)
        num_players: Number of players (2 or 4)
        algorithm: Training algorithm (default: DQN)
        level: Difficulty level (débutant, facile, expert)
        style: Playing style description
        tags: List of tags for filtering
        enabled: Whether the model is enabled
    """
    # Load existing registry
    if registry_path.exists():
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    else:
        registry = []
    
    # Default tags based on board size
    if tags is None:
        if board_size == 14:
            tags = ["expert", "duo-only", "slow"]
        elif board_size == 20:
            tags = ["expert", "standard-only", "slow"]
        else:
            tags = ["expert"]
    
    # Create new model entry
    new_entry = {
        "id": model_id,
        "name": name,
        "description": description,
        "type": "model",
        "model_path": model_path,
        "config": {
            "board_size": board_size,
            "num_players": num_players,
            "algorithm": algorithm
        },
        "level": level,
        "style": style,
        "tags": tags,
        "enabled": enabled
    }
    
    # Check if model already exists
    existing_idx = None
    for idx, entry in enumerate(registry):
        if entry.get("id") == model_id:
            existing_idx = idx
            break
    
    if existing_idx is not None:
        # Update existing entry
        registry[existing_idx] = new_entry
        print(f"✅ Updated model '{model_id}' in registry")
    else:
        # Add new entry
        registry.append(new_entry)
        print(f"✅ Added model '{model_id}' to registry")
    
    # Save registry
    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"📝 Registry saved to {registry_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Update model registry with a new trained model"
    )
    parser.add_argument(
        "--id",
        required=True,
        help="Unique model ID (e.g., 'duo_expert_v2')"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Display name (e.g., 'Expert Duo v2')"
    )
    parser.add_argument(
        "--description",
        default="IA entraînée avec Deep Q-Network. Niveau expert.",
        help="Model description"
    )
    parser.add_argument(
        "--model-path",
        required=True,
        help="Relative path to model.pt from models/ directory (e.g., 'deployed/duo_v2.pt')"
    )
    parser.add_argument(
        "--board-size",
        type=int,
        required=True,
        choices=[14, 20],
        help="Board size (14 for Duo, 20 for Standard)"
    )
    parser.add_argument(
        "--num-players",
        type=int,
        default=2,
        choices=[2, 4],
        help="Number of players (default: 2)"
    )
    parser.add_argument(
        "--algorithm",
        default="DQN",
        help="Training algorithm (default: DQN)"
    )
    parser.add_argument(
        "--level",
        default="expert",
        choices=["débutant", "facile", "expert"],
        help="Difficulty level (default: expert)"
    )
    parser.add_argument(
        "--style",
        default="efficace",
        help="Playing style description (default: efficace)"
    )
    parser.add_argument(
        "--enabled",
        action="store_true",
        default=True,
        help="Enable the model (default: True)"
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path(__file__).parent.parent / "blokus-engine" / "models" / "registry.json",
        help="Path to registry.json (default: auto-detect)"
    )
    
    args = parser.parse_args()
    
    update_registry(
        registry_path=args.registry,
        model_id=args.id,
        name=args.name,
        description=args.description,
        model_path=args.model_path,
        board_size=args.board_size,
        num_players=args.num_players,
        algorithm=args.algorithm,
        level=args.level,
        style=args.style,
        enabled=args.enabled,
    )


if __name__ == "__main__":
    main()
