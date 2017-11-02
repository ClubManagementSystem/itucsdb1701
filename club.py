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
from home import link1
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
        typesoc = request.form['typesoc']
        link = request.form['link']
        uid = current_user.get_id()
        addclub(name,type,exp,uid,typesoc,link)
        return redirect(url_for('link1.home_page'))

@link2.route('/clubProfile/<int:id>/')
def clubProfile(id):
    with dbapi2.connect(current_app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """SELECT * FROM CLUBDB WHERE (ID = %s)"""
        cursor.execute(query, (id,))
        club = cursor.fetchone()
        if club == None:
            flash("Yok boyle bir kulup")
            return redirect(url_for('link1.home_page'))
        print(club)

    return render_template('clubProfile.html', club = club)

def addclub(n,t,e,i,ts,l):
    with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO CLUBDB (NAME,TYPE,EXP,CM) VALUES (%s, %s, %s, %s)"""
            cursor.execute(query,(n,t,e,i,))
    with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT ID FROM CLUBDB WHERE (NAME = %s)"""
            cursor.execute(query,(n,))
            clubid = cursor.fetchone()
            print(clubid[0])
    with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO SOCMED (CLUBID,TYPESOC,LINK) VALUES (%s, %s, %s)"""
            cursor.execute(query,(clubid[0],ts,l,))
            return


