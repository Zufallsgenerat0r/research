"""
Particle-driven line ripples and fluid-like patterns.

Recreates the dense contour/topographic line patterns seen in screenshots 3 and 4
of the "Order From Chaos" video. Causeret described starting from a realistic river
flow system: 2D fluid simulation, texture advection, ripples, and foam. Lines are
driven by particles and resampled each frame to extend infinitely.

This script simulates particle trails in a flow field to create similar patterns.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
from scipy.ndimage import gaussian_filter
import os

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_flow_field(width, height, scale=0.01, octaves=3, time=0.0):
    """Create a 2D flow field using layered sine/cosine functions (Perlin-like)."""
    Y, X = np.mgrid[0:height, 0:width]
    Xf = X.astype(np.float64) * scale
    Yf = Y.astype(np.float64) * scale

    # Layer multiple frequencies for organic flow
    angle = np.zeros((height, width))
    amplitude = 1.0
    for i in range(octaves):
        freq = 2.0 ** i
        angle += amplitude * np.sin(Xf * freq + time * 0.5 + np.cos(Yf * freq * 0.7))
        angle += amplitude * np.cos(Yf * freq + time * 0.3 + np.sin(Xf * freq * 0.5))
        amplitude *= 0.5

    # Add circular component for spiral-like motion (as in the video)
    cx, cy = width / 2, height / 2
    dx = X - cx
    dy = Y - cy
    dist = np.sqrt(dx ** 2 + dy ** 2) + 1e-6
    circular = np.arctan2(dy, dx) + 0.3 * np.sin(dist * 0.02 + time)
    angle = angle * 0.6 + circular * 0.4

    vx = np.cos(angle)
    vy = np.sin(angle)
    return vx, vy


def trace_particles(vx, vy, n_particles=2000, n_steps=80, dt=1.5):
    """Trace particles through the flow field, recording their trails."""
    height, width = vx.shape
    trails = []

    # Initialize particles in a circular region (like the video's circular growth form)
    cx, cy = width / 2, height / 2
    max_r = min(width, height) * 0.4

    for _ in range(n_particles):
        # Distribute in a disc
        r = np.sqrt(np.random.random()) * max_r
        theta = np.random.random() * 2 * np.pi
        x = cx + r * np.cos(theta)
        y = cy + r * np.sin(theta)

        trail = [(x, y)]
        for _ in range(n_steps):
            ix = int(np.clip(x, 0, width - 1))
            iy = int(np.clip(y, 0, height - 1))
            x += vx[iy, ix] * dt
            y += vy[iy, ix] * dt

            # Boundary wrapping
            x = x % width
            y = y % height
            trail.append((x, y))

        trails.append(np.array(trail))

    return trails


def render_flow_lines(trails, width, height, style="neon_contour"):
    """Render particle trails in different styles."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 10), dpi=150)
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    if style == "neon_contour":
        # Multi-colored thin lines - like screenshots 3 & 4
        color_palettes = [
            plt.cm.cool,
            plt.cm.spring,
            plt.cm.winter,
        ]
        for i, trail in enumerate(trails):
            palette = color_palettes[i % len(color_palettes)]
            color = palette(np.random.random())
            alpha = 0.3 + np.random.random() * 0.4
            lw = 0.2 + np.random.random() * 0.5
            ax.plot(trail[:, 0], trail[:, 1], color=color, linewidth=lw, alpha=alpha)

    elif style == "causeret_ripple":
        # Dense overlapping lines mimicking the ripple system
        for i, trail in enumerate(trails):
            hue = (i / len(trails) * 0.4 + 0.45) % 1.0  # teal-blue-magenta range
            sat = 0.5 + np.random.random() * 0.4
            val = 0.5 + np.random.random() * 0.4
            color = hsv_to_rgb([hue, sat, val])
            alpha = 0.15 + np.random.random() * 0.25
            ax.plot(trail[:, 0], trail[:, 1], color=color, linewidth=0.3, alpha=alpha)

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_axis_off()
    ax.set_aspect("equal")
    plt.tight_layout(pad=0)

    filename = f"{OUTPUT_DIR}/flow_lines_{style}.png"
    fig.savefig(filename, bbox_inches="tight", pad_inches=0, facecolor="black")
    plt.close(fig)
    return filename


def render_density_contours(trails, width, height):
    """Render particle density as contour lines - creates the topographic map look."""
    # Create density map
    density = np.zeros((height, width))
    for trail in trails:
        for x, y in trail:
            ix = int(np.clip(x, 0, width - 1))
            iy = int(np.clip(y, 0, height - 1))
            density[iy, ix] += 1

    # Smooth the density
    density = gaussian_filter(density, sigma=3.0)

    fig, ax = plt.subplots(1, 1, figsize=(10, 10), dpi=150)
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    # Multi-colored contour lines
    levels = np.linspace(density.min() + 0.1, density.max() * 0.8, 25)
    if len(levels) > 1:
        colors_cyan = plt.cm.cool(np.linspace(0.3, 0.9, len(levels)))
        cs1 = ax.contour(density, levels=levels, colors=colors_cyan, linewidths=0.4)

        levels2 = np.linspace(density.min() + 0.5, density.max() * 0.6, 15)
        if len(levels2) > 1:
            colors_magenta = plt.cm.spring(np.linspace(0.2, 0.7, len(levels2)))
            ax.contour(density, levels=levels2, colors=colors_magenta, linewidths=0.3, alpha=0.6)

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_axis_off()
    ax.set_aspect("equal")
    plt.tight_layout(pad=0)

    filename = f"{OUTPUT_DIR}/flow_density_contours.png"
    fig.savefig(filename, bbox_inches="tight", pad_inches=0, facecolor="black")
    plt.close(fig)
    return filename


def main():
    print("=" * 60)
    print("Particle-Driven Flow Lines & Ripples")
    print("Inspired by Max Cooper - Order From Chaos")
    print("=" * 60)

    width, height = 800, 800

    # Generate flow field
    print("\nGenerating flow field...")
    vx, vy = create_flow_field(width, height, scale=0.008, octaves=4, time=0.0)

    # Trace particles
    print("Tracing particles (2000 particles, 80 steps each)...")
    trails = trace_particles(vx, vy, n_particles=2000, n_steps=80, dt=1.5)

    # Render in different styles
    print("Rendering neon contour style...")
    f = render_flow_lines(trails, width, height, style="neon_contour")
    print(f"  Saved: {f}")

    print("Rendering Causeret ripple style...")
    f = render_flow_lines(trails, width, height, style="causeret_ripple")
    print(f"  Saved: {f}")

    print("Rendering density contours...")
    f = render_density_contours(trails, width, height)
    print(f"  Saved: {f}")

    # Second flow field at different time for variety
    print("\nGenerating second flow field (time=2.0)...")
    vx2, vy2 = create_flow_field(width, height, scale=0.012, octaves=4, time=2.0)
    trails2 = trace_particles(vx2, vy2, n_particles=3000, n_steps=60, dt=1.2)

    print("Rendering dense ripple field...")
    f = render_flow_lines(trails2, width, height, style="causeret_ripple")
    print(f"  Saved: {f}")

    print(f"\nAll outputs saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
