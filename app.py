import os.path
import sys
import datetime



from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash, make_response, Response
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

# A secret key is needed to allow for sessions.
app.secret_key = 'Software inc.'


data_rows = None
data_columns = None

def set_data_rows(data):
    global data_rows
    data_rows = data

def set_data_columns(columns):
    global data_columns
    data_columns = columns


def get_data_rows():
    return data_rows

def get_data_columns():
    return data_columns
# A decorator to check if you are logged in. If you are, it redirects you to the requested page.
#   If you are not logged in, it instead redirects you to the login page.
#
# Used sources:
# https://stackoverflow.com/questions/35307676/check-login-status-flask
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

# A decorator to check if you are using an administrator account. If you are, it redirects you to the requested page.
#   If you are not using an administrator account, it instead redirects you to the home page.
#
# Used sources:
# https://stackoverflow.com/questions/35307676/check-login-status-flask
# https://flask.palletsprojects.com/en/2.0.x/patterns/viewdecorators/?highlight=wrap
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'isAdmin' in session and session['isAdmin'] == 1:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('index'))
    return wrap

# When requesting a new page, checks to see if the session lifetime has expired.
#   If so, it will clear the session data and you will be required to login again.
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(days=1)
    session.modified = True

# The home page. You are directed here upon establishing a connection to the website.
@app.route("/")
def index():
    return render_template(
        "home.html"
    )

# The question page. This handles all of the requests related to showing questions.
@app.route("/data", methods=['GET'])
@login_required
def question_data(table = 'vragen'):
    # Min and max value for each column of vragen (can later contain other tables as well).
    minmax = dbm.get_tables_min_max()
    # Allowed tables and none, because none is the first value when visiting without filters.
    allowed_tables = ['auteurs', 'leerdoelen', 'vragen', None]

    # Columns with integers that can be filtered by min and max values.
    allowed_between_columns = ['id', 'leerdoel', 'auteur', 'geboortejaar']

    if request.method == 'GET':
        # Needs validation (only allowed tables: auteurs, leerdoelen, vragen).
        table = request.args.get('table_choice')
        type = request.args.get('error_type')
        column = request.args.get('column')

        uitzondering = request.args.get('uitzondering')

        between_column = request.args.get('between_column')
        min = request.args.get('min')
        max = request.args.get('max')
        # Check if min or max input is filled, otherwise it is set to none.
        if min == '' or max == '':
            min = None
            max = None

        min_max_filter = False
        
        # Check if min and max are set.
        if(min != None and max != None):
            min_max_filter = True
        else:
            min_max_filter = False

        if not table:
            # Set the default table. 
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
            # Get data for the chosen error type.
            if type == 'leerdoel':
                column = 'leerdoel'
                data, columns = dbm.get_no_leerdoel(min_max_filter, between_column, min, max, uitzondering)
            elif type == 'auteur':
                column = 'auteur'
                data, columns = dbm.get_no_auteur(min_max_filter, between_column, min, max, uitzondering)
            elif type == 'html':
                column = 'vraag'
                data, columns = dbm.get_html_codes(min_max_filter, between_column, min, max, uitzondering)
            elif type == 'empty':
                data, columns = dbm.get_empty_column(table, column, min_max_filter, between_column, min, max, uitzondering)
            elif type == 'wrong_value':
                data, columns = dbm.get_wrong_value(table, column, min_max_filter, between_column, min, max, uitzondering)
            else:
                data, columns = dbm.get_requested_rows(table, min_max_filter, between_column, min, max, uitzondering)

        # Check if the table is allowed to be shown. 
        if table in allowed_tables:
            # Get leerdoelen and auteurs data if table = vragen, else return none.
            if(table == 'vragen'):
                leerdoelen = dbm.get_content('leerdoelen')
                auteurs = dbm.get_content('auteurs')
            else:
                leerdoelen = None
                auteurs = None
        else:
            # When not allowed, return 404 page.
            return render_template(
                "404.html"
            )

        # set data for csv export 
        set_data_rows(data)
        set_data_columns(columns)

        return render_template(
            "db_data.html", 
            data = data, 
            columns = columns, 
            tables = ['auteurs', 'leerdoelen', 'vragen'], 
            current_table = table, 
            current_column = column, 
            current_type = type, 
            leerdoelen = leerdoelen,
            auteurs = auteurs,
            minmax = minmax,
            current_between_column = between_column,
            chosen_min = min,
            chosen_max = max,
            allowed_between_columns = allowed_between_columns,
            current_uitzondering = uitzondering
        )

