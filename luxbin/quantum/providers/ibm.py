"""
LUXBIN IBM Quantum Provider

Implementation of the QuantumProvider interface for IBM Quantum.
Supports real hardware execution via IBM Quantum Platform.
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import asyncio
import time

from .base import (
    QuantumProvider,
    ProviderType,
    BackendStatus,
    BackendInfo,
    JobResult,
    QuantumCircuitWrapper,
)

# Try to import Qiskit
QISKIT_AVAILABLE = False
try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler, Session
    from qiskit_ibm_runtime.fake_provider import FakeManilaV2
    QISKIT_AVAILABLE = True
except ImportError:
    pass

# Try to import Aer for simulation
AER_AVAILABLE = False
try:
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel
    AER_AVAILABLE = True
except ImportError:
    pass


class IBMQuantumProvider(QuantumProvider):
    """
    IBM Quantum Provider implementation.

    Connects to IBM Quantum Platform for real quantum hardware execution.
    Falls back to Aer simulator with noise model if hardware unavailable.
    """

    def __init__(self, api_key: Optional[str] = None, channel: str = "ibm_quantum"):
        super().__init__(api_key or os.getenv("IBM_QUANTUM_TOKEN") or os.getenv("QISKIT_IBM_TOKEN"))
        self.channel = channel
        self._service: Optional['QiskitRuntimeService'] = None
        self._simulator: Optional['AerSimulator'] = None

    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.IBM

    @property
    def name(self) -> str:
        return "IBM Quantum"

    async def initialize(self) -> bool:
        """Initialize connection to IBM Quantum"""
        if not QISKIT_AVAILABLE:
            print("Qiskit not available. Install with: pip install qiskit qiskit-ibm-runtime")
            self._initialized = False
            return False

        try:
            if self.api_key:
                self._service = QiskitRuntimeService(
                    channel=self.channel,
                    token=self.api_key
                )
            else:
                # Try to use saved credentials
                self._service = QiskitRuntimeService(channel=self.channel)

            self._initialized = True
            print(f"Connected to IBM Quantum ({self.channel})")
            return True

        except Exception as e:
            print(f"Could not connect to IBM Quantum: {e}")
            print("Falling back to simulator mode")

            # Initialize simulator as fallback
            if AER_AVAILABLE:
                fake_backend = FakeManilaV2()
                noise_model = NoiseModel.from_backend(fake_backend)
                self._simulator = AerSimulator(noise_model=noise_model)
                self._initialized = True
                return True

            self._initialized = False
            return False

    async def get_backends(self) -> List[BackendInfo]:
        """Get list of available IBM backends"""
        backends = []

        if self._service:
            try:
                ibm_backends = self._service.backends()

                for backend in ibm_backends:
                    status = BackendStatus.ONLINE if backend.status().operational else BackendStatus.OFFLINE

                    info = BackendInfo(
                        name=backend.name,
                        provider=ProviderType.IBM,
                        num_qubits=backend.num_qubits,
                        status=status,
                        queue_length=backend.status().pending_jobs,
                        avg_gate_fidelity=0.99,  # Would get from calibration data
                    )
                    backends.append(info)
                    self._backends[backend.name] = info

            except Exception as e:
                print(f"Error getting IBM backends: {e}")

        # Add simulator backend if available
        if self._simulator:
            backends.append(BackendInfo(
                name="aer_simulator",
                provider=ProviderType.IBM,
                num_qubits=32,
                status=BackendStatus.ONLINE,
                queue_length=0,
            ))

        return backends

    def to_native_circuit(self, circuit: QuantumCircuitWrapper) -> 'QuantumCircuit':
        """Convert wrapper to Qiskit circuit"""
        if not QISKIT_AVAILABLE:
            raise RuntimeError("Qiskit not available")

        qr = QuantumRegister(circuit.num_qubits, 'q')
        cr = ClassicalRegister(circuit.num_clbits, 'c')
        qc = QuantumCircuit(qr, cr)

        # Apply gates
        for gate_info in circuit.gates:
            gate = gate_info['gate']
            qubits = gate_info['qubits']
            params = gate_info.get('params', [])

            if gate == 'h':
                qc.h(qubits[0])
            elif gate == 'x':
                qc.x(qubits[0])
            elif gate == 'y':
                qc.y(qubits[0])
            elif gate == 'z':
                qc.z(qubits[0])
            elif gate == 'cx':
                qc.cx(qubits[0], qubits[1])
            elif gate == 'cz':
                qc.cz(qubits[0], qubits[1])
            elif gate == 'rx':
                qc.rx(params[0], qubits[0])
            elif gate == 'ry':
                qc.ry(params[0], qubits[0])
            elif gate == 'rz':
                qc.rz(params[0], qubits[0])
            elif gate == 't':
                qc.t(qubits[0])
            elif gate == 's':
                qc.s(qubits[0])
            elif gate == 'barrier':
                qc.barrier()

        # Apply measurements
        for qubit, clbit in circuit.measurements:
            qc.measure(qr[qubit], cr[clbit])

        return qc

    async def run_circuit(
        self,
        circuit: QuantumCircuitWrapper,
        backend_name: str,
        shots: int = 1024
    ) -> JobResult:
        """Run circuit on IBM backend"""
        if not self._initialized:
            await self.initialize()

        native_circuit = self.to_native_circuit(circuit)
        start_time = time.time()

        # Try real hardware first
        if self._service and backend_name != "aer_simulator":
            try:
                backend = self._service.backend(backend_name)

                with Session(service=self._service, backend=backend) as session:
                    sampler = Sampler(session=session)
                    job = sampler.run([native_circuit], shots=shots)
                    result = job.result()

                    pub_result = result[0]
                    counts = pub_result.data.c.get_counts()

                    execution_time = time.time() - start_time

                    return JobResult(
                        job_id=job.job_id(),
                        backend=backend_name,
                        counts=counts,
                        shots=shots,
                        success=True,
                        execution_time_s=execution_time,
                        metadata={
                            'provider': 'ibm',
                            'hardware': True,
                        }
                    )

            except Exception as e:
                print(f"Hardware execution failed: {e}, falling back to simulator")

        # Fallback to simulator
        if self._simulator or AER_AVAILABLE:
            simulator = self._simulator or AerSimulator()
            transpiled = transpile(native_circuit, simulator)
            job = simulator.run(transpiled, shots=shots)
            result = job.result()
            counts = result.get_counts()

            execution_time = time.time() - start_time

            return JobResult(
                job_id=f"sim_{int(time.time())}",
                backend="aer_simulator",
                counts=counts,
                shots=shots,
                success=True,
                execution_time_s=execution_time,
                metadata={
                    'provider': 'ibm',
                    'hardware': False,
                    'noise_model': self._simulator is not None,
                }
            )

        return JobResult(
            job_id="error",
            backend=backend_name,
            counts={},
            shots=shots,
            success=False,
            execution_time_s=0,
            error="No backend available"
        )

    async def run_bell_circuit(self, shots: int = 1024) -> JobResult:
        """
        Convenience method to run a Bell state circuit.

        Creates |Phi+> = (|00> + |11>)/sqrt(2)

        Returns:
            JobResult with Bell state measurements
        """
        circuit = QuantumCircuitWrapper(2, 2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure_all()

        backend = await self.get_least_busy_backend(min_qubits=2)
        backend_name = backend.name if backend else "aer_simulator"

        return await self.run_circuit(circuit, backend_name, shots)
