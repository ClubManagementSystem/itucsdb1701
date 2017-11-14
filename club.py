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
    userId = current_user.get_id()
    with dbapi2.connect(current_app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """SELECT * FROM CLUBDB WHERE (ID = %s)"""
        cursor.execute(query, (id,))
        club = cursor.fetchone()

        if club == None:
            flash("Yok boyle bir kulup")
            return redirect(url_for('link1.home_page'))

        query = """SELECT COUNT(*) FROM CLUBMEM WHERE (CLUBID = %s AND USERID = %s)"""
        cursor.execute(query,(id, userId,))
        ismember = cursor.fetchone()[0]

        query = """SELECT LEVEL FROM CLUBMEM WHERE (CLUBID = %s AND USERID = %s)"""
        cursor.execute(query,(id, userId,))
        level = cursor.fetchone()
        if level:
            level = level[0]
        query = """SELECT COUNT(*) FROM APPTAB WHERE (CLUBID = %s AND USERID = %s)"""
        cursor.execute(query,(id, userId,))
        isapplied = cursor.fetchone()[0]

        applicant = None
        if ismember and level == 1:
            query = """SELECT USERID, NAME FROM USERDB, APPTAB WHERE (USERID = USERDB.ID AND CLUBID = %s)"""
            cursor.execute(query,(id,))
            applicant = cursor.fetchall()
    return render_template('clubProfile.html', club = club, ismember = ismember, isapplied = isapplied, level = level, applicants = applicant)

@link2.route('/next/<arg>')
def clubProfileNext(arg):
    arg_i = int(arg) + 1
    arg = str(arg_i)
    return redirect(url_for('link2.clubProfile', id = arg))

@link2.route('/previous/<arg>')
def clubProfilePrevious(arg):
    arg_i = int(arg) - 1
    arg = str(arg_i)
    return redirect(url_for('link2.clubProfile', id = arg))

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

@link2.route('/registerToClub/<int:clubId>', methods = ['GET', 'POST'])
@login_required
def registerToClub(clubId):
    if request.method == 'POST':
        userId = current_user.get_id()
        with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """INSERT INTO APPTAB (CLUBID,USERID) VALUES (%s, %s)"""
                cursor.execute(query,(clubId, userId,))
                flash("ISTEK GONDERILDI")
        return redirect(url_for('link2.clubProfile', id = clubId))

@link2.route('/welcomeApply/<clubId>/<userId>', methods = ['GET', 'POST'])
@login_required
def welcomeApply(clubId, userId):
    if request.method == 'POST':
        with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """DELETE FROM APPTAB WHERE(CLUBID = %s AND USERID = %s)"""
                cursor.execute(query,(clubId, userId,))

                query = """INSERT INTO CLUBMEM (CLUBID, USERID, LEVEL) VALUES (%s, %s, 0)"""
                cursor.execute(query,(clubId, userId,))
    return redirect(url_for('link2.clubProfile', id = clubId))

@link2.route('/deleteApply/<clubId>/<userId>', methods = ['GET', 'POST'])
@login_required
def deleteApply(clubId, userId):
    if request.method == 'POST':
        with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """DELETE FROM APPTAB WHERE(CLUBID = %s AND USERID = %s)"""
                cursor.execute(query,(clubId, userId,))
    return redirect(url_for('link2.clubProfile', id = clubId))
