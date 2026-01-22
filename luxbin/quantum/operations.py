"""
LUXBIN Quantum Operations

Unified quantum operations module providing high-level access to
quantum computing functionality across multiple providers.

This module consolidates:
- Quantum Random Number Generation (QRNG)
- Bell pair creation
- GHZ state generation
- Quantum teleportation
- Provider management
"""

import os
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional

from .providers import (
    QuantumProvider,
    IBMQuantumProvider,
    ProviderType,
    BackendInfo,
    JobResult,
    QuantumCircuitWrapper,
)
from .entanglement import (
    BellPairGenerator,
    BellState,
    BellPairResult,
    GHZStateGenerator,
    GHZResult,
    QuantumTeleportation,
    TeleportationResult,
    NVEntanglementProtocol,
    NVCenterNode,
    EntanglementResult,
)


class QuantumRNG:
    """
    Quantum Random Number Generator

    Uses quantum superposition to generate truly random bits.
    Falls back to classical RNG if quantum hardware unavailable.
    """

    def __init__(self, provider: Optional[QuantumProvider] = None):
        self.provider = provider
        self.total_bits_generated = 0
        self.job_history: List[Dict] = []

    def _create_qrng_circuit(self, num_bits: int) -> QuantumCircuitWrapper:
        """Create QRNG circuit with Hadamard gates"""
        circuit = QuantumCircuitWrapper(num_bits, num_bits)

        # Apply Hadamard to all qubits - creates superposition
        for i in range(num_bits):
            circuit.h(i)

        # Measure all qubits
        circuit.measure_all()

        return circuit

    async def generate_random_bits(self, num_bits: int = 8, shots: int = 1) -> Dict[str, Any]:
        """
        Generate random bits using quantum mechanics.

        Args:
            num_bits: Number of random bits to generate
            shots: Number of circuit executions

        Returns:
            Dict with random bits and metadata
        """
        circuit = self._create_qrng_circuit(num_bits)
        start_time = datetime.now()

        if self.provider:
            if not self.provider.is_initialized:
                await self.provider.initialize()

            backend_info = await self.provider.get_least_busy_backend(min_qubits=num_bits)
            backend_name = backend_info.name if backend_info else "simulator"

            result = await self.provider.run_circuit(circuit, backend_name, shots)
            counts = result.counts
            source = f"{self.provider.provider_type.value}_quantum"
        else:
            # Fallback to simulated quantum
            import random
            bits = format(random.getrandbits(num_bits), f'0{num_bits}b')
            counts = {bits: shots}
            source = "simulated_quantum"

        # Get most frequent result
        most_frequent = max(counts, key=counts.get)
        execution_time = (datetime.now() - start_time).total_seconds()

        self.total_bits_generated += num_bits
        self.job_history.append({
            'bits': num_bits,
            'timestamp': datetime.now().isoformat(),
        })

        return {
            'bits': most_frequent,
            'int_value': int(most_frequent, 2),
            'counts': counts,
            'source': source,
            'execution_time_seconds': execution_time,
            'shots': shots,
        }

    async def generate_random_float(self, min_val: float = 0.0, max_val: float = 1.0) -> Dict[str, Any]:
        """Generate random float using quantum RNG"""
        result = await self.generate_random_bits(32)
        normalized = result['int_value'] / (2**32 - 1)
        scaled = min_val + (normalized * (max_val - min_val))

        return {
            'value': scaled,
            'quantum_source': result['source'],
            'raw_bits': result['bits'],
        }


class QuantumMetrics:
    """Track metrics from quantum operations"""

    def __init__(self):
        self.operations: List[Dict] = []
        self.total_shots = 0
        self.total_jobs = 0
        self.backends_used: set = set()

    def record(self, operation_type: str, result: Dict[str, Any]):
        """Record a quantum operation"""
        record = {
            'type': operation_type,
            'timestamp': datetime.now().isoformat(),
            'source': result.get('source', 'unknown'),
            'backend': result.get('backend', 'simulator'),
            'shots': result.get('shots', 1),
            'fidelity': result.get('fidelity'),
            'execution_time': result.get('execution_time_seconds'),
        }

        self.operations.append(record)
        self.total_shots += result.get('shots', 1)
        self.total_jobs += 1

        if result.get('backend'):
            self.backends_used.add(result.get('backend'))

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        fidelities = [op['fidelity'] for op in self.operations if op['fidelity'] is not None]
        exec_times = [op['execution_time'] for op in self.operations if op['execution_time'] is not None]

        return {
            'total_operations': len(self.operations),
            'total_shots': self.total_shots,
            'total_jobs': self.total_jobs,
            'backends_used': list(self.backends_used),
            'average_fidelity': sum(fidelities) / len(fidelities) if fidelities else None,
            'average_execution_time': sum(exec_times) / len(exec_times) if exec_times else None,
            'operation_breakdown': {
                'qrng': len([op for op in self.operations if op['type'] == 'qrng']),
                'bell_pair': len([op for op in self.operations if op['type'] == 'bell_pair']),
                'ghz_state': len([op for op in self.operations if op['type'] == 'ghz_state']),
                'teleportation': len([op for op in self.operations if op['type'] == 'teleportation']),
                'nv_entanglement': len([op for op in self.operations if op['type'] == 'nv_entanglement']),
            }
        }


