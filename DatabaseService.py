from sqlalchemy import create_engine, ForeignKey, Column, String, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Client(Base):
    __tablename__ = "clients"

    # defining the fields of the table
    client_id = Column("clientId", Integer, primary_key=True)
    client_name = Column("clientName", String)
    client_email = Column("clientEmail", String)
    client_password = Column("clientPassword", String)
    zoom_meetings = relationship("ZoomMeeting", backref="client", lazy="dynamic")

    # class constructor
    def __init__(self, client_id, client_name, client_email, client_password):
        self.client_id = client_id
        self.client_name = client_name
        self.client_email = client_email
        self.client_password = client_password

    # function to output the table
    def __repr__(self):
        return f"ID: ({self.client_id}) Name: /{self.client_name}/ Email: /{self.client_email}/ " \
               f"Password: /{self.client_password}/"


class ZoomMeeting(Base):
    __tablename__ = "zoomMeetings"

    meeting_id = Column("meetingId", Integer, primary_key=True)
    meeting_name = Column("meetingName", String)
    meeting_sound_record = Column("meetingSoundRecord", String)
    meeting_date = Column("meetingDate", String)
    meeting_summary = Column("meetingSummary", String)
    client_id = Column("clientId", Integer, ForeignKey('clients.clientId'))

    def __init__(self, meeting_id, meeting_name, meeting_sound_record, meeting_date, meeting_summary, client_id):
        self.meeting_id = meeting_id
        self.meeting_name = meeting_name
        self.meeting_sound_record = meeting_sound_record
        self.meeting_date = meeting_date
        self.meeting_summary = meeting_summary
        self.client_id = client_id

    def __repr__(self):
        return f"ID: ({self.meeting_id}) MeetingName: /{self.meeting_name}/ " \
               f"Sound record: /{self.meeting_sound_record}/ Summary: /{self.meeting_summary}/ Date: /{self.meeting_date}/)"


engine = create_engine("sqlite:///testDB.db", echo=True)
Base.metadata.create_all(bind=engine)

# Start a session
Session = sessionmaker(bind=engine)
session = Session()


# functions to insert data into database
def insert_client(object_name, client_id, client_name, client_email, client_password):
    object_name = Client(client_id, client_name, client_email, client_password)
    session.add(object_name)
    session.commit()


def insert_zoom_meeting(object_name, meeting_id, meeting_name, meeting_sound_record, meeting_date, meeting_summary, client_id):
    object_name = ZoomMeeting(meeting_id, meeting_name, meeting_sound_record, meeting_date, meeting_summary, client_id)
    session.add(object_name)
    session.commit()


# functions to output data from database
def return_clients():
    clients = session.query(Client)
    clientsList = []
    for client in clients:
        clientsList.append(client)
    return clientsList


def return_zoom_meetings():
    meetings = session.query(ZoomMeeting)
    meetingList = []
    for meeting in meetings:
        meetingList.append(meeting)
    return meetingList


# functions to find objects
def find_client_by_email(client_email):
    client = session.query(Client).filter(Client.client_email == client_email).first()
    return client


def find_client(client_id):
    client = session.query(Client).filter(Client.client_id == client_id).first()
    return client


def find_meeting(meeting_id):
    meeting = session.query(ZoomMeeting).filter(ZoomMeeting.meeting_id == meeting_id).first()
    return meeting

def find_meeting_by_name(meeting_name):
    meeting = session.query(ZoomMeeting).filter(ZoomMeeting.meeting_name == meeting_name).first()
    return meeting

def find_meetings_by_user_id(client_id):
    meeting = session.query(ZoomMeeting).filter(ZoomMeeting.client_id == client_id)


# functions to update data in database
def update_client(id, param_client):
    client = session.query(Client).filter(Client.client_id == id).first()

    if (param_client.client_name != None):
        client.client_name = param_client.client_name

    if (param_client.client_email != None):
        client.client_email = param_client.client_email

    if (param_client.client_password != None):
        client.client_password = param_client.client_password

    session.commit()

def update_zoom_meeting(id, param_meeting):
    meeting = session.query(ZoomMeeting).filter(ZoomMeeting.meeting_id == id).first()

    if(param_meeting.meeting_name != None):
        meeting.meeting_name = param_meeting.meeting_name

    if(param_meeting.meeting_sound_record != None):
        meeting.meeting_sound_record = param_meeting.meeting_sound_record

    if(param_meeting.meeting_date != None):
        meeting.meeting_date = param_meeting.meeting_date

    if(param_meeting.meeting_summary != None):
        meeting.meeting_summary = param_meeting.meeting_summary

    if(param_meeting.client_id != None):
        meeting.client_id = param_meeting.client_id

    session.commit()


# functions to delete data in database
def delete_client(client_id):
    client = session.query(Client).filter(Client.client_id == client_id).first()
    session.delete(client)
    session.commit()


def delete_zoom_meeting(meeting_id):
    meeting = session.query(ZoomMeeting).filter(ZoomMeeting.meeting_id == meeting_id).first()
    session.delete(meeting)
    session.commit()
