#!/usr/bin/env python3
"""
Standalone SMS Test Utility
============================
Sends a single test SMS via the Fast2SMS infrastructure service to verify
that the API key, route, and network connectivity are working.

Usage:
    python -m scripts.test_sms_system          (from backend/)
    python scripts/test_sms_system.py          (from backend/)
"""

import sys
from pathlib import Path

# Ensure the backend package root is on sys.path so that
# `app.infrastructure.sms_service` can be resolved regardless of
# how this script is invoked.
BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.infrastructure.sms_service import send_sms  # noqa: E402


def main() -> None:
    test_number = "917880601408"
    test_message = (
        "CIVIX-AI [TEST]: This is an automated system verification message. "
        "If you received this, the SMS gateway is operational."
    )

    print("=" * 60)
    print("  CIVIX-AI — SMS Gateway Test")
    print("=" * 60)
    print(f"  Recipient : {test_number}")
    print(f"  Message   : {test_message}")
    print("-" * 60)
    print("  Sending …")

    result = send_sms(test_number, test_message)

    print("-" * 60)
    if result.get("error"):
        print(f"  ❌ FAILED  : {result.get('message', result)}")
        sys.exit(1)
    else:
        print(f"  ✅ SUCCESS : {result}")
    print("=" * 60)


if __name__ == "__main__":
    main()
