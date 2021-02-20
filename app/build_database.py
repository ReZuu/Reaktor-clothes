import os, requests, json
from app import db
from app.models import Product, Manufacturer

def init_db():
    #Get all the products from the API here. Once for each category
    #Categories: Gloves, Beanies, Facemasks
    #https://bad-api-assignment.reaktor.com/v2/products/<category>
    gloves = json.loads(requests.get('https://bad-api-assignment.reaktor.com/v2/products/gloves').text)
    beanies = json.loads(requests.get('https://bad-api-assignment.reaktor.com/v2/products/beanies').text)
    facemasks = json.loads(requests.get('https://bad-api-assignment.reaktor.com/v2/products/facemasks').text)
    products = []
    products.extend(gloves)
    products.extend(beanies)
    products.extend(facemasks)
    
    #From products create a list of all the manufacturers, so we know what they are.
    #Now that list can be cross-checked for stock availability when making the Product model 
    # - alternatively make a separate manufacturers database from that list that can be cross checked whenever.
    
    
      
    #clean up old database
    if os.path.exists('warehouse.db'):
        os.remove('warehouse.db')
    
    #create a new fresh database
    db.create_all()

    # fill the database with products 
    for product in products:
        p = Product(id=product['id'], name=product['name'], manufacturer=product['manufacturer'], price=product['price'])
        db.session.add(p)
        
    db.session.commit()
    
    
def update_db():
    # need to make sure the current database is still "fresh" or if 5 minutes has passed and it needs to be updated
    pass