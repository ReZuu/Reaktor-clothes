import os, requests, json
from app import db
from bs4 import BeautifulSoup

def init_db(Product, job=None):
    #Checking if job_id is None or not, in order to be able to update RQ job progress
    #if job != None:
        #try to fetch the job?

    #Get all the products from the API here. Once for each category
    #Categories: Gloves, Beanies, Facemasks
    #https://bad-api-assignment.reaktor.com/v2/products/<category>
    print ('Fetching products')
    products = []
    r_gloves = requests.get('https://bad-api-assignment.reaktor.com/v2/products/gloves')
    if (r_gloves.status_code != 503):
        gloves = json.loads(r_gloves.text)
        products += gloves
    r_beanies = requests.get('https://bad-api-assignment.reaktor.com/v2/products/beanies')
    if (r_beanies.status_code != 503):
        beanies = json.loads(r_beanies.text)
        products += beanies
    r_facemasks = requests.get('https://bad-api-assignment.reaktor.com/v2/products/facemasks')
    if (r_facemasks.status_code != 503):
        facemasks = json.loads(r_facemasks.text)
        products += facemasks
    #would flasks request.get_json() be better for these or does it even matter?
    #would try-except be better here or not?
    
    #From products create a list of all the manufacturers, so we know what they are.
    #Now that list can be cross-checked for stock availability when making the Product model 
    # - alternatively: make a separate manufacturers database from that list that can be cross checked whenever. For example in _product.html
    # pros: of checking the stock now, is if for some reason the manufacturer list/db would change, but product list not. Them being out of sync doesn't matter. Also don't need to display the manufacturers list anywhere, so the only point for it is to check the stock availability.
    # alt.pros: database queries might be faster
    
    #create a list of manufacturer names
    print ('Getting a list of all the manufacturers')
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
    print ('Getting a list of all the manufacturers products')
    manufacturer_list = []
    manu_failure = ['testcase']
    item_count = 0
    for manufacturer in manufacturer_names:
        url = 'https://bad-api-assignment.reaktor.com/v2/availability/' + manufacturer
        # this sometimes runs into the "intentional failure case", so have to separate the requests from json.loads so can check for that failure. But if it happens, what should I do?
        # - just ignore the whole case?
        # - add the name of the manufacturer to a list that failed and process it later? global, background check/task for them?
        # - - I would then need to request it in X intervals to find out if it's working again, and if it is. I would then need to get the list of it's products and go through the products of that manufacturer to update their availability. Once that would be done would still need to refresh the page on client side
        
        # for testing the fail case - should return 'uknown' as stock value when unable to get the manufacturers API info
        # headers = {'x-force-error-mode': 'all'}
        # if manufacturer == 'okkau':
            # m = requests.get(url, headers=headers)
        # else:
            # m = requests.get(url)
            
        m = requests.get(url)
        m_json = json.loads(m.text)
        
        #if len(m.text) != 0:
        if m_json['response'] != '[]':
            manufacturer_list.extend(m_json['response'])
            item_count += len(m_json['response'])
        else:
            manu_failure.append(manufacturer)
    
    print ('Failed to get these manufacturers: ')
    print (manu_failure)
    #print ('manu_list length: ')
    #print (len(manufacturer_list))
    
    print ('Cleaning and re-creating databases')
    #clean up old database
    db.drop_all()
    
    #create a new fresh database
    db.create_all()

    # fill the database with products 
    print ('Creating all the products')
    count = 0
    for product in products:
        instock = get_stock(product['id'], manufacturer_list, manu_failure)
        #instock = #find the stock availability by checking manufacturers
        p = Product(id=product['id'], category=product['type'], name=product['name'], manufacturer=product['manufacturer'], stock=instock, price=product['price'])
        db.session.add(p)
        count += 1
        job.meta['progress'] = 100.0 * count / len(products)
        print(job.meta['progress'])
        
    job.meta['progress'] = 100
    job.save_meta()
    print ('Committing products to database')
    db.session.commit()
    
def update_db():
    # need to make sure the current database is still "fresh" or if 5 minutes has passed and it needs to be updated
    pass
    
def get_stock(product_id, manufacturer_list, manu_failure):
    #print(len(manufacturer_list))
    for manufacturer in manufacturer_list:
        if manufacturer not in manu_failure:
            #print('getting stock')
            #print(manufacturer)
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
    
def empty_db():
    db.session.drop_all()
    db.session.commit()