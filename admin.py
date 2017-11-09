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

link4 = Blueprint('link4',__name__)

@link4.route('/admin_home')
@login_required
def admin_home():
    with dbapi2.connect(current_app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """ SELECT * FROM CLUBDB WHERE (ACTIVE = 0) """
        cursor.execute(query)
        app = cursor.fetchall()
        print(app)
        return render_template('admin.html', app = app)

@link4.route('/acceptApp/<int:id>/')
def acceptApp(id):
    if current_user.level == 1:
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE CLUBDB SET ACTIVE=1 WHERE (ID = %s) """
            cursor.execute(query,(id,))
        return redirect(url_for('link4.admin_home'))
    else:
        flash("Permission Denied")
        return redirect(url_for('link3.userProfile'))

@link4.route('/declineApp/<int:id>/')
def declineApp(id):
    if current_user.level == 1:
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DELETE FROM CLUBDB WHERE (ID = %s) """
            cursor.execute(query,(id,))
        return redirect(url_for('link4.admin_home'))
    else:
        flash("Permission Denied")
        return redirect(url_for('link3.userProfile'))
