from flask import Flask, request, session, jsonify
from flask_cors import CORS
import DatabaseService
import re

app = Flask(__name__)
app.secret_key = '1111'
CORS(app, origins="http://localhost:3000")


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
            if account and clientPassword == account.client_password:
                session['logged_in'] = True
                session['clientId'] = account.client_id
                session['clientName'] = account.client_name
                msg = 'Logged in successfully!'
                return jsonify({'Message': msg, 'Client name': session.get('clientName')})
            else:
                msg = 'Incorrect username or password!'
                return jsonify({'Message': msg})
        else:
            return jsonify({'Message': "There is no request data!"})


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('clientId', None)
    session.pop('clientName', None)
    return jsonify({"Message": "Logged out successfully!"})


@app.route('/check_status')
def check_status():
    isLogged = session.get('clientName')
    return jsonify({'Logged in client`s name': isLogged})


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
            msg = 'Username must contain only characters and numbers!'
        else:
            DatabaseService.insert_client('client1', clientId, clientName, clientEmail, clientPassword)
            msg = 'You have successfully registered!'
        return jsonify({'Message': msg})
    else:
        return jsonify({'Message': 'There is no request data!'})


@app.route('/client', methods=['GET'])
def read_client():
    request_data = request.get_json()
    clientId = None

    if request_data:
        if 'clientId' in request_data:
            clientId = request_data['clientId']

        account = DatabaseService.find_client(clientId)
        if account:
            return jsonify({'Client.name:': account.client_name, 'Client.email:': account.client_email})
        else:
            return jsonify({'Message': 'There is no such client!'})
    return jsonify({'Message': 'There is no request data!'})


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

        client = DatabaseService.find_client(clientId)
        if client:
            if not re.match(r'[^@]+@[^@]+\.[^@]+', clientEmail):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', clientName):
                msg = 'Username must contain only characters and numbers!'
            else:
                client.client_name = clientName
                client.client_password = clientPassword
                client.client_email = clientEmail
                DatabaseService.update_client(clientId, client)
                msg = 'You have successfully updated the client account!'
            return jsonify({'message': msg})
        else:
            msg = 'There is no such client!'
            return jsonify({'message': msg})
    else:
        return jsonify({'message': 'There is no request data!'})


@app.route('/client', methods=['DELETE'])
def delete_client():
    request_data = request.get_json()
    clientId = None

    if request_data:
        if 'clientId' in request_data:
            clientId = request_data['clientId']

        client = DatabaseService.find_client(clientId)
        if client:
            DatabaseService.delete_client(clientId)
            msg = 'User account deleted successfully!'
        else:
            msg = 'There is no such client!'
        return jsonify({'Message': msg})
    else:
        return jsonify({'Message': 'There is no request data!'})


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
            DatabaseService.insert_google_calendar('calendar', calendarId, clientEvent, clientId)
            msg = 'You have successfully added the calendar!'
        return jsonify({'Message': msg})
    else:
        return jsonify({'message': 'There is no request data!'})


@app.route('/calendar', methods=['GET'])
def read_calendar():
    request_data = request.get_json()
    calendarId = None

    if request_data:
        if 'calendarId' in request_data:
            calendarId = request_data['calendarId']

        calendar = DatabaseService.find_calendar(calendarId)
        if calendar:
            return jsonify({'Client.event:': calendar.client_event, 'Client.id:': calendar.client_id})
        else:
            return jsonify({'Message': 'There is no such calendar!'})
    return jsonify({'message': 'There is no request data!'})


@app.route('/calendar', methods=['PUT'])
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
            msg = 'There is no such calendar!'
        return jsonify({'Message': msg})
    else:
        return jsonify({'message': 'There is no request data!'})


@app.route('/calendar', methods=['DELETE'])
def delete_calendar():
    request_data = request.get_json()
    calendarId = None

    if request_data:
        if 'calendarId' in request_data:
            calendarId = request_data['calendarId']

        calendar = DatabaseService.find_calendar(calendarId)
        if calendar:
            DatabaseService.delete_google_calendar(calendarId)
            msg = 'Google calendar deleted successfully.'
        else:
            msg = 'There is no such calendar!'
        return jsonify({'Message': msg})
    else:
        return jsonify({'message': 'There is no request data!'})


@app.route('/event', methods=['POST'])
def create_event():
    request_data = request.get_json()
    eventId = None
    clientName = None
    eventDate = None
    summaryText = None
    description = None
    meetingLink = None
    calendarId = None

    if request_data:
        if 'eventId' in request_data:
            eventId = request_data['eventId']
        if 'clientName' in request_data:
            clientName = request_data['clientName']
        if 'eventDate' in request_data:
            eventDate = request_data['eventDate']
        if 'summaryText' in request_data:
            summaryText = request_data['summaryText']
        if 'description' in request_data:
            description = request_data['description']
        if 'meetingLink' in request_data:
            meetingLink = request_data['meetingLink']
        if 'calendarId' in request_data:
            calendarId = request_data['calendarId']

        event = DatabaseService.find_event(eventId)
        if event:
            msg = 'Event already exists!'
        else:
            DatabaseService.insert_calendar_event('event', eventId, clientName, eventDate, summaryText, description, meetingLink, calendarId)
            msg = 'You have successfully added the event!'
        return jsonify({'Message': msg})
    else:
        return jsonify({'message': 'There is no request data!'})


