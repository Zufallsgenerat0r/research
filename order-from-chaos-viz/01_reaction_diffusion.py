"""
Reaction-Diffusion simulation using the Gray-Scott model.

Recreates the swirling Turing patterns seen in Max Cooper's "Order From Chaos"
video by Maxime Causeret. The Gray-Scott model simulates two virtual chemicals
(U and V) that diffuse and react on a 2D grid, producing organic-looking patterns
reminiscent of coral, lichen, and biological structures.

Based on Karl Sims' tutorial and the Gray-Scott parameter space.
"""

import numpy as np
from scipy.ndimage import laplace
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import os

# Output directory
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Grid parameters
WIDTH, HEIGHT = 512, 512

# Gray-Scott parameters - these control the pattern type
# Classic coral/spots: f=0.0545, k=0.062
# Mitosis (cell division): f=0.0367, k=0.0649
# Worms/maze: f=0.029, k=0.057
# Spirals: f=0.014, k=0.045
PRESETS = {
    "coral": {"f": 0.0545, "k": 0.062, "Du": 0.16, "Dv": 0.08},
    "mitosis": {"f": 0.0367, "k": 0.0649, "Du": 0.16, "Dv": 0.08},
    "worms": {"f": 0.029, "k": 0.057, "Du": 0.16, "Dv": 0.08},
    "spirals": {"f": 0.014, "k": 0.045, "Du": 0.12, "Dv": 0.06},
    "chaos_to_order": {"f": 0.04, "k": 0.06, "Du": 0.16, "Dv": 0.08},
}


def init_grid(width, height, seed_type="center"):
    """Initialize U and V concentration grids."""
    U = np.ones((height, width), dtype=np.float64)
    V = np.zeros((height, width), dtype=np.float64)

    if seed_type == "center":
        # Central square seed
        cx, cy = width // 2, height // 2
        r = 20
        U[cy - r : cy + r, cx - r : cx + r] = 0.50
        V[cy - r : cy + r, cx - r : cx + r] = 0.25
        # Add noise for organic variation
        noise = np.random.random((2 * r, 2 * r)) * 0.1
        U[cy - r : cy + r, cx - r : cx + r] += noise
        V[cy - r : cy + r, cx - r : cx + r] += noise * 0.5

    elif seed_type == "scattered":
        # Multiple random seeds - like the initial chaos in the video
        n_seeds = 30
        for _ in range(n_seeds):
            cx = np.random.randint(50, width - 50)
            cy = np.random.randint(50, height - 50)
            r = np.random.randint(3, 15)
            y_lo, y_hi = max(0, cy - r), min(height, cy + r)
            x_lo, x_hi = max(0, cx - r), min(width, cx + r)
            U[y_lo:y_hi, x_lo:x_hi] = 0.50
            V[y_lo:y_hi, x_lo:x_hi] = 0.25

    elif seed_type == "ring":
        # Ring seed - like the circular growth forms in the video
        Y, X = np.ogrid[:height, :width]
        cx, cy = width // 2, height // 2
        dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        ring_mask = (dist > 40) & (dist < 60)
        U[ring_mask] = 0.50
        V[ring_mask] = 0.25
        noise = np.random.random((height, width)) * 0.05
        U += noise * ring_mask
        V += noise * 0.5 * ring_mask

    return U, V


def simulate_gray_scott(U, V, params, n_steps=10000, dt=1.0, save_interval=2000):
    """Run the Gray-Scott reaction-diffusion simulation."""
    f = params["f"]
    k = params["k"]
    Du = params["Du"]
    Dv = params["Dv"]

    frames = []
    for step in range(n_steps):
        # Compute Laplacians (diffusion term)
        Lu = laplace(U, mode="wrap")
        Lv = laplace(V, mode="wrap")

        # Reaction terms
        uvv = U * V * V
        dU = Du * Lu - uvv + f * (1.0 - U)
        dV = Dv * Lv + uvv - (f + k) * V

        U += dt * dU
        V += dt * dV

        # Clamp values
        np.clip(U, 0, 1, out=U)
        np.clip(V, 0, 1, out=V)

        if (step + 1) % save_interval == 0:
            frames.append((U.copy(), V.copy(), step + 1))
            print(f"  Step {step + 1}/{n_steps}")

    return frames


def create_colormap_causeret():
    """Create a colormap inspired by the Causeret video palette."""
    # Dark background with teal, blue, magenta, green accents
    colors = [
        (0.02, 0.02, 0.05),  # near-black
        (0.05, 0.15, 0.25),  # dark blue
        (0.1, 0.35, 0.45),   # teal
        (0.3, 0.7, 0.65),    # bright teal/cyan
        (0.7, 0.2, 0.5),     # magenta
        (0.9, 0.85, 0.95),   # light lavender
    ]
    return LinearSegmentedColormap.from_list("causeret", colors, N=256)


def render_frame(U, V, step, preset_name, cmap):
    """Render a single frame as a high-quality image."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 10), dpi=150)
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    # Combine U and V channels for richer visualization
    combined = V - U * 0.3

    ax.imshow(combined, cmap=cmap, interpolation="bilinear")
    ax.set_axis_off()
    plt.tight_layout(pad=0)

    filename = f"{OUTPUT_DIR}/rd_{preset_name}_step{step:06d}.png"
    fig.savefig(filename, bbox_inches="tight", pad_inches=0, facecolor="black")
    plt.close(fig)
    return filename


def render_contour_style(U, V, step, preset_name):
    """Render using contour lines - like the topographic/nested outline style in the video."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 10), dpi=150)
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    # Multi-colored contour lines like in the video
    levels = np.linspace(0.05, 0.5, 20)
    colors_list = plt.cm.cool(np.linspace(0.2, 0.9, len(levels)))
    ax.contour(V, levels=levels, colors=colors_list, linewidths=0.5)

    # Add a second set of contours in different colors
    levels2 = np.linspace(0.1, 0.6, 15)
    colors_list2 = plt.cm.spring(np.linspace(0.3, 0.8, len(levels2)))
    ax.contour(V, levels=levels2, colors=colors_list2, linewidths=0.3, alpha=0.6)

    ax.set_xlim(0, V.shape[1])
    ax.set_ylim(0, V.shape[0])
    ax.set_axis_off()
    ax.set_aspect("equal")
    plt.tight_layout(pad=0)

    filename = f"{OUTPUT_DIR}/rd_contour_{preset_name}_step{step:06d}.png"
    fig.savefig(filename, bbox_inches="tight", pad_inches=0, facecolor="black")
    plt.close(fig)
    return filename


def main():
    print("=" * 60)
    print("Reaction-Diffusion (Gray-Scott Model)")
    print("Inspired by Max Cooper - Order From Chaos")
    print("=" * 60)

    cmap = create_colormap_causeret()

    for preset_name, params in PRESETS.items():
        print(f"\nRunning preset: {preset_name}")
        print(f"  f={params['f']}, k={params['k']}")

        seed_type = "ring" if preset_name == "chaos_to_order" else "scattered"
        U, V = init_grid(WIDTH, HEIGHT, seed_type=seed_type)

        frames = simulate_gray_scott(
            U, V, params, n_steps=10000, save_interval=2500
        )

        # Render final frame in both styles
        U_final, V_final, step = frames[-1]
        f1 = render_frame(U_final, V_final, step, preset_name, cmap)
        print(f"  Saved: {f1}")

        f2 = render_contour_style(U_final, V_final, step, preset_name)
        print(f"  Saved: {f2}")

    print(f"\nAll outputs saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
