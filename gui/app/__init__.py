from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy

bootstrap = Bootstrap()
app = Flask(__name__)

def create_app(config_name):
	bootstrap.init_app(app)
	
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	return app