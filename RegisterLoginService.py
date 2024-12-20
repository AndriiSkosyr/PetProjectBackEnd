import datetime
import os.path
from dateutil import parser
import re
import pytz
from jproperties import Properties
import random

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import json
from flask import Flask, request, session, jsonify
from flask_cors import CORS

import AutocorrectService
import DatabaseService
import SentimentService
import TextToNotesService

# import FormatConverter
# import StorageService
# import AudioToTextService
import TextToNotesService

configs = Properties()

with open('app_config.properties', 'rb') as config_file:
    configs.load(config_file)

utc = pytz.UTC

app = Flask(__name__)
app.secret_key = '1111'
CORS(app, origins="http://localhost:3000")

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


@app.route('/')
def main_page():
    return 'Main page.'


@app.route('/backend_call', methods=["POST"])
def backend_call():

    # Extract clientId from the request
    client_id = request.json.get("clientId")
    if not client_id:
        return jsonify({"error": "Client ID is missing"}), 400

    print(f"Received Client ID: {client_id}")

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        # Get past 10 events
        now = datetime.datetime.now(datetime.timezone.utc)  # Current time in UTC
        beginDate = (now - datetime.timedelta(days=1)).isoformat()  # 24 hours ago in UTC
        endDate = now.isoformat()  # Current time in UTC

        print("Getting past 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=beginDate,  # Start time (24 hours ago)
                timeMax=endDate,  # End time (now)
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return jsonify({"message": "No past events found."}), 200

        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event['end'].get('dateTime', event['end'].get('date'))
            start_obj = parser.parse(start)
            end_obj = parser.parse(end)
            end_obj = end_obj + datetime.timedelta(minutes=10)
            with os.scandir(configs.get("PATH").data) as entries:
                for entry in entries:
                    print("Local record: ", entry.name)
                    create_time = os.path.getctime(configs.get("PATH").data + "/" + entry.name)
                    print('Create_time: ', create_time)
                    create_date = datetime.datetime.fromtimestamp(create_time)
                    if ((create_date.replace(tzinfo=None) > start_obj.replace(tzinfo=None)) & (
                            create_date.replace(tzinfo=None) < end_obj.replace(tzinfo=None))):
                        print('Records exists')
                        queried_meeting = DatabaseService.find_meeting_by_name(entry.name)
                        if not queried_meeting:
                            meeting_id = random.randint(1, 100)
                            meeting_sound_record = ', '.join(audio.name for audio in os.scandir(configs.get("PATH").data + '/' + entry.name + '/') if audio.is_file() and audio.name.lower().endswith(('.m4a')))
                            DatabaseService.insert_zoom_meeting('meeting', meeting_id, entry.name, meeting_sound_record, create_date, " ", client_id)
                            print("New meeting was added to the database", meeting_sound_record)
                        else: print("The meeting already exists in the database")
                print("Update complete")




                        # with os.scandir(configs.get("PATH").data + '/' + entry.name + '/') as audios:
                        #     print(audios)
                            # for audiofile in audios:
                                # if (audiofile.name.endswith("m4a")):
                                #     initialAudiofileName = configs.get("PATH").data + "/" + entry.name + '/' + audiofile.name
                                #     destinationAudiofileName = initialAudiofileName.replace('m4a', 'wav')
                                #     # FormatConverter.formatting(initialAudiofileName, destinationAudiofileName)
                                #     StorageService.store_files(destinationAudiofileName)
                                #     text = AudioToTextService.transcribe_gcs(
                                #         "gs://diploma-bucket/" + destinationAudiofileName)
                                #     print(text)
                                #     summary = TextToNotesService.summarize_text(text)
                                #     print(summary)

        return jsonify({"message": "Update complete"}), 200

    except HttpError as error:
        return jsonify({"error": f"An error occurred: {error}"}), 500


@app.route('/summarize', methods=["POST"])
def summarization():
    text = """Hello, everybody. Now I am gonna tell you how the app works. So, basically, user creates a meeting, or connects to the existing one. In the process of meeting user starts recording of the meeting. After meeting is finished, or if the user stops the recording, audiofile of the meeting lands in the user's documents folder. 

    After completing the previous step, user can proceed to the app, see the meetings in his calendar, and press the update button to get the summaries of the available meetings records.
    The backend call starts the process where our app search for the audiofiles in the user's records folder. Also, before adding the audio to the queue, the app also checks if the records are related to the meetings in the user's calendar. If audio is present and it is related to the meeting in user's calendar, this meetings is added to the related db table, and also shows on the front end.

    Next step is to choose one of the available meetings, and get the summary of it. To do it, user presses on the pen icon near the name of the meeting, and make a backend call, passing the meeting id.

    Backend gets it, and using the info from db, gets the audiofile, and go through the chain of transformations:
    formatting, speech to text, autocorrect, punctuation check, sentimental analysis and summarization. After the process is completed, user can get all the info on the front end"""
    corrected_text = AutocorrectService.auto_correct_text(text)
    summary = TextToNotesService.summarize_text(corrected_text)
    sentiment = SentimentService.analyze_sentiment(corrected_text)
    return jsonify({"sentiment": sentiment, "message": corrected_text}), 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        request_data = request.get_json()
        clientEmail = None
        clientPassword = None

        if request_data:
            if 'clientEmail' in request_data:
                clientEmail = request_data['clientEmail']
            if 'clientPassword' in request_data:
                clientPassword = request_data['clientPassword']

            account = DatabaseService.find_client_by_email(clientEmail)
            if account and clientPassword == account.client_password:
                session['logged_in'] = True
                session['clientId'] = account.client_id
                session['clientEmail'] = account.client_email
                msg = 'Logged in successfully!'
                return jsonify({'Message': msg, 'Client id': session.get('clientId')})
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
    clients = DatabaseService.return_clients()

    entitiesList = []
    for client in clients:
        listElement = jsonify({'ClientName': client.client_name, 'ClientPassword': client.client_password,
                               'ClientEmail': client.client_email, 'ClientId': client.client_id}).get_json()
        entitiesList.append(listElement)
    calendarsJSON = json.dumps(entitiesList)
    return calendarsJSON


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


@app.route('/meeting', methods=['POST'])
def create_meeting():
    request_data = request.get_json()
    meetingId = None
    meetingName = None
    meetingSoundRecord = None
    meetingDate = None
    meeting_summary = None
    clientId = None

    if request_data:
        if 'meetingId' in request_data:
            meetingId = request_data['meetingId']
        if 'meetingName' in request_data:
            meetingName = request_data['meetingName']
        if 'meetingSoundRecord' in request_data:
            meetingSoundRecord = request_data['meetingSoundRecord']
        if 'meetingDate' in request_data:
            meetingDate = request_data['meetingDate']
        if 'meetingSummary' in request_data:
            meeting_summary = request_data['meetingSummary']
        if 'clientId' in request_data:
            clientId = request_data['clientId']

        meeting = DatabaseService.find_meeting(meetingId)
        if meeting:
            msg = 'Meeting already exists!'
        else:
            DatabaseService.insert_zoom_meeting('meeting', meetingId, meetingName, meetingSoundRecord, meetingDate, meeting_summary, clientId)
            msg = 'You have successfully added the meeting!'
        return jsonify({'Message': msg})
    else:
        return jsonify({'Message': 'There is no request data!'})


@app.route('/meeting', methods=['GET'])
def read_meeting():
    meetings = DatabaseService.return_zoom_meetings()

    entitiesList = []
    for meeting in meetings:
        listElement = jsonify({'MeetingId': meeting.meeting_id, 'MeetingName': meeting.meeting_name,
                               'MeetingSoundRecord': meeting.meeting_sound_record, 'MeetingDate': meeting.meeting_date,
                               'MeetingSummary': meeting.meeting_summary, 'ClientId': meeting.client_id}).get_json()
        entitiesList.append(listElement)
    calendarsJSON = json.dumps(entitiesList)
    return calendarsJSON


@app.route('/meeting', methods=['PUT'])
def update_meeting():
    request_data = request.get_json()
    meetingId = None
    meetingName = None
    meetingSoundRecord = None
    meetingDate = None
    meetingSummary = None
    clientId = None

    if request_data:
        if 'meetingId' in request_data:
            meetingId = request_data['meetingId']
        if 'meetingName' in request_data:
            meetingName = request_data['meetingName']
        if 'meetingSoundRecord' in request_data:
            meetingSoundRecord = request_data['meetingSoundRecord']
        if 'meetingDate' in request_data:
            meetingDate = request_data['meetingDate']
        if 'meetingSummary' in request_data:
            meetingSummary = request_data['meetingSummary']
        if 'clientId' in request_data:
            clientId = request_data['clientId']

        meeting = DatabaseService.find_meeting(meetingId)
        if meeting:
            meeting.meeting_id = meetingId
            meeting.meeting_name = meetingName
            meeting.meeting_sound_record = meetingSoundRecord
            meeting.meeting_date = meetingDate
            meeting.meeting_summary = meetingSummary
            meeting.client_id = clientId
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
