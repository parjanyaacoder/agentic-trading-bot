#!/usr/bin/env python3
"""
Detailed server connection test
"""

import requests
import socket
import time

def test_port_availability():
    """Test if port 8000 is open"""
    print("🔍 Testing port 8000 availability...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("✅ Port 8000 is open and listening")
            return True
        else:
            print("❌ Port 8000 is not open")
            return False
    except Exception as e:
        print(f"❌ Port test failed: {e}")
        return False

def test_http_connection():
    """Test HTTP connection with different timeouts"""
    print("\n🌐 Testing HTTP connection...")
    
    base_url = "http://localhost:8000"
    
    # Test with different timeouts
    timeouts = [1, 3, 5, 10]
    
    for timeout in timeouts:
        try:
            print(f"📡 Testing with {timeout}s timeout...")
            response = requests.get(f"{base_url}/", timeout=timeout)
            print(f"✅ Success! Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return True
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout after {timeout}s")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection error: {e}")
            return False
        except Exception as e:
            print(f"❌ Other error: {e}")
            return False
    
    return False

def test_different_urls():
    """Test different URLs to see if any work"""
    print("\n🔗 Testing different URLs...")
    
    urls = [
        "http://localhost:8000/",
        "http://127.0.0.1:8000/",
        "http://0.0.0.0:8000/",
        "http://localhost:8000/test",
        "http://localhost:8000/docs"
    ]
    
    for url in urls:
        try:
            print(f"📡 Testing: {url}")
            response = requests.get(url, timeout=3)
            print(f"✅ Success! Status: {response.status_code}")
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    return False

def main():
    print("🧪 Detailed Server Connection Test")
    print("=" * 50)
    
    # Test 1: Port availability
    port_open = test_port_availability()
    
    # Test 2: HTTP connection
    http_working = test_http_connection()
    
    # Test 3: Different URLs
    if not http_working:
        url_working = test_different_urls()
    else:
        url_working = True
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"🔌 Port 8000 open: {'✅ Yes' if port_open else '❌ No'}")
    print(f"🌐 HTTP connection: {'✅ Working' if http_working else '❌ Failed'}")
    print(f"🔗 URL test: {'✅ Working' if url_working else '❌ Failed'}")
    
    if port_open and not http_working:
        print("\n💡 Port is open but HTTP isn't working. This might be a firewall issue.")
    elif not port_open:
        print("\n💡 Port is not open. Make sure the server is running.")
    elif http_working:
        print("\n🎉 Server is working correctly!")

if __name__ == "__main__":
    main() 