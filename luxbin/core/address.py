"""
LUXBIN Address System

Quantum internet addressing scheme with content-addressable routing.

Address Format:
    luxbin://[node_id].[wavelength].[hash]/[resource]

Examples:
    luxbin://ibm_fez.637nm.A3F9D2/webpage
    luxbin://distributed.400-700nm.B8C4E1/file.txt
    luxbin://mywebsite.550nm.XYZ123/index.html

Features:
- Content-addressable (hash-based)
- Wavelength-based routing hints
- Human-readable names (via blockchain DNS)
- Quantum-native addressing
"""

import re
import hashlib
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

from .light_encoder import LightEncoder
from .wavelength import VISIBLE_SPECTRUM_MIN, VISIBLE_SPECTRUM_MAX


@dataclass
class LuxbinAddressComponents:
    """Parsed LUXBIN address components"""
    node_id: str
    wavelength: str  # e.g., "637nm" or "400-700nm"
    content_hash: str
    resource: str
    full_address: str

    def __str__(self):
        return self.full_address

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'node_id': self.node_id,
            'wavelength': self.wavelength,
            'content_hash': self.content_hash,
            'resource': self.resource,
            'full_address': self.full_address
        }


class LuxbinAddress:
    """
    LUXBIN address parser and generator.

    Handles quantum internet addresses with:
    - Node identification
    - Wavelength-based routing
    - Content-addressable hashing
    - Resource location
    """

    # Address pattern: luxbin://node_id.wavelength.hash/resource
    ADDRESS_PATTERN = re.compile(
        r'^luxbin://([^.]+)\.([^.]+)\.([^/]+)(?:/(.+))?$'
    )

    def __init__(self):
        self._encoder = LightEncoder()

    @classmethod
    def parse(cls, address: str) -> Optional[LuxbinAddressComponents]:
        """
        Parse LUXBIN address into components.

        Args:
            address: LUXBIN URL string

        Returns:
            LuxbinAddressComponents or None if invalid

        Example:
            >>> addr = LuxbinAddress.parse("luxbin://ibm_fez.637nm.ABC123/page.html")
            >>> addr.node_id
            'ibm_fez'
        """
        if not address:
            return None

        match = cls.ADDRESS_PATTERN.match(address)
        if not match:
            return None

        node_id, wavelength, content_hash, resource = match.groups()
        resource = resource or "/"

        return LuxbinAddressComponents(
            node_id=node_id,
            wavelength=wavelength,
            content_hash=content_hash,
            resource=resource,
            full_address=address
        )

    @classmethod
    def create(
        cls,
        node_id: str,
        content: bytes,
        resource: str = "/",
        wavelength: Optional[float] = None
    ) -> str:
        """
        Create LUXBIN address for content.

        Args:
            node_id: Node identifier
            content: Content to address (bytes)
            resource: Resource path (default: "/")
            wavelength: Preferred wavelength in nm (default: auto-detect)

        Returns:
            Full LUXBIN address string
        """
        content_hash = cls.luxbin_hash(content)

        if wavelength is None:
            wavelength = cls._infer_wavelength_from_content(content)

        wavelength_str = f"{int(wavelength)}nm"
        address = f"luxbin://{node_id}.{wavelength_str}.{content_hash}"

        if resource and resource != "/":
            resource = resource.lstrip("/")
            address += f"/{resource}"

        return address

    @classmethod
    def create_name_address(
        cls,
        name: str,
        content: bytes,
        wavelength: Optional[float] = None
    ) -> str:
        """
        Create human-readable named address.

        Args:
            name: Human-readable name (e.g., "mywebsite")
            content: Content to address
            wavelength: Preferred wavelength

        Returns:
            Named LUXBIN address
        """
        return cls.create(node_id=name, content=content, wavelength=wavelength)

    @classmethod
    def luxbin_hash(cls, content: bytes, length: int = 6) -> str:
        """
        Generate LUXBIN hash of content.

        Uses LUXBIN encoding for quantum-native hashing.

        Args:
            content: Content to hash
            length: Hash length in LUXBIN characters (default: 6)

        Returns:
            LUXBIN hash string
        """
        sha_hash = hashlib.sha256(content).digest()
        encoder = LightEncoder()
        luxbin = encoder.binary_to_luxbin_chars(sha_hash, chunk_size=6)
        return luxbin[:length].upper()

    @classmethod
    def _infer_wavelength_from_content(cls, content: bytes) -> float:
        """
        Infer optimal wavelength for content based on hash.

        Args:
            content: Content bytes

        Returns:
            Wavelength in nm (400-700nm range)
        """
        content_hash = hashlib.sha256(content).digest()
        hash_value = content_hash[0]
        wavelength = VISIBLE_SPECTRUM_MIN + (hash_value / 255) * (VISIBLE_SPECTRUM_MAX - VISIBLE_SPECTRUM_MIN)
        return round(wavelength)

    @classmethod
    def validate(cls, address: str) -> Tuple[bool, Optional[str]]:
        """
        Validate LUXBIN address.

        Args:
            address: Address to validate

        Returns:
            (is_valid, error_message)
        """
        if not address:
            return False, "Address is empty"

        if not address.startswith("luxbin://"):
            return False, "Invalid protocol: expected 'luxbin://'"

        components = cls.parse(address)
        if not components:
            return False, "Invalid address format"

        if not components.node_id:
            return False, "Missing node_id"

        if not components.wavelength:
            return False, "Missing wavelength"

        if not components.content_hash:
            return False, "Missing content_hash"

        if not cls._validate_wavelength(components.wavelength):
            return False, f"Invalid wavelength format: {components.wavelength}"

        return True, None

    @classmethod
    def _validate_wavelength(cls, wavelength_str: str) -> bool:
        """Validate wavelength format (e.g., '550nm' or '400-700nm')"""
        # Single wavelength pattern
        single_pattern = re.compile(r'^(\d{3})nm$')
        match = single_pattern.match(wavelength_str)
        if match:
            wavelength = int(match.group(1))
            return 400 <= wavelength <= 700

        # Range pattern
        range_pattern = re.compile(r'^(\d{3})-(\d{3})nm$')
        match = range_pattern.match(wavelength_str)
        if match:
            min_wl = int(match.group(1))
            max_wl = int(match.group(2))
            return 400 <= min_wl <= max_wl <= 700

        return False

    @classmethod
    def extract_wavelength(cls, address: str) -> Optional[float]:
        """
        Extract wavelength value from address.

        Args:
            address: LUXBIN address

        Returns:
            Wavelength in nm (or midpoint of range)
        """
        components = cls.parse(address)
        if not components:
            return None

        wavelength_str = components.wavelength

        if '-' not in wavelength_str:
            return float(wavelength_str.replace('nm', ''))

        # Range: return midpoint
        parts = wavelength_str.replace('nm', '').split('-')
        return (float(parts[0]) + float(parts[1])) / 2

    @classmethod
    def is_compatible_wavelength(
        cls,
        address: str,
        node_wavelength_range: Tuple[float, float],
        tolerance: float = 50
    ) -> bool:
        """
        Check if address wavelength is compatible with node's range.

        Args:
            address: LUXBIN address
            node_wavelength_range: Node's wavelength specialization (min, max)
            tolerance: Acceptable deviation in nm

        Returns:
            True if compatible
        """
        addr_wavelength = cls.extract_wavelength(address)
        if addr_wavelength is None:
            return False

        min_wl, max_wl = node_wavelength_range
        return (min_wl - tolerance) <= addr_wavelength <= (max_wl + tolerance)


# Backwards compatibility alias
LUXBINAddress = LuxbinAddress
LUXBINAddressComponents = LuxbinAddressComponents
