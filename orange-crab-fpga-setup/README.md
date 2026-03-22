# OrangeCrab FPGA: Agent Setup for MicroPython Bitstream Generation

<!-- AI-GENERATED-NOTE -->
> [!NOTE]
> This is an AI-generated research report. All text and code in this report was created by an LLM (Large Language Model). For more information on how these reports are created, see the [main research repository](https://github.com/simonw/research).
<!-- /AI-GENERATED-NOTE -->

## Overview

The **OrangeCrab** is a pocket-sized FPGA development board built around the Lattice ECP5 — one of the few FPGAs with a fully open-source synthesis, place-and-route, and bitstream generation toolchain. Combined with **LiteX** (a Python-based SoC builder) and **VexRiscv** (a configurable RISC-V CPU core), it enables a completely automated pipeline for generating bitstreams that run interpreted languages like MicroPython and CircuitPython.

This report covers the full stack — from hardware specs through toolchain setup to an automated agent workflow — with a focus on FPGA cores that accelerate interpreted language execution.

**Recommended stack:**
- **Board**: OrangeCrab r0.2.1 (ECP5-85F for headroom, or 25F for cost)
- **Toolchain**: YosysHQ oss-cad-suite (Yosys + nextpnr + ecppack)
- **SoC Builder**: LiteX with litex-boards OrangeCrab target
- **CPU Core**: VexRiscv (Full variant with MMU)
- **Runtime**: MicroPython or CircuitPython via LiteX port
- **Acceleration**: Custom Function Units (CFUs) for VexRiscv

---

## 1. OrangeCrab Board Overview

The OrangeCrab is an open-source FPGA board in the Adafruit Feather form factor (22.86mm × 50.8mm), designed by Greg Davill.

### Variants

| Feature | ECP5-25F | ECP5-85F |
|---------|----------|----------|
| Look-Up Tables (LUTs) | 24,000 | 84,000 |
| Embedded Block RAM | 1,008 Kb | 3,744 Kb |
| Distributed RAM | 194 Kb | 669 Kb |
| 18×18 Multipliers | 28 | 156 |
| PLLs | 2 | 4 |

### Common Features

- **DDR3L Memory**: 128MB (1Gbit) standard, 512MB (4Gbit) extended — 16-bit data width
- **Flash**: 128Mbit QSPI — first 4Mbit reserved for DFU bootloader, rest for user bitstream + firmware
- **USB**: USB Type-C with DFU bootloader for drag-and-drop programming
- **Clock**: 48MHz oscillator
- **I/O**: 30 Feather-compatible pins (GPIO, SPI, I2C, analog, 7 differential pairs)
- **Power**: USB 5V + LiPo battery header with charge controller

### DFU Bootloader

The board ships with a pre-installed DFU (Device Firmware Update) bootloader that:
1. Instantiates a VexRiscv RISC-V CPU inside the FPGA
2. Loads RISC-V firmware from QSPI Flash
3. Exposes a USB DFU interface for bitstream and firmware upload

This means out of the box, the OrangeCrab already runs a RISC-V soft core — the same architecture used for MicroPython.

---

## 2. Open-Source FPGA Toolchain

The ECP5 is fully supported by an open-source toolchain. No vendor tools, licenses, or NDAs are required.

### Toolchain Pipeline

```
Verilog/VHDL/Amaranth → [Yosys] → Netlist → [nextpnr-ecp5] → Layout → [ecppack] → Bitstream (.bit)
```

| Stage | Tool | Repository | Purpose |
|-------|------|-----------|---------|
| Synthesis | **Yosys** | [YosysHQ/yosys](https://github.com/YosysHQ/yosys) | Converts RTL (Verilog/VHDL) to ECP5 cells |
| Place & Route | **nextpnr-ecp5** | [YosysHQ/nextpnr](https://github.com/YosysHQ/nextpnr) | Maps logic cells onto FPGA fabric, routes interconnects |
| Bitstream | **ecppack** | [YosysHQ/prjtrellis](https://github.com/YosysHQ/prjtrellis) | Packs layout into binary bitstream for ECP5 |
| Database | **Project Trellis** | [YosysHQ/prjtrellis](https://github.com/YosysHQ/prjtrellis) | ECP5 architecture documentation and tile database |

### Installation

**Recommended: oss-cad-suite (pre-built binaries)**

```bash
# Download latest nightly for your platform
wget https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2026-03-22/oss-cad-suite-linux-x64-20260322.tgz
tar -xzf oss-cad-suite-linux-x64-20260322.tgz
export PATH="$PWD/oss-cad-suite/bin:$PATH"

# Verify
yosys --version
nextpnr-ecp5 --version
ecppack --version
```

**Alternative: Build from source**

```bash
# Yosys
git clone https://github.com/YosysHQ/yosys && cd yosys
make -j$(nproc) && sudo make install

# Project Trellis
git clone --recursive https://github.com/YosysHQ/prjtrellis && cd prjtrellis/libtrellis
cmake -DCMAKE_INSTALL_PREFIX=/usr/local . && make -j$(nproc) && sudo make install

# nextpnr
git clone https://github.com/YosysHQ/nextpnr && cd nextpnr
cmake -DARCH=ecp5 -DTRELLIS_INSTALL_PREFIX=/usr/local . && make -j$(nproc) && sudo make install
```

**Verify toolchain works:**

```bash
# Quick synthesis test
echo "module top(input clk, output led); assign led = clk; endmodule" > test.v
yosys -p "synth_ecp5 -json test.json" test.v
nextpnr-ecp5 --25k --json test.json --textcfg test.config
ecppack test.config test.bit
echo "Success: $(ls -la test.bit)"
```

---

## 3. LiteX SoC Framework

[LiteX](https://github.com/enjoy-digital/litex) is a Python-based framework for building FPGA System-on-Chips. Instead of writing Verilog, you define your SoC in Python — CPU, memory controller, peripherals, and bus interconnect — and LiteX generates the RTL, invokes the toolchain, and produces a ready-to-flash bitstream.

### Why LiteX?

- **Python-native**: SoC definition, build, and scripting all in Python
- **30+ CPU cores**: VexRiscv, PicoRV32, Minerva, SERV, Mor1kx, and more
- **Modular peripherals**: LiteDRAM (DDR), LiteEth (Ethernet), LiteSPI, LiteSDCard
- **50+ board targets**: Including OrangeCrab via `litex-boards`
- **MicroPython/CircuitPython support**: Documented integration path

### Installation

```bash
# Install LiteX
pip install meson ninja
mkdir litex && cd litex
wget https://raw.githubusercontent.com/enjoy-digital/litex/master/litex_setup.py
python3 litex_setup.py --init --install

# Install board definitions
pip install litex-boards

# Install RISC-V GCC toolchain (for firmware compilation)
python3 litex_setup.py --gcc=riscv
```

### OrangeCrab Target

The OrangeCrab is a first-class target in litex-boards:

```bash
# Build default SoC for OrangeCrab (VexRiscv + DDR3L + UART)
python3 -m litex_boards.targets.gsd_orangecrab \
    --device 85F \
    --sys-clk-freq 48e6 \
    --build
```

This single command:
1. Generates a VexRiscv CPU with DDR3L memory controller
2. Adds UART, Timer, and SPI Flash peripherals
3. Runs Yosys → nextpnr → ecppack
4. Outputs `build/gsd_orangecrab/gateware/gsd_orangecrab.bit`

---

## 4. CPU Core Comparison for MicroPython

MicroPython requires a CPU with enough performance and memory to run the bytecode interpreter. Here's how the main RISC-V soft cores compare on ECP5:

| Core | HDL Language | ISA | LUTs (approx.) | DMIPS/MHz | MMU | Cache | LiteX Support | MicroPython |
|------|-------------|-----|-----------------|-----------|-----|-------|---------------|-------------|
| **VexRiscv** | SpinalHDL | RV32IMAC(FD) | 3,000–8,000 | 0.52–1.21 | Optional | I$/D$ | Excellent | Proven |
| **PicoRV32** | Verilog | RV32IMC | 2,800 | ~0.3 | No | No | Good | Functional |
| **Minerva** | Amaranth | RV32IM | ~3,500 | ~0.5 | No | Optional | Good | Supported |
| **SERV** | Verilog | RV32I | 610 | Very low | No | No | Good | Too slow |

### Recommendation: VexRiscv (Full variant)

VexRiscv is the clear winner for MicroPython workloads:

- **Performance**: The "Full" variant delivers 1.21 DMIPS/MHz — enough for responsive MicroPython execution
- **MMU support**: Enables proper memory protection and larger heap management
- **Instruction/data caches**: Critical for DDR3L performance (high latency without caching)
- **Proven MicroPython path**: Used by Fomu, FuPy, and the LiteX wiki reference implementation
- **CFU support**: Custom Function Units can be added for hardware acceleration (see Section 7)
- **18 configurable variants**: Scale from minimal (0.52 DMIPS/MHz, ~3K LUTs) to Linux-capable

For the ECP5-25F (24K LUTs), VexRiscv Full uses ~30% of available logic, leaving room for peripherals and accelerators. On the 85F (84K LUTs), there's substantial headroom for custom logic.

---

## 5. Building a MicroPython-Capable SoC

### Step 1: Generate the SoC with LiteX

```bash
# Build SoC with VexRiscv Full + DDR3L + peripherals
python3 -m litex_boards.targets.gsd_orangecrab \
    --device 85F \
    --cpu-type vexriscv \
    --cpu-variant full \
    --sys-clk-freq 48e6 \
    --with-spi-flash \
    --build
```

This generates:
- `build/gsd_orangecrab/gateware/gsd_orangecrab.bit` — FPGA bitstream
- `build/gsd_orangecrab/software/include/` — CSR definitions for firmware
- `build/gsd_orangecrab/csr.json` — Machine-readable peripheral map

### Step 2: Build MicroPython Firmware

```bash
# Clone MicroPython
git clone https://github.com/micropython/micropython.git
cd micropython

# Build mpy-cross (bytecode compiler)
make -C mpy-cross

# Build for LiteX target
cd ports/litex
make BOARD=gsd_orangecrab \
     BUILD_DIR=../../build/gsd_orangecrab \
     CROSS_COMPILE=riscv64-unknown-elf-
```

The LiteX port of MicroPython reads the CSR definitions generated by LiteX to map hardware peripherals into Python-accessible objects.

### Step 3: Flash via DFU

```bash
# Install dfu-util
sudo apt install dfu-util

# Put OrangeCrab in DFU mode (press reset while holding button)

# Flash bitstream
dfu-util -d 1209:5af0 -a 0 -D build/gsd_orangecrab/gateware/gsd_orangecrab.bit

# Flash firmware
dfu-util -d 1209:5af0 -a 1 -D build/gsd_orangecrab/software/micropython.bin
```

### Memory Map

| Region | Address | Size | Purpose |
|--------|---------|------|---------|
| ROM | 0x00000000 | 32KB | Boot code |
| SRAM | 0x10000000 | 32KB | Fast scratchpad |
| DDR3L | 0x40000000 | 128MB+ | Main memory (MicroPython heap) |
| CSR | 0xF0000000 | — | Peripheral registers |
| SPI Flash | 0x20000000 | 16MB | XIP code + filesystem |

The DDR3L provides the large contiguous memory MicroPython needs for its heap, gc, and module loading.

---

## 6. CircuitPython on LiteX

CircuitPython (Adafruit's fork of MicroPython) has an official LiteX port:

- **Documentation**: [docs.circuitpython.org/en/latest/ports/litex/](https://docs.circuitpython.org/en/latest/ports/litex/README.html)
- **Build process**: Similar to MicroPython — generate SoC with LiteX, then cross-compile CircuitPython against the CSR definitions
- **Advantages over MicroPython**: Better USB support (native USB mass storage for code upload), broader hardware library ecosystem, Adafruit community support

```bash
# Clone CircuitPython
git clone https://github.com/adafruit/circuitpython.git
cd circuitpython
git submodule update --init --recursive

# Build for Fomu (reference LiteX target) — adapt for OrangeCrab
cd ports/litex
make BOARD=fomu
```

For OrangeCrab specifically, a custom board definition may be needed in `ports/litex/boards/` that references the OrangeCrab's CSR layout and pin mapping.

---

## 7. Hardware Acceleration Strategies

Running MicroPython on a soft CPU is functional but slow compared to dedicated microcontrollers. FPGAs offer a unique advantage: you can add custom hardware to accelerate interpreter hotspots.

### Custom Function Units (CFUs) for VexRiscv

CFUs are small hardware blocks that extend the VexRiscv CPU with custom instructions, accessible via RISC-V custom opcodes.

**How it works:**
1. Define a CFU in Verilog or Amaranth that implements a specific operation
2. Connect it to VexRiscv's pipeline via LiteX
3. Use custom RISC-V instructions (`custom0`, `custom1`) from C code
4. MicroPython's C runtime calls the accelerated operations

**Acceleration targets for MicroPython:**
- **Bytecode dispatch**: Hardware lookup table for opcode → handler mapping
- **String operations**: Hardware string comparison, hashing
- **Integer arithmetic**: Multi-precision math acceleration
- **GC marking**: Parallel bitmap scanning for garbage collection
- **Dictionary lookup**: Hardware hash table operations

**Reference**: The [CFU Playground](https://cfu-playground.readthedocs.io/) project provides a framework for developing and testing CFUs with VexRiscv on LiteX, including a complete build and test infrastructure.

```python
# Example: Adding a CFU to VexRiscv in LiteX
from litex.soc.cores.cpu.vexriscv import VexRiscv

class MyAcceleratedSoC(SoCCore):
    def __init__(self, platform, **kwargs):
        SoCCore.__init__(self, platform,
            cpu_type="vexriscv",
            cpu_variant="full+cfu",  # Enable CFU interface
            **kwargs)
        # CFU is connected via VexRiscv's plugin interface
```

### FuPy: Full-Stack Python FPGA Development

The [FuPy project](https://fupy.github.io/) takes a different approach — the entire stack from hardware to firmware is Python:

- **Gateware**: Written in Migen/LiteX (Python → Verilog → bitstream)
- **Firmware**: MicroPython running on the soft CPU
- **Workflow**: Single language for both hardware and software

FuPy is valuable as a reference architecture, though it hasn't been updated recently. The core concepts (LiteX gateware + MicroPython firmware) remain the standard approach.

### PyXL: Direct Bytecode Execution

The PyXL project demonstrated executing Python bytecode directly in FPGA hardware, bypassing the software interpreter entirely. While implemented on Zynq-7000 (not ECP5), the concept is portable:

- Custom CPU that natively executes Python bytecode opcodes
- Dynamic typing handled in hardware
- Stack operations mapped to hardware data paths

This is a more radical approach — instead of accelerating a C-based interpreter, it replaces the interpreter with dedicated hardware.

### Amaranth HDL for Accelerators

[Amaranth](https://github.com/amaranth-lang/amaranth) (formerly nMigen) lets you write hardware in Python, which is natural for a MicroPython acceleration project:

```python
from amaranth import *

class BytecodeDispatcher(Elaboratable):
    """Hardware bytecode dispatch unit — maps opcode to handler address."""
    def __init__(self):
        self.opcode = Signal(8)
        self.handler_addr = Signal(32)
        self.valid = Signal()

    def elaborate(self, platform):
        m = Module()
        # Hardware lookup table for Python bytecodes
        with m.Switch(self.opcode):
            with m.Case(0x64):  # LOAD_CONST
                m.d.comb += self.handler_addr.eq(0x1000)
            with m.Case(0x7C):  # LOAD_FAST
                m.d.comb += self.handler_addr.eq(0x1040)
            # ... more opcodes
        m.d.comb += self.valid.eq(1)
        return m
```

---

## 8. Agent Workflow for Automated Bitstream Generation

The entire process from SoC configuration to flashed firmware can be automated by an agent. Here is the step-by-step procedure:

### Phase 1: Environment Setup

```bash
# 1. Install oss-cad-suite (FPGA toolchain)
wget https://github.com/YosysHQ/oss-cad-suite-build/releases/latest/download/oss-cad-suite-linux-x64.tgz
tar -xzf oss-cad-suite-linux-x64.tgz
source oss-cad-suite/environment

# 2. Install LiteX
pip install meson ninja
wget https://raw.githubusercontent.com/enjoy-digital/litex/master/litex_setup.py
python3 litex_setup.py --init --install --user
python3 litex_setup.py --gcc=riscv

# 3. Install DFU utility
sudo apt install dfu-util

# 4. Verify
yosys --version && nextpnr-ecp5 --version && ecppack --version
riscv64-unknown-elf-gcc --version
```

### Phase 2: SoC Configuration

```bash
# Generate OrangeCrab SoC with MicroPython-suitable configuration
python3 -m litex_boards.targets.gsd_orangecrab \
    --device 85F \
    --cpu-type vexriscv \
    --cpu-variant full \
    --sys-clk-freq 48e6 \
    --with-spi-flash \
    --integrated-sram-size 32768 \
    --build
```

**Key parameters:**
- `--device 85F`: Use the larger ECP5 variant for more logic headroom
- `--cpu-variant full`: VexRiscv with caches, MMU, and good performance
- `--with-spi-flash`: Enable XIP (execute in place) from flash
- `--integrated-sram-size 32768`: 32KB fast SRAM for stack/critical data

### Phase 3: Firmware Build

```bash
# Clone and build MicroPython
git clone https://github.com/micropython/micropython.git
cd micropython
make -C mpy-cross
cd ports/litex

# Build with OrangeCrab's CSR definitions
make BOARD=gsd_orangecrab \
     BUILD_DIR=../../../build/gsd_orangecrab \
     CROSS_COMPILE=riscv64-unknown-elf-
```

### Phase 4: Flash and Test

```bash
# Flash bitstream (FPGA configuration)
dfu-util -d 1209:5af0 -a 0 -D build/gsd_orangecrab/gateware/gsd_orangecrab.bit

# Flash firmware (MicroPython binary)
dfu-util -d 1209:5af0 -a 1 -D micropython/ports/litex/build/firmware.bin

# Connect via serial console
picocom -b 115200 /dev/ttyACM0

# Test MicroPython
>>> import sys
>>> sys.platform
'litex'
>>> print("Hello from OrangeCrab!")
```

### Phase 5: Iterate with Acceleration (Optional)

```bash
# Add CFU to VexRiscv for bytecode acceleration
# 1. Write CFU in Verilog/Amaranth
# 2. Modify LiteX target to include CFU
# 3. Rebuild bitstream
python3 build_orangecrab_soc.py --with-cfu --build

# 4. Rebuild MicroPython with CFU-aware opcodes
make -C micropython/ports/litex BOARD=gsd_orangecrab CFU=1
```

### Agent Automation Summary

An automated agent can execute Phases 1–4 as a single pipeline:

```
[Install Toolchain] → [Configure SoC] → [Build Bitstream] → [Build Firmware] → [Package Artifacts]
                                                                                        ↓
                                                                            gsd_orangecrab.bit
                                                                            firmware.bin
                                                                            csr.json
```

The entire pipeline is deterministic and CLI-driven — no GUI interaction required. Build time is approximately 5–15 minutes depending on the ECP5 variant and SoC complexity.

---

## 9. Key Repositories and Resources

### Core Toolchain

| Repository | Description |
|-----------|-------------|
| [YosysHQ/oss-cad-suite-build](https://github.com/YosysHQ/oss-cad-suite-build) | Pre-built open-source FPGA toolchain |
| [YosysHQ/yosys](https://github.com/YosysHQ/yosys) | RTL synthesis framework |
| [YosysHQ/nextpnr](https://github.com/YosysHQ/nextpnr) | FPGA place and route |
| [YosysHQ/prjtrellis](https://github.com/YosysHQ/prjtrellis) | ECP5 bitstream tools and docs |

### SoC Framework

| Repository | Description |
|-----------|-------------|
| [enjoy-digital/litex](https://github.com/enjoy-digital/litex) | Python SoC builder |
| [litex-hub/litex-boards](https://github.com/litex-hub/litex-boards) | 50+ board targets (includes OrangeCrab) |
| [SpinalHDL/VexRiscv](https://github.com/SpinalHDL/VexRiscv) | Configurable RISC-V CPU |
| [enjoy-digital/litedram](https://github.com/enjoy-digital/litedram) | DDR3/DDR4 memory controller |

### OrangeCrab

| Repository | Description |
|-----------|-------------|
| [orangecrab-fpga/orangecrab-hardware](https://github.com/orangecrab-fpga/orangecrab-hardware) | Board design files and docs |
| [orangecrab-fpga/orangecrab-examples](https://github.com/orangecrab-fpga/orangecrab-examples) | Example designs (Verilog + LiteX) |

### MicroPython / CircuitPython

| Repository | Description |
|-----------|-------------|
| [micropython/micropython](https://github.com/micropython/micropython) | MicroPython (includes LiteX port) |
| [adafruit/circuitpython](https://github.com/adafruit/circuitpython) | CircuitPython (LiteX port available) |
| [fupy](https://github.com/fupy) | FuPy: Full-stack Python FPGA development |
| [LiteX Wiki: MicroPython](https://github.com/enjoy-digital/litex/wiki/Run-MicroPython-CircuitPython-On-Your-SoC) | Official integration guide |

### Hardware Acceleration

| Repository | Description |
|-----------|-------------|
| [google/CFU-Playground](https://github.com/google/CFU-Playground) | Custom Function Unit framework for VexRiscv |
| [amaranth-lang/amaranth](https://github.com/amaranth-lang/amaranth) | Python-based hardware description language |
| [litex-hub/linux-on-litex-vexriscv](https://github.com/litex-hub/linux-on-litex-vexriscv) | Linux on ECP5 (reference for complex SoCs) |

### Documentation

- [OrangeCrab Getting Started](https://orangecrab-fpga.github.io/orangecrab-hardware/)
- [LiteX Wiki](https://github.com/enjoy-digital/litex/wiki)
- [CFU Playground Docs](https://cfu-playground.readthedocs.io/)
- [Yosys Manual](https://yosyshq.readthedocs.io/)

---

## Summary

The OrangeCrab + open-source toolchain provides a fully automatable path to generating FPGA bitstreams with MicroPython-capable SoCs:

1. **No vendor lock-in**: The entire flow (Yosys → nextpnr → ecppack) is open-source
2. **Python all the way down**: LiteX defines the SoC in Python, MicroPython runs on it
3. **VexRiscv is the clear CPU choice**: Proven MicroPython support, configurable performance, CFU extensibility
4. **Hardware acceleration is practical**: CFUs let you add custom instructions to accelerate Python interpreter hotspots without replacing the entire runtime
5. **Fully CLI-driven**: Every step from toolchain install to DFU flashing is scriptable — ideal for agent automation

The recommended starting point is the LiteX OrangeCrab target with VexRiscv Full, building the standard MicroPython LiteX port. Once functional, CFUs can be incrementally added to accelerate specific Python operations based on profiling data.
