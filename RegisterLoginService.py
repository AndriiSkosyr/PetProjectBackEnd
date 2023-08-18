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


@app.route('/client', methods=['POST'])
def create_client():
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

        account = DatabaseService.find_client(clientId)
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


@app.route('/client', methods=['DELETE'])
def delete_client():
    request_data = request.get_json()
    clientId = None

    if request_data:
        if 'clientId' in request_data:
            clientId = request_data['clientId']

        DatabaseService.delete_client(clientId)
        msg = 'User account deleted successfully.'
        return jsonify({'Message': msg})
    else:
        return jsonify({"message": "There is no data"})


@app.route('/client', methods=['PUT'])
def update_client():
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

        account = DatabaseService.find_client(clientId)
        if account:
            if not re.match(r'[^@]+@[^@]+\.[^@]+', clientEmail):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', clientName):
                msg = 'Username must contain only characters and numbers !'
            else:
                account.client_name = clientName
                account.client_password = clientPassword
                account.client_email = clientEmail
                DatabaseService.update_client(clientId, account)
                msg = 'You have successfully updated the client account.'
            return jsonify({"message": msg})
    else:
        return jsonify({"message": "There is no data"})


@app.route('/client', methods=['GET'])
def read_client():
    request_data = request.get_json()
    clientId = None

    if request_data:
        if 'clientId' in request_data:
            clientId = request_data['clientId']

        account = DatabaseService.find_client(clientId)

        return jsonify({"Client.name:": account.client_name, "Client.email:": account.client_email})
    return jsonify({"message": "There is no data"})


@app.route('/calendar', methods=['POST'])
def create_calendar():
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

        calendar = DatabaseService.find_calendar(calendarId)
        if calendar:
            msg = 'Calendar already exists!'
        else:
            DatabaseService.insert_google_calendar("calendar", calendarId, clientEvent, clientId)
            msg = 'You have successfully added the calendar!'
        return jsonify({"Message": msg})
    else:
        return jsonify({"message": "There is no data!"})


@app.route('/update_calendar', methods=['PUT'])
def update_calendar():
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

        calendar = DatabaseService.find_calendar(calendarId)
        if calendar:
            calendar.client_event = clientEvent
            calendar.client_id = clientId
            DatabaseService.update_google_calendar(calendarId, calendar)
            msg = 'You have successfully updated the calendar!'
        else:
            msg = "There is no such calendar!"
        return jsonify({"Message": msg})
    else:
        return jsonify({"message": "There is no data"})


@app.route('/calendar', methods=['DELETE'])
def delete_calendar():
    request_data = request.get_json()
    calendarId = None

    if request_data:
        if 'calendarId' in request_data:
            calendarId = request_data['calendarId']

        DatabaseService.delete_google_calendar(calendarId)
        msg = 'Google calendar deleted successfully.'
        return jsonify({'Message': msg})
    else:
        return jsonify({"message": "There is no data"})


@app.route('/calendar', methods=['GET'])
def read_calenar():
    request_data = request.get_json()
    calendarId = None

    if request_data:
        if 'calendarId' in request_data:
            calendarId = request_data['calendarId']

        calendar = DatabaseService.find_calendar(calendarId)

        return jsonify({"Client.event:": calendar.client_event, "Client.id:": calendar.client_id})
    return jsonify({"message": "There is no data"})


if __name__ == '__main__':
    app.run()
