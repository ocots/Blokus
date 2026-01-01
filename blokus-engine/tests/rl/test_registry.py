import pytest
import json
from pathlib import Path
import tempfile
from blokus.rl.registry import AgentRegistry, AgentMetadata

class TestAgentRegistry:
    @pytest.fixture
    def temp_registry_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            registry_path = Path(tmpdir) / "registry.json"
            data = [
                {
                    "id": "random",
                    "name": "Aléatoire",
                    "description": "Joue au hasard",
                    "type": "heuristic",
                    "class_name": "RandomAgent",
                    "enabled": True
                },
                {
                    "id": "disabled_agent",
                    "name": "Désactivé",
                    "description": "Ne devrait pas apparaître",
                    "type": "heuristic",
                    "class_name": "RandomAgent",
                    "enabled": False
                }
            ]
            with open(registry_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            yield registry_path

    def test_load_registry(self, temp_registry_file):
        """Registry should load agents from JSON."""
        registry = AgentRegistry(temp_registry_file)
        assert len(registry._agents) == 2
        assert "random" in registry._agents

    def test_list_available(self, temp_registry_file):
        """Should only list enabled agents by default."""
        registry = AgentRegistry(temp_registry_file)
        available = registry.list_available()
        assert len(available) == 1
        assert available[0].id == "random"
        
        all_agents = registry.list_available(only_enabled=False)
        assert len(all_agents) == 2

    def test_get_agent_metadata(self, temp_registry_file):
        """Should return correct metadata by ID."""
        registry = AgentRegistry(temp_registry_file)
        meta = registry.get("random")
        assert meta.id == "random"
        assert meta.name == "Aléatoire"
        
        assert registry.get("non_existent") is None

    def test_load_heuristic_agent(self, temp_registry_file):
        """Should instantiate RandomAgent correctly."""
        from blokus.rl.agents.random_agent import RandomAgent
        registry = AgentRegistry(temp_registry_file)
        agent = registry.load_agent("random")
        assert isinstance(agent, RandomAgent)

    def test_load_agent_errors(self, temp_registry_file):
        """Should raise ValueError for unknown or disabled agents."""
        registry = AgentRegistry(temp_registry_file)
        
        with pytest.raises(ValueError, match="Unknown agent"):
            registry.load_agent("ghost")
            
        with pytest.raises(ValueError, match="not enabled"):
            registry.load_agent("disabled_agent")

    def test_agent_metadata_to_api_dict(self):
        """Metadata should convert correctly for API usage."""
        meta = AgentMetadata(
            id="test",
            name="Test",
            description="Desc",
            type="heuristic",
            level="moyen",
            style="équilibré"
        )
        api_dict = meta.to_api_dict()
        assert api_dict["id"] == "test"
        assert "tooltip" in api_dict
        assert "Moyen" in api_dict["tooltip"]
