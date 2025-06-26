import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app, db
from app.models.user import User
from app.models.role import Role

# Load environment variables from .env file
load_dotenv(os.path.join(project_root, '.env'))

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

def create_admin_user(username):
    """
    Finds a user by email and grants them the 'admin' role.
    Creates the 'admin' role if it doesn't exist.
    """
    with app.app_context():
        # Ensure the 'admin' role exists
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            print("Admin role not found, creating one...")
            admin_role = Role(name='admin', description='Administrator with all permissions')
            db.session.add(admin_role)
            db.session.commit()
            print("Admin role created.")

        # Find the user by username
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"Error: User with username '{username}' not found.")
            return

        # Assign the admin role to the user
        if user.has_role('admin'):
            print(f"User '{user.username}' already has the admin role.")
        else:
            user.add_role(admin_role)
            db.session.add(user)
            db.session.commit()
            print(f"Successfully granted admin role to user '{user.username}'.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python create_admin.py <user_username>")
        print("       python create_admin.py list")
        sys.exit(1)

    if sys.argv[1] == "list":
        with app.app_context():
            users = User.query.all()
            if not users:
                print("No users found in the database.")
            else:
                print("Existing users:")
                for user in users:
                    roles = [role.name for role in user.roles]
                    print(f"  {user.username} ({user.email}) - Roles: {', '.join(roles) if roles else 'None'}")
    else:
        user_username = sys.argv[1]
        create_admin_user(user_username) 