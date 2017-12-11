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
        name = request.form['name'].title()
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
            level = -1
        query = """SELECT COUNT(*) FROM APPTAB WHERE (CLUBID = %s AND USERID = %s)"""
        cursor.execute(query,(id, userId,))
        isapplied = cursor.fetchone()[0]

        applicant = None
        if ismember and level == 1:
            query = """SELECT USERID, REALNAME FROM USERDB, APPTAB WHERE (USERID = USERDB.ID AND CLUBID = %s)"""
            cursor.execute(query,(id,))
            applicant = cursor.fetchall()

        query = """SELECT CLUBMEM.LEVEL, REALNAME, EMAIL FROM CLUBMEM, USERDB WHERE (CLUBID = %s AND USERID = USERDB.ID AND CLUBMEM.LEVEL > 0) ORDER BY CLUBMEM.LEVEL ASC"""
        cursor.execute(query,(id,))
        board = cursor.fetchall()

        query = """SELECT USERID, REALNAME FROM CLUBMEM, USERDB WHERE (CLUBID = %s AND USERID = USERDB.ID)"""
        cursor.execute(query,(id,))
        members = cursor.fetchall()

        query = """SELECT TYPESOC, LINK FROM SOCMED WHERE (CLUBID = %s)"""
        cursor.execute(query,(id,))
        socmed = cursor.fetchall()


    return render_template('clubProfile.html',socmed = socmed, events = events, club = club, members = members, ismember = ismember, isapplied = isapplied, level = level, applicants = applicant, board = board)

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
            connection.commit()
            query = """SELECT ID FROM CLUBDB WHERE (NAME = %s)"""
            cursor.execute(query,(n,))
            clubid = cursor.fetchone()
            print("2")
    if l1 and ts1:
            with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """INSERT INTO SOCMED (CLUBID,TYPESOC,LINK) VALUES (%s, %s, %s)"""
                cursor.execute(query,(clubid[0],ts1,l1,))
                connection.commit()
                return
    if l2 and ts2:
            with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """INSERT INTO SOCMED (CLUBID,TYPESOC,LINK) VALUES (%s, %s, %s)"""
                cursor.execute(query,(clubid[0],ts2,l2,))
                connection.commit()
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
                connection.commit()
                flash("Request has been sent.")
        return redirect(url_for('link2.clubProfile', id = clubId))

@link2.route('/welcomeApply/<int:clubId>/<int:userId>', methods = ['GET', 'POST'])
@login_required
def welcomeApply(clubId, userId):
    if request.method == 'POST':
        with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """DELETE FROM APPTAB WHERE(CLUBID = %s AND USERID = %s)"""
                cursor.execute(query,(clubId, userId,))

                query = """INSERT INTO CLUBMEM (CLUBID, USERID, LEVEL) VALUES (%s, %s, 0)"""
                cursor.execute(query,(clubId, userId,))
                connection.commit()
    else:
        flash("Unaccepted Method.")
    return redirect(url_for('link2.clubProfile', id = clubId))

@link2.route('/deleteApply/<int:clubId>/<int:userId>', methods = ['GET', 'POST'])
@login_required
def deleteApply(clubId, userId):
    if request.method == 'POST':
        with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """DELETE FROM APPTAB WHERE(CLUBID = %s AND USERID = %s)"""
                cursor.execute(query,(clubId, userId,))
                connection.commit()
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
                    connection.commit()

                query = """UPDATE CLUBMEM SET LEVEL = %s WHERE(CLUBID = %s AND USERID = %s)"""
                cursor.execute(query,(request.form['role'],clubId, request.form['member'],))
                connection.commit()
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
        connection.commit()
        if arr == None:
            return 0
        return arr[0]

