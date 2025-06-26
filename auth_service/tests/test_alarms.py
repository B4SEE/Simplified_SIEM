import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the Python path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db
from app.models.user import User
from app.models.role import Role
from app.models.alarm import Alarm

class AlarmEndpointTests(unittest.TestCase):
    """Test cases for the alarm blueprint endpoints."""

    def setUp(self):
        """Set up test environment before each test."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False

        self.client = self.app.test_client()

        # Create application context and database tables
        with self.app.app_context():
            db.create_all()

            # Create a test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                first_name='Test',
                last_name='User'
            )
            test_user.password = 'password123'
            
            # Create admin role and user
            admin_role = Role(name='admin', description='Administrator')
            admin_user = User(
                username='adminuser',
                email='admin@example.com',
                first_name='Admin',
                last_name='User'
            )
            admin_user.password = 'adminpass'
            admin_user.roles.append(admin_role)
            
            db.session.add(test_user)
            db.session.add(admin_role)
            db.session.add(admin_user)
            db.session.commit()

            self.test_user_id = test_user.id
            self.admin_user_id = admin_user.id

            # Create a test alarm
            test_alarm = Alarm(
                name='Test Alarm',
                description='Test alarm description',
                event_type='login_failed',
                threshold=5,
                time_window=60,
                is_active=True,
                severity='medium',
                user_id=test_user.id
            )
            db.session.add(test_alarm)
            db.session.commit()
            self.test_alarm_id = test_alarm.id

    def tearDown(self):
        """Clean up after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    @patch('app.blueprints.alarms.get_kafka_producer')
    def test_get_alarms(self, mock_kafka_producer):
        """Test getting all alarms for a user."""
        # Configure mock
        mock_producer = MagicMock()
        mock_kafka_producer.return_value = mock_producer

        # Make request with test mode headers to bypass auth
        response = self.client.get(
            '/api/alarms/',
            headers={
                'X-Test-Mode': 'true',
                'X-Test-User-ID': str(self.test_user_id)
            }
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['alarms']), 1)
        self.assertEqual(data['alarms'][0]['name'], 'Test Alarm')

    @patch('app.blueprints.alarms.get_kafka_producer')
    def test_get_specific_alarm(self, mock_kafka_producer):
        """Test getting a specific alarm."""
        # Configure mock
        mock_producer = MagicMock()
        mock_kafka_producer.return_value = mock_producer

        # Make request with test mode headers to bypass auth
        response = self.client.get(
            f'/api/alarms/{self.test_alarm_id}',
            headers={
                'X-Test-Mode': 'true',
                'X-Test-User-ID': str(self.test_user_id)
            }
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['alarm']['name'], 'Test Alarm')
        self.assertEqual(data['alarm']['event_type'], 'login_failed')

    @patch('app.blueprints.alarms.get_kafka_producer')
    def test_create_alarm(self, mock_kafka_producer):
        """Test creating a new alarm."""
        # Configure mock
        mock_producer = MagicMock()
        mock_kafka_producer.return_value = mock_producer

        # Make request with test mode headers to bypass auth
        response = self.client.post(
            '/api/alarms/',
            headers={
                'X-Test-Mode': 'true',
                'X-Test-User-ID': str(self.test_user_id)
            },
            data=json.dumps({
                'name': 'New Alarm',
                'description': 'New alarm description',
                'event_type': 'unusual_login_location',
                'threshold': 1,
                'time_window': 30,
                'severity': 'high'
            }),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Alarm created successfully')
        self.assertIn('alarm_id', data)
        self.assertEqual(data['alarm']['name'], 'New Alarm')

        # Verify Kafka producer was called
        mock_producer.produce.assert_called_once()
        mock_producer.flush.assert_called_once()

    @patch('app.blueprints.alarms.get_kafka_producer')
    def test_update_alarm(self, mock_kafka_producer):
        """Test updating an alarm."""
        # Configure mock
        mock_producer = MagicMock()
        mock_kafka_producer.return_value = mock_producer

        # Make request with test mode headers to bypass auth
        response = self.client.put(
            f'/api/alarms/{self.test_alarm_id}',
            headers={
                'X-Test-Mode': 'true',
                'X-Test-User-ID': str(self.test_user_id)
            },
            data=json.dumps({
                'name': 'Updated Alarm',
                'threshold': 10
            }),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Alarm updated successfully')
        self.assertIn('updated_fields', data)
        self.assertIn('name', data['updated_fields'])
        self.assertIn('threshold', data['updated_fields'])
        self.assertEqual(data['alarm']['name'], 'Updated Alarm')
        self.assertEqual(data['alarm']['threshold'], 10)

        # Verify Kafka producer was called
        mock_producer.produce.assert_called_once()
        mock_producer.flush.assert_called_once()

    @patch('app.blueprints.alarms.get_kafka_producer')
    def test_update_alarm_status(self, mock_kafka_producer):
        """Test updating an alarm's status."""
        # Configure mock
        mock_producer = MagicMock()
        mock_kafka_producer.return_value = mock_producer

        # Make request with test mode headers to bypass auth
        response = self.client.put(
            f'/api/alarms/{self.test_alarm_id}/status',
            headers={
                'X-Test-Mode': 'true',
                'X-Test-User-ID': str(self.test_user_id)
            },
            data=json.dumps({
                'is_active': False
            }),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Alarm disabled successfully')
        self.assertEqual(data['alarm']['is_active'], False)

        # Verify Kafka producer was called
        mock_producer.produce.assert_called_once()
        mock_producer.flush.assert_called_once()

    @patch('app.blueprints.alarms.get_kafka_producer')
    def test_delete_alarm(self, mock_kafka_producer):
        """Test deleting an alarm."""
        # Configure mock
        mock_producer = MagicMock()
        mock_kafka_producer.return_value = mock_producer

        # Make request with test mode headers to bypass auth
        response = self.client.delete(
            f'/api/alarms/{self.test_alarm_id}',
            headers={
                'X-Test-Mode': 'true',
                'X-Test-User-ID': str(self.test_user_id)
            }
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Alarm deleted successfully')
        self.assertEqual(data['alarm_details']['id'], self.test_alarm_id)

        # Verify Kafka producer was called
        mock_producer.produce.assert_called_once()
        mock_producer.flush.assert_called_once()

        # Verify alarm was deleted
        with self.app.app_context():
            alarm = Alarm.query.get(self.test_alarm_id)
            self.assertIsNone(alarm)

    @patch('app.blueprints.alarms.get_kafka_producer')
    def test_admin_can_view_all_alarms(self, mock_kafka_producer):
        """Test that admin users can view all alarms."""
        # Configure mock
        mock_producer = MagicMock()
        mock_kafka_producer.return_value = mock_producer

        # Create another alarm for the admin user
        with self.app.app_context():
            admin_alarm = Alarm(
                name='Admin Alarm',
                description='Admin alarm description',
                event_type='password_changed',
                user_id=self.admin_user_id
            )
            db.session.add(admin_alarm)
            db.session.commit()

        # Make request as admin
        response = self.client.get(
            '/api/alarms/',
            headers={
                'X-Test-Mode': 'true',
                'X-Test-User-ID': str(self.admin_user_id)
            }
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        # Admin should see both alarms
        self.assertEqual(len(data['alarms']), 2)

if __name__ == '__main__':
    unittest.main()