@app.route('/event', methods=['GET'])
def read_event():
    request_data = request.get_json()
    eventId = None

    if request_data:
        if 'eventId' in request_data:
            eventId = request_data['eventId']

        event = DatabaseService.find_event(eventId)
        if event:
            return jsonify({'EventId': event.event_id, 'ClientName': event.client_name, 'EventDate': event.event_date, 'SummaryText': event.summary_text, 'Description': event.description, 'MeetingLink': event.meeting_link, 'CalendarId': event.calendar_id})
        else:
            return jsonify({'Message': 'There is no such client!'})
    return jsonify({'Message': 'There is no request data!'})


@app.route('/event', methods=['PUT'])
def update_event():
    request_data = request.get_json()
    eventId = None
    clientName = None
    eventDate = None
    summaryText = None
    description = None
    meetingLink = None
    calendarId = None

    if request_data:
        if 'eventId' in request_data:
            eventId = request_data['eventId']
        if 'clientName' in request_data:
            clientName = request_data['clientName']
        if 'eventDate' in request_data:
            eventDate = request_data['eventDate']
        if 'summaryText' in request_data:
            summaryText = request_data['summaryText']
        if 'description' in request_data:
            description = request_data['description']
        if 'meetingLink' in request_data:
            meetingLink = request_data['meetingLink']
        if 'calendarId' in request_data:
            calendarId = request_data['calendarId']

        event = DatabaseService.find_event(eventId)
        if event:
            event.event_id = eventId
            event.client_name = clientName
            event.event_date = eventDate
            event.summary_text = summaryText
            event.description = description
            event.meeting_link = meetingLink
            event.calendar_id = calendarId
            DatabaseService.update_calendar_event(eventId, event)
            msg = 'You have successfully updated the event!'
        else:
            msg = 'There is no such event!'
        return jsonify({'Message': msg})
    else:
        return jsonify({'message': 'There is no request data!'})


@app.route('/event', methods=['DELETE'])
def delete_event():
    request_data = request.get_json()
    eventId = None

    if request_data:
        if 'eventId' in request_data:
            eventId = request_data['eventId']

        event = DatabaseService.find_event(eventId)
        if event:
            DatabaseService.delete_calendar_event(eventId)
            msg = 'Calendar event deleted successfully!'
        else:
            msg = 'There is no such event!'
        return jsonify({'Message': msg})
    else:
        return jsonify({'Message': 'There is no request data!'})


@app.route('/meeting', methods=['POST'])
def create_meeting():
    request_data = request.get_json()
    meetingId = None
    meetingSoundRecord = None
    meetingDate = None
    eventId = None

    if request_data:
        if 'meetingId' in request_data:
            meetingId = request_data['meetingId']
        if 'meetingSoundRecord' in request_data:
            meetingSoundRecord = request_data['meetingSoundRecord']
        if 'meetingDate' in request_data:
            meetingDate = request_data['meetingDate']
        if 'eventId' in request_data:
            eventId = request_data['eventId']

        meeting = DatabaseService.find_meeting(meetingId)
        if meeting:
            msg = 'Meeting already exists!'
        else:
            DatabaseService.insert_zoom_meeting('meeting', meetingId, meetingSoundRecord, meetingDate, eventId)
            msg = 'You have successfully added the meeting!'
        return jsonify({'Message': msg})
    else:
        return jsonify({'Message': 'There is no request data!'})


@app.route('/meeting', methods=['GET'])
def read_meeting():
    request_data = request.get_json()
    meetingId = None

    if request_data:
        if 'meetingId' in request_data:
            meetingId = request_data['meetingId']

        meeting = DatabaseService.find_meeting(meetingId)
        if meeting:
            return jsonify({'MeetingId': meeting.meeting_id, 'MeetingSoundRecord': meeting.meeting_sound_record, 'MeetingDate': meeting.meeting_date, 'EventId': meeting.event_id})
        else:
            return jsonify({'Message': 'There is no such meeting!'})
    return jsonify({'Message': 'There is no request data!'})


@app.route('/meeting', methods=['PUT'])
def update_meeting():
    request_data = request.get_json()
    meetingId = None
    meetingSoundRecord = None
    meetingDate = None
    eventId = None

    if request_data:
        if 'meetingId' in request_data:
            meetingId = request_data['meetingId']
        if 'meetingSoundRecord' in request_data:
            meetingSoundRecord = request_data['meetingSoundRecord']
        if 'meetingDate' in request_data:
            meetingDate = request_data['meetingDate']
        if 'eventId' in request_data:
            eventId = request_data['eventId']

        meeting = DatabaseService.find_meeting(meetingId)
        if meeting:
            meeting.meeting_id = meetingId
            meeting.meeting_sound_record = meetingSoundRecord
            meeting.meeting_date = meetingDate
            meeting.event_id = eventId
            DatabaseService.update_zoom_meeting(meetingId, meeting)
            msg = 'You have successfully updated the meeting!'
        else:
            msg = 'There is no such meeting!'
        return jsonify({'Message': msg})
    else:
        return jsonify({'Message': 'There is no request data!'})


@app.route('/meeting', methods=['DELETE'])
def delete_meeting():
    request_data = request.get_json()
    meetingId = None

    if request_data:
        if 'meetingId' in request_data:
            meetingId = request_data['meetingId']

        meeting = DatabaseService.find_meeting(meetingId)
        if meeting:
            DatabaseService.delete_zoom_meeting(meetingId)
            msg = 'Zoom meeting deleted successfully!'
        else:
            msg = 'There is no such meeting!'
        return jsonify({'Message': msg})
    else:
        return jsonify({'Message': 'There is no request data!'})


if __name__ == '__main__':
    app.run()
