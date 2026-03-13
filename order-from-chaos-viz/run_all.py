"""
Master script to generate all visualizations inspired by
Max Cooper - Order From Chaos (video by Maxime Causeret).

Run this to generate all output images in the output/ directory.
"""

import subprocess
import sys
import os

SCRIPTS = [
    ("01_reaction_diffusion.py", "Reaction-Diffusion (Gray-Scott)"),
    ("02_differential_growth.py", "Differential Growth"),
    ("03_particle_ripples.py", "Particle Flow Lines & Ripples"),
    ("04_organisms.py", "Biological Organisms"),
]


def main():
    os.makedirs("output", exist_ok=True)

    print("=" * 70)
    print("Order From Chaos - Visualization Generator")
    print("Recreating techniques from the Max Cooper / Maxime Causeret video")
    print("=" * 70)

    for script, name in SCRIPTS:
        print(f"\n{'─' * 70}")
        print(f"Running: {name} ({script})")
        print(f"{'─' * 70}")
        result = subprocess.run(
            [sys.executable, script],
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        if result.returncode != 0:
            print(f"WARNING: {script} exited with code {result.returncode}")

    print(f"\n{'=' * 70}")
    print("Done! All outputs saved to output/")
    print(f"{'=' * 70}")

    # List output files
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    if os.path.exists(output_dir):
        files = sorted(os.listdir(output_dir))
        print(f"\nGenerated {len(files)} files:")
        for f in files:
            size = os.path.getsize(os.path.join(output_dir, f))
            print(f"  {f} ({size // 1024} KB)")


if __name__ == "__main__":
    main()
