import logging

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from config import DEBUG

import os
"""
 Logging configuration
"""

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)

app.debug = DEBUG
app.secret_key = "ah5=5&%93fp7c1(9el7&on2b3t@5%#y4@!qgy@w(kq-!b)@)i$"
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}/{os.environ['DB_NAME']}"

app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://redis",
        result_backend=f"db+postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}/{os.environ['DB_NAME']}",
        task_ignore_result=False,
    ),
)

db = SQLA(app)
appbuilder = AppBuilder(app, db.session)



"""
from sqlalchemy.engine import Engine
from sqlalchemy import event

#Only include this for SQLLite constraints
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Will force sqllite contraint foreign keys
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
"""


from . import views