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





    def get_no_leerdoel(self, min_max_filter, between_column, min, max, uitzondering):
        if uitzondering == "ja":
            subquery = "and uitzondering = 1"
        elif uitzondering == "nee":
            subquery = "and uitzondering = 0"
        else:
            subquery = ""

        if(min_max_filter):
            query = f"SELECT * FROM vragen WHERE leerdoel NOT IN (SELECT id FROM leerdoelen) AND ({between_column} >= {min} AND {between_column} <= {max}) "+subquery
        else:
            query = "SELECT * FROM vragen WHERE leerdoel NOT IN (SELECT id FROM leerdoelen) "+subquery
        print(query)
        data, columns = self.return_filter_content(query)
        return data, columns

    def get_no_auteur(self, min_max_filter, between_column, min, max, uitzondering):
        if uitzondering == "ja":
            subquery = "and uitzondering = 1"
        elif uitzondering == "nee":
            subquery = "and uitzondering = 0"
        else:
            subquery = ""

        if(min_max_filter):
            query = f"SELECT * FROM vragen WHERE auteur NOT IN (SELECT id FROM auteurs) AND ({between_column} >= {min} AND {between_column} <= {max}) "+subquery
        else:
            query = "SELECT * FROM vragen WHERE auteur NOT IN (SELECT id FROM auteurs) "+subquery
        print(query)
        data, columns = self.return_filter_content(query)
        return data, columns


    def get_empty_column(self, table, column, min_max_filter, between_column, min, max, uitzondering):
        if uitzondering == "ja":
            subquery = "and uitzondering = 1"
        elif uitzondering == "nee":
            subquery = "and uitzondering = 0"
        else:
            subquery = ""
        if(min_max_filter):
            query = f"SELECT * FROM {table} WHERE {column} IS NULL AND ({between_column} >= {min} AND {between_column} <= {max}) " +subquery
        else:
            query = f"SELECT * FROM {table} WHERE {column} IS NULL " +subquery
        print(query)
        data, columns = self.return_filter_content(query)
        return data, columns

    def get_html_codes(self, min_max_filter, between_column, min, max, uitzondering):
        if uitzondering == "ja":
            subquery = "and uitzondering = 1"
        elif uitzondering == "nee":
            subquery = "and uitzondering = 0"
        else:
            subquery = ""
        if(min_max_filter):
            query = f"SELECT * FROM vragen WHERE (vraag LIKE '%<br>%' OR vraag LIKE '%&nbsp;%') AND ( {between_column} >= {min} AND {between_column} <= {max}) " +subquery
        else:
            query = "SELECT * FROM vragen WHERE vraag LIKE '%<br>%' OR vraag LIKE '%&nbsp;%' " +subquery
        print(query)
        data, columns = self.return_filter_content(query)
        return data, columns

    def get_requested_rows(self, table_name, min_max_filter, between_column, min, max, uitzondering):
        if uitzondering == "ja":
            subquery = "and uitzondering = 1"
        elif uitzondering == "nee":
            subquery = "and uitzondering = 0"
        else:
            subquery = ""
        if(min_max_filter):
            query = f"SELECT * FROM {table_name} WHERE ({between_column} >= {min} AND {between_column} <= {max}) " + subquery
        else:
            query = f"SELECT * FROM {table_name} " +subquery
        print(query)
        data, columns = self.return_filter_content(query)
        return data, columns

    def get_wrong_value(self, table_name, column, min_max_filter, between_column, min, max, uitzondering):
        if uitzondering == "ja":
            subquery = "and uitzondering = 1"
        elif uitzondering == "nee":
            subquery = "and uitzondering = 0"
        else:
            subquery = ""
        if(min_max_filter):
            query = f"SELECT * FROM {table_name} WHERE ([{column}] NOT LIKE 1 AND [{column}] NOT LIKE 0) AND ({between_column} >= {min} AND {between_column} <= {max}) " + subquery
        else:
            query = f"SELECT * FROM {table_name} WHERE ([{column}] NOT LIKE 1 AND [{column}] NOT LIKE 0) " +subquery
        print(query)
        data, columns = self.return_filter_content(query)
        return data, columns
    
    
