
import matplotlib.pyplot as plt
import pandas as pd
import sys
import os

def plot_metrics(csv_path, output_path):
    print(f"Reading metrics from {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading metrics: {e}")
        return

    if df.empty:
        print("Metrics file is empty.")
        return

    plt.figure(figsize=(12, 6))
    
    # Plot win rate if available
    if 'win_rate' in df.columns:
        plt.subplot(1, 2, 1)
        plt.plot(df['epoch'], df['win_rate'], label='Win Rate', color='blue')
        plt.xlabel('Epoch')
        plt.ylabel('Win Rate')
        plt.title('Win Rate over Time')
        plt.grid(True)
        plt.legend()
    
    # Plot loss if available
    if 'loss' in df.columns:
        plt.subplot(1, 2, 2)
        plt.plot(df['epoch'], df['loss'], label='Loss', color='red')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Training Loss')
        plt.grid(True)
        plt.legend()

    plt.tight_layout()
    print(f"Saving plot to {output_path}...")
    plt.savefig(output_path)
    print("Done.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python plot_metrics.py <csv_path> <output_path>")
        sys.exit(1)
    
    plot_metrics(sys.argv[1], sys.argv[2])
