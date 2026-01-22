"""
LUXBIN Configuration

Centralized configuration management for the LUXBIN Quantum Internet.
Handles environment variables, provider credentials, and runtime settings.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ProviderConfig:
    """Configuration for a quantum provider"""
    name: str
    api_key: Optional[str] = None
    region: Optional[str] = None
    endpoint: Optional[str] = None
    enabled: bool = True
    backends: List[str] = field(default_factory=list)


@dataclass
class NetworkConfig:
    """P2P network configuration"""
    bootstrap_nodes: List[str] = field(default_factory=list)
    listen_port: int = 8765
    max_peers: int = 50
    heartbeat_interval: float = 30.0
    peer_timeout: float = 120.0


@dataclass
class QuantumConfig:
    """Quantum operation configuration"""
    default_shots: int = 1024
    use_real_hardware: bool = True
    simulation_noise_model: bool = True
    max_qubits: int = 127
    optimization_level: int = 3


@dataclass
class EntanglementConfig:
    """LUXBIN-EIP-001 entanglement protocol configuration"""
    # NV Center parameters
    nv_wavelength_nm: float = 637.0
    optical_pump_nm: float = 532.0

    # Protocol parameters
    max_retries: int = 10
    coherence_time_us: float = 1000.0  # T2 coherence time
    target_fidelity: float = 0.9

    # Dynamical decoupling
    dd_sequence: str = "XY8"  # Options: XY4, XY8, CPMG
    dd_pi_pulses: int = 8


@dataclass
class AIConfig:
    """AI agent configuration"""
    default_backend: str = "local"
    anthropic_model: str = "claude-3-haiku-20240307"
    openai_model: str = "gpt-3.5-turbo"
    groq_model: str = "llama-3.1-8b-instant"
    max_tokens: int = 500


class LuxbinConfig:
    """
    Main configuration class for LUXBIN Quantum Internet

    Usage:
        config = LuxbinConfig()
        ibm_key = config.providers['ibm'].api_key
    """

    def __init__(self, config_path: Optional[Path] = None):
        self._config_path = config_path

        # Initialize configurations
        self.providers = self._load_providers()
        self.network = self._load_network_config()
        self.quantum = self._load_quantum_config()
        self.entanglement = self._load_entanglement_config()
        self.ai = self._load_ai_config()

    def _load_providers(self) -> Dict[str, ProviderConfig]:
        """Load quantum provider configurations from environment"""
        return {
            # IBM Quantum
            "ibm": ProviderConfig(
                name="IBM Quantum",
                api_key=os.getenv("IBM_QUANTUM_TOKEN") or os.getenv("QISKIT_IBM_TOKEN"),
                region=os.getenv("IBM_QUANTUM_REGION", "us-east"),
                backends=["ibm_fez", "ibm_torino", "ibm_marrakesh", "ibm_brisbane"],
                enabled=bool(os.getenv("IBM_QUANTUM_TOKEN") or os.getenv("QISKIT_IBM_TOKEN"))
            ),

            # IonQ
            "ionq": ProviderConfig(
                name="IonQ",
                api_key=os.getenv("IONQ_API_KEY"),
                backends=["ionq_harmony", "ionq_aria", "ionq_forte"],
                enabled=bool(os.getenv("IONQ_API_KEY"))
            ),

            # Rigetti
            "rigetti": ProviderConfig(
                name="Rigetti",
                api_key=os.getenv("RIGETTI_API_KEY"),
                backends=["rigetti_aspen"],
                enabled=bool(os.getenv("RIGETTI_API_KEY"))
            ),

            # Google/Cirq
            "cirq": ProviderConfig(
                name="Google Cirq",
                api_key=os.getenv("GOOGLE_QUANTUM_API_KEY"),
                backends=["cirq_photonic", "cirq_simulator"],
                enabled=True  # Simulator always available
            ),

            # Amazon Braket
            "braket": ProviderConfig(
                name="Amazon Braket",
                api_key=os.getenv("AWS_ACCESS_KEY_ID"),
                region=os.getenv("AWS_REGION", "us-west-1"),
                backends=["braket_ionq", "braket_rigetti", "braket_oqc"],
                enabled=bool(os.getenv("AWS_ACCESS_KEY_ID"))
            ),

            # Azure Quantum
            "azure": ProviderConfig(
                name="Azure Quantum",
                api_key=os.getenv("AZURE_SUBSCRIPTION_ID"),
                region=os.getenv("AZURE_REGION"),
                backends=["azure_quantinuum", "azure_ionq"],
                enabled=bool(os.getenv("AZURE_SUBSCRIPTION_ID"))
            ),

            # International providers
            "iqm": ProviderConfig(
                name="IQM (Finland)",
                api_key=os.getenv("IQM_API_KEY"),
                backends=["iqm_garnet", "iqm_apollo"],
                enabled=bool(os.getenv("IQM_API_KEY"))
            ),

            "pasqal": ProviderConfig(
                name="Pasqal (France)",
                api_key=os.getenv("PASQAL_API_KEY"),
                backends=["pasqal_fresnel"],
                enabled=bool(os.getenv("PASQAL_API_KEY"))
            ),

            "quandela": ProviderConfig(
                name="Quandela (France)",
                api_key=os.getenv("QUANDELA_API_KEY"),
                backends=["quandela_cloud"],
                enabled=bool(os.getenv("QUANDELA_API_KEY"))
            ),
        }

    def _load_network_config(self) -> NetworkConfig:
        """Load P2P network configuration"""
        return NetworkConfig(
            bootstrap_nodes=os.getenv("LUXBIN_BOOTSTRAP_NODES", "").split(",") if os.getenv("LUXBIN_BOOTSTRAP_NODES") else [],
            listen_port=int(os.getenv("LUXBIN_PORT", "8765")),
            max_peers=int(os.getenv("LUXBIN_MAX_PEERS", "50")),
            heartbeat_interval=float(os.getenv("LUXBIN_HEARTBEAT", "30.0")),
            peer_timeout=float(os.getenv("LUXBIN_PEER_TIMEOUT", "120.0")),
        )

    def _load_quantum_config(self) -> QuantumConfig:
        """Load quantum operation configuration"""
        return QuantumConfig(
            default_shots=int(os.getenv("LUXBIN_SHOTS", "1024")),
            use_real_hardware=os.getenv("LUXBIN_USE_REAL_HARDWARE", "true").lower() == "true",
            simulation_noise_model=os.getenv("LUXBIN_NOISE_MODEL", "true").lower() == "true",
            max_qubits=int(os.getenv("LUXBIN_MAX_QUBITS", "127")),
            optimization_level=int(os.getenv("LUXBIN_OPTIMIZATION_LEVEL", "3")),
        )

    def _load_entanglement_config(self) -> EntanglementConfig:
        """Load LUXBIN-EIP-001 protocol configuration"""
        return EntanglementConfig(
            nv_wavelength_nm=float(os.getenv("LUXBIN_NV_WAVELENGTH", "637.0")),
            optical_pump_nm=float(os.getenv("LUXBIN_PUMP_WAVELENGTH", "532.0")),
            max_retries=int(os.getenv("LUXBIN_MAX_RETRIES", "10")),
            coherence_time_us=float(os.getenv("LUXBIN_COHERENCE_TIME", "1000.0")),
            target_fidelity=float(os.getenv("LUXBIN_TARGET_FIDELITY", "0.9")),
            dd_sequence=os.getenv("LUXBIN_DD_SEQUENCE", "XY8"),
            dd_pi_pulses=int(os.getenv("LUXBIN_DD_PULSES", "8")),
        )

    def _load_ai_config(self) -> AIConfig:
        """Load AI agent configuration"""
        # Determine default backend based on available APIs
        default_backend = "local"
        if os.getenv("ANTHROPIC_API_KEY"):
            default_backend = "anthropic"
        elif os.getenv("OPENAI_API_KEY"):
            default_backend = "openai"
        elif os.getenv("GROQ_API_KEY"):
            default_backend = "groq"

        return AIConfig(
            default_backend=default_backend,
            anthropic_model=os.getenv("LUXBIN_ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
            openai_model=os.getenv("LUXBIN_OPENAI_MODEL", "gpt-3.5-turbo"),
            groq_model=os.getenv("LUXBIN_GROQ_MODEL", "llama-3.1-8b-instant"),
            max_tokens=int(os.getenv("LUXBIN_AI_MAX_TOKENS", "500")),
        )

    def get_active_providers(self) -> List[str]:
        """Get list of providers with valid API keys"""
        return [name for name, config in self.providers.items() if config.enabled]

    def get_all_backends(self) -> List[str]:
        """Get all available backend names"""
        backends = []
        for config in self.providers.values():
            if config.enabled:
                backends.extend(config.backends)
        return backends


# Global config instance
_config: Optional[LuxbinConfig] = None


def get_config() -> LuxbinConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = LuxbinConfig()
    return _config


def reload_config() -> LuxbinConfig:
    """Reload configuration from environment"""
    global _config
    _config = LuxbinConfig()
    return _config