###

    def get_exceptions(self, table_name, min_max_filter, between_column, min, max):
            if(min_max_filter):
                query = f"SELECT * FROM {table_name} WHERE {between_column} >= {min} AND {between_column} <= {max}"
            else:
                query = f"SELECT * FROM {table_name}"
            print(query)
            data, columns = self.return_filter_content(query)
            return data, columns




    def get_tables_min_max(self):
        cursor = sqlite3.connect(self.database_file).cursor()
        data = {}
        data["vragen"] = {}
        data["vragen"]["id"] = cursor.execute(f"SELECT MIN(id),MAX(id) FROM vragen").fetchone()
        data["vragen"]["leerdoel"] = cursor.execute(f"SELECT MIN(leerdoel),MAX(leerdoel) FROM vragen").fetchone()
        data["vragen"]["auteur"] = cursor.execute(f"SELECT MIN(auteur),MAX(auteur) FROM vragen").fetchone()

        data["auteurs"] = {}
        data["auteurs"]["id"] = cursor.execute(f"SELECT MIN(id),MAX(id) FROM auteurs").fetchone()
        data["auteurs"]["geboortejaar"] = cursor.execute(f"SELECT MIN(geboortejaar),MAX(geboortejaar) FROM auteurs").fetchone()

        data["leerdoelen"] = {}
        data["leerdoelen"]["id"] = cursor.execute(f"SELECT MIN(id),MAX(id) FROM leerdoelen").fetchone()
        data["leerdoelen"]["leerdoel"] = cursor.execute(f"SELECT MIN(leerdoel),MAX(leerdoel) FROM leerdoelen").fetchone()
        # print(data["auteurs"]["geboortejaar"])
        return data

       
    # The password in the query should be replaced with hashed_password later!
    def validate_login(self, username, password):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
        account = cursor.fetchone()
        if account == None or not pbkdf2_sha256.verify(password, account[3]):
            return False
        cursor.close()
        return account

    def create_user(self, username, email, password, isAdmin=0):
        hashed_password = pbkdf2_sha256.hash(password)
        db = sqlite3.connect(self.database_file)
        cursor = db.cursor()
        cursor.execute(f"INSERT INTO users (username, email, password, isAdmin) VALUES ('{username}', '{email}', '{hashed_password}', '{isAdmin}')")
        db.commit()
        db.close()

    def update_user(self, id, username, email, password):
        db = sqlite3.connect(self.database_file)
        cursor = db.cursor()
        pwd = self.get_password_by_id(id)
        if pbkdf2_sha256.verify(password, pwd) or password == None:
            qry = f"UPDATE users SET username = '{username}', email = '{email}' WHERE id = '{id}'"
        else:
            hashed_password = pbkdf2_sha256.hash(password)
            qry = f"UPDATE users SET username = '{username}', email = '{email}', password = '{hashed_password}' WHERE id = '{id}'"
        cursor.execute(qry)
        db.commit()
        db.close()

    def delete_user(self, id):
        db = sqlite3.connect(self.database_file)
        cursor = db.cursor()
        cursor.execute(f"DELETE FROM users WHERE id = '{id}'")
        db.commit()
        db.close()

    def get_password_by_id(self, id):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT password FROM users WHERE id = '{id}'")
        pwd = cursor.fetchone()
        cursor.close()
        return pwd[0]

    def get_user_by_id(self, id):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT * FROM users WHERE id = '{id}'")
        user = cursor.fetchone()
        return user
    
    def get_vraag_by_id(self, id):
        cursor = sqlite3.connect(self.database_file).cursor()
        cursor.execute(f"SELECT * FROM vragen WHERE id = '{id}'")
        item = cursor.fetchone()
        return item

    def change_question_by_id(self, question, id):
        connection = sqlite3.connect(self.database_file)
        cursor = connection.cursor()
        cursor.execute(f"UPDATE vragen SET vraag = '{question}' WHERE id = '{id}'")
        connection.commit()
        cursor.close()

    def change_exception(self, id):
            connection = sqlite3.connect(self.database_file)
            item = self.get_vraag_by_id(id)
            if item[4] == 0:
                value = 1
                print ("TRUE")
            else:
                value = 0
                print ("FALSE")
            cursor = connection.cursor()
            cursor.execute(f"UPDATE vragen  SET uitzondering = '{value}' WHERE id = '{id}'")
            connection.commit()
            cursor.close()
  
    