# The login page. When given a username and password pair, checks to see if the credentials are valid. 
#   If so, logs the user in, creates session data for the user and redirects to the question page. 
#   If not, displays an error on the screen.
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
            return redirect(url_for('question_data'))
        else:
            error = "Ongeldige gebruikersnaam en/of ongeldig wachtwoord. Probeer het opnieuw."
    return render_template(
        "login.html", 
        error = error
    )

# Logs the user out by removing the session data. The redirects the user to the home page.
# Website used: https://codeshack.io/login-system-python-flask-mysql/
@app.route("/logout")
@login_required
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('isAdmin', None)
    return render_template(
        "home.html"
    )


@app.route("/admin", methods=['GET'])
@admin_required
def admin():
    if request.method == 'GET':
        data, columns = dbm.get_content('users')
    return render_template(
        "admin.html", 
        data = data, 
        columns = columns
    )

# Obtains information about a specific user using their id and returns data in json format to the page that requested the data.
@app.route("/getuser", methods=["GET", "POST"])
@login_required
def getuser():
    data = dbm.get_user_by_id(request.args.get('id'))
    return jsonify(data)

# Modifies information about a specific user using their id.
@app.route("/edituser", methods=['GET', 'POST'])
@login_required
def edit_user():
    dbm.update_user(request.form.get('id'), request.form.get('username'), request.form.get('email'), request.form.get('password'))
    if request.method == 'POST':
        return redirect("/admin", code=302)

# Creates a new user using the credentials provided in the completed form.
@app.route("/createuser", methods=['GET', 'POST'])
@login_required
def create_user():
    user_exists = dbm.check_user_exists(request.form.get('username'), request.form.get('email'))
    if user_exists:
        flash( "Gebruikersnaam of email al in gebruik.")
    else:
        dbm.create_user(request.form.get('username'), request.form.get('email'), request.form.get('password'))
    if request.method == 'POST':
        return redirect("/admin", code=302) 

# Deletes a specific user using their id.
@app.route("/deleteuser", methods=['GET', 'POST'])
@login_required
def delete_user():
    dbm.delete_user(request.form.get('id'))
    if request.method == 'POST':
        return redirect("/admin", code=302)     

# Obtains information about a specific question using its id and returns data in json format to the page that requested the data.   
@app.route("/getitem", methods=["GET", "POST"])
@login_required
def getitem():
    table = request.args.get('table')
    if table == 'vragen':
        data_vraag = dbm.get_vraag_by_id(request.args.get('id'))
        data_leerdoelen = dbm.get_content('leerdoelen')
        data_auteurs = dbm.get_content('auteurs')
        return jsonify(data_vraag, data_leerdoelen, data_auteurs)
    elif table == 'auteurs':
        data_auteur = dbm.get_item_by_id(table, request.args.get('id'))
        return jsonify(data_auteur)
    elif table == 'leerdoelen':
        data_leerdoelen = dbm.get_item_by_id(table, request.args.get('id'))
        return jsonify(data_leerdoelen)

# Modifies information about a specific question using its id.
@app.route("/editquestion", methods=['POST', 'GET'])
@login_required
def edit_question():
    table = request.form.get('table')
    if table == 'vragen':
        dbm.change_question_by_id(request.form.get('question'), request.form.get('leerdoel'), request.form.get('auteur'), request.form.get('id'))
    elif table == 'auteurs':
        dbm.change_auteur_by_id(request.form.get('voornaam'), request.form.get('achternaam'), request.form.get('geboortejaar'), request.form.get('medewerker'), request.form.get('pensioen'), request.form.get('id'))
    elif table == 'leerdoelen':
        dbm.change_leerdoel_by_id(request.form.get('leerdoel'), request.form.get('id'))

    if request.method == 'POST':
        return redirect("/data?table_choice="+table, code=302)

# Modifies the excesption tag of a specific question using its id.
@app.route("/editexception", methods=['POST', 'GET'])
@login_required
def edit_exception():
    dbm.change_exception(request.form.get('id'))
    if request.method == 'POST':
        return redirect("/data", code=302)

# Redirects to the selected question within the test-correct platform. Access is currently not possible, as this is blocked on the 
#   Product Owner's side.
@app.route('/question/<id>')
@login_required
def test(id):
    return redirect("https://www.test-correct.nl/?vraag=" + id)

@app.route("/csv")
@login_required
def returncsv():
    csv = get_data_rows()
    columns = get_data_columns()

    def generate():
        for row in csv:
            if not None:
                yield '## '
                for column in columns:
                    yield str(column) + ','
                yield ' ## \n'

                for item in row:
                    yield str(item) + '\n'
                yield '\n'
    return Response(generate(), mimetype='text/csv')

if __name__ == "__main__":
    app.run(host=FLASK_IP, port=FLASK_PORT, debug=FLASK_DEBUG)