# logging_service/app/__init__.py

from .models import db
db.init_app(app)

# Import models
from .models.log_entry import LogEntry
