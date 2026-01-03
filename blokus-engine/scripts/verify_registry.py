
import sys
from pathlib import Path
sys.path.insert(0, "./src")

from blokus.rl.registry import get_registry

def test_load_agent():
    print("Testing agent loading...")
    registry = get_registry()
    registry.reload()
    
    # Try to load the agent we just enabled
    agent_id = "dqn_duo_v1"
    
    try:
        agent = registry.load_agent(agent_id)
        print(f"Successfully loaded agent: {agent_id}")
        print(f"Agent type: {type(agent)}")
        print(f"Agent device: {agent.device}")
        
        # Verify it has a network
        if hasattr(agent, "online_net"):
            print("Agent has online_net")
        else:
            print("ERROR: Agent missing online_net")
            
    except Exception as e:
        print(f"FAILED to load agent: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_load_agent()
