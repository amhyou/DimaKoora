
from flask import request,jsonify,Blueprint,render_template
import json
from datetime import datetime as dt
import requests as re

from database import mongo,DOMAIN

main = Blueprint('main', __name__)



@main.route('/')
def hello_world():

	today=dt.now().strftime("%Y_%m_%d")

	Matches=mongo.db.Matches.find()

	result={str(i+1):match for i,match in enumerate(Matches)}

	return render_template("index.html",today=result,time=today,base=DOMAIN)
