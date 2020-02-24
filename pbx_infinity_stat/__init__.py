from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
import json
import os


def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE_HOST='localhost',
    )
	Bootstrap(app)
	app.config['BOOTSTRAP_SERVE_LOCAL']  = True
	app.config['BOOTSTRAP_USE_MINIFIED'] = True

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
	
	@app.route('/')
	def index():
		return render_template('/index.html')
	
	@app.route('/get_data', methods=['POST'])
	def getdata():
		with open('test.json', 'r') as f:
			callgroups_dict = json.load(f)
		return callgroups_dict

	return app

	'''
	@app.route('/')
	def statistc():
		return 'Hello, World !'
	'''	

 
