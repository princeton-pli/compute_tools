"""Generates usage plots for the top users."""

import sys
import pandas as pd
import matplotlib.pyplot as plt

def main(infile, outfile="gpu_hours.png"):
    # Try to read as CSV with any delimiter (comma, tab, or whitespace)
    try:
        df = pd.read_csv(infile, delim_whitespace=True)
    except Exception:
        df = pd.read_csv(infile)

    # Ensure the relevant columns exist
    if "USER" not in df.columns or "GPU-HOURS" not in df.columns:
        print("Error: input file must contain at least 'USER' and 'GPU-HOURS' columns")
        sys.exit(1)

    # Sort users by GPU hours descending
    df = df.sort_values("GPU-HOURS", ascending=False)

    # Plot
    plt.figure(figsize=(12,6))
    plt.bar(df["USER"], df["GPU-HOURS"], color="steelblue")
    plt.xticks(rotation=90)
    plt.xlabel("User")
    plt.ylabel("GPU-Hours")
    plt.title("GPU-Hours per User")
    plt.tight_layout()
    plt.savefig(outfile, dpi=150)
    print(f"Saved plot to {outfile}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gpu_usage_plot.py <input_file> [output_file]")
        sys.exit(1)
    infile = sys.argv[1]
    outfile = sys.argv[2] if len(sys.argv) > 2 else "gpu_hours.png"
    main(infile, outfile)
