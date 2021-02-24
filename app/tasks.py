import time, sys, requests, json
from rq import get_current_job
from app import create_app, db
from app.models import Task, Product
from app.build_database import init_db, get_stock, html_parse

app = create_app()
app.app_context().push()

# could move the database creation entirely into these?
def create_db():
    try:
        job = get_current_job()
        print('Creating databases')
        #init_db(Product)products = []
        
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
         
        manufacturer_names = []
        for product in products:
            if len(manufacturer_names) != 0:
                if product['manufacturer'] not in manufacturer_names:
                    manufacturer_names.append(product['manufacturer'])
            else:
                manufacturer_names.append(product['manufacturer'])
        
        print ('testing')
        manufacturer_list = []
        manu_failure = ['testcase']
        item_count = 0
        for manufacturer in manufacturer_names:
            url = 'https://bad-api-assignment.reaktor.com/v2/availability/' + manufacturer
            
            m = requests.get(url)
            m_json = json.loads(m.text)
            
            if m_json['response'] != '[]':
                manufacturer_list.extend(m_json['response'])
                item_count += len(m_json['response'])
            else:
                manu_failure.append(manufacturer)
                
        db.drop_all()
    
        #create a new fresh database
        db.create_all()

        # fill the database with products 
        count = 0
        for product in products:
            instock = get_stock(product['id'], manufacturer_list, manu_failure)
            #instock = #find the stock availability by checking manufacturers
            p = Product(id=product['id'], category=product['type'], name=product['name'], manufacturer=product['manufacturer'], stock=instock, price=product['price'])
            db.session.add(p)
            count += 1
            job.meta['progress'] = 100.0 * count / len(products)
            job.save_meta()
            print(job['progress'])
    except:
        print('Unhandled exception')
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        print('Finished creating databases')
        _set_task_progress(100)
    
def update_db():
    try:
    print('Updating databases')
    except:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:  
        print('Finished updating databases')
        _set_task_progress(100)

def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        
        if progress >= 100:
            task.complete = True
        db.session.commit()
   
def example(seconds):
    job = get_current_job()
    print('Starting task')
    for i in range(seconds):
        job.meta['progress'] = 100.0 * i / seconds
        job.save_meta()
        print(i)
        time.sleep(1)
    job.meta['progress'] = 100
    job.save_meta()
    print('Task completed')