# Global instances
_provider: Optional[QuantumProvider] = None
_qrng: Optional[QuantumRNG] = None
_bell_generator: Optional[BellPairGenerator] = None
_ghz_generator: Optional[GHZStateGenerator] = None
_teleporter: Optional[QuantumTeleportation] = None
_nv_protocol: Optional[NVEntanglementProtocol] = None
_metrics: Optional[QuantumMetrics] = None


async def get_provider() -> QuantumProvider:
    """Get or initialize the quantum provider"""
    global _provider
    if _provider is None:
        _provider = IBMQuantumProvider()
        await _provider.initialize()
    return _provider


def get_qrng() -> QuantumRNG:
    """Get QRNG instance"""
    global _qrng, _provider
    if _qrng is None:
        _qrng = QuantumRNG(_provider)
    return _qrng


def get_bell_generator() -> BellPairGenerator:
    """Get Bell pair generator"""
    global _bell_generator, _provider
    if _bell_generator is None:
        _bell_generator = BellPairGenerator(_provider)
    return _bell_generator


def get_ghz_generator() -> GHZStateGenerator:
    """Get GHZ state generator"""
    global _ghz_generator, _provider
    if _ghz_generator is None:
        _ghz_generator = GHZStateGenerator(_provider)
    return _ghz_generator


def get_teleporter() -> QuantumTeleportation:
    """Get teleportation instance"""
    global _teleporter, _provider
    if _teleporter is None:
        _teleporter = QuantumTeleportation(_provider)
    return _teleporter


def get_nv_protocol() -> NVEntanglementProtocol:
    """Get NV entanglement protocol"""
    global _nv_protocol
    if _nv_protocol is None:
        _nv_protocol = NVEntanglementProtocol()
    return _nv_protocol


def get_metrics() -> QuantumMetrics:
    """Get metrics tracker"""
    global _metrics
    if _metrics is None:
        _metrics = QuantumMetrics()
    return _metrics


async def demo():
    """Demo quantum operations"""
    print("=" * 60)
    print("LUXBIN Quantum Operations Demo")
    print("=" * 60)

    # Initialize provider
    provider = await get_provider()
    print(f"\nProvider: {provider.name}")

    # QRNG
    print("\n1. Quantum Random Number Generation")
    print("-" * 40)
    qrng = get_qrng()
    result = await qrng.generate_random_bits(8)
    print(f"   Random bits: {result['bits']}")
    print(f"   Source: {result['source']}")
    get_metrics().record('qrng', result)

    # Bell Pair
    print("\n2. Bell Pair Generation")
    print("-" * 40)
    bell = get_bell_generator()
    bell_result = await bell.create_bell_pair()
    print(f"   Fidelity: {bell_result.fidelity:.3f}")
    print(f"   Entangled: {bell_result.is_entangled}")
    get_metrics().record('bell_pair', bell_result.to_dict())

    # GHZ State
    print("\n3. GHZ State Generation")
    print("-" * 40)
    ghz = get_ghz_generator()
    ghz_result = await ghz.create_ghz_state(num_qubits=3)
    print(f"   Entanglement: {ghz_result.entanglement_measure:.3f}")
    print(f"   Success: {ghz_result.success}")
    get_metrics().record('ghz_state', ghz_result.to_dict())

    # Teleportation
    print("\n4. Quantum Teleportation")
    print("-" * 40)
    teleporter = get_teleporter()
    tele_result = await teleporter.teleport()
    print(f"   State: {tele_result.state_teleported}")
    print(f"   Fidelity: {tele_result.fidelity_estimate:.3f}")
    get_metrics().record('teleportation', tele_result.to_dict())

    # NV Entanglement (LUXBIN-EIP-001)
    print("\n5. NV-Center Entanglement (LUXBIN-EIP-001)")
    print("-" * 40)
    nv_protocol = get_nv_protocol()
    node_a = NVCenterNode(node_id="alice")
    node_b = NVCenterNode(node_id="bob")
    nv_result = await nv_protocol.create_entanglement(node_a, node_b)
    print(f"   Success: {nv_result.success}")
    print(f"   Fidelity: {nv_result.fidelity:.4f}")
    print(f"   Bell State: {nv_result.bell_state}")
    get_metrics().record('nv_entanglement', nv_result.to_dict())

    # Metrics
    print("\n" + "=" * 60)
    print("Metrics Summary")
    print("-" * 40)
    summary = get_metrics().get_summary()
    print(f"   Total Operations: {summary['total_operations']}")
    print(f"   Backends Used: {summary['backends_used']}")

    print("\nDemo complete!")


if __name__ == "__main__":
    asyncio.run(demo())
