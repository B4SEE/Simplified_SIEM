#!/usr/bin/env python3
"""
Alarm Test Script for SIEM
==========================

Tests basic alarm scenarios:
- Login bruteforce attempts
- Distributed access attempts  
- Unusual login patterns
- High-frequency events

Usage:
    python alarm_test_script.py --scenario bruteforce --count 10
    python alarm_test_script.py --scenario distributed --ips 8
    python alarm_test_script.py --scenario unusual --distance 1000
    python alarm_test_script.py --scenario high-frequency --events 30
"""

import argparse
import json
import random
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
import sys

print('>>> Simplified alarm test script is running')

# Configuration
LOGGING_SERVICE_URL = "http://localhost:5000/api/logs"
AUTH_SERVICE_URL = "http://localhost:5001/api/alarms"
TEST_USER_ID = 1
TEST_TOKEN = "test_token"

# Test data
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0"
]

# Common IP ranges for testing
PRIVATE_IPS = [f"192.168.1.{i}" for i in range(1, 255)]
PUBLIC_IPS = [
    "203.0.113.1", "203.0.113.2", "203.0.113.3", "203.0.113.4", "203.0.113.5",
    "198.51.100.1", "198.51.100.2", "198.51.100.3", "198.51.100.4", "198.51.100.5",
    "10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5"
]

# Geographic coordinates for unusual login testing
GEO_LOCATIONS = [
    (40.7128, -74.0060),  # New York
    (34.0522, -118.2437), # Los Angeles
    (51.5074, -0.1278),   # London
    (48.8566, 2.3522),    # Paris
    (35.6762, 139.6503),  # Tokyo
    (-33.8688, 151.2093), # Sydney
    (-23.5505, -46.6333), # São Paulo
    (55.7558, 37.6176),   # Moscow
    (39.9042, 116.4074),  # Beijing
    (28.6139, 77.2090)    # New Delhi
]

