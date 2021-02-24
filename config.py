import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'is-this-really-necessary-for-this'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'warehouse.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
    #LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')