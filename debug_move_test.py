#!/usr/bin/env python3

from blokus.game import Move
from blokus.pieces import PieceType

print("=== Testing Move creation with invalid piece_type ===")

try:
    print("Creating Move with piece_type=999 (int)...")
    move = Move(player_id=0, piece_type=999, orientation=0, row=0, col=0)
    print("✅ Move created successfully!")
    print(f"   piece_type value: {move.piece_type}")
    print(f"   piece_type type: {type(move.piece_type)}")
    print(f"   Move object: {move}")
    
    # Test if we can get the piece
    try:
        piece = move.get_piece()
        print(f"   get_piece() returned: {piece}")
    except Exception as e:
        print(f"   get_piece() failed: {type(e).__name__}: {e}")
        
except Exception as e:
    print(f"❌ Exception during Move creation: {type(e).__name__}: {e}")

print("\n=== Testing with valid PieceType ===")

try:
    print("Creating Move with PieceType.I1...")
    move2 = Move(player_id=0, piece_type=PieceType.I1, orientation=0, row=0, col=0)
    print("✅ Move created successfully!")
    print(f"   piece_type value: {move2.piece_type}")
    print(f"   piece_type type: {type(move2.piece_type)}")
    
except Exception as e:
    print(f"❌ Exception: {type(e).__name__}: {e}")
