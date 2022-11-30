import os
import sqlite3


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





 ### filter types
    # filter template function
    def return_filter_content(self, query):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        columns = [column_name[0] for column_name in cursor.description]
        return data, columns

    # -----------

    def get_content(self, table_name):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        columns = [column_name[0] for column_name in cursor.description]
        return data, columns




    def get_no_leerdoel(self, min_max_filter, between_column, min, max):
        if(min_max_filter):
            query = f"SELECT * FROM vragen WHERE leerdoel NOT IN (SELECT id FROM leerdoelen) AND {between_column} >= {min} AND {between_column} <= {max}"
        else:
            query = "SELECT * FROM vragen WHERE leerdoel NOT IN (SELECT id FROM leerdoelen);"
        print(query)
        data, columns = self.return_filter_content(query)
        return data, columns

    def get_empty_column(self, table, column, min_max_filter, between_column, min, max):
        if(min_max_filter):
            query = f"SELECT * FROM {table} WHERE {column} IS NULL AND {between_column} >= {min} AND {between_column} <= {max}"
        else:
            query = f"SELECT * FROM {table} WHERE {column} IS NULL"
        print(query)
        data, columns = self.return_filter_content(query)
        return data, columns

    def get_html_codes(self, min_max_filter, between_column, min, max):
        if(min_max_filter):
            query = f"SELECT * FROM vragen WHERE (vraag LIKE '%<br>%' OR vraag LIKE '%&nbsp;%') AND ( {between_column} >= {min} AND {between_column} <= {max})"
        else:
            query = "SELECT * FROM vragen WHERE vraag LIKE '%<br>%' OR vraag LIKE '%&nbsp;%'"
        print(query)
        data, columns = self.return_filter_content(query)
        return data, columns


###



    def get_tables_min_max(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        data = {}
        data["id"] = cursor.execute(f"SELECT MIN(id),MAX(id) FROM vragen").fetchone()
        data["leerdoel"] = cursor.execute(f"SELECT MIN(leerdoel),MAX(leerdoel) FROM vragen").fetchone()
        data["auteur"] = cursor.execute(f"SELECT MIN(auteur),MAX(auteur) FROM vragen").fetchone()
        return data

       
    def validate_login(self, table_name, username, password):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE username = '{username}' AND password = '{password}'")
        account = cursor.fetchone()
        return account

