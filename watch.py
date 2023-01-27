
from flask import Blueprint, render_template,request
from database import mongo,DOMAIN
from datetime import datetime as dt

watch = Blueprint('watch', __name__)

@watch.route('/watch/<target>')
def render(target):

	nb=-1
	if target[-2]!='_':nb=-2
	number=target[nb:]
	rest=target[:nb-1]

	if rest==dt.now().strftime("%Y_%m_%d"):

		match=mongo.db.Matches.find_one({"number":number})
		return render_template("watch.html",match=match,base=DOMAIN)

	else:
		return("no such match exist")