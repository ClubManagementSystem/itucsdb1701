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
from user import getclubname
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
                query = """ SELECT * FROM CLUBMEM WHERE (LEVEL = %s) """
                cursor.execute(query, (request.form['role'],))
                temp = cursor.fetchone()
                if temp:
                    query = """ UPDATE CLUBMEM SET LEVEL = 0 WHERE (LEVEL = %s) """
                    cursor.execute(query, (request.form['role'],))

                query = """UPDATE CLUBMEM SET LEVEL = %s WHERE(CLUBID = %s AND USERID = %s)"""
                cursor.execute(query,(request.form['role'],clubId, request.form['member'],))
    else:
        flash("Method Error.")
    return redirect(url_for('link2.clubProfile', id = clubId))

@link2.route('/AddClubBalance/<int:clubId>', methods = ['GET', 'POST'])
@login_required
def AddClubBalance(clubId):
    if request.method == "POST":
        amount = request.form['amount']
        expl = request.form['expl']
        addtobalance(clubId,amount,expl)
        flash("Income/Expense amount is added to the balance sheet.")
        return redirect(url_for('link2.clubBalance', clubId=clubId))
    else:
        flash("Access Denied")
        return redirect(url_for('link2.clubBalance', clubId=clubId))


@link2.route('/clubBalance/<int:clubId>')
@login_required
def clubBalance(clubId):
    balance = totalbalance(clubId)
    allamounts = balanceSheet(clubId)
    cname = getclubname(clubId)[0]
    return render_template('clubbalance.html', balance = balance, allamounts=allamounts, cid = clubId, cname = cname)

def totalbalance(clubId):
     with dbapi2._connect(current_app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """SELECT SUM (AMOUNT) FROM BALANCE WHERE CLUBID = %s"""
        cursor.execute(query,(clubId,))
        arr = cursor.fetchone()
        if arr == None:
            return 0
        return arr[0]

def addtobalance(clubId,amount,expl):
    with dbapi2._connect(current_app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """INSERT INTO BALANCE (CLUBID,AMOUNT,EXPL) VALUES (%s, %s, %s)"""
        cursor.execute(query,(clubId,amount,expl,))
        return

def balanceSheet(clubId):
    with dbapi2._connect(current_app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """SELECT AMOUNT,EXPL FROM BALANCE WHERE CLUBID = %s"""
        cursor.execute(query,(clubId,))
        arr = cursor.fetchall()
        return arr

@link2.route('/addclubInventory/<int:clubId>', methods = ['GET', 'POST'])
@login_required
def register_inventory(clubId):
    if request.method == "POST":
        name = request.form['name']
        date = request.form['date']
        time = request.form['time']
        ts_str = date + " " + time + ":00"
        ts = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query= "INSERT INTO INVENTORY(CLUBID,INAME,DATE) VALUES (%s, %s, %s)"
            cursor.execute(query, (clubId,name,ts_str))
            connection.commit()
            flash ("Inventory registration is done!")
            return redirect(url_for('link2.clubInventory', clubId=clubId))
    else:
        flash("Access Denied")
        return redirect(url_for('link2.clubInventory', clubId=clubId))

@link2.route('/clubInventory/<int:clubId>')
@login_required

def clubInventory(clubId):
    all_inventories=showallinventory(clubId)
    cname = getclubname(clubId)[0]
    return render_template('clubInventory.html', all_inventories = all_inventories, cid=clubId,cname=cname)

def showallinventory(clubId):
    with dbapi2._connect(current_app.config['dsn']) as connection:
        cursor = connection.cursor()
        query  = """SELECT INAME,DATE FROM INVENTORY WHERE CLUBID=%s"""
        cursor.execute(query,(clubId,))
        arr = cursor.fetchall()
        return arr
