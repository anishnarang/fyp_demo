from flask import Blueprint

main = Blueprint('main', __name__)

from . import routes
from . import single_routes
from . import multiple_routes
from . import live_routes
# from .. import db
