# Research Notes: OrangeCrab FPGA Agent Setup for MicroPython Bitstream Generation

## Research Date: 2026-03-22

## Goal

Research an automated agent setup to generate FPGA bitstreams for the OrangeCrab board (Lattice ECP5), targeting soft CPU cores capable of running interpreted languages like MicroPython and CircuitPython — with a focus on hardware acceleration possibilities.

## Sources Consulted

- [OrangeCrab Hardware Documentation](https://orangecrab-fpga.github.io/orangecrab-hardware/) — Board specs, pinout, getting started
- [orangecrab-fpga/orangecrab-hardware](https://github.com/orangecrab-fpga/orangecrab-hardware) — Hardware design files
- [orangecrab-fpga/orangecrab-examples](https://github.com/orangecrab-fpga/orangecrab-examples) — Example designs and LiteX SoC
- [enjoy-digital/litex](https://github.com/enjoy-digital/litex) — Python-based SoC builder framework
- [litex-hub/litex-boards](https://github.com/litex-hub/litex-boards) — Board targets including OrangeCrab
- [LiteX Wiki: Run MicroPython/CircuitPython On Your SoC](https://github.com/enjoy-digital/litex/wiki/Run-MicroPython-CircuitPython-On-Your-SoC) — Official MicroPython integration guide
- [SpinalHDL/VexRiscv](https://github.com/SpinalHDL/VexRiscv) — Configurable RISC-V CPU core
- [YosysHQ/yosys](https://github.com/YosysHQ/yosys) — Open-source RTL synthesis
- [YosysHQ/nextpnr](https://github.com/YosysHQ/nextpnr) — Open-source place and route
- [YosysHQ/prjtrellis](https://github.com/YosysHQ/prjtrellis) — ECP5 bitstream documentation and tools
- [FuPy Project](https://fupy.github.io/) — MicroPython for FPGAs
- [fupy GitHub Organization](https://github.com/fupy) — FuPy source repositories
- [Fomu Workshop: Python on Fomu](https://workshop.fomu.im/en/latest/python.html) — MicroPython on FPGA USB device
- [CircuitPython LiteX Port](https://docs.circuitpython.org/en/latest/ports/litex/README.html) — Adafruit's LiteX CircuitPython port
- [Linux on LiteX-VexRiscv](https://github.com/litex-hub/linux-on-litex-vexriscv) — Full Linux on ECP5 boards
- [CFU Playground (arXiv:2201.01863)](https://arxiv.org/pdf/2201.01863) — Custom Function Units for VexRiscv
- [YosysHQ OSS CAD Suite](https://github.com/YosysHQ/oss-cad-suite-build) — Pre-built open-source FPGA toolchain
- [Numato: Running MicroPython on FPGA](https://numato.com/kb/running-micropython-on-mimas-a7-using-litex-and-migen/) — Step-by-step LiteX + MicroPython tutorial
- [Nick Zoic: FuPy MicroPython for FPGAs](https://nick.zoic.org/art/fupy-micropython-for-fpga/) — FuPy architecture overview

## Approach

1. Surveyed OrangeCrab hardware specifications — ECP5 variants, DDR3L memory, QSPI Flash, DFU bootloader
2. Mapped the complete open-source ECP5 toolchain: Yosys (synthesis) → nextpnr-ecp5 (place & route) → Project Trellis/ecppack (bitstream packing)
3. Evaluated LiteX as the SoC builder framework — Python-based, 30+ CPU cores, modular peripheral ecosystem
4. Compared RISC-V soft CPU cores for MicroPython workloads: VexRiscv, PicoRV32, Minerva, SERV
5. Investigated existing MicroPython/CircuitPython FPGA projects: FuPy, Fomu, LiteX wiki guides
6. Explored hardware acceleration strategies: Custom Function Units (CFUs), PyXL bytecode execution, Amaranth HDL
7. Designed an agent workflow for fully automated bitstream generation from SoC configuration to DFU flashing

## Key Findings

### OrangeCrab Hardware
- Lattice ECP5 FPGA in two variants: 25F (24K LUTs) and 85F (84K LUTs, 156 multipliers)
- DDR3L memory: 128MB standard, 512MB extended — critical for MicroPython heap
- 128Mbit QSPI Flash with DFU bootloader pre-installed (first 4Mbit reserved)
- Feather form factor (22.86mm x 50.8mm) with 30 GPIO pins
- DFU bootloader creates a VexRiscv RISC-V CPU and loads firmware from Flash

### Open-Source Toolchain
- Fully open-source flow: no vendor tools or NDAs required
- Yosys handles synthesis with `synth_lattice` for ECP5-specific optimization
- nextpnr-ecp5 performs timing-driven place and route
- Project Trellis provides ECP5 bitstream format documentation; ecppack produces final binary
- YosysHQ oss-cad-suite provides pre-built binaries — simplest installation path

### LiteX Framework
- Python-based SoC builder generating complete systems from high-level descriptions
- OrangeCrab is a supported target in litex-boards (`gsd_orangecrab.py`)
- Integrates LiteDRAM (DDR3L controller), LiteEth, LiteSPI, and other peripherals
- Supports 30+ CPU cores; VexRiscv is the primary choice for MicroPython

### CPU Core Comparison
- **VexRiscv**: Best overall — configurable (18 variants), 0.52–1.21 DMIPS/MHz, MMU support, excellent LiteX integration. Recommended for MicroPython.
- **PicoRV32**: Smallest footprint (2.8K LUTs), but lower performance. Good for minimal designs.
- **Minerva**: Written in Amaranth (Python), 6-stage pipeline. Attractive for all-Python workflows.
- **SERV**: World's smallest RISC-V (610 cells). Too slow for MicroPython, but interesting for multi-core experiments.

### MicroPython/CircuitPython on FPGA
- LiteX wiki documents both MicroPython and CircuitPython ports running on LiteX SoCs
- FuPy project provides end-to-end Python workflow: Python gateware (Migen/LiteX) + Python firmware (MicroPython)
- Fomu (iCE40) is the most accessible reference — VexRiscv + MicroPython in USB form factor
- CircuitPython has an official LiteX port maintained by Adafruit

### Hardware Acceleration
- VexRiscv Custom Function Units (CFUs) allow adding custom hardware instructions to the CPU pipeline
- CFUs can accelerate bytecode dispatch, string operations, or math-heavy Python operations
- PyXL project demonstrated direct Python bytecode execution in FPGA hardware (Zynq-7000)
- Amaranth HDL enables writing accelerator logic in Python, keeping the full stack in one language

### Agent Workflow
- Fully automatable: toolchain install → LiteX SoC config → build (Yosys/nextpnr/ecppack) → firmware build → DFU flash
- All steps are CLI-driven with deterministic outputs
- Docker containerization possible for reproducible builds
- Build time: ~5–15 minutes depending on SoC complexity and ECP5 variant
