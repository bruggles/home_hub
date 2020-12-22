import os
from dotenv import load_dotenv

app_contents = os.path.abspath(os.path.dirname(__file__))
repo_dir = os.path.abspath(os.path.join(app_contents, '../..'))
load_dotenv(os.path.join(repo_dir,'vars.env'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app_contents, 'users.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #WTF_CSRF_ENABLED = False
