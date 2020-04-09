from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
#from flask_sqlalchemy import SQLAlchemy
import json
import os
from . import db


def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE_HOST='localhost',
    )

	if test_config is None:
        # load the instance config, if it exists, when not testing
		app.config.from_pyfile('config.py', silent=True)
	else:
        # load the test config if passed in
		app.config.from_mapping(test_config)

    # ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	#db = SQLAlchemy(app)
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

	return app

	'''
	@app.route('/')
	def statistc():
		return 'Hello, World !'
	'''	

 
