import datetime
import os
import json
import re
import psycopg2 as dbapi2
from flask import redirect
from flask.helpers import url_for
from flask import Flask
from flask import render_template
from home import link1
from classes import UserList

app = Flask(__name__)
app.register_blueprint(link1)
app.secret_key = 'cigdem'
login_manager = LoginManager()

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

        query = """DROP TABLE IF EXISTS USERDB"""
        cursor.execute(query)
        query = """CREATE TABLE USERDB (ID SERIAL PRIMARY KEY,
         NAME VARCHAR(40) NOT NULL,NUMBER BIGINT,
        EMAIL VARCHAR(50), PSW VARCHAR(200), LEVEL INTEGER DEFAULT 0) """
        cursor.execute(query)

       # query = """INSERT INTO COUNTER (N) VALUES (0)"""
        #cursor.execute(query)
        login_manager.init_app(app)
        connection.commit()

    return redirect(url_for('link1.home_page'))


@app.route('/count')
def counter_page():
    with dbapi2.connect(app.config['dsn']) as connection:
        cursor = connection.cursor()

        query = "UPDATE COUNTER SET N = N + 1"
        cursor.execute(query)
        connection.commit()

        query = "SELECT N FROM COUNTER"
        cursor.execute(query)
        count = cursor.fetchone()[0]

    return "This page was accessed %d times." % count

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
    app.store = UserList(os.path.join(os.path.dirname(__file__),app.config['dsn']))
    app.run(host='0.0.0.0', port=port, debug=debug)

