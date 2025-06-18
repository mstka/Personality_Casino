"""Reporting utilities for generating radar charts."""
import math
from typing import Dict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def generate_radar_chart(scores: Dict[str, float], filepath: str) -> None:
    """Generate a radar chart image for the given scores."""
    labels = list(scores.keys())
    values = list(scores.values())
    angles = [n / float(len(labels)) * 2 * math.pi for n in range(len(labels))]
    values += values[:1]
    angles += angles[:1]

    plt.figure(figsize=(3, 3))
    ax = plt.subplot(111, polar=True)
    plt.xticks(angles[:-1], labels)
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.25)
    ax.set_yticklabels([])
    plt.savefig(filepath)
    plt.close()
