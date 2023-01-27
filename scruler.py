
from bs4 import BeautifulSoup
import requests as re
from datetime import datetime as dt
from threading import Thread
from database import *
from time import sleep

from pymongo import MongoClient

mongo = MongoClient(Mongo_db_string)
db=mongo.beinlive_test

def send(msg):
	bot_key=Bot_token
	chat=Personal_chat_id
	url=f"https://api.telegram.org/bot{bot_key}/sendMessage?chat_id={chat}&text={msg}"
	re.get(url)

def match_sctructure():
	match={"t1": "team1_name","img1":"team1_image", "t2": "team2_name","img2":"team2_image", 
			"startime": "", "score": "0:0","video_iframe":"","canal":"",
			"para1":"","para2":"","para3":"","speaker":"","dawri":"",
			"streamId":"","number":"0"
			}
	return(match)



def do_scraping():
	page = re.get("https://www.yalla-shoot.com/match/index.php")
	soup = BeautifulSoup(page.content, 'html.parser')


	events=soup.find_all("a",class_="matsh_live")
	
	matches=[match_sctructure() for _ in range(len(events))]

	domain="https://www.yalla-shoot.com"
	for nb,match in enumerate(matches):
		match["t1"],match["t2"]=map(lambda x:x.text,events[nb].find_all("td",class_="fc_name"))
		match["startime"]=events[nb].find("span",class_="fc_time").text

		match["img1"],match["img2"]=map(lambda x:domain+x["src"][2:],events[nb].find_all("img"))
		match["canal"],match["speaker"],match["dawri"]=map(lambda x:x.text,events[nb].find_all("p"))

	# Check and extract usefull infos
	ret_matches=[]

	for match in matches:
		hour=match["startime"]
		if ':' not in hour:continue
		i=hour.index(":")
		start=hour[i-2]+hour[i-1:i+3] if hour[i-2] in '0123456789' else '0'+hour[i-1:i+3]
		if "مس" in hour:
			h=str(int(start[:2])+12-3)
			if len(h)==1: h='0'+h
			start=h+start[2:]
		else:
			h=str(int(start[:2])-3)
			if len(h)==1: h='0'+h
			start=h+start[2:]
		match["startime"]=start

		text=match['canal']
		if "بي ان سبورت" in text:
			canal="Bein Sport "+text[text.index("بي ان سبورت")+12]

		elif "Premium" in text:
			canal="Bein Sport Premium "+text[text.index("Premium")+8]
		else:canal="waloo"
		
		if canal not in Canals_names.keys():
			continue
		match['canal']=canal
		ret_matches.append(match)
		ret_matches[-1]["number"]=str(len(ret_matches))
		ret_matches[-1]["video_iframe"]= Prepost_video

	return(ret_matches)

pub=[]
pool=[]

def remove_match(idd,nb,how):
	sleep(how)
	url = Streaming_server_api
	#db.Matches.delete_one({"number":nb})
	db.Today.update_one({"number":nb},{"$set":{"video_iframe":Prepost_video}})
	req = re.delete(url+idd)
	


def post_match(nb):
	global pub

	key=int(nb)-1
	

	while not pub[key]:
		hour=dt.now().strftime("%H:%M")

		match=db.Matches.find_one({"number":nb})

		if not (hour>=match["startime"]):sleep(60);continue

		today=dt.now().strftime("%Y_%m_%d")

		# Create the stream_id of the match
		url = Streaming_server_api
		source = {
				"type": "streamSource",
				"name": match["t1"]+" VS "+match["t2"]+' '+today,
				"streamUrl": Canal_source[Canals_names[match["canal"]]],
				}
		req = re.post(url+"create",json=source)
		
		
	
		# if success post the match in telegram group
		if req.status_code==200:

			req=req.json()
			match["streamId"]=req["streamId"]

			req2 = re.post(url+match["streamId"]+'/start')
			if req2.status_code==200:

				# update iframe of the match
				match["video_iframe"]=Streaming_server_iframe+match["streamId"]
				db.Matches.update_one({"number":match["number"]},{"$set":match})

				bot_key=Bot_token

				msg="Don't miss this Match: \n"
				msg+=match["t1"]+" VS "+match["t2"]+"\n"
				msg+=match["startime"]+" GMT"+"\n"
				msg+=match["canal"]+"\n"
				msg+=match["speaker"]+"\n"
				msg+=match["dawri"]+"\n"
				msg+=DOMAIN+"watch/"+today+"_"+match["number"]+"\n"
				for chat in Group_chat_id:
					url=f"https://api.telegram.org/bot{bot_key}/sendMessage?chat_id={chat}&text={msg}"
					re.get(url)

		Thread(target=remove_match,args=(match["streamId"],match["number"],60*115,),daemon=True).start()
		pub[key]=True
		break
				
today="2023_01_27"


def scheduler():
	global pub,pool,today

	
	while True:
		
		hour=dt.now().strftime("%H:%M")

		if not (today!=dt.now().strftime("%Y_%m_%d") and hour>='01:00'):sleep(60*15);continue

		pub=[True for _ in range(len(pub))]
		for event in pool:event.join()

		db.Matches.delete_many({})

		today=dt.now().strftime("%Y_%m_%d")
		# Scrape matches infos
		Matches=do_scraping()

		'''
		for i,match in enumerate(Matches):
			match["video_iframe"]= Prepost_video
		'''
		try:
			db.Matches.insert_many(Matches)
		except:
			azer=0
		

		# Telegram notification of the scrape infos
		bot_key=Bot_token
		msg="_____Today Most Important Matches_____\n"
		for ii,match in enumerate(Matches):
			msg+=match["t1"]+" VS "+match["t2"]+"\n"
			msg+=match["startime"]+" GMT"+"\n"
			msg+=match["canal"]+"\n"
			msg+=match["speaker"]+"\n"
			msg+=match["dawri"]+"\n"
			msg+=DOMAIN+"watch/"+today+"_"+str(ii+1)+"\n\n"

		chat=Personal_chat_id
		
		url=f"https://api.telegram.org/bot{bot_key}/sendMessage?chat_id={chat}&text={msg}"
		re.get(url)


		# Schedule the posts
		

		pool=[Thread(target=post_match,args=(match["number"],),daemon=True) for match in Matches]
		pub=[False for _ in range(len(pool))]
		for event in pool:event.start()

		sleep(60*15)


scheduler()