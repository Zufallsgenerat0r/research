#!/usr/bin/env python3
"""
Sample LiteX SoC build script for OrangeCrab with MicroPython support.

This script demonstrates how to configure a VexRiscv-based SoC on the
OrangeCrab FPGA board with peripherals suitable for running MicroPython.

Prerequisites:
    - oss-cad-suite or Yosys + nextpnr-ecp5 + ecppack installed
    - LiteX and litex-boards installed (pip install litex-boards)
    - RISC-V GCC toolchain (python3 litex_setup.py --gcc=riscv)

Usage:
    python3 build_orangecrab_soc.py --build
    python3 build_orangecrab_soc.py --build --device 25F
    python3 build_orangecrab_soc.py --build --with-spi-flash

Based on litex-boards/litex_boards/targets/gsd_orangecrab.py
"""

import os
import argparse

from migen import *

from litex.build.lattice import LatticeECP5Platform
from litex.soc.cores.clock import ECP5PLL
from litex.soc.cores.led import LedChaser
from litex.soc.cores.spi_flash import SpiFlash
from litex.soc.integration.soc_core import SoCCore, soc_core_args, soc_core_argdict
from litex.soc.integration.builder import Builder, builder_args, builder_argdict

from litex_boards.platforms import gsd_orangecrab


# -- Clock Domain Setup -------------------------------------------------------

class CRG(Module):
    """Clock/Reset Generator for OrangeCrab.

    Generates the system clock from the 48MHz oscillator using the ECP5 PLL.
    Also handles DDR3L clock domains if DRAM is enabled.
    """
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.clock_domains.cd_sys = ClockDomain()

        # PLL configuration
        self.submodules.pll = pll = ECP5PLL()
        self.comb += pll.reset.eq(self.rst)

        pll.register_clkin(platform.request("clk48"), 48e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)


# -- SoC Definition -----------------------------------------------------------

class OrangeCrabMicroPythonSoC(SoCCore):
    """OrangeCrab SoC configured for MicroPython execution.

    Features:
        - VexRiscv Full CPU (RV32IMAC with MMU, I$/D$)
        - DDR3L memory controller via LiteDRAM (128MB)
        - UART for serial console (MicroPython REPL)
        - SPI Flash for firmware and filesystem storage
        - Timer for MicroPython scheduling
        - LED for status indication
    """
    def __init__(self, platform, sys_clk_freq=48e6, device="85F",
                 with_spi_flash=False, **kwargs):

        # -- Clock/Reset --
        self.submodules.crg = CRG(platform, sys_clk_freq)

        # -- SoC Core --
        # VexRiscv "full" variant includes:
        #   - RV32IMAC ISA
        #   - MMU (memory management unit)
        #   - I-cache and D-cache
        #   - ~1.21 DMIPS/MHz performance
        SoCCore.__init__(self, platform, sys_clk_freq,
            cpu_type="vexriscv",
            cpu_variant="full",
            integrated_rom_size=0x8000,   # 32KB boot ROM
            integrated_sram_size=0x8000,  # 32KB fast SRAM
            **kwargs)

        # -- DDR3L Memory --
        # OrangeCrab has DDR3L (1.35V) with 16-bit data width.
        # LiteDRAM provides the memory controller.
        # For a full build, uncomment and configure:
        #
        # from litedram.modules import MT41K64M16
        # from litedram.phy import ECP5DDRPHY
        #
        # self.submodules.ddrphy = ECP5DDRPHY(
        #     platform.request("ddram"),
        #     sys_clk_freq=sys_clk_freq)
        # self.add_sdram("sdram",
        #     phy=self.ddrphy,
        #     module=MT41K64M16(sys_clk_freq, "1:2"),
        #     size=0x8000000)  # 128MB

        # -- SPI Flash (optional) --
        if with_spi_flash:
            self.submodules.spiflash = SpiFlash(
                platform.request("spiflash"),
                dummy=8,
                div=2,
                endianness="little")
            self.add_csr("spiflash")

        # -- LED --
        self.submodules.leds = LedChaser(
            pads=platform.request_all("user_led"),
            sys_clk_freq=sys_clk_freq)


# -- Build Flow ----------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Build OrangeCrab SoC for MicroPython")

    # Board options
    parser.add_argument("--device", default="85F", choices=["25F", "85F"],
                        help="ECP5 device variant (default: 85F)")
    parser.add_argument("--sys-clk-freq", default=48e6, type=float,
                        help="System clock frequency in Hz (default: 48MHz)")
    parser.add_argument("--with-spi-flash", action="store_true",
                        help="Enable SPI Flash peripheral")

    # LiteX standard arguments
    builder_args(parser)
    soc_core_args(parser)

    args = parser.parse_args()

    # Build platform
    platform = gsd_orangecrab.Platform(device=args.device, revision="0.2")

    # Build SoC
    soc = OrangeCrabMicroPythonSoC(
        platform,
        sys_clk_freq=int(args.sys_clk_freq),
        device=args.device,
        with_spi_flash=args.with_spi_flash,
        **soc_core_argdict(args))

    # Build
    builder = Builder(soc, **builder_argdict(args))
    builder.build()

    print("\n" + "="*60)
    print("Build complete!")
    print(f"  Bitstream: {builder.output_dir}/gateware/gsd_orangecrab.bit")
    print(f"  CSR map:   {builder.output_dir}/csr.json")
    print("="*60)
    print("\nFlash with:")
    print(f"  dfu-util -d 1209:5af0 -a 0 -D {builder.output_dir}/gateware/gsd_orangecrab.bit")


if __name__ == "__main__":
    main()
