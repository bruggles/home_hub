from flask import Flask
from flask_login import LoginManager
from .config import Config
from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate

# Logging stuff below - disable when running prod
from logging.config import dictConfig
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})
# Logging stuff above - disable when running prod

app = Flask(__name__)
app.config.from_object(Config)
#app.config['SERVER_NAME'] = 'brandonruggles.com'
login = LoginManager(app)
login.login_view = 'login'
db = SQLAlchemy(app)

from app_contents import routes, models
