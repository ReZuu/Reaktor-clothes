from app import db
from flask import current_app
import redis
import rq

#general table for products and their information
class Product(db.Model):
    id = db.Column(db.Text, primary_key=True)
    category = db.Column(db.String(18), index=True)
    name = db.Column(db.String)
    stock = db.Column(db.String)
    manufacturer = db.Column(db.String(64), index=True)
    color = db.Column(db.String)
    price = db.Column(db.Integer)
    
    def __repr__(self):
        return "<Product (%r, %r, %r)>" % (self.name, self.manufacturer, self.stock)
    
#currently only used for keeping track of manufacturers that failed to give their products through the API, could also just keep a general list of the names. So would only need to get them once. But if the names would change would need to check for that
class Manufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    received = db.Column(db.Boolean)
    
    def __repr__(self):
        return "<Manufacturer: (%r), received: (%r)>" % (self.name, self.received)

#table class to keep track of ongoing and complete RQ tasks
class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    complete = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(128))
    
    def __repr__(self):
        return "<Task name: (%r), complete: (%r))>" % (self.name, self.complete)
    
    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job
        
    def get_progress(self):
        job = self.get_rq_job()
        print ('job id in progress: {}, progress: {}'.format(job.get_id(), job.meta['progress']))
        return int(job.meta.get('progress', 0) if job is not None else 100)
         
#table class to keep track of Etag's from the API 
class Caches(db.Model):
    # id = Etag
    id = db.Column(db.String(128), primary_key=True)
    # name = Category or manufacturer name
    name = db.Column(db.String(36), index=True)
    
    def __repr__(self):
        return "<Cache tag for (%r)>" % (self.name)