from flask import Flask, request, redirect, url_for, session, jsonify
import DatabaseService
import re

app = Flask(__name__)
app.secret_key = '1111'


@app.route('/')
def main_page():
    return 'Main page.'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        request_data = request.get_json()
        clientName = None
        clientPassword = None

        if request_data:
            if 'clientName' in request_data:
                clientName = request_data['clientName']
            if 'clientPassword' in request_data:
                clientPassword = request_data['clientPassword']

            account = DatabaseService.find_client_by_name(clientName)
            if account:
                print('client id: ', account.client_id)
                session['logged_in'] = True
                session['clientId'] = account.client_id
                session['clientName'] = account.client_name
                msg = 'Logged in successfully!'
                return jsonify({"message": msg, "name": session.get('clientName')})
            else:
                msg = 'Incorrect username or password!'
                return jsonify({"message": msg})
    else:
        msg = 'You used get method!'
        return jsonify({"message": msg})


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('clientId', None)
    session.pop('clientName', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        request_data = request.get_json()
        clientName = None
        clientPassword = None
        clientEmail = None
        clientId = None

        if request_data:
            if 'clientName' in request_data:
                clientName = request_data['clientName']
            if 'clientPassword' in request_data:
                clientPassword = request_data['clientPassword']
            if 'clientEmail' in request_data:
                clientEmail = request_data['clientEmail']
            if 'clientId' in request_data:
                clientId = request_data['clientId']

            account = DatabaseService.find_client_by_name(clientName)
            if account:
                msg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', clientEmail):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', clientName):
                msg = 'Username must contain only characters and numbers !'
            else:
                DatabaseService.insert_client("client1", clientId, clientName, clientEmail, clientPassword)
                msg = 'You have successfully registered!'
            return jsonify({"message": msg})
        else:
            return jsonify({"message": "there is no data"})


@app.route('/check')
def check():
    isLogged = session.get('clientName')
    return isLogged


if __name__ == '__main__':
    app.run()
