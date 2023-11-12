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
    google_calendars = relationship("GoogleCalendar", backref="Client")

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


class GoogleCalendar(Base):
    __tablename__ = "googleCalendars"

    calendar_id = Column("calendarId", Integer, primary_key=True)
    client_event = Column("clientEvent", String)
    client_id = Column("clientId", Integer, ForeignKey('clients.clientId'))
    calendar_events = relationship("CalendarEvent", backref="GoogleCalendar")

    def __init__(self, calendar_id, client_event, client_id):
        self.calendar_id = calendar_id
        self.client_event = client_event
        self.client_id = client_id

    def __repr__(self):
        return f"ID: ({self.calendar_id}) Event: /{self.client_event}/ Client: ({self.client_id})"


class CalendarEvent(Base):
    __tablename__ = "calendarEvents"

    event_id = Column("eventId", Integer, primary_key=True)
    client_name = Column("clientName", String)
    event_date = Column("eventDate", String)
    summary_text = Column("summaryText", String)
    description = Column("description", String)
    meeting_link = Column("meetingLink", String)
    calendar_id = Column("calendarId", Integer, ForeignKey('googleCalendars.calendarId'))
    zoom_meeting = relationship("ZoomMeeting", backref="CalendarEvent", uselist=False)

    def __init__(self, event_id, client_name, event_date, summary_text, description, meeting_link, calendar_id):
        self.event_id = event_id
        self.client_name = client_name
        self.event_date = event_date
        self.summary_text = summary_text
        self.description = description
        self.meeting_link = meeting_link
        self.calendar_id = calendar_id

    def __repr__(self):
        return f"ID: ({self.event_id}) Name: /{self.client_name}/ Event: /{self.event_date}/ " \
               f"Text: /{self.summary_text}/ Description: " \
               f"/{self.description}/ Link: /{self.meeting_link}/ Calendar: ({self.calendar_id})"


class ZoomMeeting(Base):
    __tablename__ = "zoomMeetings"

    meeting_id = Column("meetingId", Integer, primary_key=True)
    meeting_sound_record = Column("meetingSoundRecord", String)
    meeting_date = Column("meetingDate", String)
    event_id = Column("eventId", Integer, ForeignKey('calendarEvents.eventId'))

    def __init__(self, meeting_id, meeting_sound_record, meeting_date, event_id):
        self.meeting_id = meeting_id
        self.meeting_sound_record = meeting_sound_record
        self.meeting_date = meeting_date
        self.event_id = event_id

    def __repr__(self):
        return f"ID: ({self.meeting_id}) Sound record: /{self.meeting_sound_record}/ Date: /{self.meeting_date}/" \
               f" Event: ({self.event_id})"


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


def insert_google_calendar(object_name, calendar_id, client_event, client_id):
    object_name = GoogleCalendar(calendar_id, client_event, client_id)
    session.add(object_name)
    session.commit()


def insert_calendar_event(object_name, event_id, client_name, event_date, summary_text, description, meeting_link,
                          calendar_id):
    object_name = CalendarEvent(event_id, client_name, event_date, summary_text, description, meeting_link, calendar_id)
    session.add(object_name)
    session.commit()


def insert_zoom_meeting(object_name, meeting_id, meeting_sound_record, meeting_date, event_id):
    object_name = ZoomMeeting(meeting_id, meeting_sound_record, meeting_date, event_id)
    session.add(object_name)
    session.commit()


# functions to output data from database
def return_clients():
    clients = session.query(Client)
    clientsList = []
    for client in clients:
        clientsList.append(client)
    return clientsList


def return_google_calendars():
    calendars = session.query(GoogleCalendar)
    calendarsList = []
    for calendar in calendars:
        calendarsList.append(calendar)
    return calendarsList


def return_calendar_events():
    events = session.query(CalendarEvent)
    eventsList = []
    for event in events:
        eventsList.append(event)
    return eventsList


def print_zoom_meetings():
    meetings = session.query(ZoomMeeting)
    meetingList = []
    for meeting in meetings:
        meetingList.append(meeting)
    return meetingList


# functions to find objects
def find_client_by_name(client_name):
    client = session.query(Client).filter(Client.client_name == client_name).first()
    return client


def find_client(client_id):
    client = session.query(Client).filter(Client.client_id == client_id).first()
    return client


def find_calendar(calendar_id):
    calendar = session.query(GoogleCalendar).filter(GoogleCalendar.calendar_id == calendar_id).first()
    return calendar


def find_event(event_id):
    event = session.query(CalendarEvent).filter(CalendarEvent.event_id == event_id).first()
    return event


def find_meeting(meeting_id):
    meeting = session.query(ZoomMeeting).filter(ZoomMeeting.meeting_id == meeting_id).first()
    return meeting


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


def update_google_calendar(id, param_calendar):
    calendar = session.query(GoogleCalendar).filter(GoogleCalendar.calendar_id == id).first()

    if(param_calendar.client_event != None):
        calendar.client_event = param_calendar.client_event

    if (param_calendar.client_id != None):
        calendar.client_id = param_calendar.client_id

    session.commit()


def update_calendar_event(id, param_event):
    event = session.query(CalendarEvent).filter(CalendarEvent.event_id == id).first()

    if(param_event.client_name != None):
        event.client_name = param_event.client_name

    if(param_event.event_date != None):
        event.event_date = param_event.event_date

    if(param_event.summary_text != None):
        event.summary_text = param_event.summary_text

    if(param_event.description != None):
        event.description = param_event.description

    if(param_event.meeting_link != None):
        event.meeting_link = param_event.meeting_link

    if(param_event.calendar_id != None):
        event.calendar_id = param_event.calendar_id

    session.commit()


def update_zoom_meeting(id, param_meeting):
    meeting = session.query(ZoomMeeting).filter(ZoomMeeting.meeting_id == id).first()

    if(param_meeting.meeting_sound_record != None):
        meeting.meeting_sound_record = param_meeting.meeting_sound_record

    if(param_meeting.meeting_date != None):
        meeting.meeting_date = param_meeting.meeting_date

    if(param_meeting.event_id != None):
        meeting.event_id = param_meeting.event_id

    session.commit()


# functions to delete data in database
def delete_client(client_id):
    client = session.query(Client).filter(Client.client_id == client_id).first()
    session.delete(client)
    session.commit()


def delete_google_calendar(calendar_id):
    calendar = session.query(GoogleCalendar).filter(GoogleCalendar.calendar_id == calendar_id).first()
    session.delete(calendar)
    session.commit()


def delete_calendar_event(event_id):
    event = session.query(CalendarEvent).filter(CalendarEvent.event_id == event_id).first()
    session.delete(event)
    session.commit()


def delete_zoom_meeting(meeting_id):
    meeting = session.query(ZoomMeeting).filter(ZoomMeeting.meeting_id == meeting_id).first()
    session.delete(meeting)
    session.commit()
