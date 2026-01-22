"""
LUXBIN Core Module

Foundation components for the LUXBIN Quantum Internet protocol.
"""

from .light_encoder import LightEncoder, LuxbinLightConverter, LUXBIN_ALPHABET, GRAMMAR_SHADES
from .wavelength import (
    WavelengthRegion,
    QuantumWavelength,
    NV_ZERO_PHONON_LINE,
    NV_OPTICAL_PUMP,
    VISIBLE_SPECTRUM_MIN,
    VISIBLE_SPECTRUM_MAX,
    wavelength_to_region,
    wavelength_range_for_region,
    is_nv_compatible,
    hue_to_wavelength,
    wavelength_to_hue,
)
from .address import LuxbinAddress, LuxbinAddressComponents
from .config import LuxbinConfig, get_config, reload_config

__all__ = [
    # Light Encoder
    "LightEncoder",
    "LuxbinLightConverter",
    "LUXBIN_ALPHABET",
    "GRAMMAR_SHADES",
    # Wavelength
    "WavelengthRegion",
    "QuantumWavelength",
    "NV_ZERO_PHONON_LINE",
    "NV_OPTICAL_PUMP",
    "VISIBLE_SPECTRUM_MIN",
    "VISIBLE_SPECTRUM_MAX",
    "wavelength_to_region",
    "wavelength_range_for_region",
    "is_nv_compatible",
    "hue_to_wavelength",
    "wavelength_to_hue",
    # Address
    "LuxbinAddress",
    "LuxbinAddressComponents",
    # Config
    "LuxbinConfig",
    "get_config",
    "reload_config",
]
