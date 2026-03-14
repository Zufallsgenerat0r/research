# Recreating "Order From Chaos" Visualizations

Researching and recreating the visualization techniques from **Max Cooper - Order From Chaos**, an electronic music video with visuals by French artist **Maxime Causeret**.

**Video**: https://www.youtube.com/watch?v=_7wKjTf_RlI

## About the Original

The video was created by **Maxime Causeret** (aka Maxime Teresuac) using **SideFX Houdini**, a professional 3D procedural software. Causeret built his visualizations from a 2D fluid simulation system, using particle-driven lines, reaction-diffusion patterns, and agent-based organism simulations to tell a story of biological emergence — from chaotic raindrops to complex competing lifeforms.

The video accompanies Max Cooper's track from his *Emergence* album (2016), where the music itself was created by recording rain on a window and gradually forcing the random hits toward a rhythmic grid — literally creating order from chaos.

### Key Techniques in the Video
| Technique | What It Creates | Video Section |
|-----------|----------------|---------------|
| Particle-driven line ripples | Dense flowing contour patterns | 0:00-0:50 (Abstract) |
| Reaction-diffusion (Turing patterns) | Swirling organic textures | 0:50-2:44 (Emergence) |
| Differential growth | Undulating organic blob outlines | Throughout |
| Agent-based organism simulation | Diatom-like swarming creatures | 2:44-4:00 (Creatures) |

## This Repository

Python implementations of these four core techniques, producing similar static visualizations. All scripts use only standard scientific Python libraries (NumPy, SciPy, Matplotlib).

### Setup

```bash
pip install -r requirements.txt
```

### Running

Generate all visualizations:
```bash
python run_all.py
```

Or run individual scripts:
```bash
python 01_reaction_diffusion.py   # Gray-Scott reaction-diffusion
python 02_differential_growth.py  # Organic curve growth
python 03_particle_ripples.py     # Flow field particle trails
python 04_organisms.py            # Procedural organisms + swarming
```

Outputs are saved to `output/`.

### Script Details

#### 01_reaction_diffusion.py
Implements the **Gray-Scott model** — two virtual chemicals that diffuse and react on a 2D grid. Includes 5 parameter presets (coral, mitosis, worms, spirals, chaos_to_order) and renders in both heatmap and contour-line styles. The contour rendering closely matches the nested topographic patterns in the video.

#### 02_differential_growth.py
Simulates **differential growth** — nodes on a closed curve repel each other while staying connected, with new nodes inserted as edges stretch. Starts from simple circles and grows them into complex organic blobs, matching the scattered colored circle outlines in the video's early frames.

#### 03_particle_ripples.py
Creates **particle trails in a flow field**, mimicking Causeret's technique of lines driven by particles in a 2D fluid simulation. Uses layered sine/cosine functions for the flow field with a circular component for spiral motion. Renders as both direct particle trails and density contour maps.

#### 04_organisms.py
Generates **procedural diatom-like organisms** with internal radial rib structures (matching the pink elliptical forms in the video), round cell organisms with concentric rings, and colony aggregates. Includes a simple flocking/swarming simulation.

## Going Further

To get results closer to Causeret's original:

- **Houdini** (commercial, $4,495+): The original tool. Most faithful recreation possible.
- **Blender + Geometry Nodes** (free): Closest open-source analog to Houdini's procedural workflows.
- **Processing / p5.js** (free): Great for real-time interactive versions.
- **TouchDesigner** (free non-commercial): Real-time visual programming, excellent for music-reactive visuals.
- **GPU acceleration**: Use PyTorch or CUDA for real-time reaction-diffusion on large grids (40× speedup on 2000×2000 grids per [Nils Olovsson's benchmarks](https://nils-olovsson.se/articles/reaction_diffusion_models_and_turing_patterns/)).

### Key References
- [Karl Sims' Reaction-Diffusion Tutorial](https://www.karlsims.com/rd.html)
- [Inconvergent's Differential Line Algorithm](https://github.com/inconvergent/differential-line)
- [Gray-Scott Parameter Space (MROB)](http://www.mrob.com/pub/comp/xmorphia/index.html)
- [Causeret's Order From Chaos writeup](https://teresuac.fr/2017/06/order-from-chaos/)
- [GridMarkets Causeret Profile](https://www.gridmarkets.com/maxime-causeret)
