import os, requests, json
from app import db
from bs4 import BeautifulSoup

def init_db(Product):
    #Get all the products from the API here. Once for each category
    #Categories: Gloves, Beanies, Facemasks
    #https://bad-api-assignment.reaktor.com/v2/products/<category>
    gloves = json.loads(requests.get('https://bad-api-assignment.reaktor.com/v2/products/gloves').text)
    beanies = json.loads(requests.get('https://bad-api-assignment.reaktor.com/v2/products/beanies').text)
    facemasks = json.loads(requests.get('https://bad-api-assignment.reaktor.com/v2/products/facemasks').text)
    products = gloves + beanies + facemasks 
    #would flasks request.get_json() be better for these or does it even matter?
    #change these to basic request.get so can handle exceptions from them with status_code's?
    
    #From products create a list of all the manufacturers, so we know what they are.
    #Now that list can be cross-checked for stock availability when making the Product model 
    # - alternatively: make a separate manufacturers database from that list that can be cross checked whenever. For example in _product.html
    # pros: of checking the stock now, is if for some reason the manufacturer list/db would change, but product list not. Them being out of sync doesn't matter. Also don't need to display the manufacturers list anywhere, so the only point for it is to check the stock availability.
    # alt.pros: database queries might be faster
    
    #create a list of manufacturer names
    manufacturer_names = []
    for product in products:
        if len(manufacturer_names) != 0:
            if product['manufacturer'] not in manufacturer_names:
                manufacturer_names.append(product['manufacturer'])
        else:
            manufacturer_names.append(product['manufacturer'])
    
    #create a list of all the manufacturers and their products
    # - alternative could call the API with the manufacturer + product_id to just get a single result, OR make separate list for all manufacturers, so would be easier to process and find the stock value
    # alt.cons: if the list changes before the process is done for all products, it will cause issues
    # alt.pros: don't have a massive list to process everytime I want to get the stock value 
    manufacturer_list = []
    manu_failure = ['testcase']
    for manufacturer in manufacturer_names:
        url = 'https://bad-api-assignment.reaktor.com/v2/availability/' + manufacturer
        # this sometimes runs into the "intentional failure case", so have to separate the requests from json.loads so can check for that failure. But if it happens, what should I do?
        # - just ignore the whole case?
        # - add the name of the manufacturer to a list that failed and process it later? global, background check/task for them?
        # - - I would then need to request it in X intervals to find out if it's working again, and if it is. I would then need to get the list of it's products and go through the products of that manufacturer to update their availability. Once that would be done would still need to refresh the page on client side
        m = requests.get(url)
        if len(m.text) != 0:
            manufacturer_list.extend(json.loads(m.text)['response'])
        else:
            manu_failure.extend(manufacturer)
    
    #clean up old database
    db.drop_all()
    
    #create a new fresh database
    db.create_all()

    # fill the database with products 
    for product in products:
        instock = get_stock(product['id'], manufacturer_list, manu_failure)
        #instock = #find the stock availability by checking manufacturers
        p = Product(id=product['id'], category=product['type'], name=product['name'], manufacturer=product['manufacturer'], stock=instock, price=product['price'])
        db.session.add(p)
        
    db.session.commit()
    
def update_db():
    # need to make sure the current database is still "fresh" or if 5 minutes has passed and it needs to be updated
    pass
    
def get_stock(product_id, manufacturer_list, manu_failure):
    #print(len(manufacturer_list))
    for manufacturer in manufacturer_list:
        if manufacturer not in manu_failure:
            if product_id == manufacturer['id'].lower():
                #stock = Manufacturer.query.filter_by(id=self.id).first()
                stock = html_parse(manufacturer['DATAPAYLOAD'])
                return stock
        else:
            return 'Unknown Failure'
    return 'Unknown'
    
def html_parse(line):
    soup = BeautifulSoup(line, 'html.parser')
    tag = soup.instockvalue
    return tag.string