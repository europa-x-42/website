#!/usr/bin/python3

from typing import Optional,Dict

import sqlite3
import psycopg2 #type:ignore
import logging as log
import sys,base64,hashlib,random,binascii,time,datetime,smtplib
from flask import Flask,request,render_template,redirect,make_response #type:ignore
from flask_debugtoolbar import DebugToolbarExtension #type:ignore

DEV=True
PROD=not DEV

DEBUG=False

DATABASE="europax" #TODO verify actual database name for production
DBPASSWORD="<password>" #TODO insert base64(base64(password)). use password other than 'europaxPassword'

LOGFILE="dev.log" #TODO verify name for production

log.basicConfig(level=log.INFO,format="%(asctime)s::%(levelname)s::%(message)s",
        handlers=[log.StreamHandler(),log.FileHandler(LOGFILE)])

app=Flask(__name__)

sessionTokens:Dict[str,list]={}
userTokens:Dict[str,str]={}

try:
    if PROD:
        conn:Optional[sqlite3.Connection]=psycopg2.connect("dbname='"+DATABASE+"' user='postgres' host='localhost' password='"+str(base64.b64decode(base64.b64decode(b'"+DBPASSWORD+"')),"UTF-8")+"'")
    else:
        conn=sqlite3.connect(":memory:") #NOTE sqlite3 is only used for dev

    if conn is not None:
        db:Optional[sqlite3.Cursor]=conn.cursor()

    ##### SQLITE 3 DATABASE INITIALISATION #####
    if DEV:
        if db is not None and conn is not None:
            try:
                db.execute("CREATE TABLE Users (username TEXT,email TEXT,password TEXT,isAdmin BOOLEAN);")
                conn.commit()
                #Add default admin account
                db.execute("INSERT INTO Users (username,email,password,isAdmin) VALUES ('admin','europax@yopmail.com',"
                           "'553b262eeda3ff58ffe4ad6c29ae354860f4a5a1f697b949638565fca3b00e4e',"
                           "True);") #NOTE dev password: 'europaxPassword'
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
    resp=make_response(render_template("index.html",username=user[0],admin=user[1]))
    resp.set_cookie("lastPathVisited","/")
    if user[0]==None:
        resp.set_cookie("sessionToken","xxx",expires=0)
    else:
        resp.set_cookie("sessionToken",request.cookies.get("sessionToken"),max_age=60*60*2)
    return resp

@app.route("/catalog/",methods=["GET"])
def catalogPage():
    user=updateUser(request)
    resp=make_response(render_template("catalog.html",username=user[0],admin=user[1]))
    resp.set_cookie("lastPathVisited","/catalog/")
    if user[0]==None:
        resp.set_cookie("sessionToken","xxx",expires=0)
    else:
        resp.set_cookie("sessionToken",request.cookies.get("sessionToken"),max_age=60*60*2)
    return resp

@app.route("/copyright/",methods=["GET"])
def copyrightPage():
    user=updateUser(request)
    resp=make_response(render_template("copyright.html",username=user[0],admin=user[1]))
    resp.set_cookie("lastPathVisited","/copyright/")
    if user[0]==None:
        resp.set_cookie("sessionToken","xxx",expires=0)
    else:
        resp.set_cookie("sessionToken",request.cookies.get("sessionToken"),max_age=60*60*2)
    return resp

@app.route("/terms/",methods=["GET"])
def termsPage():
    user=updateUser(request)
    resp=make_response(render_template("terms.html",username=user[0],admin=user[1]))
    resp.set_cookie("lastPathVisited","/terms/")
    if user[0]==None:
        resp.set_cookie("sessionToken","xxx",expires=0)
    else:
        resp.set_cookie("sessionToken",request.cookies.get("sessionToken"),max_age=60*60*2)
    return resp

@app.route("/onlineshop/",methods=["GET"])
def onlineShopPage():
    user=updateUser(request)
    resp=make_response(render_template("onlineshop.html",username=user[0],admin=user[1]))
    resp.set_cookie("lastPathVisited","/onlineshop/")
    if user[0]==None:
        resp.set_cookie("sessionToken","xxx",expires=0)
    else:
        resp.set_cookie("sessionToken",request.cookies.get("sessionToken"),max_age=60*60*2)
    return resp

