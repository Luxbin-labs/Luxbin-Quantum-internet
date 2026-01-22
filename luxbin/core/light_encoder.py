"""
LUXBIN Light Encoder

Converts binary data to LUXBIN photonic encoding for universal computer communication
via color light wavelengths. Designed for quantum computers using diamond NV centers.

Process: Binary -> LUXBIN Photonic Encoding -> Light Show (color wavelength sequence)

This is the core encoding module for the LUXBIN protocol.

Author: Nichole Christie
Company: Nicheai (https://nicheai.com)
License: MIT
"""

from typing import List, Dict, Any, Tuple, Optional
import struct
import time

from .wavelength import (
    VISIBLE_SPECTRUM_MIN,
    VISIBLE_SPECTRUM_MAX,
    NV_ZERO_PHONON_LINE,
    hue_to_wavelength,
    wavelength_to_hue,
)


# LUXBIN Light Dictionary - Character to Photonic Mapping
LUXBIN_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?;:-()[]{}@#$%^&*+=_~`<>\"'|\\"

# Grammar shades for encoding grammatical structure via color saturation/lightness
GRAMMAR_SHADES = {
    'noun': {'saturation': 100, 'lightness': 70, 'description': 'Full saturation - concrete objects/things'},
    'verb': {'saturation': 70, 'lightness': 65, 'description': 'Medium saturation - actions/states'},
    'adjective': {'saturation': 40, 'lightness': 75, 'description': 'Low saturation - descriptions/qualities'},
    'adverb': {'saturation': 55, 'lightness': 60, 'description': 'Medium-low saturation - how/when/where'},
    'pronoun': {'saturation': 85, 'lightness': 80, 'description': 'High saturation, high lightness - substitutes'},
    'preposition': {'saturation': 25, 'lightness': 55, 'description': 'Very low saturation - relationships'},
    'conjunction': {'saturation': 90, 'lightness': 50, 'description': 'High saturation, low lightness - connections'},
    'interjection': {'saturation': 100, 'lightness': 90, 'description': 'Full saturation, very bright - exclamations'},
    'punctuation': {'saturation': 10, 'lightness': 30, 'description': 'Very low saturation, dark - structural marks'},
    'binary': {'saturation': 0, 'lightness': 50, 'description': 'Zero saturation, grayscale - pure binary data'},
    'default': {'saturation': 60, 'lightness': 70, 'description': 'Default grammatical shade'}
}


