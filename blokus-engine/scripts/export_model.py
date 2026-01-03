import torch
import sys
import os

def export_model(checkpoint_path, output_path):
    print(f"Loading {checkpoint_path}...")
    try:
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
    except Exception as e:
        print(f"Error loading checkpoint: {e}")
        sys.exit(1)
    
    # Extract only the online_net state dict
    state_dict = None
    
    if 'model_state_dict' in checkpoint:
        # Full training checkpoint
        model_state = checkpoint['model_state_dict']
        if 'online_net' in model_state:
            state_dict = model_state['online_net']
        else:
            # Fallback if structure is different
            print("Could not find 'online_net' in 'model_state_dict'. Keys:", model_state.keys())
            sys.exit(1)
            
    elif 'online_net' in checkpoint:
        # Agent state dict
        state_dict = checkpoint['online_net']
    else:
        # Maybe it's already the state dict?
        # Check if keys look like weights
        keys = list(checkpoint.keys())
        if keys and isinstance(keys[0], str) and ('weight' in keys[0] or 'bias' in keys[0]):
             state_dict = checkpoint
        else:
             print("Unknown checkpoint format. Keys:", keys[:5])
             sys.exit(1)
        
    print(f"Saving inference model weights to {output_path}...")
    # Convert to half precision to save space (106MB -> 53MB)
    state_dict_half = {k: v.half() for k, v in state_dict.items()}
    torch.save(state_dict_half, output_path)
    
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Done. File size: {size_mb:.2f} MB")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python export_model.py <checkpoint_path> <output_path>")
        sys.exit(1)
    
    export_model(sys.argv[1], sys.argv[2])
