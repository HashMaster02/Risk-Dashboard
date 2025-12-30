import sys

# Add your project directory to the sys.path
project_home = '/home/yourusername/riskdashboard'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the Flask app
from main import app

# Flask apps are already WSGI-compatible
application = app
