#!/usr/bin/env python3
"""
Test script to verify if TIDAL's OAuth device flow works with IP address differences.

This script helps determine if TIDAL validates that all OAuth requests come from the same IP.
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import tidalapi
sys.path.insert(0, str(Path(__file__).parent.parent))

from tidalapi import Session
import requests


def test_oauth_flow_with_different_ips():
    """Test if TIDAL's OAuth flow works when requests come from different IPs"""
    
    print("Testing TIDAL OAuth Device Flow IP Validation")
    print("=" * 50)
    
    # Create a session with a proxy for the initial request
    session = Session()
    
    # You can test this by:
    # 1. Using a proxy for the device authorization request
    # 2. Using your normal IP for browser authentication  
    # 3. Using the proxy again for polling
    
    print("Step 1: Getting device authorization (this request shows your current IP)")
    
    # Show current IP
    try:
        response = requests.get("https://httpbin.org/ip")
        current_ip = response.json()["origin"]
        print(f"Current IP address: {current_ip}")
    except:
        print("Could not determine current IP")
    
    # Get device authorization
    try:
        link_login = session.get_link_login()
        print(f"✅ Device authorization successful!")
        print(f"Verification URL: {link_login.verification_uri_complete}")
        print(f"Device Code: {link_login.device_code[:10]}...")
        print(f"Expires in: {link_login.expires_in} seconds")
        
        print("\nStep 2: Manual test instructions")
        print("-" * 30)
        print("To test IP validation:")
        print("1. Use a VPN or proxy to change your IP address")
        print("2. Open the verification URL in your browser with the new IP")
        print("3. Complete the authentication")
        print("4. Return here and press Enter to continue polling")
        print("\nIf TIDAL allows this, then IP validation is not enforced.")
        print("If it fails, then TIDAL requires consistent IP addresses.")
        
        input("\nPress Enter after completing browser authentication...")
        
        print("\nStep 3: Polling for completion (checking with original IP)")
        # Try to complete the login
        try:
            result = session._check_link_login(link_login, until_expiry=False)
            print("✅ Polling successful! IP validation is NOT enforced by TIDAL.")
            print("This means proxy-based OAuth should work fine.")
            
            # Complete the process
            if session.process_auth_token(result, is_pkce_token=False):
                print(f"✅ Full login successful!")
                print(f"Session ID: {session.session_id}")
                print(f"User: {session.user.id if session.user else 'Unknown'}")
                
        except Exception as e:
            if "authorization_pending" in str(e).lower():
                print("⏳ Authentication still pending - user may not have completed browser auth")
            elif "access_denied" in str(e).lower():
                print("❌ Access denied - possible IP validation failure")
                print("TIDAL may be enforcing IP consistency")
            else:
                print(f"❌ Error during polling: {e}")
                
    except Exception as e:
        print(f"❌ Device authorization failed: {e}")


def test_with_proxy_simulation():
    """Simulate the proxy scenario more directly"""
    
    print("\nTesting Proxy Scenario Simulation")
    print("=" * 35)
    
    session1 = Session()  # Simulates proxy requests
    session2 = Session()  # Simulates direct browser requests
    
    # Get device code with "proxy" session
    print("Getting device code (simulating proxy request)...")
    try:
        link_login = session1.get_link_login()
        print(f"✅ Device code obtained: {link_login.device_code[:10]}...")
        
        print(f"\nNow open this URL in your browser: {link_login.verification_uri_complete}")
        print("Complete the authentication, then return here.")
        
        input("Press Enter after completing authentication...")
        
        # Poll with different session object (simulating different IP)
        print("Polling with different session (simulating proxy)...")
        
        # Manual polling attempt
        import requests
        url = session1.config.api_oauth2_token
        params = {
            "client_id": session1.config.client_id,
            "client_secret": session1.config.client_secret,
            "device_code": link_login.device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "scope": "r_usr w_usr w_sub",
        }
        
        response = requests.post(url, params)
        result = response.json()
        
        if response.ok:
            print("✅ Success! TIDAL doesn't enforce strict IP validation")
            print("Proxy-based OAuth should work fine")
        else:
            print(f"❌ Failed: {result}")
            if "invalid_grant" in result.get("error", ""):
                print("This might indicate IP validation or expired code")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    print("TIDAL OAuth IP Validation Test")
    print("This test helps determine if proxy-based OAuth will work")
    print()
    
    choice = input("Choose test type:\n1. Manual IP change test\n2. Simulation test\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_oauth_flow_with_different_ips()
    elif choice == "2":
        test_with_proxy_simulation()
    else:
        print("Invalid choice. Running manual test...")
        test_oauth_flow_with_different_ips()
