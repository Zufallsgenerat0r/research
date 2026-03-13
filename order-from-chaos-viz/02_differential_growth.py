"""
Differential Growth simulation.

Recreates the organic blob/circle outlines seen in the second screenshot of
the "Order From Chaos" video. Nodes on a closed curve repel each other while
staying connected, and new nodes are inserted when segments stretch too far.
This creates organic, undulating shapes that grow over time.

Based on the algorithm by Anders Hoff (Inconvergent) and Nervous System's Floraform.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import os

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class DifferentialGrowthCurve:
    """A single closed curve that grows via differential growth."""

    def __init__(self, center, radius, n_points=60, color=None):
        angles = np.linspace(0, 2 * np.pi, n_points, endpoint=False)
        noise = np.random.randn(n_points) * radius * 0.02
        self.points = np.column_stack([
            center[0] + (radius + noise) * np.cos(angles),
            center[1] + (radius + noise) * np.sin(angles),
        ])
        self.color = color if color is not None else hsv_to_rgb(
            [np.random.random(), 0.7, 0.85]
        )

    def step(
        self,
        repulsion_radius=15.0,
        repulsion_strength=0.8,
        attraction_strength=0.1,
        max_edge_len=10.0,
        damping=0.5,
    ):
        n = len(self.points)
        forces = np.zeros_like(self.points)

        # Repulsion between all nearby nodes
        for i in range(n):
            diff = self.points - self.points[i]
            dist = np.linalg.norm(diff, axis=1)
            mask = (dist > 0) & (dist < repulsion_radius)
            if np.any(mask):
                direction = diff[mask] / dist[mask, np.newaxis]
                strength = (repulsion_radius - dist[mask]) / repulsion_radius
                forces[i] -= np.sum(
                    direction * strength[:, np.newaxis] * repulsion_strength, axis=0
                )

        # Attraction to neighbors (keep curve connected)
        for i in range(n):
            prev_idx = (i - 1) % n
            next_idx = (i + 1) % n
            mid = (self.points[prev_idx] + self.points[next_idx]) / 2
            forces[i] += (mid - self.points[i]) * attraction_strength

        # Apply forces with damping
        self.points += forces * damping

        # Insert new nodes where edges are too long
        new_points = []
        for i in range(n):
            new_points.append(self.points[i])
            next_idx = (i + 1) % n
            edge = self.points[next_idx] - self.points[i]
            edge_len = np.linalg.norm(edge)
            if edge_len > max_edge_len:
                mid = (self.points[i] + self.points[next_idx]) / 2
                noise = np.random.randn(2) * 0.5
                new_points.append(mid + noise)

        self.points = np.array(new_points)


def create_scattered_circles(n_circles=40, width=1400, height=800):
    """Create multiple scattered growth curves like in the video screenshot."""
    curves = []
    for _ in range(n_circles):
        cx = np.random.uniform(50, width - 50)
        cy = np.random.uniform(50, height - 50)
        r = np.random.uniform(8, 40)
        n_pts = max(12, int(r * 2))
        color = hsv_to_rgb([np.random.random(), 0.6 + np.random.random() * 0.3, 0.7 + np.random.random() * 0.3])
        curve = DifferentialGrowthCurve(
            center=(cx, cy), radius=r, n_points=n_pts, color=color
        )
        curves.append(curve)
    return curves


def render_curves(curves, width, height, step, style="outline"):
    """Render all curves to an image."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 8), dpi=150)
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    for curve in curves:
        pts = np.vstack([curve.points, curve.points[0]])  # close the curve

        if style == "outline":
            ax.plot(
                pts[:, 0], pts[:, 1],
                color=curve.color, linewidth=1.0, alpha=0.85,
            )
        elif style == "filled":
            from matplotlib.patches import Polygon
            poly = Polygon(
                curve.points, closed=True,
                facecolor=(*curve.color, 0.1),
                edgecolor=curve.color,
                linewidth=0.8,
            )
            ax.add_patch(poly)

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_axis_off()
    ax.set_aspect("equal")
    plt.tight_layout(pad=0)

    filename = f"{OUTPUT_DIR}/diff_growth_{style}_step{step:04d}.png"
    fig.savefig(filename, bbox_inches="tight", pad_inches=0, facecolor="black")
    plt.close(fig)
    return filename


def render_single_growth(n_steps=200):
    """Grow a single circle from simple to complex - like the video's emergence theme."""
    curve = DifferentialGrowthCurve(
        center=(400, 400), radius=50, n_points=80,
        color=hsv_to_rgb([0.5, 0.7, 0.8])
    )

    for step in range(n_steps):
        curve.step(
            repulsion_radius=12.0,
            repulsion_strength=0.6,
            attraction_strength=0.08,
            max_edge_len=8.0,
            damping=0.4,
        )

    fig, ax = plt.subplots(1, 1, figsize=(8, 8), dpi=150)
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    pts = np.vstack([curve.points, curve.points[0]])
    ax.plot(pts[:, 0], pts[:, 1], color=(0.3, 0.8, 0.7), linewidth=0.6, alpha=0.9)
    ax.fill(pts[:, 0], pts[:, 1], color=(0.1, 0.3, 0.3), alpha=0.15)

    ax.set_axis_off()
    ax.set_aspect("equal")
    plt.tight_layout(pad=0)

    filename = f"{OUTPUT_DIR}/diff_growth_single_organic.png"
    fig.savefig(filename, bbox_inches="tight", pad_inches=0, facecolor="black")
    plt.close(fig)
    print(f"  Saved: {filename}")
    return filename


def main():
    print("=" * 60)
    print("Differential Growth")
    print("Inspired by Max Cooper - Order From Chaos")
    print("=" * 60)

    width, height = 1400, 800

    # Phase 1: Scattered circles (like early video frames)
    print("\nPhase 1: Scattered circle outlines...")
    curves = create_scattered_circles(n_circles=50, width=width, height=height)
    f = render_curves(curves, width, height, step=0, style="outline")
    print(f"  Saved: {f}")

    # Phase 2: Grow them a bit
    print("\nPhase 2: Growing circles (20 steps)...")
    for step in range(20):
        for curve in curves:
            curve.step(
                repulsion_radius=12.0,
                repulsion_strength=0.5,
                attraction_strength=0.1,
                max_edge_len=10.0,
            )
    f = render_curves(curves, width, height, step=20, style="outline")
    print(f"  Saved: {f}")

    # Phase 3: Grow more - organic blobs emerge
    print("\nPhase 3: Further growth (80 steps)...")
    for step in range(60):
        for curve in curves:
            curve.step(
                repulsion_radius=15.0,
                repulsion_strength=0.6,
                attraction_strength=0.08,
                max_edge_len=8.0,
            )
    f = render_curves(curves, width, height, step=80, style="outline")
    print(f"  Saved: {f}")

    # Phase 4: Single organism growth
    print("\nPhase 4: Single organic form growth...")
    render_single_growth(n_steps=250)

    print(f"\nAll outputs saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
