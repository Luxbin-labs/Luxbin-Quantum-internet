#!/usr/bin/env python3
"""
Test IBM Quantum connection and account status
"""

import os
import sys

def main():
    # Check for token
    token = os.environ.get('QISKIT_IBM_TOKEN') or os.environ.get('IBM_TOKEN')
    if not token:
        print("❌ No IBM token found.")
        print("Set with: export QISKIT_IBM_TOKEN=your_token_here")
        return

    print(f"🔑 Using token: {token[:10]}...")
    print("🚀 Testing IBM Quantum connection...")

    try:
        # Try IBMProvider first
        from qiskit_ibm_provider import IBMProvider
        provider = IBMProvider(token=token)
        backends = provider.backends()
        real_backends = [b for b in backends if not b.simulator]
        print("✅ IBMProvider connection successful!")
        print(f"📊 Total backends: {len(backends)}")
        print(f"⚛️ Real quantum computers: {len(real_backends)}")
        for b in real_backends[:3]:
            print(f"  - {b.name}: {b.num_qubits} qubits")

    except Exception as e:
        print(f"❌ IBMProvider failed: {e}")

        # Try QiskitRuntimeService
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService
            service = QiskitRuntimeService(channel='ibm_quantum_platform')
            backends = service.backends()
            real_backends = [b for b in backends if not b.simulator]
            print("✅ QiskitRuntimeService connection successful!")
            print(f"📊 Total backends: {len(backends)}")
            print(f"⚛️ Real quantum computers: {len(real_backends)}")
            for b in real_backends[:3]:
                print(f"  - {b.name}: {b.num_qubits} qubits")
        except Exception as e2:
            print(f"❌ QiskitRuntimeService also failed: {e2}")

    print("\n💡 If connection works, your token is valid!")
    print("🎯 Next: run submit_ibm_job.py to submit a real job")

if __name__ == "__main__":
    main()