# Helper module to fetch user roles from the auth_service DB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Dict, List
import os

# Set the AUTH DB URI via env or default
AUTH_DB_URI = os.environ.get('AUTH_DB_URI', 'postgresql://siem_user:secure_password@postgres:5432/siem_db')

def fetch_user_roles(user_ids: List[int]) -> Dict[int, List[str]]:
    """Fetch user roles for a list of user IDs from the auth_service database."""
    if not user_ids:
        return {}
    engine = create_engine(AUTH_DB_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Query user_roles join table and roles
        result = session.execute(
            """
            SELECT ur.user_id, r.name FROM user_roles ur
            JOIN roles r ON ur.role_id = r.id
            WHERE ur.user_id = ANY(:user_ids)
            """,
            {"user_ids": user_ids}
        )
        user_roles_map = {}
        for user_id, role_name in result:
            user_roles_map.setdefault(user_id, []).append(role_name)
        return user_roles_map
    finally:
        session.close()
