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
from flask_login import login_manager, login_user, logout_user, confirm_login,current_user
from urllib.parse import urlparse, urljoin
from user import getclubname
from datetime import timedelta
link5 = Blueprint('link5',__name__)
@link5.route('/events')
def events():
    arr = getevent(0)
    return render_template('events.html', events = arr)

@link5.route('/create_event/<int:id>/')
def create_event(id):
    cname = getclubname(id)[0]
    return  render_template('create_event.html',cname = cname,cid = id,today = datetime.datetime.today().strftime("%Y-%m-%d"))

@link5.route('/delete_event/<int:cid>/<int:eid>/', methods=['GET', 'POST'])
def delete_event(cid,eid):
    if request.method == 'POST':
        with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """DELETE FROM EVENT WHERE(ID = %s)"""
                cursor.execute(query,(eid,))
    else:
        flash("Unaccepted Method.")
    return redirect(url_for('link2.clubProfile', id = cid))

@link5.route('/addnotice/<int:cid>/')
def addnotice(cid):
    cname = getclubname(cid)[0]
    return render_template('addnotice.html',cname = cname,cid = cid)

@link5.route('/savenotice/<int:cid>/', methods=['GET', 'POST'])
def savenotice(cid):
    if request.method == 'POST':
        title = request.form['title'].title()
        exp = request.form['exp']
        date = datetime.datetime.now()
        with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """ INSERT INTO NOTICE(CLUBID,TITLE,EXP,DATE) VALUES (%s,%s,%s,%s)"""
                cursor.execute(query, (cid,title,exp,date,))
                connection.commit()
                flash("Notification has been saved.")
                return redirect(url_for('link2.clubProfile', id = cid))

@link5.route('/deletenotice/<int:cid>/<int:id>/', methods=['GET', 'POST'])
def deletenotice(cid,id):
    with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DELETE FROM NOTICE WHERE(ID = %s)"""
            cursor.execute(query, (id,))
            flash("Notice has been deleted.")
            return redirect(url_for('link2.clubProfile', id = cid))

def getnotices(cid):
    with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT NOTICE.ID,TITLE,DATE,NOTICE.EXP,CLUBDB.NAME,CLUBID FROM NOTICE,CLUBDB WHERE (CLUBID = %s AND CLUBDB.ID = CLUBID) ORDER BY DATE DESC"""
            cursor.execute(query, (cid,))
            arr = cursor.fetchall()
            for i in range(len(arr)):
                arr[i] = list(arr[i])
                arr[i][2] = arr[i][2].strftime("%d-%m-%Y %H:%M:%S")
                print(arr[i][2])
                arr[i] = tuple(arr[i])
            return arr

@link5.route('/register_event/<int:id>/', methods=['GET', 'POST'])
def register_event(id):
    if request.method == "POST":
        name = request.form['name']
        date = request.form['date']
        time = request.form['time']
        exp = request.form['exp']
        loc = request.form['location']
        ts_str = date + " " + time + ":00"
        ts = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = "INSERT INTO EVENT (CLUBID,NAME,EXP,DATE,LOCATION) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (id,name,exp,ts_str,loc))
            connection.commit()
        flash ("Event registration is done!")
        return redirect(url_for('link2.clubProfile', id = id))

def cleanevents():
    with dbapi2.connect(current_app.config['dsn']) as connection:
        now = datetime.datetime.now()
        cursor = connection.cursor()
        query = """DELETE FROM EVENT WHERE(DATE < %s)"""
        cursor.execute(query,(now,))

def getevent(id):
    cleanevents()
    if id == 0:
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """ SELECT CLUBDB.NAME,EVENT.NAME,EVENT.EXP,DATE,LOCATION,EVENT.ID,CLUBDB.ID FROM EVENT,CLUBDB WHERE (CLUBID = CLUBDB.ID) ORDER BY EVENT.DATE """
            cursor.execute(query)
            arr = cursor.fetchall()
            editedarr = []
            for a in arr:
                a = list(a)
                a.append(a[3].strftime("%H:%M"))
                a[3] = a[3].strftime("%d %B %Y, %A")
                a = tuple(a)
                editedarr.append(a)
            return editedarr
    else:
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """ SELECT NAME,EXP,DATE,LOCATION,ID FROM EVENT WHERE (CLUBID = %s) ORDER BY DATE """
            cursor.execute(query,(id,))
            arr = cursor.fetchall()
            editedarr = []
            for a in arr:
                a = list(a)
                a.append(a[2].strftime("%H:%M"))
                a[2] = a[2].strftime("%d %B %Y, %A")
                a = tuple(a)
                editedarr.append(a)
            return editedarr
