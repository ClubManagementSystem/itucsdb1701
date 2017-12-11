import datetime
import os
import json
import re
import datetime
import psycopg2 as dbapi2
from flask import redirect, Blueprint, flash
from flask.helpers import url_for
from flask import Flask
from flask import render_template, Response
from flask import request, current_app
from classes import User
from event import getevent
from passlib.apps import custom_app_context as pwd_context
from flask_login.utils import login_required
from flask_login import login_manager, login_user, logout_user,current_user

link6 = Blueprint('link6',__name__)

@link6.route('/message/<furom>/<int:role>/') # clubname = 0 if dir == true
def message(furom, role):
	tu = []
	messages = []
	newAdresses = []
	clearAdresses = []
	with dbapi2.connect(current_app.config['dsn']) as connection:
		cursor = connection.cursor()
		tus = []
		if role == 1:
			print("role = true")
			query = """SELECT CLUBDB.ID, CLUBDB.NAME FROM MESSAGE, USERDB, CLUBDB WHERE(USERID = USERDB.ID AND USERID = %s AND CLUBID = CLUBDB.ID) ORDER BY DATE ASC"""
			cursor.execute(query, (furom,))
			temp = cursor.fetchall()
			for t in temp:
				if t not in tus:
					tus.append(t)

			query = """SELECT CLUBID, CLUBDB.NAME FROM CLUBMEM, CLUBDB WHERE (CLUBID = CLUBDB.ID AND USERID = %s)"""
			cursor.execute(query,(furom,))
			members = cursor.fetchall()
			for m in members:
				if m not in tus:
					temp = [m[0], m[1]]
					newAdresses.append(temp)
				if m in tus:
					temp = [m[0], m[1]]
					clearAdresses.append(temp)

		else:
			query = """SELECT USERDB.ID, USERDB.REALNAME FROM MESSAGE, USERDB, CLUBDB WHERE(USERID = USERDB.ID AND CLUBID = %s AND CLUBID = CLUBDB.ID) ORDER BY DATE ASC """
			cursor.execute(query, (furom,))
			temp = cursor.fetchall()
			for t in temp:
				if t not in tus:
					tus.append(t)

			query = """SELECT USERID, REALNAME FROM CLUBMEM, USERDB WHERE (CLUBID = %s AND USERID = USERDB.ID) ORDER BY REALNAME"""
			cursor.execute(query,(furom,))
			members = cursor.fetchall()
			for m in members:
				if m not in tus:
					temp = [m[0], m[1]]
					newAdresses.append(temp)
				if m in tus:
					temp = [m[0], m[1]]
					clearAdresses.append(temp)
		connection.commit()

	return render_template('message.html', conversations = tus, adresses = newAdresses, adressesr = clearAdresses, id = furom, role = role)

@link6.route('/getMessages/<furom>/<int:role>/<int:ti>/')
def getMessages(furom, role, ti):
	tus = []
	newAdresses = []
	clearAdresses = []
	with dbapi2.connect(current_app.config['dsn']) as connection:
		cursor = connection.cursor()
		tus = []
		if role == 1:
			query = """SELECT CLUBDB.ID, CLUBDB.NAME FROM MESSAGE, USERDB, CLUBDB WHERE(USERID = USERDB.ID AND USERID = %s AND CLUBID = CLUBDB.ID) ORDER BY DATE ASC"""
			cursor.execute(query, (furom,))
			temp = cursor.fetchall()
			for t in temp:
				if t not in tus:
					tus.append(t)
			query = """SELECT CLUBID, CLUBDB.NAME FROM CLUBMEM, CLUBDB WHERE (CLUBID = CLUBDB.ID AND USERID = %s)"""
			cursor.execute(query,(furom,))
			members = cursor.fetchall()
			for m in members:
				if m not in tus:
					temp = [m[0], m[1]]
					newAdresses.append(temp)
				if m in tus:
					temp = [m[0], m[1]]
					clearAdresses.append(temp)
		else:
			query = """SELECT USERDB.ID, USERDB.REALNAME FROM MESSAGE, USERDB, CLUBDB WHERE(USERID = USERDB.ID AND CLUBID = %s AND CLUBID = CLUBDB.ID) ORDER BY DATE ASC """
			cursor.execute(query, (furom,))
			temp = cursor.fetchall()
			for t in temp:
				if t not in tus:
					tus.append(t)
			query = """SELECT USERID, REALNAME FROM CLUBMEM, USERDB WHERE (CLUBID = %s AND USERID = USERDB.ID) ORDER BY REALNAME"""
			cursor.execute(query,(furom,))
			members = cursor.fetchall()
			for m in members:
				if m not in tus:
					temp = [m[0], m[1]]
					newAdresses.append(temp)
				if m in tus:
					temp = [m[0], m[1]]
					clearAdresses.append(temp)
		connection.commit()

	name = []
	with dbapi2.connect(current_app.config['dsn']) as connection:
		cursor = connection.cursor()
		if role == 1:
			query = """SELECT CLUBDB.ID, CLUBDB.NAME, MSG, DATE, DIR FROM MESSAGE, USERDB, CLUBDB WHERE(USERID = USERDB.ID AND USERID = %s AND CLUBID = CLUBDB.ID AND CLUBID = %s) ORDER BY DATE"""
			cursor.execute(query, (furom, ti,))
			messages= cursor.fetchall()
		else:
			query = """SELECT USERDB.ID, USERDB.REALNAME, MSG, DATE, DIR FROM MESSAGE, USERDB, CLUBDB WHERE(USERID = USERDB.ID AND CLUBID = %s AND USERID = %s AND CLUBID = CLUBDB.ID) ORDER BY DATE"""
			cursor.execute(query, (furom, ti,))
			messages = cursor.fetchall()
		name.append(messages[0][0])
		name.append(messages[0][1])
		connection.commit()

	return render_template('message.html', conversations = tus, name = name, adresses = newAdresses, adressesr = clearAdresses, id = furom, role = role, messages = messages)

