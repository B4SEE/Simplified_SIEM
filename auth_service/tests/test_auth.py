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
from datetime import datetime

class AuthEndpointTests(unittest.TestCase):
    """Test cases for the auth blueprint endpoints."""

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
            db.session.add(test_user)
            db.session.commit()

            self.test_user_id = test_user.id

    def tearDown(self):
        """Clean up after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    @patch('app.blueprints.auth.get_kafka_producer')
    def test_status_endpoint(self, mock_kafka_producer):
        """Test the status endpoint."""
        response = self.client.get('/api/auth/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'Auth service is running')
        self.assertEqual(data['service'], 'auth')

    @patch('app.blueprints.auth.get_kafka_producer')
    def test_login_success(self, mock_kafka_producer):
        """Test successful login."""
        # Configure mock
        mock_producer = MagicMock()
        mock_kafka_producer.return_value = mock_producer

        # Make request
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({'username': 'testuser', 'password': 'password123'}),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Login successful')
        self.assertIn('token', data)
        self.assertIn('user_id', data)

        # Verify Kafka producer was called
        mock_producer.produce.assert_called_once()
        mock_producer.flush.assert_called_once()

    @patch('app.blueprints.auth.get_kafka_producer')
    def test_login_invalid_credentials(self, mock_kafka_producer):
        """Test login with invalid credentials."""
        # Configure mock
        mock_producer = MagicMock()
        mock_kafka_producer.return_value = mock_producer

        # Make request with wrong password
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({'username': 'testuser', 'password': 'wrongpassword'}),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Invalid credentials')

        # Verify Kafka producer was called
        mock_producer.produce.assert_called_once()
        mock_producer.flush.assert_called_once()

    @patch('app.blueprints.auth.get_kafka_producer')
    def test_login_missing_fields(self, mock_kafka_producer):
        """Test login with missing fields."""
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps({'username': 'testuser'}),  # Missing password
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Missing username or password')

        # Kafka producer should not be called
        mock_kafka_producer.assert_not_called()

    @patch('app.blueprints.auth.get_kafka_producer')
    def test_register_success(self, mock_kafka_producer):
        """Test successful user registration."""
        # Configure mock
        mock_producer = MagicMock()
        mock_kafka_producer.return_value = mock_producer

        # Make request
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'newpassword123',
                'confirm_password': 'newpassword123',
                'first_name': 'New',
                'last_name': 'User'
            }),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('Registration successful', data['message'])
        self.assertIn('user_id', data)

        # Verify user was created in database
        with self.app.app_context():
            user = User.query.filter_by(username='newuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'new@example.com')

        # Verify Kafka producer was called
        mock_producer.produce.assert_called_once()
        mock_producer.flush.assert_called_once()

    @patch('app.blueprints.auth.get_kafka_producer')
    def test_register_password_mismatch(self, mock_kafka_producer):
        """Test registration with password mismatch."""
        # Configure mock
        mock_producer = MagicMock()
        mock_kafka_producer.return_value = mock_producer

        # Make request with mismatched passwords
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'password123',
                'confirm_password': 'differentpassword',
                'first_name': 'New',
                'last_name': 'User'
            }),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Passwords do not match')

        # Kafka producer should not be called
        mock_producer.produce.assert_not_called()

    @patch('app.blueprints.auth.get_kafka_producer')
    def test_register_duplicate_username(self, mock_kafka_producer):
        """Test registration with duplicate username."""
        # Configure mock
        mock_producer = MagicMock()
        mock_kafka_producer.return_value = mock_producer

        # Make request with existing username
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': 'testuser',  # Already exists
                'email': 'different@example.com',
                'password': 'newpassword123',
                'confirm_password': 'newpassword123'
            }),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Username already exists')

        # Kafka producer should not be called
        mock_producer.produce.assert_not_called()

    @patch('app.blueprints.auth.get_kafka_producer')
    def test_get_profile(self, mock_kafka_producer):
        """Test getting user profile."""
        # Configure mock
        mock_producer = MagicMock()
        mock_kafka_producer.return_value = mock_producer

        # Make request with test mode headers to bypass auth
        response = self.client.get(
            '/api/auth/profile',
            headers={
                'X-Test-Mode': 'true',
                'X-Test-User-ID': str(self.test_user_id)
            }
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['profile']['username'], 'testuser')
        self.assertEqual(data['profile']['email'], 'test@example.com')
        self.assertEqual(data['profile']['first_name'], 'Test')
        self.assertEqual(data['profile']['last_name'], 'User')

    @patch('app.blueprints.auth.get_kafka_producer')
    def test_update_profile(self, mock_kafka_producer):
        """Test updating user profile."""
        # Configure mock
        mock_producer = MagicMock()
        mock_kafka_producer.return_value = mock_producer

        # Make request with test mode headers to bypass auth
        response = self.client.put(
            '/api/auth/profile',
            headers={
                'X-Test-Mode': 'true',
                'X-Test-User-ID': str(self.test_user_id)
            },
            data=json.dumps({
                'first_name': 'Updated',
                'last_name': 'Name'
            }),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Profile updated successfully')
        self.assertIn('first_name', data['updated_fields'])
        self.assertIn('last_name', data['updated_fields'])

        # Verify Kafka producer was called
        mock_producer.produce.assert_called_once()
        mock_producer.flush.assert_called_once()

        # Verify database changes
        with self.app.app_context():
            user = User.query.get(self.test_user_id)
            self.assertEqual(user.first_name, 'Updated')
            self.assertEqual(user.last_name, 'Name')

    @patch('app.blueprints.auth.get_kafka_producer')
    def test_change_password(self, mock_kafka_producer):
        """Test changing user password."""
        # Configure mock
        mock_producer = MagicMock()
        mock_kafka_producer.return_value = mock_producer

        # Make request with test mode headers to bypass auth
        response = self.client.put(
            '/api/auth/password',
            headers={
                'X-Test-Mode': 'true',
                'X-Test-User-ID': str(self.test_user_id)
            },
            data=json.dumps({
                'current_password': 'password123',
                'new_password': 'newpassword456',
                'confirm_password': 'newpassword456'
            }),
            content_type='application/json'
        )

        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Password updated successfully')

        # Verify Kafka producer was called
        mock_producer.produce.assert_called_once()
        mock_producer.flush.assert_called_once()

        # Verify password was changed
        with self.app.app_context():
            user = User.query.get(self.test_user_id)
            self.assertTrue(user.verify_password('newpassword456'))
            self.assertFalse(user.verify_password('password123'))

if __name__ == '__main__':
    unittest.main()
