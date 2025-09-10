#!/usr/bin/env python3

import requests
import sys

def test_backend_endpoints():
    """Test the actual backend endpoints that exist"""
    base_url = "http://localhost:8001"  # Internal backend port
    
    print("🚀 Testing Backend Endpoints")
    print("=" * 40)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Root endpoint
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint (/) - Status: 200")
            print(f"   Response: {response.json()}")
            tests_passed += 1
        else:
            print(f"❌ Root endpoint (/) - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint (/) - Error: {e}")
    
    # Test 2: Health check endpoint
    tests_total += 1
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ Health endpoint (/api/health) - Status: 200")
            print(f"   Response: {response.json()}")
            tests_passed += 1
        else:
            print(f"❌ Health endpoint (/api/health) - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint (/api/health) - Error: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Results: {tests_passed}/{tests_total} tests passed")
    
    return tests_passed == tests_total

if __name__ == "__main__":
    success = test_backend_endpoints()
    sys.exit(0 if success else 1)