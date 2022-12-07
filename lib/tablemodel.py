import os
import sqlite3
from passlib.hash import pbkdf2_sha256


class DatabaseModel:
    """This class is a wrapper around the sqlite3 database. It provides a simple interface that maps methods
    to database queries. The only required parameter is the database file."""

    def __init__(self, database_file):
        self.database_file = database_file
        if not os.path.exists(self.database_file):
            raise FileNotFoundError(f"Could not find database file: {database_file}")

    # Using the built-in sqlite3 system table, return a list of all tables in the database
    def get_table_list(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        return tables

    # Given a table name, return the rows and column names
    def get_table_content(self, table_name):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        # An alternative for this 2 var approach is to set a sqlite row_factory on the connection
        table_headers = [column_name[0] for column_name in cursor.description]
        table_content = cursor.fetchall()

        # Note that this method returns 2 variables!
        return table_content, table_headers

    def get_content(self, table_name):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        # An alternative for this 2 var approach is to set a sqlite row_factory on the connection
        # table_headers = [column_name[0] for column_name in cursor.description]
        # table_content = cursor.fetchall()
        data = cursor.fetchall()
        columns = [column_name[0] for column_name in cursor.description]
        # Note that this method returns 2 variables!
        return data, columns

    def get_no_leerdoel(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute("SELECT * FROM vragen WHERE leerdoel NOT IN (SELECT id FROM leerdoelen);")
        data = cursor.fetchall()
        columns = [column_name[0] for column_name in cursor.description]
        return data, columns

    def get_empty_column(self, table, column):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE {column} IS NULL")
        data = cursor.fetchall()
        columns = [column_name[0] for column_name in cursor.description]
        return data, columns

    def get_html_codes(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute("SELECT * FROM vragen WHERE vraag LIKE '%<br>%' OR vraag LIKE '%&nbsp;%';")
        data = cursor.fetchall()
        columns = [column_name[0] for column_name in cursor.description]
        return data, columns

    # The password in the query should be replaced with hashed_password later!
    def validate_login(self, username, password):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
        account = cursor.fetchone()
        pbkdf2_sha256.verify(password, account[3])
        return account

    def create_user(self, username, email, password, isAdmin=0):
        hashed_password = pbkdf2_sha256.hash(password)
        db = sqlite3.connect(self.database_file)
        cursor = db.cursor()
        cursor.execute(f"INSERT INTO users (username, email, password, isAdmin) VALUES ('{username}', '{email}', '{hashed_password}', '{isAdmin}')")
        db.commit()

    def update_user(self, table_name, id, username, email, password):
        hashed_password = pbkdf2_sha256.hash(password)
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"UPDATE '{table_name}' SET username = '{username}', email = '{email}', password = '{password}' WHERE id = '{id}'")

    def delete_user(self, table_name, id):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"DELETE FROM '{table_name}' WHERE id = '{id}'")