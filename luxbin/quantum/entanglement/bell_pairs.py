"""
LUXBIN Bell Pair Generator

Creates and measures Bell pairs on quantum hardware.
Supports all four Bell states for entanglement distribution.

Bell States:
- |Φ+⟩ = (|00⟩ + |11⟩)/√2
- |Φ-⟩ = (|00⟩ - |11⟩)/√2
- |Ψ+⟩ = (|01⟩ + |10⟩)/√2
- |Ψ-⟩ = (|01⟩ - |10⟩)/√2
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

from ..providers.base import QuantumCircuitWrapper, JobResult, QuantumProvider


class BellState(Enum):
    """The four maximally entangled Bell states"""
    PHI_PLUS = "phi_plus"    # (|00⟩ + |11⟩)/√2
    PHI_MINUS = "phi_minus"  # (|00⟩ - |11⟩)/√2
    PSI_PLUS = "psi_plus"    # (|01⟩ + |10⟩)/√2
    PSI_MINUS = "psi_minus"  # (|01⟩ - |10⟩)/√2


@dataclass
class BellPairResult:
    """Result from Bell pair creation and measurement"""
    bell_state: BellState
    counts: Dict[str, int]
    fidelity: float
    is_entangled: bool
    correlation: Dict[str, int]
    shots: int
    backend: str
    execution_time_s: float
    job_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'bell_state': self.bell_state.value,
            'counts': self.counts,
            'fidelity': self.fidelity,
            'is_entangled': self.is_entangled,
            'correlation': self.correlation,
            'shots': self.shots,
            'backend': self.backend,
            'execution_time_s': self.execution_time_s,
            'job_id': self.job_id,
        }


class BellPairGenerator:
    """
    Creates and measures Bell pairs on quantum hardware.

    Usage:
        from luxbin.quantum.providers import IBMQuantumProvider

        provider = IBMQuantumProvider()
        await provider.initialize()

        generator = BellPairGenerator(provider)
        result = await generator.create_bell_pair(BellState.PHI_PLUS)
    """

    # Fidelity threshold for "good" entanglement
    ENTANGLEMENT_THRESHOLD = 0.7

    def __init__(self, provider: Optional[QuantumProvider] = None):
        """
        Initialize Bell pair generator.

        Args:
            provider: Quantum provider to use. If None, uses simulator.
        """
        self.provider = provider
        self.history: List[BellPairResult] = []

    def create_bell_circuit(self, bell_state: BellState = BellState.PHI_PLUS) -> QuantumCircuitWrapper:
        """
        Create a circuit that generates the specified Bell state.

        Args:
            bell_state: Which Bell state to create

        Returns:
            QuantumCircuitWrapper configured for Bell state
        """
        circuit = QuantumCircuitWrapper(2, 2)

        # Create |Φ+⟩ base state
        circuit.h(0)      # Hadamard on first qubit
        circuit.cx(0, 1)  # CNOT

        # Modify for different Bell states
        if bell_state == BellState.PHI_MINUS:
            circuit.z(0)  # Phase flip
        elif bell_state == BellState.PSI_PLUS:
            circuit.x(1)  # Bit flip on second qubit
        elif bell_state == BellState.PSI_MINUS:
            circuit.z(0)
            circuit.x(1)

        # Measure both qubits
        circuit.measure_all()

        return circuit

    async def create_bell_pair(
        self,
        bell_state: BellState = BellState.PHI_PLUS,
        shots: int = 1024,
        backend_name: Optional[str] = None,
    ) -> BellPairResult:
        """
        Create and measure a Bell pair.

        Args:
            bell_state: Which Bell state to create
            shots: Number of measurements
            backend_name: Specific backend to use

        Returns:
            BellPairResult with measurement results and fidelity
        """
        circuit = self.create_bell_circuit(bell_state)
        start_time = time.time()

        if self.provider:
            # Use real quantum provider
            if not self.provider.is_initialized:
                await self.provider.initialize()

            if backend_name is None:
                backend_info = await self.provider.get_least_busy_backend(min_qubits=2)
                backend_name = backend_info.name if backend_info else "simulator"

            job_result = await self.provider.run_circuit(circuit, backend_name, shots)
            counts = job_result.counts
            job_id = job_result.job_id
        else:
            # Simulate locally
            counts = self._simulate_bell_state(bell_state, shots)
            backend_name = "local_simulator"
            job_id = f"sim_{int(time.time())}"

        execution_time = time.time() - start_time

        # Calculate fidelity and correlation
        fidelity = self._calculate_fidelity(counts, bell_state)
        correlation = self._extract_correlation(counts)
        is_entangled = fidelity > self.ENTANGLEMENT_THRESHOLD

        result = BellPairResult(
            bell_state=bell_state,
            counts=counts,
            fidelity=fidelity,
            is_entangled=is_entangled,
            correlation=correlation,
            shots=shots,
            backend=backend_name,
            execution_time_s=execution_time,
            job_id=job_id,
            metadata={
                'timestamp': datetime.now().isoformat(),
                'provider': self.provider.provider_type.value if self.provider else 'simulator',
            }
        )

        self.history.append(result)
        return result

    def _simulate_bell_state(self, bell_state: BellState, shots: int) -> Dict[str, int]:
        """Simulate Bell state measurement outcomes"""
        import random

        # Ideal Bell state probabilities
        if bell_state in [BellState.PHI_PLUS, BellState.PHI_MINUS]:
            # Should see only 00 and 11
            base_probs = {'00': 0.5, '11': 0.5, '01': 0.0, '10': 0.0}
        else:
            # Should see only 01 and 10
            base_probs = {'00': 0.0, '11': 0.0, '01': 0.5, '10': 0.5}

        # Add realistic noise
        noise = 0.05
        counts = {}
        for outcome, prob in base_probs.items():
            noisy_prob = prob * (1 - noise) + noise * 0.25
            counts[outcome] = int(shots * noisy_prob + random.gauss(0, shots * 0.01))
            counts[outcome] = max(0, counts[outcome])

        # Normalize to exact shot count
        total = sum(counts.values())
        if total != shots:
            diff = shots - total
            max_key = max(counts, key=counts.get)
            counts[max_key] += diff

        return counts

    def _calculate_fidelity(self, counts: Dict[str, int], bell_state: BellState) -> float:
        """Calculate fidelity of measured state to ideal Bell state"""
        total = sum(counts.values())
        if total == 0:
            return 0.0

        # For Φ states, correlated outcomes are 00 and 11
        # For Ψ states, correlated outcomes are 01 and 10
        if bell_state in [BellState.PHI_PLUS, BellState.PHI_MINUS]:
            correlated = counts.get('00', 0) + counts.get('11', 0)
        else:
            correlated = counts.get('01', 0) + counts.get('10', 0)

        return correlated / total

    def _extract_correlation(self, counts: Dict[str, int]) -> Dict[str, int]:
        """Extract correlation statistics"""
        return {
            '00': counts.get('00', 0),
            '01': counts.get('01', 0),
            '10': counts.get('10', 0),
            '11': counts.get('11', 0),
        }

    async def create_multiple_pairs(
        self,
        count: int,
        bell_state: BellState = BellState.PHI_PLUS,
        shots: int = 1024,
    ) -> List[BellPairResult]:
        """Create multiple Bell pairs"""
        results = []
        for _ in range(count):
            result = await self.create_bell_pair(bell_state, shots)
            results.append(result)
        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from Bell pair history"""
        if not self.history:
            return {'total_pairs': 0}

        successful = [r for r in self.history if r.is_entangled]
        fidelities = [r.fidelity for r in self.history]

        return {
            'total_pairs': len(self.history),
            'successful_entanglements': len(successful),
            'success_rate': len(successful) / len(self.history),
            'average_fidelity': sum(fidelities) / len(fidelities),
            'min_fidelity': min(fidelities),
            'max_fidelity': max(fidelities),
        }
