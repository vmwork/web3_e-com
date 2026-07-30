#!/usr/bin/env python3
"""
Test script for OneWay API authentication via wallet signature.

Usage:
    python test_auth.py

This script:
    1. Generates a test wallet (or uses a provided private key)
    2. Signs a message
    3. Sends a POST request to /api/v1/auth/connect
    4. Displays the JWT token and user data
    5. Optionally decodes and shows JWT payload
"""

import json
import os
import sys
from datetime import datetime
from eth_account import Account
from eth_account.messages import encode_defunct
import requests


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = os.getenv("API_URL", "http://localhost:8000")
AUTH_ENDPOINT = f"{API_URL}/api/v1/auth/connect"

# Test private key (DO NOT use in production!)
# You can replace this with your own key or set PRIVATE_KEY env var
DEFAULT_PRIVATE_KEY = "0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318"
SIGN_MESSAGE = "Sign in to OneWay API"


# ============================================================
# FUNCTIONS
# ============================================================

def get_private_key() -> str:
    """Get private key from environment or use default test key."""
    key = os.getenv("PRIVATE_KEY", DEFAULT_PRIVATE_KEY)
    if not key.startswith("0x"):
        key = f"0x{key}"
    return key


def generate_wallet(private_key: str) -> tuple[str, str]:
    """Generate wallet address and private key."""
    account = Account.from_key(private_key)
    return account.address, private_key


def sign_message(message: str, private_key: str) -> str:
    """Sign a message using the private key."""
    message_hash = encode_defunct(text=message)
    signed = Account.sign_message(message_hash, private_key)
    return signed.signature.hex()


def decode_jwt(token: str) -> dict:
    """Decode JWT without verification (for testing only)."""
    import base64
    parts = token.split('.')
    if len(parts) != 3:
        return {"error": "Invalid JWT format"}

    try:
        # Decode payload (second part)
        payload = parts[1]
        # Add padding if necessary
        padding = 4 - (len(payload) % 4)
        if padding != 4:
            payload += "=" * padding
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        return {"error": f"Failed to decode JWT: {str(e)}"}


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title: str, data: dict) -> None:
    """Print a section with data."""
    print(f"\n{title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ============================================================
# MAIN
# ============================================================

def main():
    print_header("OneWay API Authentication Test")

    # 1. Generate wallet
    print("\n[1] Generating test wallet...")
    private_key = get_private_key()
    wallet_address, _ = generate_wallet(private_key)
    print(f"    Address: {wallet_address}")
    print(f"    Private: {private_key[:10]}...{private_key[-6:]}")

    # 2. Sign message
    print("\n[2] Signing message...")
    signature = sign_message(SIGN_MESSAGE, private_key)
    print(f"    Message: {SIGN_MESSAGE}")
    print(f"    Signature: {signature[:30]}...")

    # 3. Build request
    print("\n[3] Sending request...")
    payload = {
        "wallet_address": wallet_address,
        "message": SIGN_MESSAGE,
        "signature": signature,
    }

    try:
        response = requests.post(AUTH_ENDPOINT, json=payload, timeout=10)
        print(f"    Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print_section("[4] Response", data)

            # Decode JWT
            if "access_token" in data:
                print("\n[5] JWT Payload (decoded):")
                decoded = decode_jwt(data["access_token"])
                print(json.dumps(decoded, indent=2, ensure_ascii=False))

            # Show user info
            if "user" in data:
                print_section("[6] User Data", data["user"])

            print("\n✅ Authentication successful!")
            print(f"   Token expires: {datetime.fromtimestamp(decoded.get('exp', 0)).strftime('%Y-%m-%d %H:%M:%S')}")

        elif response.status_code == 401:
            print("\n❌ Authentication failed: Invalid signature")
            print(f"   Response: {response.text}")

        elif response.status_code == 422:
            print("\n❌ Validation error (check payload fields)")
            print(f"   Response: {response.text}")

        elif response.status_code == 429:
            print("\n⏳ Rate limited: Too many requests")
            print(f"   Response: {response.text}")

        else:
            print(f"\n⚠️  Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("\n❌ Connection error: Make sure the server is running!")
        print(f"   Tried to connect to: {AUTH_ENDPOINT}")
        sys.exit(1)

    except requests.exceptions.Timeout:
        print("\n❌ Timeout: Server did not respond in time.")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()