class AlarmTestScript:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.test_results = []
        
    def log(self, message: str):
        """Print log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
            
    def send_log(self, log_data: Dict[str, Any]) -> bool:
        """Send a log entry to the logging service"""
        try:
            # Add test marker
            log_data['additional_data'] = {
                'test_mode': True,
                'test_timestamp': datetime.utcnow().isoformat(),
                'test_scenario': getattr(self, 'current_scenario', 'unknown')
            }
            
            response = requests.post(
                LOGGING_SERVICE_URL,
                json=log_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log(f"Log sent successfully: {log_data['event_type']}")
                return True
            else:
                print(f"Failed to send log: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending log: {e}")
            return False
    
    def create_login_log(self, event_type: str, ip_address: str, user_id: int = TEST_USER_ID, 
                        geo: Optional[Tuple[float, float]] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
        """Create a login event log entry"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': ip_address,
            'event_type': event_type,
            'user_ID': user_id,
            'user_agent': user_agent or random.choice(USER_AGENTS),
            'geo': geo or (random.uniform(-90, 90), random.uniform(-180, 180)),
            'severity': 'high' if event_type == 'login_failed' else 'low'
        }
    
    def test_bruteforce_scenario(self, count: int = 10, delay: float = 0.1):
        """Test login bruteforce scenario - multiple failed logins from same IP"""
        print(f"\nTesting Bruteforce Scenario: {count} failed logins")
        print("=" * 50)
        
        self.current_scenario = "bruteforce"
        attack_ip = random.choice(PUBLIC_IPS)
        success_count = 0
        
        for i in range(count):
            log_data = self.create_login_log(
                event_type='login_failed',
                ip_address=attack_ip,
                user_agent=random.choice(USER_AGENTS)
            )
            
            if self.send_log(log_data):
                success_count += 1
                print(f"  {i+1:2d}. Failed login from {attack_ip}")
            
            time.sleep(delay)
        
        print(f"\nBruteforce test completed: {success_count}/{count} logs sent")
        print(f"   Attack IP: {attack_ip}")
        self.test_results.append({
            'scenario': 'bruteforce',
            'success_count': success_count,
            'total_count': count,
            'attack_ip': attack_ip
        })
    
    def test_distributed_scenario(self, user_count: int = 3, ip_count: int = 10, delay: float = 0.1):
        """Test distributed access scenario - same user from multiple IPs"""
        print(f"\nTesting Distributed Access Scenario: User from {ip_count} IPs")
        print("=" * 50)
        
        self.current_scenario = "distributed"
        attack_ips = random.sample(PUBLIC_IPS, min(ip_count, len(PUBLIC_IPS)))
        success_count = 0
        
        for i, ip in enumerate(attack_ips):
            log_data = self.create_login_log(
                event_type='login_success',
                ip_address=ip,
                user_agent=random.choice(USER_AGENTS)
            )
            
            if self.send_log(log_data):
                success_count += 1
                print(f"  {i+1:2d}. Login from {ip}")
            
            time.sleep(delay)
        
        print(f"\nDistributed access test completed: {success_count}/{len(attack_ips)} logs sent")
        print(f"   User ID: {TEST_USER_ID}")
        print(f"   IPs used: {len(attack_ips)}")
        self.test_results.append({
            'scenario': 'distributed',
            'success_count': success_count,
            'total_count': len(attack_ips),
            'user_id': TEST_USER_ID,
            'ips_used': len(attack_ips)
        })
    
    def test_unusual_login_scenario(self, distance_km: int = 1000, delay: float = 0.1):
        """Test unusual login location scenario - login from distant location"""
        print(f"\nTesting Unusual Login Scenario: Login from {distance_km}km away")
        print("=" * 50)
        
        self.current_scenario = "unusual_login"
        
        # Get two distant locations
        location1, location2 = random.sample(GEO_LOCATIONS, 2)
        
        # First login from normal location
        log_data1 = self.create_login_log(
            event_type='login_success',
            ip_address=random.choice(PRIVATE_IPS),
            geo=location1
        )
        
        if self.send_log(log_data1):
            print(f"  1. Normal login from {location1}")
            time.sleep(delay)
            
            # Second login from distant location
            log_data2 = self.create_login_log(
                event_type='login_success',
                ip_address=random.choice(PUBLIC_IPS),
                geo=location2
            )
            
            if self.send_log(log_data2):
                print(f"  2. Unusual login from {location2}")
        
        print(f"\nUnusual login test completed")
        print(f"   From: {location1}")
        print(f"   To: {location2}")
        self.test_results.append({
            'scenario': 'unusual_login',
            'success_count': 2,
            'total_count': 2,
            'from_location': location1,
            'to_location': location2
        })
    
    def test_high_frequency_scenario(self, event_count: int = 50, delay: float = 0.05):
        """Test high-frequency events scenario - many events from same IP"""
        print(f"\nTesting High-Frequency Scenario: {event_count} events from same IP")
        print("=" * 50)
        
        self.current_scenario = "high_frequency"
        attack_ip = random.choice(PUBLIC_IPS)
        success_count = 0
        
        # Mix of different event types for high frequency
        event_types = ['login_success', 'login_failed', 'password_reset', 'profile_updated']
        
        for i in range(event_count):
            log_data = self.create_login_log(
                event_type=random.choice(event_types),
                ip_address=attack_ip,
                user_agent=random.choice(USER_AGENTS)
            )
            
            if self.send_log(log_data):
                success_count += 1
                if i % 10 == 0:  # Print every 10th event
                    print(f"  {i+1:2d}. Event from {attack_ip}")
            
            time.sleep(delay)
        
        print(f"\nHigh-frequency test completed: {success_count}/{event_count} events sent")
        print(f"   Attack IP: {attack_ip}")
        self.test_results.append({
            'scenario': 'high_frequency',
            'success_count': success_count,
            'total_count': event_count,
            'attack_ip': attack_ip
        })
    
    def check_alarms(self):
        """Check if any alarms were triggered (optional)"""
        try:
            response = requests.get(
                AUTH_SERVICE_URL,
                headers={
                    'Authorization': f'Bearer {TEST_TOKEN}',
                    'X-User-Id': str(TEST_USER_ID)
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    alarms = data.get('alarms', [])
                    print(f"\nAlarm Status: {len(alarms)} alarms found")
                    for alarm in alarms:
                        print(f"   - {alarm['name']}: {alarm['event_type']} (Active: {alarm['is_active']})")
                    return alarms
                else:
                    print(f"Failed to get alarms: {data.get('message', 'Unknown error')}")
            else:
                print(f"Failed to check alarms: {response.status_code}")
                
        except Exception as e:
            print(f"Error checking alarms: {e}")
        
        return []
    
    def run_scenario(self, scenario: str, **kwargs):
        """Run a specific test scenario"""
        scenario_methods = {
            'bruteforce': self.test_bruteforce_scenario,
            'distributed': self.test_distributed_scenario,
            'unusual': self.test_unusual_login_scenario,
            'high-frequency': self.test_high_frequency_scenario
        }
        
        if scenario not in scenario_methods:
            print(f"Unknown scenario: {scenario}")
            print(f"Available scenarios: {', '.join(scenario_methods.keys())}")
            return
        
        method = scenario_methods[scenario]
        method(**kwargs)
    
    def run_all_scenarios(self, delay: float = 0.5):
        """Run all four core test scenarios"""
        print("Running All Core Test Scenarios")
        print("=" * 60)
        
        scenarios = [
            ('bruteforce', {'count': 8}),
            ('distributed', {'ip_count': 8}),
            ('unusual', {'distance_km': 1000}),
            ('high-frequency', {'event_count': 30})
        ]
        
        for scenario, params in scenarios:
            self.run_scenario(scenario, **params)
            time.sleep(delay)  # Pause between scenarios
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_logs = sum(result.get('success_count', 0) for result in self.test_results)
        total_tests = len(self.test_results)
        
        print(f"Total scenarios tested: {total_tests}")
        print(f"Total logs sent: {total_logs}")
        print(f"Test user ID: {TEST_USER_ID}")
        print(f"Test timestamp: {datetime.now().isoformat()}")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            scenario = result['scenario']
            success = result.get('success_count', 0)
            total = result.get('total_count', 0)
            print(f"  {scenario:20s}: {success}/{total} logs sent")
        
        print("\nNext Steps:")
        print("  1. Check the alarms page in your SIEM dashboard")
        print("  2. Review the logs page for test entries")
        print("  3. Verify that alarms were triggered for the test scenarios")
        print("  4. Check alarm thresholds and time windows")

def main():
    parser = argparse.ArgumentParser(description='Simplified Alarm Test Script for SIEM')
    parser.add_argument('--scenario', choices=[
        'bruteforce', 'distributed', 'unusual', 'high-frequency', 'all'
    ], default='all', help='Test scenario to run')
    
    parser.add_argument('--count', type=int, default=10, help='Number of events to generate')
    parser.add_argument('--users', type=int, default=3, help='Number of users for distributed test')
    parser.add_argument('--ips', type=int, default=10, help='Number of IPs for distributed test')
    parser.add_argument('--distance', type=int, default=1000, help='Distance in km for unusual login')
    parser.add_argument('--events', type=int, default=50, help='Number of events for high-frequency test')
    parser.add_argument('--delay', type=float, default=0.1, help='Delay between events in seconds')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--check-alarms', action='store_true', help='Check alarm status after tests')
    
    args = parser.parse_args()
    
    # Create test script instance
    script = AlarmTestScript(verbose=args.verbose)
    
    try:
        print("Simplified Alarm Test Script for SIEM")
        print("=" * 60)
        print(f"Logging Service: {LOGGING_SERVICE_URL}")
        print(f"Auth Service: {AUTH_SERVICE_URL}")
        print(f"Test User ID: {TEST_USER_ID}")
        print(f"Scenario: {args.scenario}")
        print("=" * 60)
        
        # Run the specified scenario
        if args.scenario == 'all':
            script.run_all_scenarios(delay=args.delay)
        else:
            # Create scenario-specific parameter dictionaries
            if args.scenario == 'bruteforce':
                params = {'count': args.count, 'delay': args.delay}
            elif args.scenario == 'distributed':
                params = {'user_count': args.users, 'ip_count': args.ips, 'delay': args.delay}
            elif args.scenario == 'unusual':
                params = {'distance_km': args.distance, 'delay': args.delay}
            elif args.scenario == 'high-frequency':
                params = {'event_count': args.events, 'delay': args.delay}
            else:
                params = {'delay': args.delay}
            
            script.run_scenario(args.scenario, **params)
        
        # Check alarms if requested
        if args.check_alarms:
            print("\nChecking alarm status...")
            script.check_alarms()
        
        # Print summary
        script.print_summary()
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        script.print_summary()
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 