"""
LUXBIN GHZ State Generator

Creates Greenberger-Horne-Zeilinger (GHZ) states for distributed
quantum entanglement across multiple nodes.

GHZ State: |GHZ_n⟩ = (|0...0⟩ + |1...1⟩)/√2

GHZ states are maximally entangled states that form the foundation
of distributed quantum computing and quantum internet protocols.
"""

import asyncio
import time
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional

from ..providers.base import QuantumCircuitWrapper, QuantumProvider

from ...core.wavelength import (
    NV_ZERO_PHONON_LINE,
    wavelength_to_region,
)


@dataclass
class GHZResult:
    """Result from GHZ state creation"""
    num_qubits: int
    counts: Dict[str, int]
    entanglement_measure: float
    success: bool
    backend: str
    shots: int
    execution_time_s: float
    job_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def unique_states(self) -> int:
        return len(self.counts)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'num_qubits': self.num_qubits,
            'counts': self.counts,
            'entanglement_measure': self.entanglement_measure,
            'success': self.success,
            'unique_states': self.unique_states,
            'backend': self.backend,
            'job_id': self.job_id,
        }


class GHZStateGenerator:
    """
    Creates GHZ states for distributed quantum entanglement.

    GHZ states enable:
    - Multi-party quantum communication
    - Distributed quantum computing
    - Quantum secret sharing
    - Network-wide entanglement verification

    Usage:
        generator = GHZStateGenerator(provider)
        result = await generator.create_ghz_state(num_qubits=5)
    """

    def __init__(self, provider: Optional[QuantumProvider] = None):
        self.provider = provider
        self.history: List[GHZResult] = []

    def create_ghz_circuit(
        self,
        num_qubits: int,
        add_phase_gates: bool = True,
    ) -> QuantumCircuitWrapper:
        """
        Create a circuit that generates an n-qubit GHZ state.

        Args:
            num_qubits: Number of qubits in GHZ state
            add_phase_gates: Add T gates for quantum interference

        Returns:
            Circuit for GHZ state preparation
        """
        circuit = QuantumCircuitWrapper(num_qubits, num_qubits)

        # Hadamard on first qubit
        circuit.h(0)

        # CNOT cascade to entangle all qubits
        for i in range(num_qubits - 1):
            circuit.cx(i, i + 1)

        # Optional phase gates for interference patterns
        if add_phase_gates:
            for i in range(num_qubits):
                circuit.t(i)

        # Measure all qubits
        circuit.measure_all()

        return circuit

    def create_luxbin_ghz_circuit(
        self,
        wavelengths: List[Dict[str, float]],
        num_qubits: int,
    ) -> QuantumCircuitWrapper:
        """
        Create LUXBIN-encoded GHZ circuit with wavelength-based rotations.

        Encodes LUXBIN wavelength data into the GHZ state phases.

        Args:
            wavelengths: List of wavelength dicts with 'wavelength_nm' key
            num_qubits: Number of qubits

        Returns:
            LUXBIN-encoded GHZ circuit
        """
        circuit = QuantumCircuitWrapper(num_qubits, num_qubits)

        # Encode first wavelength
        if wavelengths:
            wavelength = wavelengths[0].get('wavelength_nm', NV_ZERO_PHONON_LINE.wavelength_nm)
            theta, phi = self._wavelength_to_angles(wavelength)
            circuit.h(0)
            circuit.ry(theta, 0)
            circuit.rz(phi, 0)
        else:
            circuit.h(0)

        # Create GHZ entanglement
        for i in range(num_qubits - 1):
            circuit.cx(i, i + 1)

        # Encode additional wavelengths
        for i in range(1, min(num_qubits, len(wavelengths))):
            wavelength = wavelengths[i].get('wavelength_nm', 550)
            theta, phi = self._wavelength_to_angles(wavelength)
            circuit.ry(theta, i)
            circuit.rz(phi, i)

        # Reverse entanglement for stronger correlations
        for i in range(num_qubits - 1):
            circuit.cx(num_qubits - 1 - i, num_qubits - 2 - i)

        # Phase gates
        for i in range(num_qubits):
            circuit.t(i)

        circuit.measure_all()
        return circuit

    def _wavelength_to_angles(self, wavelength_nm: float) -> tuple:
        """Convert wavelength to rotation angles for quantum encoding"""
        # Normalize wavelength to 0-1 range (400-700nm)
        normalized = (wavelength_nm - 400) / 300
        normalized = max(0, min(1, normalized))

        # Convert to Bloch sphere angles
        theta = normalized * math.pi  # 0 to π
        phi = normalized * 2 * math.pi  # 0 to 2π

        return theta, phi

    async def create_ghz_state(
        self,
        num_qubits: int = 5,
        shots: int = 1024,
        backend_name: Optional[str] = None,
    ) -> GHZResult:
        """
        Create and measure a GHZ state.

        Args:
            num_qubits: Number of qubits (default: 5)
            shots: Number of measurements
            backend_name: Specific backend to use

        Returns:
            GHZResult with measurements and entanglement metrics
        """
        circuit = self.create_ghz_circuit(num_qubits)
        start_time = time.time()

        if self.provider:
            if not self.provider.is_initialized:
                await self.provider.initialize()

            if backend_name is None:
                backend_info = await self.provider.get_least_busy_backend(min_qubits=num_qubits)
                backend_name = backend_info.name if backend_info else "simulator"

            job_result = await self.provider.run_circuit(circuit, backend_name, shots)
            counts = job_result.counts
            job_id = job_result.job_id
        else:
            counts = self._simulate_ghz_state(num_qubits, shots)
            backend_name = "local_simulator"
            job_id = f"sim_{int(time.time())}"

        execution_time = time.time() - start_time

        # Calculate entanglement measure
        entanglement = self._calculate_entanglement_measure(counts)

        result = GHZResult(
            num_qubits=num_qubits,
            counts=counts,
            entanglement_measure=entanglement,
            success=entanglement > 0.5,
            backend=backend_name,
            shots=shots,
            execution_time_s=execution_time,
            job_id=job_id,
            metadata={'timestamp': datetime.now().isoformat()},
        )

        self.history.append(result)
        return result

    def _simulate_ghz_state(self, num_qubits: int, shots: int) -> Dict[str, int]:
        """Simulate GHZ state measurements"""
        import random

        # Ideal GHZ: only |00...0⟩ and |11...1⟩
        all_zeros = '0' * num_qubits
        all_ones = '1' * num_qubits

        # Add noise
        noise = 0.1
        counts = {}

        ideal_per_state = shots // 2
        counts[all_zeros] = int(ideal_per_state * (1 - noise) + random.gauss(0, shots * 0.02))
        counts[all_ones] = int(ideal_per_state * (1 - noise) + random.gauss(0, shots * 0.02))

        # Add some noisy states
        remaining = shots - counts[all_zeros] - counts[all_ones]
        if remaining > 0:
            # Distribute among other states
            for _ in range(min(remaining, 10)):
                noisy_state = ''.join(random.choice('01') for _ in range(num_qubits))
                if noisy_state not in counts:
                    counts[noisy_state] = 0
                counts[noisy_state] += remaining // 10

        return counts

    def _calculate_entanglement_measure(self, counts: Dict[str, int]) -> float:
        """
        Calculate entanglement measure from measurement results.

        Uses normalized entropy as entanglement indicator.
        """
        import numpy as np

        total = sum(counts.values())
        if total == 0:
            return 0.0

        probs = np.array(list(counts.values())) / total
        probs = probs[probs > 0]  # Remove zeros for log

        # Shannon entropy
        entropy = -np.sum(probs * np.log2(probs))

        # Normalize by max entropy
        max_entropy = np.log2(len(counts)) if len(counts) > 1 else 1
        normalized = entropy / max_entropy if max_entropy > 0 else 0

        return float(normalized)

    async def create_distributed_ghz(
        self,
        backends: List[str],
        num_qubits_per_backend: int = 5,
        shots: int = 100,
    ) -> List[GHZResult]:
        """
        Create GHZ states distributed across multiple quantum backends.

        This demonstrates the foundation of distributed quantum computing.

        Args:
            backends: List of backend names to use
            num_qubits_per_backend: Qubits per backend
            shots: Number of measurements

        Returns:
            List of GHZResults from each backend
        """
        results = []

        for backend_name in backends:
            result = await self.create_ghz_state(
                num_qubits=num_qubits_per_backend,
                shots=shots,
                backend_name=backend_name,
            )
            results.append(result)

        return results

    def analyze_distributed_entanglement(self, results: List[GHZResult]) -> Dict[str, Any]:
        """
        Analyze entanglement correlations across distributed GHZ states.

        Args:
            results: List of GHZ results from different backends

        Returns:
            Analysis of distributed entanglement
        """
        if len(results) < 2:
            return {'error': 'Need at least 2 backends for distributed analysis'}

        # Find common states across backends
        correlations = []
        for i, r1 in enumerate(results):
            for r2 in results[i + 1:]:
                states1 = set(r1.counts.keys())
                states2 = set(r2.counts.keys())
                common = states1 & states2

                if common:
                    correlation = len(common) / min(len(states1), len(states2))
                    correlations.append({
                        'backend_a': r1.backend,
                        'backend_b': r2.backend,
                        'common_states': len(common),
                        'correlation': correlation,
                    })

        avg_entanglement = sum(r.entanglement_measure for r in results) / len(results)

        return {
            'num_backends': len(results),
            'total_qubits': sum(r.num_qubits for r in results),
            'average_entanglement': avg_entanglement,
            'correlations': correlations,
            'network_quality': 'high' if avg_entanglement > 0.7 else 'moderate' if avg_entanglement > 0.4 else 'low',
        }
