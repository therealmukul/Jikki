import sqlite3


class SQLiteClient:
    def __init__(self, database_file):
        self.conn = None  # Initialize connection later
        self.database_file = database_file

    def connect(self):
        """Connects to the SQLite database."""
        self.conn = sqlite3.connect(self.database_file)

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()

    def execute(self, query, params=None):
        """Executes an SQL query."""
        cursor = self.conn.cursor()
        cursor.execute(query, params or ())  # Protects against SQL injection
        return cursor

    def create_table(self, query):
        """Creates a new table."""
        try:
            self.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def insert_data(self, query, data):
        """Inserts data into a table."""
        try:
            self.execute(query, data)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")

    def select_data(self, query, params=None):
        """Fetches data from a table."""
        try:
            cursor = self.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error selecting data: {e}")
