"""
LUXBIN Wavelength Constants

Core wavelength definitions for photonic quantum operations.
These are the foundational physical constants for the LUXBIN protocol.

Key wavelengths:
- 637nm: NV Center zero-phonon line (primary entanglement wavelength)
- 532nm: NV Center optical pumping
- Visible spectrum: 400-700nm for LUXBIN encoding
"""

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class WavelengthRegion(Enum):
    """Visible spectrum regions for LUXBIN routing"""
    VIOLET = (380, 450)
    BLUE = (450, 500)
    GREEN = (500, 570)
    YELLOW = (570, 590)
    ORANGE = (590, 620)
    RED = (620, 700)

    @property
    def min_nm(self) -> int:
        return self.value[0]

    @property
    def max_nm(self) -> int:
        return self.value[1]

    @property
    def center_nm(self) -> float:
        return (self.value[0] + self.value[1]) / 2

    @classmethod
    def from_wavelength(cls, wavelength_nm: float) -> 'WavelengthRegion':
        """Get region from wavelength in nm"""
        for region in cls:
            if region.min_nm <= wavelength_nm < region.max_nm:
                return region
        # Default to closest region
        if wavelength_nm < 380:
            return cls.VIOLET
        return cls.RED


@dataclass(frozen=True)
class QuantumWavelength:
    """Physical wavelength specification for quantum operations"""
    wavelength_nm: float
    name: str
    description: str
    transition_type: str

    @property
    def frequency_thz(self) -> float:
        """Convert to frequency in THz (c = lambda * f)"""
        c = 299792458  # m/s
        return c / (self.wavelength_nm * 1e-9) / 1e12

    @property
    def energy_ev(self) -> float:
        """Photon energy in electron volts (E = hf)"""
        h = 4.135667696e-15  # eV*s
        return h * self.frequency_thz * 1e12


# =============================================================================
# NV Center Wavelengths (Primary LUXBIN-EIP-001 wavelengths)
# =============================================================================

NV_ZERO_PHONON_LINE = QuantumWavelength(
    wavelength_nm=637.0,
    name="NV_ZPL",
    description="NV Center zero-phonon line - primary entanglement wavelength",
    transition_type="spin_photon_entanglement"
)

NV_OPTICAL_PUMP = QuantumWavelength(
    wavelength_nm=532.0,
    name="NV_PUMP",
    description="NV Center optical pumping wavelength (green laser)",
    transition_type="spin_initialization"
)

NV_PHONON_SIDEBAND_MIN = QuantumWavelength(
    wavelength_nm=650.0,
    name="NV_PSB_MIN",
    description="NV Center phonon sideband lower bound",
    transition_type="phonon_assisted"
)

NV_PHONON_SIDEBAND_MAX = QuantumWavelength(
    wavelength_nm=800.0,
    name="NV_PSB_MAX",
    description="NV Center phonon sideband upper bound",
    transition_type="phonon_assisted"
)


# =============================================================================
# Ion Trap Wavelengths (for provider compatibility)
# =============================================================================

CALCIUM_40_D2 = QuantumWavelength(
    wavelength_nm=397.0,
    name="Ca40_D2",
    description="Calcium-40 D2 line - ion trapping/cooling",
    transition_type="cooling"
)

STRONTIUM_88 = QuantumWavelength(
    wavelength_nm=422.0,
    name="Sr88",
    description="Strontium-88 intercombination line",
    transition_type="state_preparation"
)

YTTERBIUM_171 = QuantumWavelength(
    wavelength_nm=729.0,
    name="Yb171",
    description="Ytterbium-171 qubit transition",
    transition_type="two_qubit_gate"
)

RUBIDIUM_87_D2 = QuantumWavelength(
    wavelength_nm=854.0,
    name="Rb87_D2",
    description="Rubidium-87 D2 line",
    transition_type="cooling"
)


# =============================================================================
# LUXBIN Encoding Constants
# =============================================================================

# Visible spectrum range for LUXBIN encoding
VISIBLE_SPECTRUM_MIN = 400  # nm (violet)
VISIBLE_SPECTRUM_MAX = 700  # nm (red)

# Network wavelength regions for routing
NETWORK_REGIONS = {
    "blue": (400, 500),   # Blue region nodes
    "green": (500, 600),  # Green region nodes
    "red": (600, 700),    # Red region nodes
}


def wavelength_to_region(wavelength_nm: float) -> str:
    """Map wavelength to network routing region"""
    if wavelength_nm < 500:
        return "blue"
    elif wavelength_nm < 600:
        return "green"
    else:
        return "red"


def wavelength_range_for_region(region: str) -> Tuple[int, int]:
    """Get wavelength range for a network region"""
    return NETWORK_REGIONS.get(region, (400, 700))


def is_nv_compatible(wavelength_nm: float, tolerance_nm: float = 5.0) -> bool:
    """Check if wavelength is compatible with NV center operations"""
    return abs(wavelength_nm - NV_ZERO_PHONON_LINE.wavelength_nm) <= tolerance_nm


def hue_to_wavelength(hue_degrees: int) -> float:
    """
    Convert HSL hue (0-360) to approximate wavelength (400-700nm)

    Note: This is a simplified mapping. Real CIE color matching is more complex.
    """
    # Normalize hue to 0-1
    normalized = hue_degrees / 360.0
    # Map to visible spectrum
    return VISIBLE_SPECTRUM_MIN + normalized * (VISIBLE_SPECTRUM_MAX - VISIBLE_SPECTRUM_MIN)


def wavelength_to_hue(wavelength_nm: float) -> int:
    """Convert wavelength (nm) to approximate HSL hue (0-360)"""
    # Clamp to visible spectrum
    wavelength_nm = max(VISIBLE_SPECTRUM_MIN, min(VISIBLE_SPECTRUM_MAX, wavelength_nm))
    # Normalize to 0-1
    normalized = (wavelength_nm - VISIBLE_SPECTRUM_MIN) / (VISIBLE_SPECTRUM_MAX - VISIBLE_SPECTRUM_MIN)
    return int(normalized * 360)


# All quantum wavelengths for reference
ALL_QUANTUM_WAVELENGTHS = [
    NV_ZERO_PHONON_LINE,
    NV_OPTICAL_PUMP,
    CALCIUM_40_D2,
    STRONTIUM_88,
    YTTERBIUM_171,
    RUBIDIUM_87_D2,
]
