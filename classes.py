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
from home import dsn

class User:
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