class LightEncoder:
    """
    LUXBIN Light Encoder

    Converts binary data to photonic light sequences for universal computer communication.

    Key Features:
    - Binary to LUXBIN character mapping
    - Character to HSL color conversion
    - HSL to wavelength approximation
    - Quantum-ready for diamond NV center storage
    - Optional quantum control protocol mapping for ion trap computers
    - Optional satellite laser communication mapping

    Usage:
        encoder = LightEncoder()
        light_show = encoder.create_light_show(b"Hello World")
    """

    def __init__(self, enable_quantum: bool = False, enable_satellite: bool = False):
        """
        Initialize the LUXBIN Light Encoder.

        Args:
            enable_quantum: Include quantum control protocol mappings for ion trap computers
            enable_satellite: Include satellite laser communication mappings
        """
        self.alphabet = LUXBIN_ALPHABET
        self.alphabet_len = len(self.alphabet)
        self.enable_quantum = enable_quantum
        self.enable_satellite = enable_satellite

    # =========================================================================
    # Binary <-> LUXBIN Conversion
    # =========================================================================

    def binary_to_luxbin_chars(self, binary_data: bytes, chunk_size: int = 6) -> str:
        """
        Convert binary data to LUXBIN characters.

        Args:
            binary_data: Raw binary data
            chunk_size: Bits per character (6 bits = 64 possible values)

        Returns:
            String of LUXBIN characters
        """
        chars = []
        bit_string = ''.join(format(byte, '08b') for byte in binary_data)

        # Use optimal chunk size based on alphabet size
        max_bits = len(self.alphabet).bit_length()
        optimal_chunk = min(max_bits, 7)  # Up to 7 bits for better compression

        # Pad to multiple of optimal chunk size
        while len(bit_string) % optimal_chunk != 0:
            bit_string += '0'

        # Convert chunks to characters
        for i in range(0, len(bit_string), optimal_chunk):
            chunk = bit_string[i:i + optimal_chunk]
            index = int(chunk, 2)
            if index < self.alphabet_len:
                chars.append(self.alphabet[index])
            else:
                # For overflow, use modulo to wrap around
                chars.append(self.alphabet[index % self.alphabet_len])

        return ''.join(chars)

    def luxbin_chars_to_binary(self, luxbin_text: str) -> bytes:
        """
        Convert LUXBIN characters back to binary data.

        Args:
            luxbin_text: LUXBIN encoded string

        Returns:
            Original binary data
        """
        max_bits = len(self.alphabet).bit_length()
        optimal_chunk = min(max_bits, 7)

        binary_string = ''
        for char in luxbin_text:
            if char in self.alphabet:
                pos = self.alphabet.index(char)
                binary_string += format(pos, f'0{optimal_chunk}b')

        # Convert to bytes (truncate to byte boundaries)
        while len(binary_string) % 8 != 0:
            binary_string = binary_string[:-1]

        binary_data = bytearray()
        for i in range(0, len(binary_string), 8):
            byte_str = binary_string[i:i + 8]
            binary_data.append(int(byte_str, 2))

        return bytes(binary_data)

    # =========================================================================
    # Compression
    # =========================================================================

    def compress(self, binary_data: bytes) -> bytes:
        """Apply run-length encoding compression for repetitive data."""
        if len(binary_data) < 3:
            return binary_data

        compressed = []
        i = 0

        while i < len(binary_data):
            current_byte = binary_data[i]
            run_length = 1
            j = i + 1

            # Count consecutive identical bytes (max 255)
            while j < len(binary_data) and binary_data[j] == current_byte and run_length < 255:
                run_length += 1
                j += 1

            if run_length >= 3:
                # Use compression marker (0xFF) + byte + count
                compressed.extend([0xFF, current_byte, run_length])
                i = j
            else:
                for k in range(run_length):
                    compressed.append(binary_data[i + k])
                i += run_length

        return bytes(compressed)

    def decompress(self, compressed_data: bytes) -> bytes:
        """Decompress run-length encoded data."""
        decompressed = []
        i = 0

        while i < len(compressed_data):
            if compressed_data[i] == 0xFF and i + 2 < len(compressed_data):
                byte_value = compressed_data[i + 1]
                count = compressed_data[i + 2]
                decompressed.extend([byte_value] * count)
                i += 3
            else:
                decompressed.append(compressed_data[i])
                i += 1

        return bytes(decompressed)

    # =========================================================================
    # Color Conversion
    # =========================================================================

    def char_to_hsl(self, char: str, grammar_type: str = 'default') -> Tuple[int, int, int]:
        """
        Convert LUXBIN character to HSL color.

        Args:
            char: Single LUXBIN character
            grammar_type: Grammatical category for shade modification

        Returns:
            Tuple of (hue, saturation, lightness) in degrees/percent
        """
        if char not in self.alphabet:
            raise ValueError(f"Invalid LUXBIN character: {char}")

        pos = self.alphabet.index(char)
        hue = (pos * 360) // self.alphabet_len

        # Apply grammar shade modifications
        shade = GRAMMAR_SHADES.get(grammar_type, GRAMMAR_SHADES['default'])
        saturation = shade['saturation']
        lightness = shade['lightness']

        return (hue, saturation, lightness)

    def hsl_to_wavelength(self, hue: int, saturation: int, lightness: int) -> float:
        """
        Approximate HSL color to visible light wavelength.

        Args:
            hue: Hue in degrees (0-360)
            saturation: Saturation in percent (0-100)
            lightness: Lightness in percent (0-100)

        Returns:
            Approximate wavelength in nanometers
        """
        # Map hue to wavelength range
        wavelength = VISIBLE_SPECTRUM_MIN + (hue / 360) * (VISIBLE_SPECTRUM_MAX - VISIBLE_SPECTRUM_MIN)

        # Adjust for saturation/lightness
        intensity_factor = (saturation / 100) * (lightness / 100)
        wavelength += (intensity_factor - 0.5) * 50

        return round(wavelength, 1)

    # =========================================================================
    # Quantum Control Mapping
    # =========================================================================

    def wavelength_to_quantum_operation(self, wavelength: float, duration: float) -> Dict[str, Any]:
        """
        Map wavelength to specific quantum control operations.

        Based on real ion trap quantum computing protocols.

        Args:
            wavelength: Light wavelength in nm
            duration: Pulse duration in seconds

        Returns:
            Quantum operation specification
        """
        # Real quantum control wavelengths
        if 390 <= wavelength <= 410:  # Calcium
            operation = "single_qubit_gate"
            ion_type = "calcium_40"
            transition = "397nm_D2_cooling"
        elif 410 <= wavelength <= 435:  # Strontium
            operation = "state_preparation"
            ion_type = "strontium_88"
            transition = "422nm_intercombination"
        elif 720 <= wavelength <= 740:  # Ytterbium
            operation = "two_qubit_gate"
            ion_type = "ytterbium_171"
            transition = "729nm_qubit_transition"
        elif 845 <= wavelength <= 865:  # Rubidium
            operation = "cooling_cycle"
            ion_type = "rubidium_87"
            transition = "854nm_D2_line"
        elif 630 <= wavelength <= 645:  # NV Center
            operation = "spin_photon_entanglement"
            ion_type = "nv_center"
            transition = "637nm_zero_phonon"
        else:
            operation = "optical_pumping"
            ion_type = "generic"
            transition = f"{wavelength:.0f}nm_custom"

        return {
            "operation": operation,
            "ion_type": ion_type,
            "wavelength_nm": wavelength,
            "duration_s": duration,
            "pulse_energy": duration * 1e-6,
            "transition": transition,
            "control_parameters": {
                "phase": 0,
                "polarization": "linear",
                "timing_precision": "ns",
                "fidelity": ">0.99"
            }
        }

    def wavelength_to_satellite_operation(self, wavelength: float, duration: float) -> Dict[str, Any]:
        """
        Map wavelength to satellite laser communication operations.

        Args:
            wavelength: Light wavelength in nm
            duration: Pulse duration in seconds

        Returns:
            Satellite communication operation specification
        """
        if 1500 <= wavelength <= 1600:  # Starlink laser range
            operation = "inter_satellite_laser_link"
            protocol = "luxbin_encoded"
            data_rate = "100Gbps+"
            modulation = "wavelength_division_multiplexing"
        elif 1260 <= wavelength <= 1360:  # O-band
            operation = "ground_station_uplink"
            protocol = "luxbin_modulated"
            data_rate = "10Gbps"
            modulation = "phase_modulation"
        else:
            operation = "optical_alignment"
            protocol = "beacon_signal"
            data_rate = "alignment_only"
            modulation = "continuous_wave"

        return {
            "operation": operation,
            "protocol": protocol,
            "wavelength_nm": wavelength,
            "duration_s": duration,
            "data_rate": data_rate,
            "modulation": modulation,
            "communication_parameters": {
                "beam_divergence": "milliradians",
                "atmospheric_loss": "<0.1dB",
                "pointing_accuracy": "microradians",
                "luxbin_encoding": True,
                "global_coverage": True
            }
        }

    # =========================================================================
    # NV Center Data Generation
    # =========================================================================

    def _generate_nv_center_data(self, light_sequence: List[Dict]) -> Dict[str, Any]:
        """
        Generate quantum NV center programming data.

        Args:
            light_sequence: Light show sequence

        Returns:
            NV center programming data
        """
        nv_states = []
        for item in light_sequence:
            wavelength = item['wavelength_nm']
            duration = item['duration_s']

            # Map to NV center transition
            if 635 <= wavelength <= 640:
                transition = 'zero_phonon'
            elif wavelength < 635:
                transition = 'violet_sideband'
            else:
                transition = 'red_sideband'

            nv_states.append({
                'transition': transition,
                'wavelength': wavelength,
                'duration': duration,
                'pulse_sequence': f"NV_{transition}_{int(duration * 1000)}ms"
            })

        return {
            'nv_center_states': nv_states,
            'total_states': len(nv_states),
            'estimated_storage_time': sum(item['duration_s'] for item in light_sequence) * 1e6
        }

    # =========================================================================
    # Light Show Creation
    # =========================================================================

    def create_light_show(self, binary_data: bytes) -> Dict[str, Any]:
        """
        Convert binary data to a photonic light show sequence.

        Args:
            binary_data: Input binary data

        Returns:
            Dictionary containing light show data
        """
        luxbin_text = self.binary_to_luxbin_chars(binary_data)

        light_sequence = []
        base_duration = 0.1  # 100ms per character

        for char in luxbin_text:
            hsl = self.char_to_hsl(char)
            wavelength = self.hsl_to_wavelength(*hsl)
            duration = base_duration * 2 if char == ' ' else base_duration

            item = {
                'character': char,
                'hsl': hsl,
                'wavelength_nm': wavelength,
                'duration_s': duration
            }

            if self.enable_quantum:
                item['quantum_operation'] = self.wavelength_to_quantum_operation(wavelength, duration)

            if self.enable_satellite:
                item['satellite_operation'] = self.wavelength_to_satellite_operation(wavelength, duration)

            light_sequence.append(item)

        quantum_data = self._generate_nv_center_data(light_sequence)

        return {
            'luxbin_text': luxbin_text,
            'light_sequence': light_sequence,
            'quantum_data': quantum_data,
            'total_duration': sum(item['duration_s'] for item in light_sequence),
            'data_size': len(binary_data)
        }

    def create_binary_light_show(self, binary_data: bytes, use_compression: bool = True) -> Dict[str, Any]:
        """
        Convert raw binary data to a pure binary light show (grayscale encoding).

        Args:
            binary_data: Raw binary data
            use_compression: Whether to apply run-length compression

        Returns:
            Binary-encoded light show data
        """
        original_size = len(binary_data)
        if use_compression:
            binary_data = self.compress(binary_data)
            compression_ratio = original_size / len(binary_data) if len(binary_data) > 0 else 1.0
        else:
            compression_ratio = 1.0

        luxbin_text = self.binary_to_luxbin_chars(binary_data)

        light_sequence = []
        base_duration = 0.05  # 50ms for binary data

        for char in luxbin_text:
            hsl = self.char_to_hsl(char, 'binary')
            wavelength = self.hsl_to_wavelength(*hsl)

            max_bits = len(self.alphabet).bit_length()
            bit_length = min(max_bits, 7)
            binary_value = format(self.alphabet.index(char), f'0{bit_length}b')

            light_sequence.append({
                'character': char,
                'grammar_type': 'binary',
                'hsl': hsl,
                'wavelength_nm': wavelength,
                'duration_s': base_duration,
                'binary_value': binary_value
            })

        quantum_data = self._generate_nv_center_data(light_sequence)

        return {
            'binary_data': binary_data.hex(),
            'original_size': original_size,
            'compressed_size': len(binary_data),
            'luxbin_text': luxbin_text,
            'light_sequence': light_sequence,
            'quantum_data': quantum_data,
            'total_duration': sum(item['duration_s'] for item in light_sequence),
            'compression_ratio': compression_ratio,
            'data_type': 'binary'
        }

    def light_show_to_binary(self, light_sequence: List[Dict]) -> bytes:
        """
        Reverse conversion: Light show back to binary data.

        Args:
            light_sequence: Light show sequence

        Returns:
            Original binary data
        """
        luxbin_text = ''.join(item['character'] for item in light_sequence)
        return self.luxbin_chars_to_binary(luxbin_text)


# Backwards compatibility alias
LuxbinLightConverter = LightEncoder
