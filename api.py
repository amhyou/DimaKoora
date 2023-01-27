
from flask import Blueprint,jsonify,request
from datetime import datetime as dt
from database import mongo,DOMAIN,Streaming_server_api
import requests as re



api = Blueprint('api', __name__)


@api.route('/matches',methods=["POST"])
def matches_do():
	Matches=mongo.db.Matches.find()
	msg=''
	for match in Matches:
		msg+=match["t1"]+" VS "+match["t2"]+"\n"+match["number"]+":"+match["streamId"]+"\n\n"

	return (msg)

@api.route('/fixhour',methods=["POST"])
def fix_hour():


	com=request.json
	match_key=com["key"]
	hour=com["hour"]

	mongo.db.Matches.update_one({"number":match_key},{"$set":{"startime":hour}})

	return 'updated!!'


@api.route('/fixstream',methods=["POST"])
def fix_stream():

	send=request.json

	idd=mongo.db.Matches.find_one({"number":send["key"]})
	print(idd)
	
	url = Streaming_server_api+idd["streamId"]
	print(url,send)
	infos = {
			"streamUrl": send["lien"]
			}

	req = re.put(url,json=infos)
	st=req.status_code

	if st==200 and req.json()["success"]:
		return("nice")
	else:
		return("xi 9lwaa maxi hya hadik f stream server")

@api.route('/bda',methods=["POST"])
def bda():
	send=request.json

	url = Streaming_server_api

	idd=mongo.db.Matches.find_one({"number":send["key"]})

	req = re.post(url+idd["streamId"]+'/start')
	st=req.status_code

	if st==200:
		return("nice")
	else:
		return(req.text)

@api.route('/hbs',methods=["POST"])
def hbs():
	send=request.json

	url = Streaming_server_api

	idd=mongo.db.Matches.find_one({"number":send["key"]})

	req = re.post(url+idd["streamId"]+'/stop')
	st=req.status_code

	if st==200:
		return("nice")
	else:
		return(req.text)

@api.route('/update',methods=["POST"])
def update():

	today=dt.now().strftime("%Y_%m_%d")
	today='1'+today[1:]
	mongo.db.Today.update_one({},{"$set":{"value":today}})

	return("ok")
	