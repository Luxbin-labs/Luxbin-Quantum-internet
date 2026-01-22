"""
LUXBIN Quantum Provider Base Interface

Abstract base class for quantum computing providers.
Supports IBM, IonQ, Rigetti, Cirq, Braket, Azure, and more.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
import asyncio


class ProviderType(Enum):
    """Supported quantum provider types"""
    IBM = "ibm"
    IONQ = "ionq"
    RIGETTI = "rigetti"
    CIRQ = "cirq"
    BRAKET = "braket"
    AZURE = "azure"
    IQM = "iqm"
    PASQAL = "pasqal"
    QUANDELA = "quandela"
    SIMULATOR = "simulator"


class BackendStatus(Enum):
    """Backend operational status"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    CALIBRATING = "calibrating"
    UNKNOWN = "unknown"


@dataclass
class BackendInfo:
    """Information about a quantum backend"""
    name: str
    provider: ProviderType
    num_qubits: int
    status: BackendStatus = BackendStatus.UNKNOWN
    queue_length: int = 0
    avg_gate_fidelity: float = 0.99
    t1_us: float = 100.0  # T1 coherence time
    t2_us: float = 50.0   # T2 coherence time
    connectivity: List[Tuple[int, int]] = field(default_factory=list)
    last_calibration: Optional[datetime] = None

    @property
    def is_available(self) -> bool:
        return self.status == BackendStatus.ONLINE


@dataclass
class JobResult:
    """Result from a quantum job"""
    job_id: str
    backend: str
    counts: Dict[str, int]
    shots: int
    success: bool
    execution_time_s: float
    raw_data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def probabilities(self) -> Dict[str, float]:
        """Convert counts to probabilities"""
        total = sum(self.counts.values())
        return {k: v / total for k, v in self.counts.items()}


class QuantumCircuitWrapper:
    """
    Provider-agnostic quantum circuit wrapper.

    Allows circuits to be transpiled to different provider formats.
    """

    def __init__(self, num_qubits: int, num_clbits: Optional[int] = None):
        self.num_qubits = num_qubits
        self.num_clbits = num_clbits or num_qubits
        self.gates: List[Dict[str, Any]] = []
        self.measurements: List[Tuple[int, int]] = []

    def h(self, qubit: int) -> 'QuantumCircuitWrapper':
        """Hadamard gate"""
        self.gates.append({'gate': 'h', 'qubits': [qubit]})
        return self

    def x(self, qubit: int) -> 'QuantumCircuitWrapper':
        """Pauli-X gate"""
        self.gates.append({'gate': 'x', 'qubits': [qubit]})
        return self

    def y(self, qubit: int) -> 'QuantumCircuitWrapper':
        """Pauli-Y gate"""
        self.gates.append({'gate': 'y', 'qubits': [qubit]})
        return self

    def z(self, qubit: int) -> 'QuantumCircuitWrapper':
        """Pauli-Z gate"""
        self.gates.append({'gate': 'z', 'qubits': [qubit]})
        return self

    def cx(self, control: int, target: int) -> 'QuantumCircuitWrapper':
        """CNOT gate"""
        self.gates.append({'gate': 'cx', 'qubits': [control, target]})
        return self

    def cz(self, control: int, target: int) -> 'QuantumCircuitWrapper':
        """Controlled-Z gate"""
        self.gates.append({'gate': 'cz', 'qubits': [control, target]})
        return self

    def rx(self, theta: float, qubit: int) -> 'QuantumCircuitWrapper':
        """Rotation around X axis"""
        self.gates.append({'gate': 'rx', 'qubits': [qubit], 'params': [theta]})
        return self

    def ry(self, theta: float, qubit: int) -> 'QuantumCircuitWrapper':
        """Rotation around Y axis"""
        self.gates.append({'gate': 'ry', 'qubits': [qubit], 'params': [theta]})
        return self

    def rz(self, theta: float, qubit: int) -> 'QuantumCircuitWrapper':
        """Rotation around Z axis"""
        self.gates.append({'gate': 'rz', 'qubits': [qubit], 'params': [theta]})
        return self

    def t(self, qubit: int) -> 'QuantumCircuitWrapper':
        """T gate (pi/4 rotation)"""
        self.gates.append({'gate': 't', 'qubits': [qubit]})
        return self

    def s(self, qubit: int) -> 'QuantumCircuitWrapper':
        """S gate (pi/2 rotation)"""
        self.gates.append({'gate': 's', 'qubits': [qubit]})
        return self

    def barrier(self) -> 'QuantumCircuitWrapper':
        """Add barrier for visualization"""
        self.gates.append({'gate': 'barrier', 'qubits': list(range(self.num_qubits))})
        return self

    def measure(self, qubit: int, clbit: int) -> 'QuantumCircuitWrapper':
        """Measure qubit to classical bit"""
        self.measurements.append((qubit, clbit))
        return self

    def measure_all(self) -> 'QuantumCircuitWrapper':
        """Measure all qubits"""
        for i in range(self.num_qubits):
            self.measurements.append((i, i))
        return self

    @property
    def depth(self) -> int:
        """Approximate circuit depth"""
        return len([g for g in self.gates if g['gate'] != 'barrier'])


class QuantumProvider(ABC):
    """
    Abstract base class for quantum computing providers.

    All provider implementations must inherit from this class.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._backends: Dict[str, BackendInfo] = {}
        self._initialized = False

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Return the provider type"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name"""
        pass

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize connection to the provider.

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_backends(self) -> List[BackendInfo]:
        """
        Get list of available backends.

        Returns:
            List of BackendInfo objects
        """
        pass

    @abstractmethod
    async def run_circuit(
        self,
        circuit: QuantumCircuitWrapper,
        backend_name: str,
        shots: int = 1024
    ) -> JobResult:
        """
        Run a circuit on the specified backend.

        Args:
            circuit: Provider-agnostic circuit wrapper
            backend_name: Name of the backend to use
            shots: Number of measurement shots

        Returns:
            JobResult with counts and metadata
        """
        pass

    @abstractmethod
    def to_native_circuit(self, circuit: QuantumCircuitWrapper) -> Any:
        """
        Convert wrapper circuit to provider-native format.

        Args:
            circuit: Provider-agnostic circuit

        Returns:
            Native circuit object (e.g., qiskit.QuantumCircuit)
        """
        pass

    async def get_least_busy_backend(self, min_qubits: int = 2) -> Optional[BackendInfo]:
        """
        Get the least busy backend with required qubits.

        Args:
            min_qubits: Minimum number of qubits needed

        Returns:
            BackendInfo or None if no suitable backend
        """
        backends = await self.get_backends()
        available = [
            b for b in backends
            if b.is_available and b.num_qubits >= min_qubits
        ]

        if not available:
            return None

        # Sort by queue length
        available.sort(key=lambda b: b.queue_length)
        return available[0]

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(provider={self.provider_type.value}, initialized={self._initialized})"
