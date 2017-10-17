import datetime
import os
import json
import re
import psycopg2 as dbapi2
from flask import redirect, Blueprint
from flask.helpers import url_for
from flask import Flask
from flask import render_template
from flask import request
from flask_login import UserMixin, LoginManager
from passlib.apps import custom_app_context as pwd_context
dsn = """user='vagrant' password='vagrant' host='localhost' port=5432 dbname='itucsdb'"""

class User(UserMixin):
    def __init__(self, name, number, email, psw):
        self.name = name
        self.number = number
        self.email = email
        self.psw = psw
        self.level = 0

class UserList:
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.last_key = None

    def add_user(self, newuser):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "INSERT INTO USERDB (NAME, NUMBER, EMAIL, PSW) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (newuser.name,newuser.number, newuser.email, newuser.psw))
            connection.commit()
            self.last_key = cursor.lastrowid

    def verify_user(self,uname,upsw):
        with dbapi2.connect(self.dbfile) as connection:
            cursor = connection.cursor()
            query = "SELECT NAME, PSW FROM USERDB WHERE (NAME = %s)"
            cursor.execute(query, (uname,))
            usr = cursor.fetchone()
            print (usr)
            if usr == None:
                return -2 # user yok

            else:
                if pwd_context.verify(upsw,usr[1]):
                    return 0 # sifre dogru
                else:
                    return -1 # sifre yanlis


