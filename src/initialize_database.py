import sqlite3
import os

DATABASE = 'DB\database.db'
SQL_INIT_FILE = "DB\db_init.sql"

def initialize_database_from_file(sql_file_path, db_name="dnd_from_file.db"):
    """
    Creates and initializes a new SQLite database using a schema from a .sql file.

    Args:
        sql_file_path (str): The path to the .sql file containing the schema.
        db_name (str): The name of the database file to create.
                       Defaults to "dnd_from_file.db".
    """
    # Check if the SQL file exists
    if not os.path.exists(sql_file_path):
        print(f"Error: SQL file '{sql_file_path}' not found.")
        return

    # Check if the database file already exists and ask before overwriting
    if os.path.exists(db_name):
        overwrite = input(f"Database '{db_name}' already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Database initialization cancelled.")
            return
        else:
            os.remove(db_name)
            print(f"Removed existing database '{db_name}'.")

    conn = None  # Initialize conn to None
    try:
        # Read the SQL schema from the file
        with open(sql_file_path, 'r') as f:
            sql_schema = f.read()
        print(f"Read schema from '{sql_file_path}'.")

        # Connect to the database (this will create the file)
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        print(f"Creating schema in '{db_name}'...")

        # Execute the multi-statement SQL script
        # The first line of your SQL file is "PRAGMA foreign_keys = ON;"
        # We should execute this separately or ensure it's handled correctly.
        # executescript handles multiple statements including PRAGMA.
        cursor.executescript(sql_schema)

        # Commit the changes
        conn.commit()

        print(f"Database '{db_name}' created and initialized successfully using '{sql_file_path}'.")

    except sqlite3.Error as e:
        print(f"An SQLite error occurred: {e}")
        # If an error occurs during creation, try to remove the partial file
        if os.path.exists(db_name):
            if conn: # Ensure connection is closed before trying to remove
                conn.close()
                conn = None # Set to None after closing
            try:
                os.remove(db_name)
                print(f"Removed potentially corrupted database file '{db_name}'.")
            except Exception as remove_e:
                 print(f"Could not remove database file '{db_name}': {remove_e}")
    except IOError as e:
        print(f"An I/O error occurred while reading '{sql_file_path}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()
            print("Database connection closed.")


# --- Main execution block ---
if __name__ == "__main__":

    initialize_database_from_file(SQL_INIT_FILE, DATABASE)
