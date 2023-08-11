from flask import Flask, render_template, request, redirect, url_for, session
import re
import DatabaseService


app = Flask(__name__)

app.route('/')

app.route('/login', methods=['GET', 'POST'])


def login():
    msg = ''
    # checking the method and if is there any info in form
    if request.method == 'POST' and 'clientName' in request.form and 'clientPassword' in request.form:
        clientName = request.form['clientName']
        clientPassword = request.form['clientPassword']
        account = DatabaseService.find_client_by_name(clientName)
        if account:
            session['loggedin'] = True
            session['clientId'] = account['clientId']
            session['clientName'] = account['clientName']
            msg = "Logged in succesfully!"
            return render_template('index.html', msg=msg)
        else:
            msg = "Incorrect username or password!"
    return render_template('login.html', msg=msg)


app.run()

if __name__ == '__main__':
    login()


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('clientId', None)
    session.pop('clientName',  None)
    return redirect(url_for('login'))


app.run()

if __name__ == '__main__':
    logout()


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'clientName' in request.form and 'clientPassword' in request.form and 'clientEmail' in request.form:
        clientName = request.form['clientName']
        clientPassword = request.form['clientPassword']
        clientEmail = request.form['clientEmail']
        account = DatabaseService.find_client_by_name(clientName)
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', clientEmail):
            msg = 'Invalid email adress!'
        elif not re.match(r'[A-Za-z0-9]+', clientName):
            msg = 'Username must contain only characters and numbers !'
        elif not clientName or not clientPassword or not clientEmail:
            msg = 'Please fill out the form !'
        else:
            DatabaseService.insert_client("client1", 1, clientName, clientEmail, clientPassword)
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


app.run()

if __name__ == '__main__':
    register()
