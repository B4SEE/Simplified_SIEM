from datetime import datetime, timedelta, timezone
from collections import defaultdict
from dateutil import parser
from geopy.distance import geodesic
import logging
import ipaddress
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def is_private_ip(ip):
    """Check if an IP address is private."""
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False

def calculate_velocity(geo1, geo2, time1, time2):
    """Calculate the velocity between two points in km/h."""
    try:
        distance = geodesic(geo1, geo2).kilometers
        time_diff = (time2 - time1).total_seconds() / 3600  # Convert to hours
        if time_diff > 0:
            return distance / time_diff
        return float('inf')
    except (ValueError, TypeError):
        return 0

def analyze_logs(log_entries, user_data, reference_time=None, time_window_minutes=5, thresholds=None, distance_threshold_km=500):
    """
    Enhanced log analysis with advanced security features.

    #### Args:
        log_entries (list): List of log dictionaries with 'timestamp', 'ip_address', 'event_type', 'user_ID', and 'geo'.
        user_data (dict): Maps user_ID to their last known login geo location (tuple: latitude, longitude).
        reference_time (datetime, optional): End of the time window.
        time_window_minutes (int): Time window size in minutes.
        thresholds (dict, optional): Event types and their alert thresholds.
        distance_threshold_km (int): Distance threshold in kilometers for unusual login detection.

    #### Returns:
        list: List of alert dictionaries detailing detected anomalies.
    """
    logging.info("Starting enhanced log analysis")
    
    if reference_time is None:
        reference_time = datetime.now(timezone.utc)
    elif reference_time.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=timezone.utc)

    if thresholds is None:
        thresholds = {
            "login_failed": 5,      # Excessive failed logins
            "password_reset": 3,    # Excessive password resets
            "profile_updated": 3,   # Excessive profile updates
            "password_changed": 2   # Excessive password changes
        }

    window_start = reference_time - timedelta(minutes=time_window_minutes)
    alerts = []
    
    # Enhanced tracking dictionaries
    event_counts = defaultdict(lambda: defaultdict(int))
    user_sessions = defaultdict(list)  # Track user sessions for impossible travel
    ip_user_mapping = defaultdict(set)  # Track IPs used by each user
    user_ip_mapping = defaultdict(set)  # Track users per IP
    suspicious_patterns = defaultdict(int)  # Track suspicious patterns
    user_agents = defaultdict(set)  # Track user agents per user

    # Process logs chronologically
    sorted_logs = sorted(log_entries, key=lambda x: parser.isoparse(x["timestamp"]))
    
    for entry in sorted_logs:
        try:
            ts = parser.isoparse(entry["timestamp"])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            else:
                ts = ts.astimezone(timezone.utc)
            
            if window_start <= ts <= reference_time:
                ip = entry["ip_address"]
                event_type = entry["event_type"]
                user_id = entry.get("user_ID")
                geo = entry.get("geo")
                user_agent = entry.get("user_agent", "")

                # Basic threshold monitoring
                if event_type in thresholds:
                    event_counts[event_type][ip] += 1

                if user_id:
                    # Track user sessions
                    user_sessions[user_id].append((ts, geo, ip))
                    ip_user_mapping[ip].add(user_id)
                    user_ip_mapping[user_id].add(ip)
                    user_agents[user_id].add(user_agent)

                    # Check for impossible travel
                    if len(user_sessions[user_id]) >= 2:
                        prev_session = user_sessions[user_id][-2]
                        if prev_session[1] and geo:  # If both have geo data
                            velocity = calculate_velocity(
                                prev_session[1], geo,
                                prev_session[0], ts
                            )
                            if velocity > 1000:  # Faster than commercial airplane
                                alerts.append({
                                    "alert_type": "impossible_travel",
                                    "user_ID": user_id,
                                    "velocity_kmh": velocity,
                                    "from_ip": prev_session[2],
                                    "to_ip": ip,
                                    "from_geo": prev_session[1],
                                    "to_geo": geo,
                                    "severity": "high"
                                })

                    # Check for multiple user agents
                    if len(user_agents[user_id]) > 3:
                        alerts.append({
                            "alert_type": "multiple_user_agents",
                            "user_ID": user_id,
                            "count": len(user_agents[user_id]),
                            "user_agents": list(user_agents[user_id]),
                            "severity": "medium"
                        })

                # Check for account sharing (multiple users from same IP)
                if len(ip_user_mapping[ip]) > 3:
                    alerts.append({
                        "alert_type": "potential_account_sharing",
                        "ip_address": ip,
                        "user_count": len(ip_user_mapping[ip]),
                        "users": list(ip_user_mapping[ip]),
                        "severity": "medium"
                    })

                # Check for distributed access (user logging in from many IPs)
                if len(user_ip_mapping.get(user_id, set())) > 5:
                    alerts.append({
                        "alert_type": "distributed_access",
                        "user_ID": user_id,
                        "ip_count": len(user_ip_mapping[user_id]),
                        "ips": list(user_ip_mapping[user_id]),
                        "severity": "high"
                    })

                # Detect unusual login locations
                if event_type == "login_success" and user_id in user_data:
                    last_geo = user_data[user_id]
                    if last_geo and geo:
                        distance = geodesic(last_geo, geo).kilometers
                        if distance > distance_threshold_km:
                            alerts.append({
                                "alert_type": "unusual_login_location",
                                "user_ID": user_id,
                                "ip_address": ip,
                                "distance_km": distance,
                                "last_login_geo": last_geo,
                                "current_geo": geo,
                                "severity": "high" if distance > 1000 else "medium"
                            })

                # Check for suspicious IP addresses
                if not is_private_ip(ip):
                    suspicious_patterns[ip] += 1

        except (KeyError, ValueError) as e:
            logging.warning(f"Skipping malformed log entry: {entry}. Error: {e}")
            continue

    # Generate threshold-based alerts
    for event_type, ips in event_counts.items():
        threshold = thresholds[event_type]
        for ip, count in ips.items():
            if count >= threshold:
                alerts.append({
                    "alert_type": f"excessive_{event_type}",
                    "ip_address": ip,
                    "count": count,
                    "severity": "high" if count >= threshold * 2 else "medium"
                })

    # Alert on suspicious patterns
    for ip, count in suspicious_patterns.items():
        if count > 10:  # More than 10 events from a public IP
            alerts.append({
                "alert_type": "suspicious_ip_activity",
                "ip_address": ip,
                "event_count": count,
                "severity": "medium"
            })

    # Sort alerts by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    alerts.sort(key=lambda x: severity_order[x["severity"]])

    logging.info(f"Analysis complete. Generated {len(alerts)} alerts")
    return alerts