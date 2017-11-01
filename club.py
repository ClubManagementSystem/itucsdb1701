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

link2 = Blueprint('link2',__name__)


@link2.route('/clubapp')
@login_required
def club_application():
    return render_template('clubapp.html')

@link2.route('/clubregister', methods = ['GET', 'POST'])
@login_required
def clubregister():
    if request.method == "POST":
        name = request.form['name']
        type = request.form['type']
        exp = request.form['exp']

        uid = current_user.get_id()
        addclub(name,type,exp,uid)
        return redirect(url_for('link1.home_page'))


def addclub(n,t,e,i):
    with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO CLUBDB (NAME,TYPE,EXP,CM) VALUES (%s, %s, %s, %s)"""
            cursor.execute(query,(n,t,e,i))
            return
