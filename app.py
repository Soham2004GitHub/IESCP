from flask import Flask 
from backend.models import *
app=None #initially none


from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from flask import request
from flask import current_app as app #Alias for current running app
from flask import flash, redirect, url_for
import datetime 


def init_app():
    #AIS = Admin Influencer Sponsor
    ais_app=Flask(__name__) #object of Flask
    ais_app.debug=True
    ais_app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///ais.sqlite3"
    ais_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    ais_app.config["SECRET_KEY"] = "your_secret_key_here"
    ais_app.app_context().push() #Direct access app by other modules(db, authentication)
    db.init_app(ais_app)
    print("AIS application started....")
    return ais_app

app=init_app()

from backend.controllers import *

if __name__=="__main__":
    app.run(debug=True)



