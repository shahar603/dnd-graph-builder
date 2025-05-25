from flask import Flask
import os
from utils import init_db_schema, close_db_connection

# Import blueprints from the pages directory
from pages.auth import auth_bp
from pages.dashboard import dashboard_bp
from pages.view_db import view_db_bp
from pages.import_notes import import_notes_bp
from pages.graph_view import graph_view_bp # Import the new blueprint

app = Flask(__name__)
app.secret_key = os.urandom(24) # Set a secret key for session management

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(view_db_bp)
app.register_blueprint(import_notes_bp)
app.register_blueprint(graph_view_bp) # Register the new blueprint

# Register teardown function for database connection
app.teardown_appcontext(close_db_connection)

if __name__ == '__main__':
    # Initialize the database schema when the app starts
    # This will create the DB file and tables if they don't exist.
    init_db_schema()
    app.run(debug=True)
