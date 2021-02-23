from app import db
from app.build_database import init_db


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
