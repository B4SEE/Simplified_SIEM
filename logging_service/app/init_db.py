from app import create_app
from app.models import db

def init_db():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Created all database tables.")

if __name__ == '__main__':
    init_db() 