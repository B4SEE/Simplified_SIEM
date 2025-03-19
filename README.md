# **Enterprise Logging and Monitoring System (Simplified SIEM)**  

A logging and monitoring system that tracks authentication events, detects suspicious patterns, and provides real-time visualization. The project simulates basic security monitoring for authentication activity.  

## **Table of Contents**  
- [**Enterprise Logging and Monitoring System (Simplified SIEM)**](#enterprise-logging-and-monitoring-system-simplified-siem)
  - [**Table of Contents**](#table-of-contents)
  - [**Overview**](#overview)
  - [**Features**](#features)
  - [**Installation \& Setup**](#installation--setup)
  - [**Usage**](#usage)
  - [**Development Guide**](#development-guide)
    - [**Project Structure**](#project-structure)
  - [**Additional Documentation**](#additional-documentation)
  - [**Team Members \& Contact**](#team-members--contact)

---

## **Overview**  
This project is designed to track user authentication events, store logs, analyze suspicious patterns, and visualize data in a real-time dashboard. It simulates an enterprise-level **Security Information and Event Management (SIEM)** system with a focus on login monitoring.  

**Key functionalities include:**  
- **User authentication system** (registration, login, password reset, etc.)  
- **Log collection & storage** for authentication events  
- **Suspicious activity detection** (brute-force attacks, login anomalies, unusual password resets)  
- **Real-time dashboard** for visualizing logs and alerts  

---

## **Features**  
- User authentication system (Login, Register, Password Reset)  
- Log collection for authentication events  
- Suspicious activity detection logic  
- API for log retrieval and analysis  
- Real-time dashboard for log visualization  
- Local deployment with containerization  

---

## **Installation & Setup**  
[To be completed]  

---

## **Usage**  
[To be completed]  

---

## **Development Guide**  
### **Project Structure**  
```plaintext
📂 Simplified_SIEM/
├── 📂 authentication_service/
│   ├── 📂 app/
│   │   ├── __init__.py        # Flask app initialization
│   │   ├── 📂 models/
│   │   │   └── user.py        # User model (SQLAlchemy)
│   │   ├── 📂 blueprints/
│   │   │   └── auth.py        # Authentication routes (login, register, etc.)
│   │   ├── 📂 tasks/
│   │   │   └── email_tasks.py # Celery tasks (e.g., sending emails)
│   │   ├── celery.py          # Celery configuration
│   │   └── config.py          # Configuration settings
│   ├── run.py                 # Entry point to run the Flask app
│   ├── 📂 alembic/               # Database migrations with Alembic
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/          # Migration scripts
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Docker configuration for this service
│   └── 📂 tests/
│       └── test_auth.py       # Unit/integration tests
├── 📂 logging_service/
│   ├── 📂 app/
│   │   ├── __init__.py        # Flask app initialization
│   │   ├── 📂 blueprints/
│   │   │   ├── api.py         # REST API endpoints for logs/alerts
│   │   │   └── websocket.py   # WebSocket for real-time updates
│   │   ├── log_ingester.py    # Kafka consumer for log ingestion
│   │   ├── log_analyzer.py    # Log analysis logic
│   │   ├── alert_generator.py # Alert generation logic
│   │   ├── celery.py          # Celery configuration
│   │   └── config.py          # Configuration settings
│   ├── run.py                 # Entry point to run the Flask app
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Docker configuration for this service
│   └── 📂 tests/
│       └── test_logging.py    # Unit/integration tests
├── 📂 frontend/
├── docker-compose.yml         # Docker Compose for local orchestration
├── README.md                  # Project overview and instructions
├── .gitignore                 # Git ignore file
└── 📂 docs/
```
[To be completed]  

---

## **Additional Documentation**  
More details, including system architecture, diagrams, and technical documentation, can be found in the [Project Wiki](https://github.com/B4SEE/Simplified_SIEM/wiki).  

---

## **Team Members & Contact**  
| Name              | Role                           | Contact Info                          |
|-------------------|--------------------------------|---------------------------------------|
| B4SEE             | Algorithms Backend & Team Lead | [GitHub](https://github.com/B4SEE)    |
| M2kura            | Backend Developer 1            | [GitHub](https://github.com/M2kura)   |
| ponny12           | Backend Developer 2            | [GitHub](https://github.com/ponny12)  |
| mamaegeo          | Frontend Developer 1           | [GitHub](https://github.com/mamaegeo) |
| vhs-cake          | Frontend Developer 2           | [GitHub](https://github.com/vhs-cake) |


