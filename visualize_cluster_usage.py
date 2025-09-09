import sys
import re
import pandas as pd
import matplotlib.pyplot as plt

def parse_quantity(s: str) -> float:
    """Convert strings like 1024000MB into MB as float."""
    m = re.match(r"(\d+)([A-Za-z]*)", s)
    if not m:
        return 0.0
    val = float(m.group(1))
    unit = m.group(2).upper()
    K = 1024
    factor = {"B": 1/(K*K), "KB": 1/K, "MB": 1, "GB": K, "TB": K*K}
    return val * factor.get(unit, 1)

def parse_stats_file(filename: str) -> pd.DataFrame:
    rows = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line or "NODELIST" in line or "STATE" in line:
                continue
            parts = line.split()
            if len(parts) < 6:
                continue
            name, state, cpu, load, mem, gpu, *rest = parts
            try:
                c_free, c_tot = map(int, cpu.split("/"))
                cpu_load = float(load)
                m_match = re.match(r"(\d+)/(\d+)(\w+)", mem)
                m_avail = parse_quantity(m_match.group(1) + m_match.group(3))
                m_tot = parse_quantity(m_match.group(2) + m_match.group(3))
                g_free, g_tot = map(int, gpu.split("/"))
                rows.append({
                    "name": name,
                    "state": state,
                    "cpu_free": c_free,
                    "cpu_total": c_tot,
                    "cpu_used": c_tot - c_free,
                    "cpu_load": cpu_load,
                    "mem_avail": m_avail,
                    "mem_total": m_tot,
                    "mem_used": m_tot - m_avail,
                    "gpu_free": g_free,
                    "gpu_total": g_tot,
                    "gpu_used": g_tot - g_free,
                })
            except Exception as e:
                print("Skipping line:", line, "error:", e)
    return pd.DataFrame(rows)

def plot_per_node(df: pd.DataFrame, outfile="nodes.png"):
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    # CPUs
    axes[0].bar(df["name"], df["cpu_used"], label="Used", color="steelblue")
    axes[0].bar(df["name"], df["cpu_free"], bottom=df["cpu_used"], label="Free", color="#cccccc")
    axes[0].set_ylabel("CPUs")
    axes[0].legend()

    # Memory
    axes[1].bar(df["name"], df["mem_used"], label="Used", color="seagreen")
    axes[1].bar(df["name"], df["mem_avail"], bottom=df["mem_used"], label="Free", color="#cccccc")
    axes[1].set_ylabel("Memory (MB)")
    axes[1].legend()

    # GPUs
    axes[2].bar(df["name"], df["gpu_used"], label="Used", color="salmon")
    axes[2].bar(df["name"], df["gpu_free"], bottom=df["gpu_used"], label="Free", color="#cccccc")
    axes[2].set_ylabel("GPUs")
    axes[2].legend()

    # Rotate x-axis labels vertically
    for ax in axes:
        ax.tick_params(axis='x', rotation=90)

    plt.suptitle("Per-node Resource Usage at Princeton PLI")
    plt.tight_layout()
    plt.savefig(outfile, dpi=150)
    print(f"Saved per-node stacked plot to {outfile}")

def plot_aggregate(df: pd.DataFrame, outfile="aggregate.png"):
    labels = ["CPUs", "Memory (MB)", "GPUs"]
    used = [
        df["cpu_used"].sum(),
        df["mem_used"].sum(),
        df["gpu_used"].sum(),
    ]
    free = [
        df["cpu_free"].sum(),
        df["mem_avail"].sum(),
        df["gpu_free"].sum(),
    ]

    fig, ax = plt.subplots(figsize=(6,4))
    ax.bar(labels, used, color=["steelblue","seagreen","salmon"], label="Used")
    ax.bar(labels, free, bottom=used, color="#cccccc", label="Free")
    ax.set_ylabel("Resources")
    ax.set_title("Aggregate Resource Usage (Used + Free)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(outfile, dpi=150)
    print(f"Saved aggregate stacked plot to {outfile}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cluster_stats_plot.py <statsfile>")
        sys.exit(1)
    df = parse_stats_file(sys.argv[1])
    if df.empty:
        print("No data parsed.")
        sys.exit(1)
    plot_per_node(df, "nodes.png")
    plot_aggregate(df, "aggregate.png")
