import datetime
import os
import json
import re
import psycopg2 as dbapi2
from flask import redirect, Blueprint, flash
from flask.helpers import url_for
from flask import Flask
from flask import render_template, Response
from flask import request, current_app
from classes import User
from passlib.apps import custom_app_context as pwd_context
from flask_login.utils import login_required
from flask_login import login_manager, login_user, logout_user,current_user

link3 = Blueprint('link3',__name__)

@link3.route('/profile')
@login_required
def userProfile():
    clr=userclub(current_user.get_id())
    clubnames = []
    for i in clr:
        cn = getclubname(i)
        clubnames.append(cn[0])
    return render_template('profile.html',clubnames = clubnames)


def userclub(id):
    with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT CLUBID FROM CLUBMEM WHERE (USERID=%s)"""
            cursor.execute(query,(id))
            arr=cursor.fetchall()
            return arr

def getclubname(id):
    with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT NAME FROM CLUBDB WHERE (ID=%s)"""
            cursor.execute(query,(id))
            na=cursor.fetchone()
            return na