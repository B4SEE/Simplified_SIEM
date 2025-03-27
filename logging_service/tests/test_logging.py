from datetime import datetime, timedelta
import random
import logging
import sys
import os

# Constants
DEFAULT_NUM_ENTRIES = 100
DEFAULT_USER_IDS = [1, 2, 3]
IP_RANGE_START = 1
IP_RANGE_END = 11
EVENT_TYPES = ["login_success", "login_failed", "logout", "password_reset"]
MAX_LOGIN_DELAY_MINUTES = 10
MAX_BRUTE_FORCE_ATTEMPTS = 1000
DEFAULT_GEO_COORDS = {
    1: (40.7128, -74.0060),  # New York
    2: (34.0522, -118.2437),  # Los Angeles
    3: (51.5074, -0.1278)  # London
}
BRUTE_FORCE_IP = "192.168.1.200"
UNUSUAL_LOGIN_IP = "192.168.1.100"

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.log_analyzer import analyze_logs

def generate_dummy_logs(num_entries=DEFAULT_NUM_ENTRIES, user_ids=DEFAULT_USER_IDS):
    """
    Generate dummy log entries with user_ID and geo data for testing.

    #### Args:
        num_entries (int): Number of log entries to generate.
        user_ids (list): List of user IDs to include in logs.

    #### Returns:
        list: List of log entry dictionaries.
    """
    logging.info("Generating dummy logs...")
    ips = [f"192.168.1.{i}" for i in range(IP_RANGE_START, IP_RANGE_END)]
    logs = []
    now = datetime.utcnow()

    for _ in range(num_entries):
        ip = random.choice(ips)
        event_type = random.choice(EVENT_TYPES)
        timestamp = now - timedelta(minutes=random.randint(0, MAX_LOGIN_DELAY_MINUTES))
        user_id = random.choice(user_ids)
        geo = (random.uniform(-90, 90), random.uniform(-180, 180))
        logs.append({
            "timestamp": timestamp.isoformat() + "Z",
            "ip_address": ip,
            "event_type": event_type,
            "user_ID": user_id,
            "geo": geo
        })

    # Unusual login location test
    logging.debug("Adding unusual login location test entry...")
    user_geo = DEFAULT_GEO_COORDS[1]
    distant_geo = (34.0522, -118.2437) if user_geo == (40.7128, -74.0060) else (40.7128, -74.0060)
    logs.append({
        "timestamp": now.isoformat() + "Z",
        "ip_address": UNUSUAL_LOGIN_IP,
        "event_type": "login_success",
        "user_ID": 1,
        "geo": distant_geo
    })

    # Brute-force test
    logging.debug("Adding brute-force test entries...")
    for _ in range(random.randint(0, MAX_BRUTE_FORCE_ATTEMPTS)):
        timestamp = now - timedelta(minutes=random.randint(0, MAX_LOGIN_DELAY_MINUTES))
        logs.append({
            "timestamp": timestamp.isoformat() + "Z",
            "ip_address": BRUTE_FORCE_IP,
            "event_type": "login_failed",
            "user_ID": random.choice(user_ids),
            "geo": (random.uniform(-90, 90), random.uniform(-180, 180))
        })

    logging.info("Dummy logs generation complete.")
    return logs

if __name__ == "__main__":
    logging.info("Starting log analysis...")
    user_data = DEFAULT_GEO_COORDS
    now = datetime.utcnow()
    log_entries = generate_dummy_logs(user_ids=DEFAULT_USER_IDS)
    alerts = analyze_logs(log_entries, user_data, reference_time=now)

    # Display alerts
    if alerts:
        logging.warning("Detected anomalies:")
        for alert in alerts:
            if alert["alert_type"] == "unusual_login_location":
                logging.warning(f"Alert: Unusual login for user {alert['user_ID']} from IP {alert['ip_address']}, "
                                f"distance {alert['distance_km']:.2f} km, severity {alert['severity']}")
            else:
                logging.warning(f"Alert: {alert['alert_type']} from IP {alert['ip_address']} with {alert['count']} events, "
                                f"severity {alert['severity']}")
    else:
        logging.info("No anomalies detected.")