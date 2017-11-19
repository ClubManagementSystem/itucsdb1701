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
        clubnames.append(tuple([i[0],cn[0]]))
    return render_template('profile.html',clubnames = clubnames)


def userclub(id):
    with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT CLUBID FROM CLUBMEM WHERE (USERID=%s)"""
            cursor.execute(query,(id,))
            arr=cursor.fetchall()
            return arr

def getclubname(id):
    with dbapi2._connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT NAME FROM CLUBDB WHERE (ID=%s)"""
            cursor.execute(query,(id,))
            na=cursor.fetchone()
            return na

@link3.route('/edit')
@login_required
def editProfile():
    return render_template('edit.html')


@link3.route('/edit_profile',methods=['GET', 'POST'])
@login_required
def updateProfile():
    if request.method == "POST":
        userpsw0 = request.form['psw']
        userpwd1 = request.form['psw-repeat']
        useremail = request.form['email']
        if userpsw0 != None:
            if userpsw0 != userpwd1:
                flash('Passwords do not match!')
                return redirect(url_for('link3.editProfile'))
            else:
                userpsw = pwd_context.encrypt(userpsw0)
                userid=current_user.get_id()
                with dbapi2._connect(current_app.config['dsn']) as connection:
                    cursor = connection.cursor()
                    query = """UPDATE USERDB SET PSW=%s WHERE(ID=%s)"""
                    cursor.execute(query,(userpsw,userid,))
        if useremail!= None:
            userid=current_user.get_id()
            with dbapi2._connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                query = """UPDATE USERDB SET EMAIL=%s WHERE(ID=%s)"""
                cursor.execute(query,(useremail,userid,))
        else:
            return redirect(url_for('link3.userProfile'))
    return redirect(url_for('link3.userProfile'))
