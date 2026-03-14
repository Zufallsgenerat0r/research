"""
Biological organism simulation with swarming behavior.

Recreates the diatom/cell-like organisms seen in screenshot 5 of the
"Order From Chaos" video. Causeret described creating "simple living forms
in an ancient marine environment, looking at morphological specialisation,
emergent swarming behaviours, and simple motile life competing for resources."

This script creates procedural organism-like shapes with internal structures,
then simulates swarming/flocking behavior.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Circle, FancyBboxPatch
from matplotlib.collections import PatchCollection, LineCollection
from matplotlib.colors import hsv_to_rgb
import os

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class Diatom:
    """A procedural diatom-like organism with internal radial structures."""

    def __init__(self, x, y, size=None, color_hue=None):
        self.x = x
        self.y = y
        self.size = size or np.random.uniform(8, 25)
        self.hue = color_hue if color_hue is not None else np.random.choice(
            [0.85, 0.9, 0.95, 0.0, 0.05]  # pink/magenta range
        )
        self.angle = np.random.uniform(0, 2 * np.pi)
        self.aspect = np.random.uniform(0.5, 0.9)
        self.n_ribs = np.random.randint(5, 15)
        self.vx = np.random.randn() * 0.3
        self.vy = np.random.randn() * 0.3

    def draw(self, ax):
        """Draw the diatom with internal structure."""
        color = hsv_to_rgb([self.hue, 0.6, 0.7])
        color_bright = hsv_to_rgb([self.hue, 0.7, 0.85])

        # Outer ellipse
        e = Ellipse(
            (self.x, self.y),
            self.size * 2, self.size * 2 * self.aspect,
            angle=np.degrees(self.angle),
            facecolor="none", edgecolor=color_bright, linewidth=0.8, alpha=0.8,
        )
        ax.add_patch(e)

        # Internal ribs (radial lines typical of diatoms)
        cos_a = np.cos(self.angle)
        sin_a = np.sin(self.angle)
        rib_lines = []
        for i in range(self.n_ribs):
            frac = (i + 1) / (self.n_ribs + 1) - 0.5
            # Position along major axis
            local_x = frac * self.size * 1.6
            # Rib extends perpendicular to major axis
            rib_half = self.size * self.aspect * 0.7 * (1 - (2 * frac) ** 2)
            if rib_half > 0:
                x1 = self.x + local_x * cos_a - rib_half * sin_a
                y1 = self.y + local_x * sin_a + rib_half * cos_a
                x2 = self.x + local_x * cos_a + rib_half * sin_a
                y2 = self.y + local_x * sin_a - rib_half * cos_a
                rib_lines.append([(x1, y1), (x2, y2)])

        if rib_lines:
            lc = LineCollection(
                rib_lines, colors=[(*color, 0.4)], linewidths=0.4
            )
            ax.add_collection(lc)

        # Central line along major axis
        x1 = self.x - self.size * 0.8 * cos_a
        y1 = self.y - self.size * 0.8 * sin_a
        x2 = self.x + self.size * 0.8 * cos_a
        y2 = self.y + self.size * 0.8 * sin_a
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=0.5, alpha=0.5)


class RoundOrganism:
    """A round cell/organism with internal dot structures - like the green circles in the video."""

    def __init__(self, x, y, size=None, color_hue=None):
        self.x = x
        self.y = y
        self.size = size or np.random.uniform(5, 15)
        self.hue = color_hue if color_hue is not None else np.random.choice(
            [0.45, 0.5, 0.55, 0.35]  # teal/cyan/green range
        )
        self.n_rings = np.random.randint(1, 4)
        self.vx = np.random.randn() * 0.2
        self.vy = np.random.randn() * 0.2

    def draw(self, ax):
        color_edge = hsv_to_rgb([self.hue, 0.7, 0.85])
        color_fill = hsv_to_rgb([self.hue, 0.5, 0.6])

        for ring in range(self.n_rings):
            r = self.size * (1.0 - ring * 0.3)
            if r > 0:
                c = Circle(
                    (self.x, self.y), r,
                    facecolor="none", edgecolor=color_edge,
                    linewidth=0.8, alpha=0.7 - ring * 0.15,
                )
                ax.add_patch(c)

        # Central dot
        c = Circle(
            (self.x, self.y), self.size * 0.15,
            facecolor=color_fill, edgecolor="none", alpha=0.8,
        )
        ax.add_patch(c)


class ColonyOrganism:
    """A complex colony organism made of many packed circles - like the central
    aggregate in screenshot 5."""

    def __init__(self, x, y, size=30):
        self.x = x
        self.y = y
        self.size = size
        self.sub_organisms = []

        # Pack circles inside
        n = np.random.randint(30, 80)
        for _ in range(n):
            r = np.sqrt(np.random.random()) * size * 0.9
            theta = np.random.random() * 2 * np.pi
            ox = x + r * np.cos(theta)
            oy = y + r * np.sin(theta)
            sub_size = np.random.uniform(1, size * 0.2)
            hue = np.random.choice([0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.85, 0.9, 0.1])
            self.sub_organisms.append((ox, oy, sub_size, hue))

    def draw(self, ax):
        # Outer boundary
        boundary_color = hsv_to_rgb([0.5, 0.6, 0.8])
        angles = np.linspace(0, 2 * np.pi, 60)
        noise = np.random.randn(60) * self.size * 0.05
        bx = self.x + (self.size + noise) * np.cos(angles)
        by = self.y + (self.size + noise) * np.sin(angles)
        ax.fill(bx, by, facecolor=(0.1, 0.3, 0.3, 0.2), edgecolor=boundary_color,
                linewidth=1.0, alpha=0.8)

        # Sub-organisms
        for ox, oy, sub_size, hue in self.sub_organisms:
            color = hsv_to_rgb([hue, 0.6, 0.75])
            c = Circle(
                (ox, oy), sub_size,
                facecolor=(*color, 0.5),
                edgecolor=(*color, 0.8),
                linewidth=0.5,
            )
            ax.add_patch(c)


def simulate_swarm(organisms, n_steps=100, width=1400, height=800):
    """Simple flocking/swarming simulation."""
    for _ in range(n_steps):
        for org in organisms:
            if not hasattr(org, "vx"):
                continue

            # Apply slight attraction toward center
            cx, cy = width / 2, height / 2
            dx = cx - org.x
            dy = cy - org.y
            dist = np.sqrt(dx ** 2 + dy ** 2) + 1e-6
            org.vx += dx / dist * 0.01
            org.vy += dy / dist * 0.01

            # Random walk component
            org.vx += np.random.randn() * 0.05
            org.vy += np.random.randn() * 0.05

            # Damping
            org.vx *= 0.98
            org.vy *= 0.98

            # Update position
            org.x += org.vx
            org.y += org.vy

            # Boundary wrapping
            org.x = org.x % width
            org.y = org.y % height

            # Align orientation with velocity
            if hasattr(org, "angle"):
                org.angle = np.arctan2(org.vy, org.vx)


def main():
    print("=" * 60)
    print("Biological Organism Simulation")
    print("Inspired by Max Cooper - Order From Chaos")
    print("=" * 60)

    width, height = 1400, 800

    # Create diatom-like organisms (pink/magenta ellipses with internal ribs)
    print("\nCreating diatom population...")
    diatoms = [
        Diatom(
            np.random.uniform(0, width),
            np.random.uniform(0, height),
        )
        for _ in range(200)
    ]

    # Create round organisms (teal/cyan circles)
    round_orgs = [
        RoundOrganism(
            np.random.uniform(0, width),
            np.random.uniform(0, height),
        )
        for _ in range(40)
    ]

    # Central colony
    colony = ColonyOrganism(width / 2, height / 2, size=60)

    # Simulate swarming
    print("Simulating swarm behavior (100 steps)...")
    all_mobile = diatoms + round_orgs
    simulate_swarm(all_mobile, n_steps=100, width=width, height=height)

    # Render
    print("Rendering organism scene...")
    fig, ax = plt.subplots(1, 1, figsize=(14, 8), dpi=150)
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    # Draw diatoms first (background layer)
    for d in diatoms:
        d.draw(ax)

    # Draw round organisms
    for r in round_orgs:
        r.draw(ax)

    # Draw colony on top
    colony.draw(ax)

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_axis_off()
    ax.set_aspect("equal")
    plt.tight_layout(pad=0)

    filename = f"{OUTPUT_DIR}/organisms_swarm.png"
    fig.savefig(filename, bbox_inches="tight", pad_inches=0, facecolor="black")
    plt.close(fig)
    print(f"  Saved: {filename}")

    # Render just diatoms for the classic "Order From Chaos" look
    print("Rendering diatom-only scene...")
    fig, ax = plt.subplots(1, 1, figsize=(14, 8), dpi=150)
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    for d in diatoms:
        d.draw(ax)

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_axis_off()
    ax.set_aspect("equal")
    plt.tight_layout(pad=0)

    filename = f"{OUTPUT_DIR}/diatoms_only.png"
    fig.savefig(filename, bbox_inches="tight", pad_inches=0, facecolor="black")
    plt.close(fig)
    print(f"  Saved: {filename}")

    print(f"\nAll outputs saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
