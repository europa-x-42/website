#!/usr/bin/python3

from typing import Optional,Dict

import sqlite3
#import psycopg2
import sys,base64,hashlib,random,binascii,time,datetime,smtplib
from flask import Flask,request,render_template,redirect,make_response #type:ignore
from flask_debugtoolbar import DebugToolbarExtension #type:ignore

DATABASE="europax" #TODO verify actual database name for production
DBPASSWORD="<password>" #TODO insert base64(base64(db password))

DEBUG=False

app=Flask(__name__)

sessionTokens:Dict[str,list]={}
userTokens:Dict[str,str]={}

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
            db.execute("CREATE TABLE Users (username TEXT,email TEXT,password TEXT,isAdmin BOOLEAN);")
            conn.commit()
            db.execute("INSERT INTO Users (username,email,password,isAdmin) VALUES ('admin','europax@yopmail.com','553b262eeda3ff58ffe4ad6c29ae354860f4a5a1f697b949638565fca3b00e4e',True);") #NOTE dev password: 'europaxPassword'
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
    user=updateUser(request)
    return render_template("index.html",username=user[0],admin=user[1])

@app.route("/catalog/",methods=["GET"])
def catalogPage():
    user=updateUser(request)
    return render_template("catalog.html",username=user[0],admin=user[1])

@app.route("/copyright/",methods=["GET"])
def copyrightPage():
    user=updateUser(request)
    return render_template("copyright.html",username=user[0],admin=user[1])

@app.route("/terms/",methods=["GET"])
def termsPage():
    user=updateUser(request)
    return render_template("terms.html",username=user[0],admin=user[1])

@app.route("/onlineshop/",methods=["GET"])
def onlineShopPage():
    user=updateUser(request)
    return render_template("onlineshop.html",username=user[0],admin=user[1])

@app.route("/signin/",methods=["GET"])
def signInPage():
    user=updateUser(request)
    return render_template("signin.html",username=user[0],admin=user[1])

@app.route("/signup/",methods=["GET"])
def signUpPage():
    user=updateUser(request)
    return render_template("signup.html",username=user[0],admin=user[1])

def updateUser(request):
    sessionToken=request.cookies.get("sessionToken")
    timeLimit=time.time()-60*60*2
    for token in sessionTokens:
        if sessionTokens[token][3]<timeLimit:
            print()
            print("Timed Out:",sessionTokens[token])
            print()
            del userTokens[sessionTokens[token][0]]
            del sessionTokens[token]
    print("Signed In:",str(list(sessionTokens.values())))
    print()
    if sessionToken in sessionTokens:
        sessionTokens[sessionToken][3]=time.time()
        return sessionTokens[sessionToken]
    else:
        return [None,False,time.time()]

def hashPassword(username):
    salt="qd>BqùoJDBNùLJQDNBùeqnvgùqV%QBDv%JQLNBqBVmkqjdbvkljQD,N"+username+"AOZDBObÙOUojbnegozgboQegbIgojHqouehNObNiuJNgouinboBOQBGpioBGouNbO<NojbnoujbGUOjivbOULNV"
    salt=hashlib.sha256(bytes(salt,"UTF-8")).hexdigest()
    password=hashlib.pbkdf2_hmac('sha256',bytes(password,"UTF-8"),bytes(salt,"UTF-8"),100000)
    password=str(binascii.hexlify(password),"UTF-8")
    return password

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
