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
from event import getevent
from passlib.apps import custom_app_context as pwd_context
from flask_login.utils import login_required
from flask_login import login_manager, login_user, logout_user,current_user

link2 = Blueprint('link2',__name__)

@link2.route('/clubs')
def clubs():
    with dbapi2.connect(current_app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """SELECT ID, NAME, TYPE FROM CLUBDB WHERE (ACTIVE = 1)"""
        cursor.execute(query)
        clubs = cursor.fetchall()
        return render_template('clubs.html', clubs = clubs)
    flash("Can not connect to the DB.")
    return render_template('home.html')

@link2.route('/clubapp')
@login_required
def club_application():
    return render_template('clubapp.html')

@link2.route('/clubregister', methods = ['GET', 'POST'])
@login_required
def clubregister():
    if request.method == "POST":
        name = request.form['name']
        typ = request.form['type']
        exp = request.form['exp']
        typesoc1 = request.form.get('typesoc1')
        typesoc2 = request.form.get('typesoc2')
        l1 = request.form['link1']
        l2 = request.form['link2']
        uid = current_user.get_id()
        addclub(name,typ,exp,uid,typesoc1,typesoc2,l1,l2)
        flash("Registration is completed and it is waiting for admin confirmation.")
        return redirect(url_for('link3.userProfile'))
    else:
        flash("Access Denied")
        return redirect(url_for('link1.home_page'))

@link2.route('/clubProfile/<int:id>/')
def clubProfile(id):
    userId = current_user.get_id()
    events = getevent(id)
    with dbapi2.connect(current_app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """SELECT * FROM CLUBDB WHERE (ID = %s)"""
        cursor.execute(query, (id,))
        club = cursor.fetchone()

        if club == None:
            flash("Wrong Club URL!")
            return redirect(url_for('link1.home_page'))

        query = """SELECT COUNT(*) FROM CLUBMEM WHERE (CLUBID = %s AND USERID = %s)"""
        cursor.execute(query,(id, userId,))
        ismember = cursor.fetchone()[0]

        query = """SELECT LEVEL FROM CLUBMEM WHERE (CLUBID = %s AND USERID = %s)"""
        cursor.execute(query,(id, userId,))
        level = cursor.fetchone()
        if level:
            level = level[0]
        else:
            level = 0
        query = """SELECT COUNT(*) FROM APPTAB WHERE (CLUBID = %s AND USERID = %s)"""
        cursor.execute(query,(id, userId,))
        isapplied = cursor.fetchone()[0]

        applicant = None
        if ismember and level == 1:
            query = """SELECT USERID, NAME FROM USERDB, APPTAB WHERE (USERID = USERDB.ID AND CLUBID = %s)"""
            cursor.execute(query,(id,))
            applicant = cursor.fetchall()

        query = """SELECT CLUBMEM.LEVEL, REALNAME, EMAIL FROM CLUBMEM, USERDB WHERE (CLUBID = %s AND USERID = USERDB.ID AND CLUBMEM.LEVEL > 0) ORDER BY CLUBMEM.LEVEL ASC"""
        cursor.execute(query,(id,))
        board = cursor.fetchall()

        query = """SELECT USERID, REALNAME FROM CLUBMEM, USERDB WHERE (CLUBID = %s AND USERID = USERDB.ID)"""
        cursor.execute(query,(id,))
        members = cursor.fetchall()
    return render_template('clubProfile.html', events = events, club = club, members = members, ismember = ismember, isapplied = isapplied, level = level, applicants = applicant, board = board)

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

def addclub(n,t,e,i,ts1,ts2,l1,l2):
    with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO CLUBDB (NAME,TYPE,EXP,CM) VALUES (%s, %s, %s, %s)"""
            cursor.execute(query,(n,t,e,i,))
            query = """SELECT ID FROM CLUBDB WHERE (NAME = %s)"""
            cursor.execute(query,(n,))
            clubid = cursor.fetchone()
            print("2")
    if l1 and ts1:
            with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """INSERT INTO SOCMED (CLUBID,TYPESOC,LINK) VALUES (%s, %s, %s)"""
                cursor.execute(query,(clubid[0],ts1,l1,))
                return
    if l2 and ts2:
            with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """INSERT INTO SOCMED (CLUBID,TYPESOC,LINK) VALUES (%s, %s, %s)"""
                cursor.execute(query,(clubid[0],ts2,l2,))
                return
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
                flash("Request has been sent.")
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
    else:
        flash("Unaccepted Method.")
    return redirect(url_for('link2.clubProfile', id = clubId))

@link2.route('/deleteApply/<clubId>/<userId>', methods = ['GET', 'POST'])
@login_required
def deleteApply(clubId, userId):
    if request.method == 'POST':
        with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """DELETE FROM APPTAB WHERE(CLUBID = %s AND USERID = %s)"""
                cursor.execute(query,(clubId, userId,))
    else:
        flash("Unaccepted Method.")
    return redirect(url_for('link2.clubProfile', id = clubId))

@link2.route('/assignBoard/<int:clubId>', methods = ['GET', 'POST'])
@login_required
def assignBoard(clubId):
    if request.method == 'POST':
        with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """UPDATE CLUBMEM SET LEVEL = %s WHERE(CLUBID = %s AND USERID = %s)"""
                cursor.execute(query,(request.form['role'],clubId, request.form['member'],))
    else:
        flash("Method Error.")
    return redirect(url_for('link2.clubProfile', id = clubId))
