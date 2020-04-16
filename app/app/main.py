from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
import json
import os
from . import db




app = Flask(__name__, instance_relative_config=True)
#app.config.from_mapping(
#	SECRET_KEY='dev',
#        DATABASE_HOST='localhost',
#)

app.config.from_pyfile('config.py', silent=True)

# ensure the instance folder exists
try:
	os.makedirs(app.instance_path)
except OSError:
	pass

Bootstrap(app)
@app.route('/')
def index():
	return render_template('/index.html')
	
@app.route('/get_data', methods=['POST'])
def getdata():
		# with open('test.json', 'r') as f:
		# 	callgroups_dict = json.load(f)
		# return callgroups_dict
	return  db.get_ACDQueuesMembers()

@app.route('/get_stats', methods=['POST'])
def getstats():
	return db.get_StatisticsByCall()

@app.route('/get_queues', methods=['POST'])
def getqueues():
	return db.get_QueuesByCall()
