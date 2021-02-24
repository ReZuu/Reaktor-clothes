from app import db
from app.build_database import init_db
import redis
import rq


class Product(db.Model):
    id = db.Column(db.Text, primary_key=True)
    category = db.Column(db.String(18), index=True)
    name = db.Column(db.String)
    stock = db.Column(db.String)
    manufacturer = db.Column(db.String(64), index=True)
    #color = db.Column(db.String)
    price = db.Column(db.Integer)
    
    def __repr__(self):
        return "<Product (%r, %r, %r)>" % (self.name, self.manufacturer, self.stock)
    
        
class Manufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    product_id = db.Column(db.Text, db.ForeignKey('product.id'))
    stock = db.Column(db.String)
    
    def __repr__(self):
        return "<Manufacturer (%r, %r, %r)>" % (self.name, self.product, self.stock)
        
# is this necessary for tying the two tables together? Are the id/names flipped? Only if I use the manufacturer model to begin with      
# stocks = db.Table('stocks',
    # db.Column('product_id', db.Text, db.ForeignKey('product.id')),
    # db.Column('manufacturer_name', db.String, db.ForeignKey('manufacturer.name'))
# )

class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    complete = db.Column(db.Boolean, default=False)
    
    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job
        
    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100
        
def get_tasks_in_progress():
    return Task.query.filter_by(complete=False).all()
    
def get_task_in_progress(name):
    return Task.query.filter_by(name=name, complete=False).first()