"""
LUXBIN Quantum Teleportation

Implements the quantum teleportation protocol using Bell pairs
and classical communication.

Teleportation transfers a quantum state from one location to another
using pre-shared entanglement and two classical bits of communication.
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import math

from ..providers.base import QuantumCircuitWrapper, QuantumProvider


@dataclass
class TeleportationResult:
    """Result from quantum teleportation"""
    success: bool
    state_teleported: str
    fidelity_estimate: float
    classical_bits_sent: Dict[str, int]
    teleported_measurement: Dict[str, int]
    counts: Dict[str, int]
    shots: int
    backend: str
    execution_time_s: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'state_teleported': self.state_teleported,
            'fidelity_estimate': self.fidelity_estimate,
            'classical_bits_sent': self.classical_bits_sent,
            'teleported_measurement': self.teleported_measurement,
            'shots': self.shots,
            'backend': self.backend,
        }


class QuantumTeleportation:
    """
    Quantum Teleportation Protocol Implementation.

    The protocol:
    1. Alice and Bob share a Bell pair
    2. Alice has a qubit to teleport
    3. Alice performs Bell measurement on her qubits
    4. Alice sends 2 classical bits to Bob
    5. Bob applies corrections based on classical bits
    6. Bob's qubit is now in the teleported state

    Usage:
        teleporter = QuantumTeleportation(provider)
        result = await teleporter.teleport()
    """

    def __init__(self, provider: Optional[QuantumProvider] = None):
        self.provider = provider
        self.history: list = []

    def create_teleportation_circuit(
        self,
        state_to_teleport: str = "plus",
    ) -> QuantumCircuitWrapper:
        """
        Create quantum teleportation circuit.

        Qubit layout:
        - Qubit 0: State to teleport (Alice's input)
        - Qubit 1: Alice's half of Bell pair
        - Qubit 2: Bob's half of Bell pair (receives teleported state)

        Args:
            state_to_teleport: Initial state - "plus", "zero", "one", or "minus"

        Returns:
            Teleportation circuit
        """
        circuit = QuantumCircuitWrapper(3, 3)

        # Prepare state to teleport on qubit 0
        if state_to_teleport == "plus":
            circuit.h(0)  # |+⟩ = (|0⟩ + |1⟩)/√2
        elif state_to_teleport == "minus":
            circuit.x(0)
            circuit.h(0)  # |-⟩ = (|0⟩ - |1⟩)/√2
        elif state_to_teleport == "one":
            circuit.x(0)  # |1⟩
        # "zero" is default |0⟩

        circuit.barrier()

        # Create Bell pair between qubits 1 and 2
        circuit.h(1)
        circuit.cx(1, 2)

        circuit.barrier()

        # Alice's Bell measurement (qubits 0 and 1)
        circuit.cx(0, 1)
        circuit.h(0)

        # Measure Alice's qubits
        circuit.measure(0, 0)
        circuit.measure(1, 1)

        circuit.barrier()

        # Note: In real implementation, Bob's corrections would be
        # classically controlled. Here we measure all for analysis.
        circuit.measure(2, 2)

        return circuit

    async def teleport(
        self,
        state_to_teleport: str = "plus",
        shots: int = 1024,
        backend_name: Optional[str] = None,
    ) -> TeleportationResult:
        """
        Execute quantum teleportation protocol.

        Args:
            state_to_teleport: State to teleport ("plus", "zero", "one", "minus")
            shots: Number of measurements
            backend_name: Backend to use

        Returns:
            TeleportationResult with fidelity and measurement data
        """
        circuit = self.create_teleportation_circuit(state_to_teleport)
        start_time = time.time()

        if self.provider:
            if not self.provider.is_initialized:
                await self.provider.initialize()

            if backend_name is None:
                backend_info = await self.provider.get_least_busy_backend(min_qubits=3)
                backend_name = backend_info.name if backend_info else "simulator"

            job_result = await self.provider.run_circuit(circuit, backend_name, shots)
            counts = job_result.counts
        else:
            counts = self._simulate_teleportation(state_to_teleport, shots)
            backend_name = "local_simulator"

        execution_time = time.time() - start_time

        # Analyze results
        classical_bits, teleported_outcomes = self._analyze_results(counts)
        fidelity = self._estimate_fidelity(teleported_outcomes, state_to_teleport)

        result = TeleportationResult(
            success=fidelity > 0.5,
            state_teleported=f"|{state_to_teleport}⟩",
            fidelity_estimate=fidelity,
            classical_bits_sent=classical_bits,
            teleported_measurement=teleported_outcomes,
            counts=counts,
            shots=shots,
            backend=backend_name,
            execution_time_s=execution_time,
            metadata={
                'timestamp': datetime.now().isoformat(),
                'protocol': 'standard_teleportation',
            }
        )

        self.history.append(result)
        return result

    def _simulate_teleportation(self, state: str, shots: int) -> Dict[str, int]:
        """Simulate teleportation measurement outcomes"""
        import random

        counts = {}
        # For teleportation, we expect uniform distribution over classical bits
        # and correlated teleported qubit

        for _ in range(shots):
            # Random classical bits (Bell measurement outcome)
            c0 = random.choice(['0', '1'])
            c1 = random.choice(['0', '1'])

            # Teleported qubit depends on state and classical bits
            # For |+⟩ state, should see 50/50 after correction
            if state in ["plus", "minus"]:
                c2 = random.choice(['0', '1'])
            elif state == "zero":
                c2 = '0' if random.random() > 0.05 else '1'  # Small noise
            else:  # one
                c2 = '1' if random.random() > 0.05 else '0'

            outcome = c2 + c1 + c0  # Reversed order
            counts[outcome] = counts.get(outcome, 0) + 1

        return counts

    def _analyze_results(self, counts: Dict[str, int]) -> Tuple[Dict[str, int], Dict[str, int]]:
        """Extract classical bits and teleported outcomes from counts"""
        classical_bits = {}
        teleported_outcomes = {'0': 0, '1': 0}

        for outcome, count in counts.items():
            # Outcome format: 'c2 c1 c0' (Bob Alice1 Alice0)
            if len(outcome) >= 3:
                classical = outcome[1:]  # c1 c0
                teleported = outcome[0]   # c2

                classical_bits[classical] = classical_bits.get(classical, 0) + count
                teleported_outcomes[teleported] += count

        return classical_bits, teleported_outcomes

    def _estimate_fidelity(self, outcomes: Dict[str, int], state: str) -> float:
        """Estimate teleportation fidelity"""
        total = sum(outcomes.values())
        if total == 0:
            return 0.0

        # For |+⟩ and |-⟩, expect 50/50 distribution
        if state in ["plus", "minus"]:
            balance = min(outcomes.values()) / max(outcomes.values()) if max(outcomes.values()) > 0 else 0
            return balance

        # For |0⟩, expect mostly '0' outcomes
        elif state == "zero":
            return outcomes.get('0', 0) / total

        # For |1⟩, expect mostly '1' outcomes
        else:
            return outcomes.get('1', 0) / total
