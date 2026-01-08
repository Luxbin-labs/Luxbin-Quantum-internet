#!/usr/bin/env python3
"""
Beaconcha.in API Setup and Validator Discovery
Tests API connection and finds your validators
"""

import json
import urllib.request
import urllib.error
import sys

API_KEY = "p394i31QvTe8WfzT08IEGbt85shA6HlmS75OxKzM8H9"
BASE_URL_V1 = "https://beaconcha.in/api/v1"
BASE_URL_V2 = "https://beaconcha.in/api/v2"

def make_request(url, method="GET", data=None, api_version="v1"):
    """Make authenticated request to Beaconcha.in API"""
    try:
        req = urllib.request.Request(url, method=method)

        # Add authentication header
        req.add_header('Authorization', f'Bearer {API_KEY}')
        req.add_header('User-Agent', 'LUXBIN-Quantum-Validator/1.0')

        if data:
            req.add_header('Content-Type', 'application/json')
            data = json.dumps(data).encode('utf-8')

        with urllib.request.urlopen(req, data=data, timeout=10) as response:
            result = json.loads(response.read().decode())
            return {'success': True, 'data': result, 'status': response.status}

    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.read() else str(e)
        try:
            error_data = json.loads(error_body)
        except:
            error_data = {'error': error_body}
        return {'success': False, 'error': error_data, 'status': e.code}

    except Exception as e:
        return {'success': False, 'error': str(e), 'status': None}


def test_api_connection():
    """Test basic API connection"""
    print("🔍 Testing Beaconcha.in API Connection...")
    print("=" * 60)

    # Test V1 API - Network stats (no auth needed)
    print("\n1. Testing V1 API (network stats)...")
    result = make_request(f"{BASE_URL_V1}/epoch/latest")
    if result['success']:
        print(f"   ✅ V1 API is accessible")
        data = result['data'].get('data', {})
        print(f"   Latest Epoch: {data.get('epoch', 'N/A')}")
    else:
        print(f"   ❌ V1 API error: {result.get('error')}")

    # Test V2 API authentication
    print("\n2. Testing V2 API authentication...")
    test_data = {
        "validator": {
            "validator_identifiers": [1]  # Test with validator 1
        },
        "chain": "mainnet",
        "page_size": 1
    }

    result = make_request(
        f"{BASE_URL_V2}/ethereum/validators/rewards-list",
        method="POST",
        data=test_data,
        api_version="v2"
    )

    if result['success']:
        print(f"   ✅ Authentication working!")
    else:
        print(f"   ⚠️  Auth test: {result.get('error')}")

    print("\n" + "=" * 60)


def discover_validators():
    """Try to discover user's validators"""
    print("\n🔎 Discovering Your Validators...")
    print("=" * 60)

    # Method 1: Try user stats
    print("\n1. Checking user account statistics...")
    result = make_request(f"{BASE_URL_V1}/user/stats")
    if result['success']:
        print("   ✅ Found user data:")
        print(json.dumps(result['data'], indent=2))
    else:
        print(f"   ℹ️  User stats not available via API")
        print(f"   Error: {result.get('error')}")

    # Method 2: Try dashboard endpoint
    print("\n2. Checking dashboard...")
    result = make_request(f"{BASE_URL_V1}/dashboard")
    if result['success']:
        print("   ✅ Dashboard data:")
        print(json.dumps(result['data'], indent=2))
    else:
        print(f"   ℹ️  Dashboard endpoint: {result.get('error')}")

    print("\n" + "=" * 60)


def get_validator_info(validator_index):
    """Get info for specific validator"""
    print(f"\n📊 Fetching Validator {validator_index} Info...")
    print("=" * 60)

    result = make_request(f"{BASE_URL_V1}/validator/{validator_index}")

    if result['success']:
        data = result['data'].get('data', {})
        print(f"   ✅ Validator {validator_index} Found!")
        print(f"   Status: {data.get('status', 'Unknown')}")
        print(f"   Balance: {data.get('balance', 0) / 1e9:.4f} ETH")
        print(f"   Effective Balance: {data.get('effectivebalance', 0) / 1e9:.4f} ETH")
        return data
    else:
        print(f"   ❌ Could not fetch validator {validator_index}")
        return None


def check_multiple_validators(start_index=0, count=10):
    """Check a range of validator indices"""
    print(f"\n🔍 Checking Validators {start_index} to {start_index + count}...")
    print("=" * 60)

    found_validators = []

    for i in range(start_index, start_index + count):
        result = make_request(f"{BASE_URL_V1}/validator/{i}")
        if result['success']:
            data = result['data'].get('data', {})
            print(f"   Validator {i}: {data.get('status', 'Unknown')}")
            found_validators.append({'index': i, 'data': data})

    return found_validators


def save_config(validators):
    """Save validator configuration"""
    config = {
        'api_key': API_KEY,
        'validators': validators,
        'base_url_v1': BASE_URL_V1,
        'base_url_v2': BASE_URL_V2,
        'quantum_enabled': True
    }

    with open('beaconchain_config.json', 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n💾 Configuration saved to beaconchain_config.json")


def interactive_setup():
    """Interactive setup wizard"""
    print("\n" + "=" * 60)
    print("🌐⚛️ LUXBIN Quantum Validator Setup")
    print("=" * 60)

    # Test connection
    test_api_connection()

    # Try to discover validators
    discover_validators()

    # Ask user
    print("\n" + "=" * 60)
    print("📝 Validator Configuration")
    print("=" * 60)
    print()
    print("Options:")
    print("  1. I know my validator index/indices")
    print("  2. Search for my validators")
    print("  3. Use demo mode (no validators)")
    print()

    choice = input("Choose option (1-3): ").strip()

    validators = []

    if choice == "1":
        indices = input("Enter validator indices (comma-separated): ").strip()
        for idx in indices.split(','):
            try:
                idx = int(idx.strip())
                validator_data = get_validator_info(idx)
                if validator_data:
                    validators.append({'index': idx, 'data': validator_data})
            except ValueError:
                print(f"   ⚠️  Invalid index: {idx}")

    elif choice == "2":
        start = input("Start index (default 0): ").strip()
        start = int(start) if start else 0
        count = input("How many to check (default 100): ").strip()
        count = int(count) if count else 100
        validators = check_multiple_validators(start, count)

    else:
        print("\n   ℹ️  Running in demo mode")
        validators = []

    # Save configuration
    if validators or choice == "3":
        save_config(validators)

        print("\n✅ Setup Complete!")
        print(f"\nFound {len(validators)} validator(s)")
        print("\nNext steps:")
        print("  1. Run: python3 quantum_validator_bridge.py")
        print("  2. Open: http://localhost:8766")
        print("  3. Watch your validators with quantum security! ⚛️")
    else:
        print("\n⚠️  No validators configured")
        print("\nYou can manually add validators to beaconchain_config.json")


if __name__ == '__main__':
    try:
        interactive_setup()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
