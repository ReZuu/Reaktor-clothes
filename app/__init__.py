from flask import Flask, request, current_app
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
bootstrap = Bootstrap()


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
bootstrap.init_app(app)
#app.redis = Redis.from_url(app.config['REDIS_URL'])

    
    
from app import routes, models