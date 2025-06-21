"""
Alert Generator for SIEM Testing
===============================

Generates alarms for basic security scenarios:
- Login bruteforce attempts
- Distributed access attempts  
- Unusual login patterns
- High-frequency events

Simple implementation for testing alarm functionality.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import requests
from threading import Thread, Lock

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertGenerator:
    """
    Simple alert generator for testing basic security scenarios.
    """
    
    def __init__(self, 
                 auth_service_url: str = "http://auth_service:5000/api/alarms",
                 test_user_id: int = 3,
                 test_token: str = "9b2149b1-1e29-481e-8be1-ab33b6270042"):
        
        self.auth_service_url = auth_service_url
        self.test_user_id = test_user_id
        self.test_token = test_token
        
        # Simple tracking for test scenarios
        self.ip_failed_logins = defaultdict(int)  # IP -> failed login count
        self.user_ip_mapping = defaultdict(set)   # User -> set of IPs
        self.ip_event_count = defaultdict(int)    # IP -> total event count
        self.user_locations = {}  # User -> last known location
        
        # Test-specific thresholds
        self.thresholds = {
            'bruteforce': 3,        # 3 failed logins = bruteforce
            'distributed': 5,       # 5 different IPs = distributed access
            'high_frequency': 10,   # 10 events = high frequency
            'unusual_location': 1000  # 1000km = unusual location
        }
        
        # Time windows (in minutes)
        self.time_windows = {
            'bruteforce': 5,
            'distributed': 10, 
            'high_frequency': 2
        }
        
        # Track recent events with timestamps
        self.recent_events = deque(maxlen=500)
        self.lock = Lock()
        
        # Track created alarms to avoid duplicates
        self.created_alarms = set()
        
        logger.info("Simplified Alert Generator initialized")
    
    def add_event(self, log_entry: Dict[str, Any]) -> None:
        """
        Add a new log event for analysis.
        """
        with self.lock:
            # Add to recent events
            self.recent_events.append(log_entry)
            
            # Extract key information
            timestamp = self._parse_timestamp(log_entry.get('timestamp'))
            ip_address = log_entry.get('ip_address')
            event_type = log_entry.get('event_type')
            user_id = log_entry.get('user_ID')
            geo = log_entry.get('geo')
            
            if not all([timestamp, ip_address, event_type]):
                return
            
            # Update tracking
            if event_type == 'login_failed':
                self.ip_failed_logins[ip_address] += 1
            
            if user_id:
                self.user_ip_mapping[user_id].add(ip_address)
                
                if geo and event_type == 'login_success':
                    self.user_locations[user_id] = geo
            
            self.ip_event_count[ip_address] += 1
            
            # Clean old data
            self._cleanup_old_data(timestamp)
            
            # Check for test scenarios
            self._check_test_scenarios(log_entry)
    
    def _parse_timestamp(self, timestamp) -> datetime:
        """Parse timestamp string to datetime object."""
        if isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                return datetime.utcnow()
        elif isinstance(timestamp, datetime):
            return timestamp
        else:
            return datetime.utcnow()
    
    def _cleanup_old_data(self, current_time: datetime) -> None:
        """Remove old data outside of analysis windows."""
        cutoff_time = current_time - timedelta(minutes=max(self.time_windows.values()))
        
        # Clean recent events
        while self.recent_events and self._parse_timestamp(self.recent_events[0].get('timestamp')) < cutoff_time:
            old_event = self.recent_events.popleft()
            
            # Update counters
            if old_event.get('event_type') == 'login_failed':
                ip = old_event.get('ip_address')
                if ip in self.ip_failed_logins:
                    self.ip_failed_logins[ip] = max(0, self.ip_failed_logins[ip] - 1)
            
            # Update event count
            ip = old_event.get('ip_address')
            if ip in self.ip_event_count:
                self.ip_event_count[ip] = max(0, self.ip_event_count[ip] - 1)
    
    def _check_test_scenarios(self, log_entry: Dict[str, Any]) -> None:
        """Check for the four core test scenarios."""
        ip_address = log_entry.get('ip_address')
        user_id = log_entry.get('user_ID')
        event_type = log_entry.get('event_type')
        geo = log_entry.get('geo')
        
        # 1. Bruteforce detection
        if self.ip_failed_logins[ip_address] >= self.thresholds['bruteforce']:
            alarm_key = f"bruteforce_{ip_address}"
            if alarm_key not in self.created_alarms:
                self._create_alarm('bruteforce', {
                    'ip_address': ip_address,
                    'failed_count': self.ip_failed_logins[ip_address],
                    'description': f'Bruteforce attack detected from {ip_address}'
                })
                self.created_alarms.add(alarm_key)
        
        # 2. Distributed access detection
        if user_id and len(self.user_ip_mapping[user_id]) >= self.thresholds['distributed']:
            alarm_key = f"distributed_{user_id}"
            if alarm_key not in self.created_alarms:
                self._create_alarm('distributed', {
                    'user_ID': user_id,
                    'ip_count': len(self.user_ip_mapping[user_id]),
                    'ips': list(self.user_ip_mapping[user_id]),
                    'description': f'User {user_id} accessing from {len(self.user_ip_mapping[user_id])} different IPs'
                })
                self.created_alarms.add(alarm_key)
        
        # 3. High-frequency events
        if self.ip_event_count[ip_address] >= self.thresholds['high_frequency']:
            alarm_key = f"high_freq_{ip_address}"
            if alarm_key not in self.created_alarms:
                self._create_alarm('high_frequency', {
                    'ip_address': ip_address,
                    'event_count': self.ip_event_count[ip_address],
                    'description': f'High frequency events from {ip_address}'
                })
                self.created_alarms.add(alarm_key)
        
        # 4. Unusual login location (if we have geo data)
        if event_type == 'login_success' and user_id and geo and user_id in self.user_locations:
            last_geo = self.user_locations[user_id]
            if last_geo != geo:  # Different location
                distance = self._calculate_distance(last_geo, geo)
                if distance > self.thresholds['unusual_location']:
                    alarm_key = f"unusual_location_{user_id}_{ip_address}"
                    if alarm_key not in self.created_alarms:
                        self._create_alarm('unusual_location', {
                            'user_ID': user_id,
                            'ip_address': ip_address,
                            'distance_km': distance,
                            'description': f'Unusual login location for user {user_id} from {ip_address}'
                        })
                        self.created_alarms.add(alarm_key)
    
    def _calculate_distance(self, geo1: tuple, geo2: tuple) -> float:
        """Calculate distance between two geo coordinates in km."""
        try:
            from geopy.distance import geodesic
            return geodesic(geo1, geo2).kilometers
        except:
            return 0
    
    def _create_alarm(self, alarm_type: str, details: Dict[str, Any]) -> None:
        """Create an alarm via the auth service API."""
        try:
            alarm_data = {
                "name": f"{alarm_type.title()} Alert",
                "description": details.get('description', f'{alarm_type} detected'),
                "severity": "high" if alarm_type in ['bruteforce', 'unusual_location'] else "medium",
                "user_ID": self.test_user_id,
                "details": details
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.test_token}"
            }
            
            response = requests.post(
                self.auth_service_url,
                json=alarm_data,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 201:
                logger.info(f"Created {alarm_type} alarm: {details}")
            else:
                logger.warning(f"Failed to create {alarm_type} alarm: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error creating {alarm_type} alarm: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current statistics for monitoring."""
        with self.lock:
            return {
                "total_events": len(self.recent_events),
                "failed_logins": dict(self.ip_failed_logins),
                "user_ip_mapping": {str(k): list(v) for k, v in self.user_ip_mapping.items()},
                "ip_event_counts": dict(self.ip_event_count),
                "created_alarms": len(self.created_alarms)
            }

# Global instance
_alert_generator = None

def initialize_alert_generator(auth_service_url: str = None, test_user_id: int = None, test_token: str = None) -> AlertGenerator:
    """Initialize the global alert generator instance."""
    global _alert_generator
    if _alert_generator is None:
        _alert_generator = AlertGenerator(
            auth_service_url=auth_service_url or "http://auth_service:5000/api/alarms",
            test_user_id=test_user_id or 3,
            test_token=test_token or "9b2149b1-1e29-481e-8be1-ab33b6270042"
        )
    return _alert_generator

def process_log_entry(log_entry: Dict[str, Any]) -> None:
    """Process a log entry through the alert generator."""
    if _alert_generator:
        _alert_generator.add_event(log_entry)

def get_alert_generator() -> Optional[AlertGenerator]:
    """Get the global alert generator instance."""
    return _alert_generator
