from app.models import db

def create_tables():
    # Create all tables
    db.create_all()
    print("Created all database tables.")

if __name__ == '__main__':
    create_tables() 