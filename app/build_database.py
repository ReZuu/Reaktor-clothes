import os, requests, json
from app import db
from app.models import Manufacturer, Product, Caches
from bs4 import BeautifulSoup
from flask import g

def init_db(job):

    #could fairly easily expand/lighten this process to multiple workers.
    #one for each manufactrer or category, but don't think heroku free limits would allow that.

    #Get all the products from the API here. Once for each category
    #Categories: Gloves, Beanies, Facemasks
    #https://bad-api-assignment.reaktor.com/v2/products/<category>
    print ('Fetching products')
    products = []
    r_gloves = requests.get('https://bad-api-assignment.reaktor.com/v2/products/gloves')
    if (r_gloves.status_code != 503):
        gloves = json.loads(r_gloves.text)
        products += gloves
    gloves_etag = Caches(id=r_gloves.headers['Etag'], name='Gloves')
    db.session.add(gloves_etag)
    
    r_beanies = requests.get('https://bad-api-assignment.reaktor.com/v2/products/beanies')
    if (r_beanies.status_code != 503):
        beanies = json.loads(r_beanies.text)
        products += beanies
    beanies_etag = Caches(id=r_beanies.headers['Etag'], name='Beanies')
    db.session.add(beanies_etag)
        
    r_facemasks = requests.get('https://bad-api-assignment.reaktor.com/v2/products/facemasks')
    if (r_facemasks.status_code != 503):
        facemasks = json.loads(r_facemasks.text)
        products += facemasks
    facemasks_etag = Caches(id=r_facemasks.headers['Etag'], name='Facemasks')
    db.session.add(facemasks_etag)
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
        if product['manufacturer'] not in manufacturer_names:
            if product['manufacturer'] not in Manufacturer.query.all():
                new_manu = Manufacturer(name=product['manufacturer'])
                db.session.add(new_manu)
            manufacturer_names.append(product['manufacturer'])
    db.session.commit()
    #print(manufacturer_names)
    #print(Manufacturer.query.all())
    
    #create a list of all the manufacturers and their products
    # - alternative could call the API with the manufacturer + product_id to just get a single result, OR make separate list for all manufacturers, so would be easier to process and find the stock value
    # alt.cons: if the list changes before the process is done for all products, it will cause issues
    # alt.pros: don't have a massive list to process everytime I want to get the stock value 
    print ('Getting a list of all the manufacturers products')
    manufacturer_list = get_manufacturers_products(manufacturer_names)
    
    print ('Failed to get these manufacturers: {}'.format(Manufacturer.query.all()))
    #create a new background task for getting the stock value from these, with a short delay

    # fill the database with products 
    print ('Creating all the products')
    create_product(products, manufacturer_list, job)
    
def fill_stock(job):
    # fill the missing stock values for products
    products = Product.query.filter_by(stock='Unknown').all()
    
    #get the manufacturer names from database
    manu_names = []
    m_query = Manufacturer.query.filter_by(received=False).all()
    if m_query:
        for item in m_query:
            manu_names.append(item.name)
    manu_list = get_manufacturers_products(manu_names)
    
    #could add some update boolean to the function, so don't have to have this twice
    #create_product(products, manu_list, job)
    
    count = 0
    for product in products:
        instock = get_stock(product.id, manu_list)
        product.stock = instock
        count += 1
        job.meta['progress'] = 100.0 * count / len(products)
        job.save_meta()
        print(job.meta['progress'])
    
    job.meta['progress'] = 100
    job.save_meta()
    print ('Committing products to database')
    db.session.commit()
    
    #check if there are still failed manufacturers in the table and requeue a new job for it, with a delay
  
def get_manufacturers_products(names):
    manu_list = []
    print (names)
    for name in names:
        print('Getting products from {}.'.format(name))
        headers = {'x-force-error-mode': 'all'}
        url = 'https://bad-api-assignment.reaktor.com/v2/availability/' + name
        
        # if name == 'okkau':
            # m = requests.get(url, headers=headers)
        # else:
            # m = requests.get(url)
        m = requests.get(url)
        print ('m.text length: {}'.format(len(m.text)))
        m_json = json.loads(m.text)
        m_query = Manufacturer.query.filter_by(name = name).first()
        
        if m_json['response'] != '[]':
            m_etag = Caches(id=m.headers['Etag'], name=name)
            db.session.add(m_etag)
            manu_list.extend(m_json['response'])
            if m_query.received != True:
                m_query.received = True
        else:
            m_query.received = False
    return manu_list
    
def create_product(products, manu_list, job):
    count = 0
    for product in products:
        instock = get_stock(product['id'], manu_list)
        p = Product(id=product['id'], category=product['type'], name=product['name'], manufacturer=product['manufacturer'], stock=instock, price=product['price'])
        db.session.add(p)
        #db.session.commit() #slows down the process extremily
        count += 1
        job.meta['progress'] = 100.0 * count / len(products)
        job.save_meta()
        print(job.meta['progress'])
    
    job.meta['progress'] = 100
    job.save_meta()
    print ('Committing products to database')
    db.session.commit()
  
def get_stock(product_id, manufacturer_list):
    #print(len(manufacturer_list))
    manu_fail = Manufacturer.query.all()
    for manufacturer in manufacturer_list:
        if manufacturer not in manu_fail:
            #print('getting stock')
            #print(manufacturer)
            if product_id == manufacturer['id'].lower():
                stock = html_parse(manufacturer['DATAPAYLOAD'])
                return stock
        else:
            return 'Unknown Failure'
    return 'Unknown'
    
def html_parse(line):
    soup = BeautifulSoup(line, 'html.parser')
    tag = soup.instockvalue
    return tag.string