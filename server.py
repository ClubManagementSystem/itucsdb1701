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
from event import link5
from classes import UserList, User
from flask_login import login_manager, current_user
from flask_login.login_manager import LoginManager
from passlib.apps import custom_app_context as pwd_context
from datetime import timedelta
from flask_login.utils import login_required

app = Flask(__name__)
app.register_blueprint(link1)
app.register_blueprint(link2)
app.register_blueprint(link3)
app.register_blueprint(link4)
app.register_blueprint(link5)
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

@app.route('/initdb/<int:key>/<int:kay>')
def initdbVerification(key,kay):
    if (ord(app.secret_key[0]) - kay) == key:
        initialize_database()
    return redirect(url_for('link1.home_page'))


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

            query = """CREATE TABLE CLUBMEM (ID SERIAL PRIMARY KEY,CLUBID INT REFERENCES CLUBDB(ID) ON DELETE CASCADE, USERID INT REFERENCES USERDB(ID), LEVEL INTEGER DEFAULT 0)"""
            cursor.execute(query)
            connection.commit()

            query = """DROP TABLE IF EXISTS SOCMED CASCADE"""
            cursor.execute(query)

            query = """CREATE TABLE SOCMED (ID SERIAL PRIMARY KEY,CLUBID INT REFERENCES CLUBDB(ID) ON DELETE CASCADE, TYPESOC VARCHAR(20), LINK VARCHAR(100))"""
            cursor.execute(query)
            connection.commit()

            query = """DROP TABLE IF EXISTS APPTAB CASCADE"""
            cursor.execute(query)

            query = """CREATE TABLE APPTAB(ID SERIAL PRIMARY KEY,CLUBID INT REFERENCES CLUBDB(ID) ON DELETE CASCADE, USERID INT REFERENCES USERDB(ID))"""
            cursor.execute(query)
            connection.commit()

            query = """DROP TABLE IF EXISTS EVENT CASCADE"""
            cursor.execute(query)

            query = """ CREATE TABLE EVENT (ID SERIAL PRIMARY KEY, CLUBID INT REFERENCES CLUBDB(ID) ON DELETE CASCADE ,NAME VARCHAR(40) NOT NULL,
            EXP VARCHAR(200), DATE TIMESTAMP NOT NULL, LOCATION VARCHAR(20)) """
            cursor.execute(query)
            connection.commit()

            query = """DROP TABLE IF EXISTS BALANCE CASCADE"""
            cursor.execute(query)

            query = """ CREATE TABLE BALANCE (ID SERIAL PRIMARY KEY, CLUBID INT REFERENCES CLUBDB(ID) ON DELETE CASCADE ,AMOUNT FLOAT NOT NULL,
            EXPL VARCHAR(200)) """
            cursor.execute(query)

            query = """DROP TABLE IF EXISTS INVENTORY CASCADE"""
            cursor.execute(query)

            query = """ CREATE TABLE INVENTORY (ID SERIAL PRIMARY KEY, CLUBID INT REFERENCES CLUBDB(ID) ON DELETE CASCADE, INAME VARCHAR(80) NOT NULL, USERNAMEID INTEGER REFERENCES USERDB(ID),PRICE INTEGER, AVAILABLE INTEGER DEFAULT 0)"""
            cursor.execute(query)


            query = """ INSERT INTO USERDB(NAME,REALNAME,NUMBER,EMAIL,PSW,LEVEL) VALUES ('ceyda', 'Ceyda Aladag', 123456, 'ceyda@itu.edu.tr', '$6$rounds=656000$2pciOKNmxUaBMP9o$E/9Gs1CKiuCE9wtqxOr3kQskYyhm52BzHyZz5QG3qFjuHxcKo3LUsq77sK/fSc5JG5hcXTqiMS/saAyKBFEuh.', 0);
                        INSERT INTO USERDB(NAME,REALNAME,NUMBER,EMAIL,PSW,LEVEL) VALUES ('melis', 'Melis Gulenay', 4123, 'melis@itu.edu.tr', '$6$rounds=656000$ndu2sy9DMg5bVp1D$uPIOHBTnMWBjAjI4PuendQeYY5tNS7RcCfLSpaGxdxXBBcojaK07bMilkSXFC4qx7IqH1IgbcoelFYurcH.JS0', 0);
                        INSERT INTO USERDB(NAME,REALNAME,NUMBER,EMAIL,PSW,LEVEL) VALUES ('mert', 'Mert Kartaltepe', 4125, 'mert@itu.edu.tr', '$6$rounds=656000$yi1XAGdkPXFN/S8x$Rayqxk8A7lmsrz/ScCkUn2zBHBd2wxtjpZ3aYBCAPo5WHLmjIyTHUf0oyeLtqys8TdWlSHxgu2zlwFpD.a.G4.', 0);
                        INSERT INTO CLUBDB(NAME,TYPE,EXP,ACTIVE,CM) VALUES ('E-sport Kulubu', 'Sport', 'Online oyun sporlari', 1, 3);
                        INSERT INTO CLUBDB(NAME,TYPE,EXP,ACTIVE,CM) VALUES ('Felsefe Kulubu', 'Culture/Art', 'Felsefi akim tartismalari', 1, 4);
                        INSERT INTO CLUBDB(NAME,TYPE,EXP,ACTIVE,CM) VALUES ('Paten Kulubu', 'Sport', 'Tekerlekli patenle yapilan tum sporlar', 1, 2);
                        INSERT INTO CLUBDB(NAME,TYPE,EXP,ACTIVE,CM) VALUES ('Bilisim Kulubu', 'Profession', 'Turkiye''de bilisim teknolojisi bilincinin arttirilmasi uzerine calismalar', 1, 7);
                        INSERT INTO APPTAB(CLUBID,USERID) VALUES (1, 4);
                        INSERT INTO APPTAB(CLUBID,USERID) VALUES (1, 5);
                        INSERT INTO CLUBMEM(CLUBID,USERID,LEVEL) VALUES (1, 3, 1);
                        INSERT INTO CLUBMEM(CLUBID,USERID,LEVEL) VALUES (2, 4, 1);
                        INSERT INTO CLUBMEM(CLUBID,USERID,LEVEL) VALUES (3, 2, 1);
                        INSERT INTO CLUBMEM(CLUBID,USERID,LEVEL) VALUES (1, 2, 3);
                        INSERT INTO CLUBMEM(CLUBID,USERID,LEVEL) VALUES (1, 6, 0);
                        INSERT INTO CLUBMEM(CLUBID,USERID,LEVEL) VALUES (1, 7, 4);
                        INSERT INTO CLUBMEM(CLUBID,USERID,LEVEL) VALUES (4, 7, 1);
                        INSERT INTO CLUBMEM(CLUBID,USERID,LEVEL) VALUES (3, 3, 0);
                        INSERT INTO EVENT(CLUBID,NAME,EXP,DATE,LOCATION) VALUES (1, 'Hearthstone Turnuvasi', 'Odullu Hearthstone turnuvasi', '2017-12-29 20:00:00', 'MED');
                        INSERT INTO EVENT(CLUBID,NAME,EXP,DATE,LOCATION) VALUES (2, 'Platon Hakkinda', 'Eserleri hakkinda tartisma', '2017-12-22 18:00:00', 'FEB');
                        INSERT INTO EVENT(CLUBID,NAME,EXP,DATE,LOCATION) VALUES (3, 'Inline Hokey Maci', 'Hazirlik karsilasmasi', '2017-12-26 19:00:00', 'Spor Salonu');
                        INSERT INTO SOCMED(CLUBID,TYPESOC,LINK) VALUES (2, 'Facebook', 'facebook.com/felsefeitu');
                        """
            cursor.execute(query)

        flash("Database initialized.")

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
