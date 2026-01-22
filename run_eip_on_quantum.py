#!/usr/bin/env python3
"""
Run LUXBIN EIP protocols on quantum hardware or simulator
"""

import os
import sys
import argparse
from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# Import EIP implementations
try:
    from eip_implementations import LUXBINEIPImplementations
except ImportError:
    print("❌ Could not import EIP implementations. Run from Luxbin-Quantum-internet directory")
    sys.exit(1)

def run_eip_on_quantum(eip_name: str, use_simulator: bool = False, shots: int = 1024):
    """
    Run a specific EIP protocol on quantum hardware or simulator

    Args:
        eip_name: Name of EIP (EIP-001, EIP-002, etc.)
        use_simulator: If True, use simulator instead of real hardware
        shots: Number of measurement shots
    """
    # Set token
    token = os.environ.get('QISKIT_IBM_TOKEN') or os.environ.get('IBM_TOKEN')
    if not token and not use_simulator:
        print("❌ No IBM token found. Set QISKIT_IBM_TOKEN or IBM_TOKEN environment variable")
        print("💡 Use --simulator flag to test on simulator without token")
        return

    print(f"🚀 Running {eip_name} on quantum hardware...")

    try:
        if not use_simulator:
            QiskitRuntimeService.save_account(token=token, channel="ibm_quantum_platform", overwrite=True)
            service = QiskitRuntimeService()
            print("✅ Connected to IBM Quantum!")

            # Get available backends
            backends = service.backends()
            real_backends = [b for b in backends if not b.simulator and b.status().operational]
            print(f"✅ Found {len(real_backends)} operational quantum computers")

            if not real_backends:
                print("❌ No operational quantum computers available")
                return

            # Use the first available backend
            backend = real_backends[0]
            print(f"🎯 Using backend: {backend.name} ({backend.num_qubits} qubits)")
        else:
            # Use simulator
            from qiskit_aer import AerSimulator
            backend = AerSimulator()
            print("🎯 Using AerSimulator for testing")

        # Get EIP circuit
        eip_circuits = LUXBINEIPImplementations.get_all_eip_circuits()
        if eip_name not in eip_circuits:
            print(f"❌ Unknown EIP: {eip_name}")
            print(f"Available EIPs: {list(eip_circuits.keys())}")
            return

        qc, description = eip_circuits[eip_name]
        print(f"⚛️ {description}")
        print(f"Circuit: {qc.num_qubits} qubits, depth {qc.depth()}")
        print("Circuit diagram:")
        print(qc.draw(output='text', fold=-1))

        # Transpile for the backend
        transpiled_qc = transpile(qc, backend)
        print("✅ Circuit transpiled for backend")

        # Submit job using Sampler
        print(f"📡 Submitting job with {shots} shots...")

        if use_simulator:
            # Run directly on simulator
            job = backend.run(transpiled_qc, shots=shots)
            result = job.result()
            counts = result.get_counts()
        else:
            # Submit to IBM Quantum
            sampler = Sampler(backend)
            job = sampler.run([transpiled_qc], shots=shots)
            print(f"📋 Job ID: {job.job_id()}")

            # Wait for completion (this may take time)
            print("⏳ Waiting for job completion...")
            result = job.result()
            counts = result[0].data.c.get_counts()

        print("🎉 Job completed!")
        print("📊 Results:")
        print(counts)

        # Verify protocol success based on EIP
        if eip_name == "EIP-002":
            # Bell pair should show ~50% |00> and ~50% |11>
            total_shots = sum(counts.values())
            prob_00 = counts.get('00', 0) / total_shots
            prob_11 = counts.get('11', 0) / total_shots
            print(f"Probability |00⟩: {prob_00:.2f}")
            print(f"Probability |11⟩: {prob_11:.2f}")
        elif eip_name == "EIP-003":
            # GHZ state should show ~50% |000> and ~50% |111>
            total_shots = sum(counts.values())
            prob_000 = counts.get('000', 0) / total_shots
            prob_111 = counts.get('111', 0) / total_shots
            print(f"Probability |000⟩: {prob_000:.2f}")
            print(f"Probability |111⟩: {prob_111:.2f}")
        elif eip_name == "EIP-004":
            # Teleportation success depends on state preparation
            print("📝 Quantum teleportation requires classical post-processing for full verification")

    except Exception as e:
        print(f"❌ Error running EIP: {e}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="Run LUXBIN EIP protocols on quantum hardware")
    parser.add_argument("eip", help="EIP to run (EIP-001, EIP-002, EIP-003, EIP-004)")
    parser.add_argument("--simulator", action="store_true", help="Use simulator instead of real hardware")
    parser.add_argument("--shots", type=int, default=1024, help="Number of measurement shots")

    args = parser.parse_args()
    run_eip_on_quantum(args.eip, args.simulator, args.shots)

if __name__ == "__main__":
    main()