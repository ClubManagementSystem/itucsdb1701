import datetime
import os
import json
import re
import psycopg2 as dbapi2
from flask import redirect
from flask.helpers import url_for
from flask import Flask, flash
from flask import render_template
from home import link1
from club import link2
from user import link3
from admin import link4
from classes import UserList, User
from flask_login import login_manager, current_user
from flask_login.login_manager import LoginManager
from passlib.apps import custom_app_context as pwd_context
from datetime import timedelta

app = Flask(__name__)
app.register_blueprint(link1)
app.register_blueprint(link2)
app.register_blueprint(link3)
app.register_blueprint(link4)
app.secret_key = 'gallifrey'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'link1.home_page'
login_manager.fresh_view = 'link1.home_page'

@login_manager.user_loader
def load_user(user_id):
    return User("zzz","zzz", 9999, "zzz", "zzz").get_user(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    flash("Unauthorized Access. Please Sign In or Sign Up!")
    return redirect(url_for('link1.home_page'))

def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn


@app.route('/initdb')
def initialize_database():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = """DROP TABLE IF EXISTS USERDB CASCADE"""
        cursor.execute(query)
        query = """CREATE TABLE USERDB (ID SERIAL PRIMARY KEY,
         NAME VARCHAR(40) NOT NULL, REALNAME VARCHAR(50) NOT NULL,NUMBER BIGINT,
        EMAIL VARCHAR(50), PSW VARCHAR(200), LEVEL INTEGER DEFAULT 0) """
        cursor.execute(query)

        query = """INSERT INTO USERDB(NAME,REALNAME,PSW,LEVEL) VALUES(%s, %s, %s, %s)   """
        cursor.execute(query,('admin','Admin', pwd_context.encrypt('admin'), 1,))

        query = """INSERT INTO USERDB(NAME,REALNAME,PSW,NUMBER,EMAIL) VALUES(%s, %s, %s, %s, %s)   """
        cursor.execute(query,('koray','Bulent Koray Oz', pwd_context.encrypt('123'),12345, 'koray@itu.edu.tr',))

        query = """INSERT INTO USERDB(NAME,REALNAME,PSW,NUMBER,EMAIL) VALUES(%s, %s, %s, %s, %s)   """
        cursor.execute(query,('turgut','Turgut Can Aydinalev', pwd_context.encrypt('123'),12345, 'turgut@itu.edu.tr',))

        query = """INSERT INTO USERDB(NAME,REALNAME,PSW,NUMBER,EMAIL) VALUES(%s, %s, %s, %s, %s)   """
        cursor.execute(query,('beste','Beste Burcu Bayhan', pwd_context.encrypt('123'),12345, 'beste@itu.edu.tr',))

        query = """DROP TABLE IF EXISTS CLUBDB CASCADE"""
        cursor.execute(query)

        query = """ CREATE TABLE CLUBDB (ID SERIAL PRIMARY KEY, NAME VARCHAR(40) NOT NULL, TYPE VARCHAR(40) NOT NULL,
        EXP VARCHAR(2000), ACTIVE INTEGER DEFAULT 0, CM INT REFERENCES USERDB(ID) ) """
        cursor.execute(query)

        query = """DROP TABLE IF EXISTS CLUBMEM CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE CLUBMEM (CLUBID INT REFERENCES CLUBDB(ID), USERID INT REFERENCES USERDB(ID), LEVEL INTEGER DEFAULT 0)"""
        cursor.execute(query)
        connection.commit()

        query = """DROP TABLE IF EXISTS SOCMED CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE SOCMED (CLUBID INT REFERENCES CLUBDB(ID), TYPESOC VARCHAR(20), LINK VARCHAR(100))"""
        cursor.execute(query)
        connection.commit()

        query = """DROP TABLE IF EXISTS APPTAB CASCADE"""
        cursor.execute(query)

        query = """CREATE TABLE APPTAB(CLUBID INT REFERENCES CLUBDB(ID), USERID INT REFERENCES USERDB(ID))"""
        cursor.execute(query)
        connection.commit()

    return redirect(url_for('link1.home_page'))

if __name__ == '__main__':
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True
    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='vagrant' password='vagrant'
                               host='localhost' port=5432 dbname='itucsdb'"""

    REMEMBER_COOKIE_DURATION = timedelta(seconds = 10)
    app.store = UserList(os.path.join(os.path.dirname(__file__),app.config['dsn']))
    app.run(host='0.0.0.0', port=port, debug=debug)
