"""
AI Agent Registry for Blokus.

Provides a centralized catalog of available AI personas with metadata
for both backend instantiation and frontend display.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any

from blokus.rl.agents.base import Agent
from blokus.rl.agents.random_agent import RandomAgent


@dataclass
class AgentMetadata:
    """Metadata for an AI agent."""
    id: str
    name: str
    description: str
    type: str  # "heuristic" or "model"
    level: str  # "débutant", "facile", "moyen", "difficile", "expert"
    style: str  # "agressif", "défensif", "efficace", "imprévisible"
    tags: List[str] = field(default_factory=list)
    enabled: bool = True
    
    # For heuristic agents
    class_name: Optional[str] = None
    
    # For model-based agents
    model_path: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    
    def to_api_dict(self) -> dict:
        """Convert to dict for API response."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "style": self.style,
            "tags": self.tags,
            "enabled": self.enabled,
            "tooltip": f"Niveau: {self.level.capitalize()} | Style: {self.style.capitalize()}"
        }


class AgentRegistry:
    """
    Registry for managing available AI agents.
    
    Loads agent definitions from a JSON file and provides:
    - List of available agents (for API)
    - Agent instantiation (Factory pattern)
    """
    
    # Mapping from class_name to actual class
    HEURISTIC_AGENTS = {
        "RandomAgent": RandomAgent,
        # Add more heuristic agents here
    }
    
    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize registry.
        
        Args:
            registry_path: Path to registry.json. Defaults to models/registry.json
        """
        if registry_path is None:
            # Default path relative to blokus-engine
            registry_path = Path(__file__).parent.parent.parent.parent / "models" / "registry.json"
        
        self.registry_path = Path(registry_path)
        self._agents: Dict[str, AgentMetadata] = {}
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Load agent definitions from JSON file."""
        if not self.registry_path.exists():
            print(f"Warning: Registry file not found at {self.registry_path}")
            return
        
        with open(self.registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for entry in data:
            metadata = AgentMetadata(
                id=entry["id"],
                name=entry["name"],
                description=entry["description"],
                type=entry["type"],
                level=entry.get("level", "moyen"),
                style=entry.get("style", "équilibré"),
                tags=entry.get("tags", []),
                enabled=entry.get("enabled", True),
                class_name=entry.get("class_name"),
                model_path=entry.get("model_path"),
                config=entry.get("config")
            )
            self._agents[metadata.id] = metadata
    
    def list_available(self, only_enabled: bool = True) -> List[AgentMetadata]:
        """
        List available agents.
        
        Args:
            only_enabled: If True, only return enabled agents
            
        Returns:
            List of agent metadata
        """
        agents = list(self._agents.values())
        if only_enabled:
            agents = [a for a in agents if a.enabled]
        return agents
    
    def list_for_api(self, only_enabled: bool = True) -> List[dict]:
        """
        List agents formatted for API response.
        
        Args:
            only_enabled: If True, only return enabled agents
            
        Returns:
            List of dicts ready for JSON serialization
        """
        return [a.to_api_dict() for a in self.list_available(only_enabled)]
    
    def get(self, agent_id: str) -> Optional[AgentMetadata]:
        """Get agent metadata by ID."""
        return self._agents.get(agent_id)
    
    def load_agent(self, agent_id: str) -> Agent:
        """
        Instantiate an agent by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Instantiated Agent
            
        Raises:
            ValueError: If agent not found or not loadable
        """
        metadata = self.get(agent_id)
        if metadata is None:
            raise ValueError(f"Unknown agent: {agent_id}")
        
        if not metadata.enabled:
            raise ValueError(f"Agent '{agent_id}' is not enabled")
        
        if metadata.type == "heuristic":
            return self._load_heuristic_agent(metadata)
        elif metadata.type == "model":
            return self._load_model_agent(metadata)
        else:
            raise ValueError(f"Unknown agent type: {metadata.type}")
    
    def _load_heuristic_agent(self, metadata: AgentMetadata) -> Agent:
        """Load a heuristic-based agent."""
        if metadata.class_name not in self.HEURISTIC_AGENTS:
            raise ValueError(f"Unknown heuristic agent class: {metadata.class_name}")
        
        agent_class = self.HEURISTIC_AGENTS[metadata.class_name]
        return agent_class()
    
    def _load_model_agent(self, metadata: AgentMetadata) -> Agent:
        """Load a model-based agent (DQN, etc.)."""
        if metadata.model_path is None:
            raise ValueError(f"Model path not specified for agent: {metadata.id}")
        
        # Resolve path relative to models directory
        models_dir = self.registry_path.parent
        model_path = models_dir / metadata.model_path
        
        if not model_path.exists():
            raise ValueError(f"Model file not found: {model_path}")
        
        # Import and load DQN agent (to be implemented)
        # For now, raise NotImplementedError
        raise NotImplementedError(
            f"Model-based agents not yet implemented. "
            f"Would load from: {model_path}"
        )
    
    def reload(self) -> None:
        """Reload registry from disk."""
        self._agents.clear()
        self._load_registry()


# Global singleton instance
_registry: Optional[AgentRegistry] = None


def get_registry() -> AgentRegistry:
    """Get the global registry instance."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry
