import datetime
import os
import json
import re
import datetime
import psycopg2 as dbapi2
from flask import redirect, Blueprint, flash
from flask.helpers import url_for
from flask import Flask
from flask import render_template, Response
from flask import request, current_app
from classes import User
from event import getevent
from passlib.apps import custom_app_context as pwd_context
from flask_login.utils import login_required
from flask_login import login_manager, login_user, logout_user,current_user

link7 = Blueprint('link7',__name__)

@link7.route('/recgetclubs')
def getClubs():
	userid = current_user.get_id()[0]
	eventNumber = []
	with dbapi2.connect(current_app.config['dsn']) as connection:
		cursor = connection.cursor()
		query = """SELECT CLUBID, CLUBDB.NAME, CLUBDB.TYPE, ACTIVE FROM CLUBMEM, CLUBDB WHERE (CLUBID = CLUBDB.ID AND USERID = %s)"""
		cursor.execute(query,(userid,))
		clubs = cursor.fetchall()
		userctypes = []
		clubrank = []
		for c in clubs:
			if c[2] not in userctypes:
				userctypes.append(c[2])
				query = """SELECT CLUBID FROM EVENT, CLUBDB WHERE (CLUBID = CLUBDB.ID AND CLUBID = %s AND TYPE = %s) GROUP BY CLUBID ORDER BY COUNT(EVENT.CLUBID) DESC"""
				cursor.execute(query,(c[0], c[2],))
				clubrank.append(cursor.fetchall())

	return str(clubrank)