#!/usr/bin/env python3
"""
Simple API test script
"""

import requests
import time
import subprocess
import sys
import os

def test_api_endpoints():
    """Test API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing API Endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
        return False
    
    # Test grants endpoint
    try:
        response = requests.get(f"{base_url}/grants")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Grants endpoint working - {data['count']} grants found")
        else:
            print(f"❌ Grants endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Grants endpoint error: {e}")
        return False
    
    # Test stats endpoint
    try:
        response = requests.get(f"{base_url}/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats endpoint working - {data['total_grants']} total grants")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats endpoint error: {e}")
        return False
    
    # Test filtering
    try:
        response = requests.get(f"{base_url}/grants?bucket=Early Stage")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Filtering working - {data['count']} Early Stage grants")
        else:
            print(f"❌ Filtering failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Filtering error: {e}")
        return False
    
    print("🎉 All API endpoints working correctly!")
    return True

def start_api_server():
    """Start the API server in background"""
    print("🚀 Starting API server...")
    
    # Start the server in background
    process = subprocess.Popen([
        sys.executable, "main.py", "--mode", "api"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    return process

def main():
    """Main test function"""
    print("🚀 Starting API Test...")
    
    # Start API server
    server_process = start_api_server()
    
    try:
        # Test API endpoints
        success = test_api_endpoints()
        
        if success:
            print("\n🎉 API test completed successfully!")
            print("\nAPI server is running on http://localhost:5000")
            print("You can test it manually:")
            print("  - Health: http://localhost:5000/health")
            print("  - Grants: http://localhost:5000/grants")
            print("  - Stats: http://localhost:5000/stats")
        else:
            print("\n❌ API test failed!")
            
    finally:
        # Clean up
        print("Stopping API server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    main() 