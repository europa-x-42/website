#!/usr/bin/python3

from typing import Optional

import sqlite3
#import psycopg2
import sys,base64,hashlib,random,binascii,time,datetime,smtplib
from flask import Flask,request,render_template,redirect,make_response #type:ignore
from flask_debugtoolbar import DebugToolbarExtension #type:ignore

DATABASE="europax" #TODO verify actual database name for production
DBPASSWORD="<password>" #TODO insert base64(base64(db password))

DEBUG=False

app=Flask(__name__)
try:
    #conn=psycopg2.connect("dbname='"+DATABASE+"' user='postgres' host='localhost' password='"+str(base64.b64decode(base64.b64decode(b'"+DBPASSWORD+"')),"UTF-8")+"'")
    #TODO change to using postgresql for production
    conn:Optional[sqlite3.Connection]=sqlite3.connect(":memory:") #NOTE sqlite3 only used for dev

    if conn is not None:
        db:Optional[sqlite3.Cursor]=conn.cursor()

    ##### SQLITE 3 DATABASE INITIALISATION #####
    #TODO Remove or comment for production
    if db is not None and conn is not None:
        try:
            db.execute("")
            conn.commit()
        except:
            conn.rollback()
            db.close()
            db=None
            conn.close()
            conn=None
    ############################################
except:
    conn=None
    db=None

if db is None or conn is None:
    sys.exit(1)

username=None
admin=False

@app.route("/",methods=["GET"])
def indexPage():
    return render_template("index.html",username=username,admin=admin)

@app.route("/catalog/",methods=["GET"])
def catalogPage():
    return render_template("catalog.html",username=username,admin=admin)

@app.route("/copyright/",methods=["GET"])
def copyrightPage():
    return render_template("copyright.html",username=username,admin=admin)

@app.route("/onlineshop/",methods=["GET"])
def onlineShopPage():
    return render_template("onlineshop.html",username=username,admin=admin)

@app.route("/signin/",methods=["GET"])
def signInPage():
    return render_template("signin.html",username=username,admin=admin)

@app.route("/signup/",methods=["GET"])
def signUpPage():
    return render_template("signup.html",username=username,admin=admin)

if __name__=="__main__":
    try:
        app.debug=DEBUG
        app.config['SECRET_KEY']='123'
        app.config['DEBUG_TB_ENABLED']=DEBUG
        app.config['DEBUG_TB_INTERCEPT_REDIRECTS']=False
        app.config['DEBUG_TB_PANELS']=('flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel','flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel','flask_debugtoolbar.panels.template.TemplateDebugPanel','flask_debugtoolbar.panels.logger.LoggingPanel','flask_debugtoolbar.panels.profiler.ProfilerDebugPanel')
        app.config['DEBUG_TB_HOSTS']=('127.0.0.1','localhost')
        toolbar = DebugToolbarExtension(app)
        app.run(host="0.0.0.0",port=5000)
    except Exception as e:
        if db is not None:
            db.close()
        if conn is not None:
            conn.close()
        print(e)
