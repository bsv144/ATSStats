from flask import Flask
from flask_bootstrap import Bootstrap
import os

from .nav import nav

def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE_HOST='localhost',
    )
	Bootstrap(app)
	app.config['BOOTSTRAP_SERVE_LOCAL'] = True

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
	
	nav.init_app(app)
	
	return app

	'''
	@app.route('/')
	def statistc():
		return 'Hello, World !'
	'''	

 
