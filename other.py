

from flask import Blueprint, render_template,request
from datetime import datetime as dt
from database import mongo,DOMAIN,Bot_token,Personal_chat_id,site_key,secret
import requests as re
import json

other = Blueprint('other', __name__)




@other.route('/contact',methods=['POST','GET'])
def contact():
	global secret,site_key
	if request.method=='POST':
		
		fname=request.form.get('fname')
		fmail=request.form.get('fmail')
		fmessage=request.form.get('ftext')
		captcha_response = request.form['g-recaptcha-response']
		payload = {'response':captcha_response, 'secret':secret}
		response = re.post("https://www.google.com/recaptcha/api/siteverify", payload)
		response_text = json.loads(response.text)

		red="<script>setTimeout(function(){window.location='https://koora.amhyou.com/';},2000)</script>"
		if response_text['success']:
			bot_key=Bot_token
			chat=Personal_chat_id
			msg="_____New DimaKoora Contact_____\n"
			msg+="- name : "+fname+"\n"
			msg+="- mail : "+fmail+"\n"
			msg+="- text : "+fmessage+"\n"

			url=f"https://api.telegram.org/bot{bot_key}/sendMessage?chat_id={chat}&text={msg}"
			re.get(url)

			return("Your message was succesfully sent."+red)

		return("Your just a robot, so your message was ignored."+red)
		
	else:
		return render_template("contact.html",base=DOMAIN,captcha=site_key)

@other.route('/about')
def about():

	return render_template("about.html",base=DOMAIN)

@other.route('/copyright')
def copyright():

	return render_template("copyright.html",base=DOMAIN)

@other.route('/donate')
def donate():

	return render_template("donate.html",base=DOMAIN)