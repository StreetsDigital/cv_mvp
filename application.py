# WSGI application entry point for Elastic Beanstalk
from app.main import app

# Elastic Beanstalk looks for an 'application' callable
application = app

if __name__ == "__main__":
    application.run()