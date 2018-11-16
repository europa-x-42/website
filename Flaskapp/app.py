#!/usr/bin/python3

from typing import Optional,Dict

import psycopg2 #type:ignore
import logging as log
import sys,base64,hashlib,random,binascii,time,datetime,smtplib
from flask import Flask,request,render_template,redirect,make_response #type:ignore
from flask_debugtoolbar import DebugToolbarExtension #type:ignore

DEV=True
PROD=not DEV

DEBUG=False

DATABASE="europax" if PROD else "europax-dev" #TODO verify actual database name for production
DBPASSWORD="WVhwbGNHOXA="

LOGFILE="/home/adrian/Documents/projects/europax/"+("europax.log" if PROD else "europax-dev.log") #TODO verify name for production

log.basicConfig(level=log.INFO,format="%(asctime)s::%(levelname)s::%(message)s",
        handlers=[log.StreamHandler(),log.FileHandler(LOGFILE)])

app=Flask(__name__)

sessionTokens:Dict[str,list]={}
userTokens:Dict[str,str]={}

try:
    conn=psycopg2.connect("dbname='"+DATABASE+"' user='postgres' host='localhost' password='"+\
            str(base64.b64decode(base64.b64decode(bytes(DBPASSWORD,"UTF-8"))),"UTF-8")+"'")
    if conn is not None:
        db=conn.cursor()
    else:
        db=None
except:
    conn=None
    db=None

if db is None or conn is None:
    log.error("connection to database failed")
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

@app.route("/admin/",methods=["GET"])
def adminPage():
    user=updateUser(request)
    resp=make_response(render_template("admin.html",username=user[0],admin=user[1]))
    resp.set_cookie("lastPathVisited","/admin/")
    if user[0]==None:
        resp.set_cookie("sessionToken","xxx",expires=0)
    else:
        resp.set_cookie("sessionToken",request.cookies.get("sessionToken"),max_age=60*60*2)
    return resp

@app.route("/account/",methods=["GET"])
def accountPage():
    user=updateUser(request)
    resp=make_response(render_template("account.html",username=user[0],admin=user[1]))
    resp.set_cookie("lastPathVisited","/account/")
    if user[0]==None:
        resp.set_cookie("sessionToken","xxx",expires=0)
    else:
        resp.set_cookie("sessionToken",request.cookies.get("sessionToken"),max_age=60*60*2)
    return resp

@app.route("/signin/",methods=["GET"])
def signInPage():
    user=updateUser(request)
    error="error" in request.args
    errorMessage=request.args["error"] if error else ""
    resp=make_response(render_template("signin.html",username=user[0],admin=user[1],error=error,errorMessage=errorMessage))
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
        token=genToken()
        sessionTokens[token]=[username,res[0][0],time.time()]
        userTokens[username]=token
        resp=make_response(redirect(request.cookies.get("lastPathVisited") if "lastPathVisited" in request.cookies else "/"))
        resp.set_cookie("sessionToken",token,max_age=60*60*24)
        return resp
    log.info("Sign In Failed")
    resp=make_response(redirect("/signin/?error=Error: The combination of username and password that you have provided is wrong."))
    if user[0]==None:
        resp.set_cookie("sessionToken","xxx",expires=0)
    else:
        resp.set_cookie("sessionToken",request.cookies.get("sessionToken"),max_age=60*60*2)
    return resp

@app.route("/signup/",methods=["GET"])
def signUpPage():
    user=updateUser(request)
    error="error" in request.args
    errorMessage=request.args["error"] if error else ""
    resp=make_response(render_template("signup.html",username=user[0],admin=user[1],error=error,errorMessage=errorMessage))
    resp.set_cookie("lastPathVisited","/signup/")
    if user[0]==None:
        resp.set_cookie("sessionToken","xxx",expires=0)
    else:
        resp.set_cookie("sessionToken",request.cookies.get("sessionToken"),max_age=60*60*2)
    return resp

@app.route("/confirmsignup/",methods=["POST"])
def signUp():
    user=updateUser(request)
    username=request.form["username"]
    email=request.form["email"]
    password=request.form["password"]
    confirmpassword=request.form["confirmpassword"]
    if not all([c in "azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN1234567890&é(è!çà)-_$@#[]{}ù%µ|" for c in username]):
        resp=make_response(redirect("/signup/?error=Error: You have used a prohibited character in the username."))
        if user[0]==None:
            resp.set_cookie("sessionToken","xxx",expires=0)
        else:
            resp.set_cookie("sessionToken",request.cookies.get("sessionToken"),max_age=60*60*2)
        return resp
    if password==confirmpassword:
        isAdmin="admincheckbox" in request.form and user[1]
        log.info("Sign Up Attempt")
        log.info("Username: "+username)
        log.info("Email: "+email)
        log.info("Password: *****")
        log.info("Is Admin: "+str(isAdmin))
        password=hashPassword(password,username)
        if "checkbox" in request.form:
            try:
                db.execute("SELECT username, email FROM users WHERE username = %s or email = %s",(username,email))
                res=db.fetchall()
            except:
                conn.rollback()
                res=[]
            if len(res)==0:
                log.info("Sign Up Successful")
                try:
                    db.execute("INSERT INTO Users (username,email,password,isAdmin) VALUES (%s,%s,%s,%s)",(username,email,password,isAdmin))
                    conn.commit()
                except:
                    conn.rollback()
                if "signincheckbox" in request.form:
                    if username in userTokens:
                        del sessionTokens[userTokens[username]]
                    token=genToken()
                    sessionTokens[token]=[username,isAdmin,time.time()]
                    userTokens[username]=token
                    resp=make_response(redirect(request.cookies.get("lastPathVisited") if "lastPathVisited" in request.cookies else "/"))
                    resp.set_cookie("sessionToken",token)
                    return resp
                resp=make_response(redirect(request.cookies.get("lastPathVisited") if "lastPathVisited" in request.cookies else "/"))
                return resp
            log.info("Sign Up Failed")
            if username in [entry[0] for entry in res]:
                resp=make_response(redirect("/signup/?error=Error: This username is already being used."))
                if user[0]==None:
                    resp.set_cookie("sessionToken","xxx",expires=0)
                else:
                    resp.set_cookie("sessionToken",request.cookies.get("sessionToken"),max_age=60*60*2)
                return resp
            resp=make_response(redirect("/signup/?error=Error: This email is already being used."))
            if user[0]==None:
                resp.set_cookie("sessionToken","xxx",expires=0)
            else:
                resp.set_cookie("sessionToken",request.cookies.get("sessionToken"),max_age=60*60*2)
            return resp
        resp=make_response(redirect("/signup/?error=Error: You have not accepted the general terms and conditions."))
        if user[0]==None:
            resp.set_cookie("sessionToken","xxx",expires=0)
        else:
            resp.set_cookie("sessionToken",request.cookies.get("sessionToken"),max_age=60*60*2)
        return resp
    resp=make_response(redirect("/signup/?error=Error: You have entered two different passwords."))
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
    tokens=list(sessionTokens.keys())
    for token in tokens:
        if sessionTokens[token][2]<timeLimit:
            log.info("Timed Out: "+str(sessionTokens[token]))
            del userTokens[sessionTokens[token][0]]
            del sessionTokens[token]
    log.info("Signed In: "+str(list(sessionTokens.values())))
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

def genToken():
    token=hex(random.randint(1000000000,1000000000000000))[2:]
    while token in sessionTokens:
        token=hex(random.randint(1000000000,1000000000000000))[2:]
    return token

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
