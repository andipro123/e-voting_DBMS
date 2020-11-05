from flask import Flask, request, render_template, session, redirect, url_for
from flaskext.mysql import MySQL
import sys
import hashlib

app = Flask(__name__)

app.secret_key = 'DBMS mini project'

#load the configuration file
app.config.from_pyfile('./config.cfg')

# MySQL configurations
app.config['MYSQL_DATABASE_USER']
app.config['MYSQL_DATABASE_PASSWORD']
app.config['MYSQL_DATABASE_DB']
app.config['MYSQL_DATABASE_HOST']

# MySQL Object
mysql = MySQL()
mysql.init_app(app)


@app.route("/login", methods=["GET", "POST"])
def login():

    form_filled = 'username' in request.form and 'password' in request.form
    message = ""
    if request.method == 'POST' and form_filled:
        username = request.form['username']
        password = request.form['password']
        isAdmin = request.form.get('admin', False) == 'on'

        salt = "evoting"
        db_pass = password + salt
        h = hashlib.md5(db_pass.encode())
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            if not isAdmin:
                cursor.execute(
                    'SELECT * FROM voter WHERE username = %s AND password = %s',
                    (username, h.hexdigest()))
                account = cursor.fetchone()
                print(account)
                if account:
                    session['loggedin'] = True
                    session['voter_id'] = account[0]
                    session['voter_name'] = account[1]
                    session['username'] = account[2]
                    session['role'] = 'voter'
                    message = "Login successful"

                    return redirect(url_for('vote'))
                else:
                    message = 'Incorrect username or password'

            else:
                cursor.execute(
                    'SELECT * FROM admin WHERE username = %s AND password = %s',
                    (username, h.hexdigest()))
                account = cursor.fetchone()
                print(account)
                if account:
                    session['loggedin'] = True
                    session['admin_id'] = account[0]
                    session['username'] = account[2]
                    session['role'] = 'admin'
                    message = "Login successful"

                    return redirect(url_for('admin'))

                else:
                    message = 'Incorrect user name and password'

        except Exception as e:
            print(e)

    return render_template('login.html', message=message)


@app.route("/register", methods=['GET', 'POST'])
def register():

    form_filled = 'voter_id' in request.form and 'name' in request.form and 'username' in request.form and 'password' in request.form and 'assembly' in request.form
    message = ""

    if request.method == 'POST' and form_filled:
        voter_id = request.form['voter_id']
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        has_voted = False
        assembly = request.form['assembly']
        isAdmin = request.form.get('admin', False)

        # For storing password, we need to hash it
        salt = "evoting"
        db_pass = password + salt
        h = hashlib.md5(db_pass.encode())

        try:

            conn = mysql.connect()
            cursor = conn.cursor()

            if not isAdmin:

                cursor.execute('SELECT * FROM voter WHERE voter_id = %s',
                               (voter_id, ))
                account = cursor.fetchone()

                if not account:
                    cursor.execute(
                        'INSERT INTO voter VALUES (%s, %s, %s, %s, false, %s)',
                        (voter_id, name, username, h.hexdigest(), assembly))
                    conn.commit()
                    response = cursor.fetchall()
                    print(response)
                    message = "Account created succesfully"
                    print(message)
                else:
                    message = "Account already exists"
                    print(message)

            else:
                cursor.execute('SELECT * FROM admin WHERE admin_id = %s',
                               (voter_id, ))
                account = cursor.fetchone()

                if not account:
                    cursor.execute(
                        'INSERT INTO admin VALUES (%s, %s, %s, %s, %s)',
                        (voter_id, name, username, h.hexdigest(), assembly))
                    conn.commit()
                    response = cursor.fetchall()
                    print(response)
                    message = "Account created successfully"
                    print(message)
                else:
                    message = "Account already exists"
                    print(message)

        except Exception as e:
            print(e)

    elif request.method == "POST":
        message = "Please fill out the form completely"

    return render_template('register.html', message=message)


@app.route('/')
def index():
    isLogged = session.get('loggedin', False)
    if isLogged:
        return redirect(url_for('vote'))

    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('voter_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/vote', methods=['GET', 'POST'])
