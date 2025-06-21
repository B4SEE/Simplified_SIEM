#!/usr/bin/env python3
"""
Simple test script to verify the alert generator is working.
"""

import requests
import json
from datetime import datetime

# Test the alert generator by sending logs directly to the logging service
LOGGING_SERVICE_URL = "http://localhost:5000/api/logs"

def test_alert_generator():
    print("🧪 Testing Alert Generator")
    print("=" * 40)
    
    # Send 4 failed logins from the same IP (should trigger bruteforce alarm)
    test_ip = "192.168.1.100"
    
    for i in range(4):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': test_ip,
            'event_type': 'login_failed',
            'user_ID': 3,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'geo': [40.7128, -74.0060],  # New York
            'severity': 'high',
            'additional_data': {
                'test_mode': True,
                'test_scenario': 'alert_generator_test'
            }
        }
        
        try:
            response = requests.post(
                LOGGING_SERVICE_URL,
                json=log_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Log {i+1} sent successfully")
            else:
                print(f"❌ Failed to send log {i+1}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error sending log {i+1}: {e}")
    
    print("\n📊 Now check your SIEM dashboard for automatically generated alarms!")
    print("   The alert generator should have created a 'Bruteforce Attack Detected' alarm.")

if __name__ == "__main__":
    test_alert_generator() 