def addtobalance(clubId,amount,expl):
    with dbapi2._connect(current_app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """INSERT INTO BALANCE (CLUBID,AMOUNT,EXPL) VALUES (%s, %s, %s)"""
        cursor.execute(query,(clubId,amount,expl,))
        connection.commit()
        return

def balanceSheet(clubId):
    with dbapi2._connect(current_app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """SELECT AMOUNT,EXPL FROM BALANCE WHERE CLUBID = %s"""
        cursor.execute(query,(clubId,))
        arr = cursor.fetchall()
        return arr

@link2.route('/deletemember/<int:clubId>/<int:userId>', methods = ['GET', 'POST'])
@login_required
def deletemember(clubId, userId):
    if request.method == 'POST':
        curuid = current_user.get_id()
        if curuid == userId:
            flash("You cannot remove yourself from the club.")
            return redirect(url_for('link2.memberlist', cid = clubId))
        with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """DELETE FROM CLUBMEM WHERE(CLUBID = %s AND USERID = %s)"""
                cursor.execute(query,(clubId, userId,))
                connection.commit()
    else:
        flash("Unaccepted Method.")
    return redirect(url_for('link2.memberlist', cid = clubId))

@link2.route('/deletesocmed/<int:id>', methods = ['GET', 'POST'])
@login_required
def deletesocmed(id):
    if request.method == 'POST':
        with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """SELECT CLUBID FROM SOCMED WHERE(ID = %s)"""
                cursor.execute(query,(id,))
                clubId = cursor.fetchone()[0]
                query = """DELETE FROM SOCMED WHERE(ID = %s)"""
                cursor.execute(query,(id,))
                connection.commit()
                return redirect(url_for('link2.socmed', cid=clubId))

@link2.route('/addsocmed/<int:cid>', methods = ['GET', 'POST'])
@login_required
def addsocmed(cid):
    if request.method == 'POST':
        typesoc = request.form['typesoc']
        link = request.form['link']
        with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """INSERT INTO SOCMED(CLUBID,TYPESOC,LINK) VALUES (%s,%s,%s)"""
                cursor.execute(query,(cid,typesoc,link))
                connection.commit()
                return redirect(url_for('link2.socmed', cid=cid))

@link2.route('/socmed/<int:cid>')
@login_required
def socmed(cid):
    with dbapi2._connect(current_app.config['dsn']) as connection:
            curuid = current_user.get_id()
            cname = getclubname(cid)[0]
            cursor = connection.cursor()
            query = """ SELECT LEVEL FROM CLUBMEM WHERE (CLUBID = %s AND USERID = %s)"""
            cursor.execute(query,(cid,curuid,))
            level = cursor.fetchone()
            if level == None:
                lvl = 0
            else:
                lvl = level[0]

            query = """SELECT TYPESOC, LINK,ID FROM SOCMED WHERE (CLUBID = %s)"""
            cursor.execute(query,(cid,))
            socmed = cursor.fetchall()
            return render_template('socmed.html', socmed = socmed, level = lvl, cid = cid, cname = cname)



@link2.route('/memberlist/<int:cid>')
@login_required
def memberlist(cid):
    curuid = current_user.get_id()
    cname = getclubname(cid)[0]
    with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """ SELECT LEVEL FROM CLUBMEM WHERE (CLUBID = %s AND USERID = %s)"""
            cursor.execute(query,(cid,curuid,))
            level = cursor.fetchone()
            if level == None:
                lvl = 0
            else:
                lvl = level[0]
            query = """SELECT USERID, REALNAME,CLUBMEM.LEVEL FROM CLUBMEM, USERDB WHERE (CLUBID = %s AND USERID = USERDB.ID) ORDER BY REALNAME"""
            cursor.execute(query,(cid,))
            members = cursor.fetchall()
            return render_template('memlist.html', members = members,cname = cname,cid = cid, level = lvl)


@link2.route('/addclubInventory/<int:clubId>', methods = ['GET', 'POST'])
@login_required
def register_inventory(clubId):
    if request.method == "POST":
        name = request.form['name']
        price = request.form['price']
        with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query= "INSERT INTO INVENTORY(CLUBID,INAME,PRICE,USERNAMEID) VALUES (%s, %s, %s,1)"
            cursor.execute(query, (clubId,name,price,))
            connection.commit()
            flash ("Inventory registration is done!")
            return redirect(url_for('link2.clubInventory', clubId=clubId))
    else:
        flash("Access Denied")
        return redirect(url_for('link2.clubInventory', clubId=clubId))

@link2.route('/clubInventory/<int:clubId>', methods = ['GET', 'POST'])
@login_required
def clubInventory(clubId):
    uid = current_user.get_id()[0]
    with dbapi2._connect(current_app.config['dsn']) as connection:
        cursor = connection.cursor()
        query = """ SELECT LEVEL FROM CLUBMEM WHERE (CLUBID = %s AND USERID = %s)"""
        cursor.execute(query,(clubId,uid,))
        level = cursor.fetchone()
        if level == None:
            lvl = 0
        else:
            lvl = level[0]
    availableinventories=showavailableinventories(clubId)
    cname = getclubname(clubId)[0]
    return render_template('clubInventory.html', availableinventories = availableinventories,cid=clubId,cname=cname, uid = uid,level = lvl )

def showavailableinventories(clubId):
    with dbapi2._connect(current_app.config['dsn']) as connection:
        cursor = connection.cursor()
        query  = """SELECT INVENTORY.ID,INAME,AVAILABLE,PRICE,USERDB.REALNAME,USERDB.ID FROM INVENTORY,USERDB WHERE (USERDB.ID = INVENTORY.USERNAMEID AND CLUBID=%s)"""
        cursor.execute(query,(clubId,))
        arr = cursor.fetchall()
        print(str(arr))
        return arr

@link2.route('/releaseitem/<int:cid>/<int:id>', methods = ['GET', 'POST'])
def releaseitem(cid,id):
    if request.method == "POST":
        with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query  = """UPDATE INVENTORY SET AVAILABLE=0 WHERE (ID = %s)  """
            cursor.execute(query,(id,))
            connection.commit()
            return redirect(url_for('link2.clubInventory',clubId=cid))

@link2.route('/deleteitem/<int:cid>/<int:id>', methods = ['GET', 'POST'])
def deleteitem(cid,id):
    if request.method == "POST":
        with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query  = """DELETE FROM INVENTORY WHERE (ID = %s)  """
            cursor.execute(query,(id,))
            connection.commit()
            return redirect(url_for('link2.clubInventory',clubId=cid))

@link2.route('/inventoryapp/<int:cid>/<int:id>', methods = ['GET', 'POST'])
def apply_inventory(cid,id):
    if request.method == "POST":
        uid = current_user.get_id()
        with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query  = """UPDATE INVENTORY SET AVAILABLE=1,USERNAMEID=%s WHERE (ID = %s)  """
            cursor.execute(query,(uid,id,))
            connection.commit()
            return redirect(url_for('link2.clubInventory',clubId=cid))