def vote():

    if request.method == 'GET':
        isLogged = session.get('loggedin', False)
        if isLogged:
            try:
                conn = mysql.connect()
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM candidate')
                candidates = cursor.fetchall()
                print(candidates)
                return render_template('vote.html', candidates=candidates)

            except Exception as e:
                print(e)

        return redirect(url_for('login'))

    elif request.method == 'POST':
        isLogged = session.get('loggedin', False)
        message = ""
        if isLogged:
            voter_id = session['voter_id']

            # try:
            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute('SELECT has_voted FROM voter where voter_id=%s',
                           (voter_id, ))
            has_voted = cursor.fetchone()

            if has_voted[0]:
                message = "You have already cast your vote!"
                return render_template('login.html', message=message)
            else:
                print(request.form)
                candidate_id = request.form['candidate_id']

                cursor.execute(
                    'INSERT INTO vote VALUES (DEFAULT, %s, %s, DEFAULT)', (
                        candidate_id,
                        voter_id,
                    ))

                voter_name = session['voter_name']

                cursor.execute(
                    'SELECT name FROM candidate WHERE candidate_id=%s',
                    (candidate_id, ))
                candidate_name = cursor.fetchone()

                cursor.execute(
                    'INSERT INTO votes_for VALUES (%s, %s, %s, %s)',
                    (voter_id, voter_name, candidate_id, candidate_name))
                response = cursor.fetchall()
                print(response)

                cursor.execute(
                    'UPDATE voter SET has_voted=true WHERE voter_id=%s',
                    (voter_id, ))

                response = cursor.fetchall()
                print(response)

                cursor.execute(
                    'UPDATE candidate SET number_of_votes=number_of_votes+1 WHERE candidate_id=%s',
                    (candidate_id, ))

                conn.commit()
                response = cursor.fetchall()
                print(response)

                message = 'Vote casted successfully!'
                return render_template('login.html', message1=message)

            # except Exception as e:
            #     print(e)
            #     return redirect(url_for('vote'))

        else:
            return redirect(url_for('login'))


@app.route('/results', methods=['GET'])
def results():
    if request.method == "GET":
        isLogged = session.get('loggedin', False)
        if isLogged:

            try:
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT candidate_id, name, party, assembly, number_of_votes FROM candidate ORDER BY number_of_votes DESC;'
                )

                results = cursor.fetchall()

                return render_template('results.html', results=results)

            except Exception as e:
                print(e)

    return redirect(url_for('login'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        isLogged = session.get('loggedin', False)
        isAdmin = session.get('role', False) == 'admin'
        if isLogged and isAdmin:
            try:
                conn = mysql.connect()
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM candidate')
                candidates = cursor.fetchall()
                cursor.execute('SELECT * FROM voter')
                voters = cursor.fetchall()
                print(voters)
                return render_template('admin.html',
                                       candidates=candidates,
                                       voters=voters)

            except Exception as e:
                print(e)

        return redirect(url_for('login'))


@app.route('/disqualify_c', methods=['POST'])
def disqualify_c():
    if request.method == 'POST':
        isLogged = session.get('loggedin', False)
        isAdmin = session.get('role', False) == 'admin'
        if isLogged and isAdmin:
            candidates = []
            for ele in request.form:
                candidates.append(int(ele[0]))
            candidates = tuple(candidates)

            try:
                conn = mysql.connect()
                cursor = conn.cursor()

                cursor.execute(
                    'DELETE from candidate WHERE candidate_id in %s',
                    (candidates, ))
                conn.commit()
                res = cursor.fetchall()
                print(res)

            except Exception as e:
                print(e)

        return redirect(url_for('admin'))

    return redirect(url_for('admin'))


@app.route('/disqualify_v', methods=['POST'])
def disqualify_v():
    if request.method == 'POST':
        isLogged = session.get('loggedin', False)
        isAdmin = session.get('role', False) == 'admin'

        if isLogged and isAdmin:
            voters = []
            for ele in request.form:
                voters.append(int(ele[0]))
            voters = tuple(voters)

            try:
                conn = mysql.connect()
                cursor = conn.cursor()

                cursor.execute('DELETE from voter WHERE voter_id in %s',
                               (voters, ))
                conn.commit()
                res = cursor.fetchall()
                print(res)

            except Exception as e:
                print(e)

        return redirect(url_for('admin'))

    return redirect(url_for('admin'))


@app.route('/publish', methods=['POST'])
def publish():
    if request.method == 'POST':
        isLogged = session.get('loggedin', False)
        isAdmin = session.get('role', False) == 'admin'

        if isLogged and isAdmin:
            admin_id = session['admin_id']

            try:
                conn = mysql.connect()
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT candidate_id, name, party, assembly, number_of_votes FROM candidate ORDER BY number_of_votes DESC;'
                )

                results = cursor.fetchall()

                cursor.execute(
                    'INSERT INTO results VALUES (DEFAULT, %s, %s, %s, %s, %s, %s,)',
                    (admin_id, results[0][0], results[0][1], results[0][4],
                     results[0][2], results[0][3]))

                conn.commit()
                res = cursor.fetchall()
                print(res)

                return render_template('results.html', results=results)

            except Exception as e:
                print(e)

    return redirect(url_for('admin'))


app.run(host='0.0.0.0', port=5000, debug=True)