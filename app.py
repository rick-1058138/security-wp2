import os.path
import sys


from flask import Flask, render_template, request, redirect, url_for, session

from lib.tablemodel import DatabaseModel
from lib.demodatabase import create_demo_database

# This demo glues a random database and the Flask framework. If the database file does not exist,
# a simple demo dataset will be created.
LISTEN_ALL = "0.0.0.0"
FLASK_IP = LISTEN_ALL
FLASK_PORT = 81
FLASK_DEBUG = True

app = Flask(__name__)
# This command creates the "<application directory>/databases/testcorrect_vragen.db" path
DATABASE_FILE = os.path.join(app.root_path, 'databases', 'testcorrect_vragen.db')

# Check if the database file exists. If not, create a demo database
if not os.path.isfile(DATABASE_FILE):
    print(f"Could not find database {DATABASE_FILE}, creating a demo database.")
    create_demo_database(DATABASE_FILE)
dbm = DatabaseModel(DATABASE_FILE)

app.secret_key = 'Software inc.'

# Main route that shows a list of tables in the database
# Note the "@app.route" decorator. This might be a new concept for you.
# It is a way to "decorate" a function with additional functionality. You
# can safely ignore this for now - or look into it as it is a really powerful
# concept in Python.
# @app.route("/")
# def index():
#     tables = dbm.get_table_list()
#     return render_template(
#         "tables.html", table_list=tables, database_file=DATABASE_FILE
#     )

@app.route("/")
def index():
    return render_template(
        "home.html"
    )


@app.route("/data/<table>")
@app.route("/data", methods=['GET'])
def question_data(table = 'vragen'):
    # min and max value for each column of vragen (can later contain other tables as well)
    minmax = dbm.get_tables_min_max()
    # allowed tables and none because none is the first value when visiting without filters
    allowed_tables = ['auteurs', 'leerdoelen', 'vragen', None]
    if request.method == 'GET':
        # needs validation ( only allowed tables: auteurs, leerdoelen, vragen)
        table = request.args.get('table_choice')
        type = request.args.get('error_type')
        column = request.args.get('column')

        # check if table is allowed to be shown 
        if table in allowed_tables:
            # get leerdoelen data is table = vragen, else return none
            if(table == 'vragen'):
                leerdoelen = dbm.get_content('leerdoelen')
            else:
                leerdoelen = None
        else:
            # when not allowed return 404 page 
            return render_template(
                "404.html"
            )
    if not table:
        # set default table 
        print("default")
        DEFAULT = 'vragen'
        table = DEFAULT
        type = 'leerdoel'
        column = 'id'
        data, columns = dbm.get_content(table)
    else:
        # set chosen table
        data, columns = dbm.get_content(table)

        if type == 'leerdoel':
            column = 'leerdoel'
            data, columns = dbm.get_no_leerdoel()
        elif type == 'html':
            column = 'vraag'
            data, columns = dbm.get_html_codes()
        elif type == 'empty':
            data, columns = dbm.get_empty_column(table, column)


    return render_template(
        "db_data.html", 
        data = data, 
        columns = columns, 
        tables = ['auteurs', 'leerdoelen', 'vragen'], 
        current_table = table, 
        current_column = column, 
        current_type = type, 
        leerdoelen = leerdoelen,
        minmax = minmax
    )

# Website used: https://codeshack.io/login-system-python-flask-mysql/
@app.route("/login", methods=['POST', 'GET'])
def login():
    table_name = 'users'
    error = None
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = dbm.validate_login(table_name, username, password)
        if(account):
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            return 'Logged in successfully!'
        else:
            error = "Invalid username or password"
    return render_template(
        "login.html", 
        error = error
    )

# Website used: https://codeshack.io/login-system-python-flask-mysql/
@app.route("/logout")
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return render_template(
        "home.html"
    )

@app.route("/edit")
def edit():
    return render_template(
        "edit.html"
    )


# The table route displays the content of a table
@app.route("/table_details/<table_name>")
def table_content(table_name=None):
    if not table_name:
        return "Missing table name", 400  # HTTP 400 = Bad Request
    else:
        rows, column_names = dbm.get_table_content(table_name)
        return render_template(
            "table_details.html", rows=rows, columns=column_names, table_name=table_name
        )

if __name__ == "__main__":
    app.run(host=FLASK_IP, port=FLASK_PORT, debug=FLASK_DEBUG)
