from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache   

bootstrap = Bootstrap()
cache = Cache()
app = Flask(__name__)

def create_app(config_name):
	bootstrap.init_app(app)
	cache.init_app(app)
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	return app