@app.route("/signin/",methods=["GET"])
def signInPage():
    user=updateUser(request)
    resp=make_response(render_template("signin.html",username=user[0],admin=user[1]))
    resp.set_cookie("lastPathVisited","/signin/")
    if user[0]==None:
        resp.set_cookie("sessionToken","xxx",expires=0)
    else:
        resp.set_cookie("sessionToken",request.cookies.get("sessionToken"),max_age=60*60*2)
    return resp

@app.route("/confirmsignin/",methods=["POST"])
def signIn():
    user=updateUser(request)
    username=request.form["username"]
    password=hashPassword(request.form["password"],username)
    log.info("Sign In: "+username)
    try:
        db.execute("SELECT isAdmin FROM Users WHERE username = %s and password = %s",(username,password))
        res=db.fetchall()
    except:
        conn.rollback()
        res=[]
    if len(res)>0:
        log.info("Sign In Successful")
        if username in userTokens:
            del sessionTokens[userTokens[username]]
        token=hex(random.randint(1000000000,1000000000000000))[2:]
        while token in sessionTokens:
            token=hex(random.randint(1000000000,1000000000000000))[2:]
        sessionTokens[token]=[username,res[0][0],time.time()]
        userTokens[username]=token
        log.info("Signed In: "+str(list(sessionTokens.values())))
        resp=make_response(redirect(request.cookies.get("lastPathVisited") if "lastPathVisited" in request.cookies else "/"))
        resp.set_cookie("sessionToken",token,max_age=60*60*24)
        return resp
    log.info("Sign In Failed")
    #resp=make_response(redirect("/signin/Error: The combination of username and password that you have provided is wrong./"))
    resp=make_response(redirect("/signin/"))
    if user[0]==None:
        resp.set_cookie("sessionToken","xxx",expires=0)
    else:
        resp.set_cookie("sessionToken",request.cookies.get("sessionToken"),max_age=60*60*2)
    return resp

@app.route("/signup/",methods=["GET"])
def signUpPage():
    user=updateUser(request)
    resp=make_response(render_template("signup.html",username=user[0],admin=user[1]))
    resp.set_cookie("lastPathVisited","/signup/")
    if user[0]==None:
        resp.set_cookie("sessionToken","xxx",expires=0)
    else:
        resp.set_cookie("sessionToken",request.cookies.get("sessionToken"),max_age=60*60*2)
    return resp

@app.route("/signout/",methods=["GET"])
def signOut():
    user=updateUser(request)
    if user[0] in userTokens:
        log.info("Sign Out: "+user[0])
        del sessionTokens[userTokens[user[0]]]
        del userTokens[user[0]]
    resp=make_response(redirect(request.cookies.get("lastPathVisited") if "lastPathVisited" in request.cookies else "/"))
    resp.set_cookie("sessionToken","xxx",expires=0)
    return resp

def updateUser(request):
    sessionToken=request.cookies.get("sessionToken")
    timeLimit=time.time()-60*60*2
    for token in sessionTokens:
        if sessionTokens[token][2]<timeLimit:
            print()
            print("Timed Out:",sessionTokens[token])
            print()
            del userTokens[sessionTokens[token][0]]
            del sessionTokens[token]
    print("Signed In:",str(list(sessionTokens.values())))
    print()
    if sessionToken in sessionTokens:
        sessionTokens[sessionToken][2]=time.time()
        return sessionTokens[sessionToken]
    else:
        return [None,False,time.time()]

def hashPassword(password,username):
    salt="qd>BqùoJDBNùLJQDNBùeqnvgùqV%QBDv%JQLNBqBVmkqjdbvkljQD,N"+username+\
         "AOZDBObÙOUojbnegozgboQegbIgojHqouehNObNiuJNgouinboBOQBGpioBGouNbO<NojbnoujbGUOjivbOULNV"
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
