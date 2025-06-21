# Alarm Test Script for SIEM

This script tests alarm functionality in your SIEM system. It simulates basic attack scenarios to verify alarm triggers work correctly.

## Features

### Test Scenarios

1. **Bruteforce Attacks** - Multiple failed login attempts from the same IP
2. **Distributed Access** - Same user logging in from multiple IP addresses
3. **Unusual Login Locations** - Logins from geographically distant locations
4. **High-Frequency Events** - Rapid succession of various security events

### Configurable Parameters

- **Event Count**: Number of events to generate per scenario
- **Delay**: Time between events (to control attack speed)
- **IP Addresses**: Uses realistic public and private IP ranges
- **Geographic Locations**: Real-world coordinates for location-based testing
- **User Agents**: Various browser and device user agents

### Safety Features

- **Test Markers**: All generated logs are marked with `test_mode: true`
- **Non-Interfering**: Uses test user ID and doesn't affect production data
- **Configurable**: Adjustable parameters for different testing needs
- **Clear Output**: Detailed logging and result summaries

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements_test.txt
   ```

2. **Verify Services**:
   - Ensure your Docker containers are running
   - Logging Service should be accessible at `localhost:5000`
   - Auth Service should be accessible at `localhost:5001`

## Usage

### Basic Usage

```bash
# Run all test scenarios
python alarm_test_script.py

# Run a specific scenario
python alarm_test_script.py --scenario bruteforce

# Run with custom parameters
python alarm_test_script.py --scenario distributed --ips 15 --delay 0.2
```

### Command Line Options

```bash
python alarm_test_script.py [OPTIONS]

Options:
  --scenario {bruteforce,distributed,unusual,high-frequency,all}
                        Test scenario to run (default: all)
  --count COUNT         Number of events to generate (default: 10)
  --users USERS         Number of users for distributed test (default: 3)
  --ips IPS             Number of IPs for distributed test (default: 10)
  --distance DISTANCE   Distance in km for unusual login (default: 1000)
  --events EVENTS       Number of events for high-frequency test (default: 50)
  --delay DELAY         Delay between events in seconds (default: 0.1)
  --verbose, -v         Enable verbose output
  --check-alarms        Check alarm status after tests
```

### Example Commands

```bash
# Test bruteforce with 15 failed logins
python alarm_test_script.py --scenario bruteforce --count 15

# Test distributed access with 20 different IPs
python alarm_test_script.py --scenario distributed --ips 20

# Test unusual login with 2000km distance
python alarm_test_script.py --scenario unusual --distance 2000

# Test high-frequency with 100 events rapidly
python alarm_test_script.py --scenario high-frequency --events 100 --delay 0.02

# Run all scenarios with verbose output and alarm checking
python alarm_test_script.py --verbose --check-alarms
```

## Test Scenarios Details

### 1. Bruteforce Scenario
- **Purpose**: Tests excessive failed login detection
- **Method**: Sends multiple `login_failed` events from the same IP
- **Expected Alarm**: Should trigger "bruteforce" alarm
- **Parameters**: `--count` (number of failed attempts)

### 2. Distributed Access Scenario
- **Purpose**: Tests detection of user logging in from many locations
- **Method**: Sends `login_success` events from multiple IPs for the same user
- **Expected Alarm**: Should trigger "distributed" alarm
- **Parameters**: `--ips` (number of different IPs)

### 3. Unusual Login Scenario
- **Purpose**: Tests geographic anomaly detection
- **Method**: Sends two logins from distant geographic locations
- **Expected Alarm**: Should trigger "unusual_location" alarm
- **Parameters**: `--distance` (distance in kilometers)

### 4. High-Frequency Scenario
- **Purpose**: Tests rapid event detection
- **Method**: Sends many events of different types rapidly
- **Expected Alarm**: Should trigger "high_frequency" alarm
- **Parameters**: `--events` (number of events), `--delay` (time between events)

## Output and Results

### Console Output
The script provides real-time feedback:
```
Alarm Test Script for SIEM
============================================================
Logging Service: http://localhost:5000/api/logs
Auth Service: http://localhost:5001/api/alarms
Test User ID: 3
Scenario: all
============================================================

Testing Bruteforce Scenario: 8 failed logins
==================================================
   1. Failed login from 203.0.113.1
   2. Failed login from 203.0.113.1
   ...
Bruteforce test completed: 8/8 logs sent
   Attack IP: 203.0.113.1
```

### Summary Report
After completion, a detailed summary is provided:
```
============================================================
TEST RESULTS SUMMARY
============================================================
Total scenarios tested: 4
Total logs sent: 48
Test user ID: 3
Test timestamp: 2024-01-15T10:30:45.123456

Detailed Results:
  bruteforce         : 8/8 logs sent
  distributed        : 8/8 logs sent
  unusual_login      : 2/2 logs sent
  high_frequency     : 30/30 logs sent
```

## Verification Steps

After running the test script:

1. **Check Alarms Dashboard**:
   - Navigate to your SIEM alarms page
   - Look for newly triggered alarms
   - Verify alarm details match the test scenarios

2. **Review Logs**:
   - Check the logs page for test entries
   - Look for entries with `test_mode: true` in additional_data
   - Verify event types and IP addresses match test scenarios

3. **Verify Alarm Triggers**:
   - Confirm that bruteforce alarms trigger after multiple failed logins
   - Check that distributed access alarms trigger for multiple IPs
   - Verify unusual location alarms for distant logins

## Troubleshooting

### Common Issues

**Connection Errors**:
- Ensure Docker containers are running
- Check that services are accessible on correct ports
- Verify network connectivity

**No Alarms Generated**:
- Check alert generator is running
- Verify thresholds are set correctly
- Ensure test user ID and token are valid

**Test Data Not Appearing**:
- Check logging service is receiving requests
- Verify log format matches expected structure
- Check for any validation errors

### Debug Mode

Enable verbose output for detailed debugging:
```bash
python alarm_test_script.py --verbose --scenario bruteforce
```

This will show:
- Individual log transmission status
- Detailed error messages
- Step-by-step progress

## Configuration

### Test User Settings
- **User ID**: 3 (default test user)
- **Token**: `9b2149b1-1e29-481e-8be1-ab33b6270042`

### Alert Generator Thresholds
Thresholds can be adjusted in `logging_service/app/alert_generator.py`:
- Bruteforce: 3 failed logins
- Distributed: 5 different IPs
- High-frequency: 10 events
- Unusual location: 1000km distance

## Integration

This test script integrates with:
- **Logging Service**: Sends test logs via REST API
- **Alert Generator**: Triggers alarms based on patterns
- **Auth Service**: Creates and manages alarms
- **Dashboard**: Displays test results and alarms

The script is designed to work seamlessly with the existing SIEM infrastructure while providing comprehensive testing capabilities. 