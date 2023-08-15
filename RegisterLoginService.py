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


@app.route('/check_status')
def check_status():
    isLogged = session.get('clientName')
    return jsonify({"Logged in client`s name": isLogged})


@app.route('/register', methods=['GET', 'POST'])
def register_user():
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
            return jsonify({"message": "There is no data"})


@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        request_data = request.get_json()
        clientId = None

        if request_data:
            if 'clientId' in request_data:
                clientId = request_data['clientId']

            DatabaseService.delete_client(clientId)
            msg = 'User account deleted successfully.'
            return jsonify({'Message': msg})
        else:
            msg = 'You used get method!'
            return jsonify({"message": msg})


@app.route('/update_user', methods=['GET', 'POST'])
def update_user():
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
                if not re.match(r'[^@]+@[^@]+\.[^@]+', clientEmail):
                    msg = 'Invalid email address!'
                elif not re.match(r'[A-Za-z0-9]+', clientName):
                    msg = 'Username must contain only characters and numbers !'
                else:
                    DatabaseService.insert_client("client", clientId, clientName, clientEmail, clientPassword)
                    msg = 'You have successfully updated the user account.'
                return jsonify({"message": msg})
        else:
            return jsonify({"message": "There is no data"})


@app.route('/read_users')
def read_users():
    return None

@app.route('/add_calendar', methods=['GET', 'POST'])
def add_calendar():
    if request.method == 'POST':
        request_data = request.get_json()
        calendarId = None
        clientEvent = None
        clientId = None

        if request_data:
            if 'calendarId' in request_data:
                calendarId = request_data['calendarId']
            if 'clientEvent' in request_data:
                clientEvent = request_data['clientEvent']
            if 'clientId' in request_data:
                clientId = request_data['clientId']

            DatabaseService.insert_google_calendar('calendar1', calendarId, clientEvent, clientId)
            msg = 'You have successfully added the calendar!'
            return jsonify({"message": msg})
        else:
            return jsonify({"message": "There is no data"})
    else:
        msg = 'You used get method!'
        return jsonify({"message": msg})


@app.route('/update_calendar', methods=['GET', 'POST'])
def update_calendar():
    if request.method == 'POST':
        request_data = request.get_json()
        calendarId = None
        clientEvent = None
        clientId = None

        if request_data:
            if 'calendarId' in request_data:
                calendarId = request_data['calendarId']
            if 'clientEvent' in request_data:
                clientEvent = request_data['clientEvent']
            if 'clientId' in request_data:
                clientId = request_data['clientId']

            DatabaseService.update_google_calendar()
    else:
        msg = 'You used get method!'
        return jsonify({"message": msg})


if __name__ == '__main__':
    app.run()
