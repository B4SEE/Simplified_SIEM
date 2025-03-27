from datetime import datetime, timedelta, timezone
from collections import defaultdict
from dateutil import parser
from geopy.distance import geodesic
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# NOTE: The logic for the analyze_logs function is overly simplified
def analyze_logs(log_entries, user_data, reference_time=None, time_window_minutes=5, thresholds=None, distance_threshold_km=500):
    """
    Analyze log entries to detect anomalies based on event thresholds and geographical distances.

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

    logging.info("Starting log analysis")
    
    # Ensure reference_time is provided and timezone-aware
    if reference_time is None:
        reference_time = datetime.now(timezone.utc)
        logging.debug("Reference time not provided. Using current UTC time.")
    elif reference_time.tzinfo is None:
        reference_time = reference_time.replace(tzinfo=timezone.utc)
        logging.debug("Reference time was naive. Converted to timezone-aware.")

    # Set a default threshold if not provided
    if thresholds is None:
        thresholds = {
            "login_failed": 5,   # Threshold for excessive failed logins
            "password_reset": 3  # Threshold for excessive password resets
        }
        logging.debug("Thresholds not provided. Using default thresholds.")

    # Calculate the start of the window
    window_start = reference_time - timedelta(minutes=time_window_minutes)
    logging.info(f"Analyzing logs within the time window: {window_start} to {reference_time}")

    alerts = []
    event_counts = defaultdict(lambda: defaultdict(int))

    # Process each log entry
    for entry in log_entries:
        try:
            # Parse the timestamp
            ts = parser.isoparse(entry["timestamp"])
            # Ensure ts is aware and in UTC:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            else:
                ts = ts.astimezone(timezone.utc)
            
            if window_start <= ts <= reference_time:
                ip = entry["ip_address"]
                event_type = entry["event_type"]
                user_id = entry.get("user_ID")
                geo = entry.get("geo")

                logging.debug(f"Processing log entry: {entry}")

                # IP-based threshold alerts
                if event_type in thresholds:
                    event_counts[event_type][ip] += 1

                # Detect unusual login locations for successful logins
                if event_type == "login_success" and user_id in user_data and user_data[user_id] is not None:
                    last_geo = user_data[user_id]
                    current_geo = geo
                    if last_geo and current_geo:
                        distance = geodesic(last_geo, current_geo).kilometers
                        logging.info(f"User {user_id} logged in from a new location. Distance: {distance} km")
                        if distance > distance_threshold_km:
                            alerts.append({
                                "user_ID": user_id,
                                "ip_address": ip,
                                "alert_type": "unusual_login_location",
                                "distance_km": distance,
                                "last_login_geo": last_geo,
                                "current_geo": current_geo,
                                "severity": "high" if distance > 1000 else "medium"
                            })
        except (KeyError, ValueError) as e:
            logging.warning(f"Skipping malformed log entry: {entry}. Error: {e}")
            continue

    # Generate IP-based threshold alerts
    for event_type, ips in event_counts.items():
        threshold = thresholds[event_type]
        for ip, count in ips.items():
            if count >= threshold:
                logging.info(f"Excessive {event_type} detected from IP {ip}. Count: {count}")
                alerts.append({
                    "ip_address": ip,
                    "alert_type": f"excessive_{event_type}",
                    "count": count,
                    "severity": "medium"
                })

    logging.info("Log analysis complete")
    return alerts