@link6.route('/sendMessages/<int:furom>/<int:tu>/<int:role>/', methods = ['POST', 'GET'])
def sendMessages(furom, role, tu):
	if request.method == 'POST':
		message = request.form['message']
		with dbapi2.connect(current_app.config['dsn']) as connection:
			cursor = connection.cursor()
			if role == 1:
				query = """INSERT INTO MESSAGE(USERID, CLUBID, DATE, MSG, DIR) VALUES(%s, %s, %s, %s, true)"""
				cursor.execute(query, (furom, tu, datetime.datetime.now(), message,))
			else:
				query = """INSERT INTO MESSAGE(USERID, CLUBID, DATE, MSG, DIR) VALUES(%s, %s, %s, %s, false)"""
				cursor.execute(query, (tu, furom, datetime.datetime.now(), message,))
			connection.commit()
		return redirect(url_for('link6.getMessages', furom = furom, role = role, ti = tu))
	else:
		return "sendmessage method fault"

@link6.route('/createConversation/<int:furom>/<int:role>/', methods = ['POST', 'GET'])
def createConversation(furom, role):
	if request.method == 'POST':
		try:
			tu = request.form['newAdress']
		except:
			flash("Choose somebody to create a conversation")
			return redirect(url_for('link6.message', furom = furom, role = role))
		with dbapi2.connect(current_app.config['dsn']) as connection:
			cursor = connection.cursor()
			if role == 1:
				query = """INSERT INTO MESSAGE(USERID, CLUBID, DATE, MSG, DIR) VALUES(%s, %s, %s, %s, true)"""
				cursor.execute(query, (furom, tu, datetime.datetime.now(), "Conversation Created",))
			else:
				query = """INSERT INTO MESSAGE(USERID, CLUBID, DATE, MSG, DIR) VALUES(%s, %s, %s, %s, false)"""
				cursor.execute(query, (tu, furom, datetime.datetime.now(), "Conversation Created",))
			connection.commit()
		return redirect(url_for('link6.getMessages', furom = furom, role = role, ti = tu))
	else:
		return "hatali method"

@link6.route('/deleteConversation/<int:furom>/<int:role>/', methods = ['POST', 'GET'])
def deleteConversation(furom, role):
	if request.method == 'POST':
		try:
			tu = request.form['newAdress']
		except:
			flash("Choose somebody to delete the conversation")
			return redirect(url_for('link6.message', furom = furom, role = role))
		tu = request.form['newAdress']
		with dbapi2.connect(current_app.config['dsn']) as connection:
			cursor = connection.cursor()
			if role == 1:
				query = """DELETE FROM MESSAGE WHERE(CLUBID = %s)"""
				cursor.execute(query, (tu,))
			else:
				query = """DELETE FROM MESSAGE WHERE(USERID = %s)"""
				cursor.execute(query, (tu,))
			connection.commit()
		return redirect(url_for('link6.message', furom = furom, role = role))
	else:
		return "hatali method"
