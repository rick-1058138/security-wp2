import os.path
import sys
import datetime



from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from functools import wraps


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


# Used sources:
# https://stackoverflow.com/questions/35307676/check-login-status-flask
#
# https://flask.palletsprojects.com/en/2.0.x/patterns/viewdecorators/?highlight=wrap
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'loggedin' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('login'))
    return wrap

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(days=1)
    session.modified = True

@app.route("/")
def index():
    return render_template(
        "home.html"
    )

@app.route("/data", methods=['GET'])
@login_required
def question_data(table = 'vragen'):
    # min and max value for each column of vragen (can later contain other tables as well)
    minmax = dbm.get_tables_min_max()
    # allowed tables and none because none is the first value when visiting without filters
    allowed_tables = ['auteurs', 'leerdoelen', 'vragen', None]

    # columns with integers that can be filtered by min and max values 
    allowed_between_columns = ['id', 'leerdoel', 'auteur', 'geboortejaar']

    if request.method == 'GET':
        # needs validation ( only allowed tables: auteurs, leerdoelen, vragen)
        table = request.args.get('table_choice')
        type = request.args.get('error_type')
        column = request.args.get('column')

        uitzondering = request.args.get('uitzondering')

        between_column = request.args.get('between_column')
        min = request.args.get('min')
        max = request.args.get('max')
        # check if min or max input is filled else set to none
        if min == '' or max == '':
            min = None
            max = None

        min_max_filter = False
        
        # check if min and max are set
        if(min != None and max != None):
            min_max_filter = True
            print("min & max value zijn gezet")

        else:
            min_max_filter = False

        

        if not table:
            # set default table 
            print("default")
            DEFAULT_TABLE = 'vragen'
            DEFAULT_TYPE = 'alles'
            DEFAULT_COLUMN = 'id'
            DEFAULT_UITZONDERING = 'alles'
            table = DEFAULT_TABLE
            type = DEFAULT_TYPE
            column = DEFAULT_COLUMN
            uitzondering = DEFAULT_UITZONDERING
            data, columns = dbm.get_content(table)
        else:
            # get data for chosen error type
            if type == 'leerdoel':
                column = 'leerdoel'
                data, columns = dbm.get_no_leerdoel(min_max_filter, between_column, min, max, uitzondering)
            elif type == 'html':
                column = 'vraag'
                data, columns = dbm.get_html_codes(min_max_filter, between_column, min, max, uitzondering)
            elif type == 'empty':
                data, columns = dbm.get_empty_column(table, column, min_max_filter, between_column, min, max, uitzondering)
            elif type == 'wrong_value':
                data, columns = dbm.get_wrong_value(table, column, min_max_filter, between_column, min, max, uitzondering)
            # # elif type == 'uitzondering':
            #     data, columns = dbm.get_exception(table, column, min_max_filter, between_column, min, max)
            else:
                print("else")
                # if type == 'alles' and else
                data, columns = dbm.get_requested_rows(table, min_max_filter, between_column, min, max, uitzondering)

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

        return render_template(
            "db_data.html", 
            data = data, 
            columns = columns, 
            tables = ['auteurs', 'leerdoelen', 'vragen'], 
            current_table = table, 
            current_column = column, 
            current_type = type, 
            leerdoelen = leerdoelen,
            minmax = minmax,
            current_between_column = between_column,
            chosen_min = min,
            chosen_max = max,
            allowed_between_columns = allowed_between_columns,
            current_uitzondering = uitzondering
        )


# Website used: https://codeshack.io/login-system-python-flask-mysql/
@app.route("/login", methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = dbm.validate_login(username, password)
        if(account):
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            session['isAdmin'] = account[4]
            flash('Logged in succefully!')
            return redirect(url_for('index'))
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
    session.pop('isAdmin', None)
    return render_template(
        "home.html"
    )

@app.route("/admin", methods=['GET'])
@login_required
def admin():
    table_name = 'users'
    if request.method == 'GET':
        data, columns = dbm.get_content(table_name)
    elif request.method == 'POST':
        raise ValueError('Build an add users function first!')
        #dbm.create_user('F', 'F@random.com', '0000')
        data, columns = dbm.get_content(table_name)
    return render_template(
        "admin.html", 
        data = data, 
        columns = columns
    )

@app.route("/getuser", methods=["GET", "POST"])
def getuser():
    data = dbm.get_user_by_id(request.args.get('id'))
    print(request.args.get('id'))
    return jsonify(data)

@app.route("/edituser", methods=['GET', 'POST'])
def edit_user():
    dbm.update_user(request.form.get('id'), request.form.get('username'), request.form.get('email'), request.form.get('password'))
    if request.method == 'POST':
        return redirect("/admin", code=302)

@app.route("/createuser", methods=['GET', 'POST'])
def create_user():
    dbm.create_user(request.form.get('username'), request.form.get('email'), request.form.get('password'))
    if request.method == 'POST':
        return redirect("/admin", code=302)      
    
@app.route("/getitem", methods=["GET", "POST"])
def getitem():
    data = dbm.get_vraag_by_id(request.args.get('id'))
    print(request.args.get('id'));
    return jsonify(data);

@app.route("/editquestion", methods=['POST', 'GET'])
def edit_question():
    dbm.change_question_by_id(request.form.get('question'), request.form.get('id'))
    if request.method == 'POST':
        return redirect("/data", code=302)

@app.route("/editexception", methods=['POST', 'GET'])
def edit_exception():
    dbm.change_exception(request.form.get('id'))
    if request.method == 'POST':
        return redirect("/data", code=302)

@app.route('/question/<id>')
def test(id):
    return redirect("https://www.test-correct.nl/?vraag=" + id)
    
@app.route("/user")
def incorrect_data():
    return render_template(
        "user.html"
    )


# The table route displays the content of a table
@app.route("/table_details/<table_name>")
@login_required
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
