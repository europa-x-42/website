#!/usr/bin/python3

import sqlite3
from flask import Flask,request,render_template #type:ignore
from flask_debugtoolbar import DebugToolbarExtension #type:ignore

app=Flask(__name__)
conn=sqlite3.connect(":memory:") #TODO change to actual file
db=conn.cursor()

if __name__=="__main__":
    try:
        app.debug = True
        app.config['SECRET_KEY'] = '123'
        app.config['DEBUG_TB_ENABLED'] = False
        app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
        app.config['DEBUG_TB_PANELS']=('flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel', 'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel', 'flask_debugtoolbar.panels.template.TemplateDebugPanel', 'flask_debugtoolbar.panels.logger.LoggingPanel', 'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel')
        app.config['DEBUG_TB_HOSTS'] = ('127.0.0.1','localhost')
        toolbar = DebugToolbarExtension(app)
        app.run(host="0.0.0.0",port=5000)
    except Exception as e:
        if db!=None:
            db.close()
        if conn!=None:
            conn.close()
        print(e)
