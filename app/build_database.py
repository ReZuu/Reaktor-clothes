import os, requests, json
from app import db

def init_db(Product):
    #Get all the products from the API here. Once for each category
    #Categories: Gloves, Beanies, Facemasks
    #https://bad-api-assignment.reaktor.com/v2/products/<category>
    gloves = json.loads(requests.get('https://bad-api-assignment.reaktor.com/v2/products/gloves').text)
    beanies = json.loads(requests.get('https://bad-api-assignment.reaktor.com/v2/products/beanies').text)
    facemasks = json.loads(requests.get('https://bad-api-assignment.reaktor.com/v2/products/facemasks').text)
    products = []
    # products.extend(gloves)
    # products.extend(beanies)
    # products.extend(facemasks)
    products = gloves + beanies + facemasks # this should work as well
    #would flasks request.get_json() be better for these or does it even matter?
    
    #From products create a list of all the manufacturers, so we know what they are.
    #Now that list can be cross-checked for stock availability when making the Product model 
    # - alternatively: make a separate manufacturers database from that list that can be cross checked whenever. For example in _product.html
    #pros of checking the stock now, is if for some reason the manufacturer list/db would change, but product list not. Them being out of sync doesn't matter. Also don't need to display the manufacturers list anywhere, so the only point for it is to check the stock availability.
    
    #create a list of manufacturer names
    manufacturer_names = []
    for product in products:
        if len(manufacturer_names) != 0:
            if product['manufacturer'] not in manufacturer_names:
                manufacturer_names.append(product['manufacturer'])
        else:
            manufacturer_names.append(product['manufacturer'])
    
    #create a list of all the manufacturers and their products
    for item in manufacturer_names:
        print(item)
    # manufacturer_list = []
    # for manufacturer in manufacturer_names:
        # m = json.loads(requests.get('https://bad-api-assignment.reaktor.com/v2/products/' + manufacturer).text)
        # manufacturer_list.extend(m)
      
    #clean up old database
    # if os.path.exists('warehouse.db'):
        # os.remove('warehouse.db')
    #clear_data()
    db.drop_all()
    
    #create a new fresh database
    db.create_all()

    # fill the database with products 
    for product in products:
        #stock = #find the stock availability by checking manufacturers
        p = Product(id=product['id'], name=product['name'], manufacturer=product['manufacturer'], price=product['price'])
        db.session.add(p)
        
    db.session.commit()
    
def clear_data():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()
    
def update_db():
    # need to make sure the current database is still "fresh" or if 5 minutes has passed and it needs to be updated
    pass