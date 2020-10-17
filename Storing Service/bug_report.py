from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class BugReport(Base):
    """ Bug Report """

    __tablename__ = "bug_report"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(250), nullable=False)
    location = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)
    date = Column(String(100))
    date_created = Column(String(100), nullable=False)

    def __init__(self, title, description, location, type, date):
        """ Initializes a bug report """
        self.title = title
        self.description = description
        self.location = location
        self.type = type
        self.date = date or datetime.datetime.now() # Sets the date for current date if user did not defined
        self.date_created = datetime.datetime.now() # Sets the date/time record is created

    def to_dict(self):
        """ Dictionary Representation of a bug report """
        dict = {}
        dict['title'] = self.title
        dict['description'] = self.description
        dict['location'] = self.location
        dict['type'] = self.type
        dict['date'] = self.date
        dict['date_created'] = self.date_created

        return dict
