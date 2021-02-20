from app import db


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
        
    def get_stock(self, manufacturer):
        stock = Manufacturer.query.filter_by(id=self.id).first()
        return stock.stock
        
class Manufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    product_id = db.Column(db.Text, db.ForeignKey('product.id'))
    stock = db.Column(db.String)
    
    def __repr__(self):
        return "<Manufacturer (%r, %r, %r)>" % (self.name, self.product, self.stock)
        