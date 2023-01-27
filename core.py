from flask import Flask 


from main import main
from api import api
from watch import watch
from other import other
from database import mongo,Mongo_db_string


app = Flask(__name__)
app.register_blueprint(main)
app.register_blueprint(api)
app.register_blueprint(watch)
app.register_blueprint(other)

app.config["MONGO_URI"] = Mongo_db_string
mongo.init_app(app)



if __name__=="__main__":

	app.run(port=5000,debug=True,host="0.0.0.0")