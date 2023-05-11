from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from . import db

"""

You can use the extra Flask-AppBuilder fields and Mixin's

AuditMixin will add automatic timestamp of created and modified by who


"""


class Movie(Model):
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    directors = Column(String)
    genres = Column(String)
    duration = Column(String)
    release_date = Column(Date)

    # year = Column(Integer)
    def __repr__(self):
        return self.name


db.create_all()
