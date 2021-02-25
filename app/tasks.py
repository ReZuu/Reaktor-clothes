import time, sys, requests, json
from rq import get_current_job
from app import create_app, db
from app.models import Task, Product, Caches, Manufacturer
from app.build_database import init_db, fill_stock
from flask import g

app = create_app()
app.app_context().push()

def create_db():
    try:
        job = get_current_job()
        print('Creating databases')
        task = Task(id=job.get_id(), name='Create db', description='Creating product databases - progress: ')
        _set_task_progress(0)
        
        print ('Cleaning and re-creating databases')
        #clean up old database
        db.drop_all()
        
        #create a new fresh database
        db.create_all()
        
        db.session.add(task)
        db.session.commit()
        init_db(job)
        
    except:
        print('Unhandled exception on creating db')
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
        _set_task_progress(100)
    finally:
        print('Finished creating databases')
        _set_task_progress(100)
        #at this point would want to trigger an event that would cause ajax to reload the page
    
def update_db():
    try:
        job = get_current_job()
        print('Updating databases')
        task = Task(id=job.get_id(), name='Updating db', description='Updating product databases - progress: ')
        _set_task_progress(0)
        
        db.session.add(task)
        fill_stock(job)
    except:
        print('Unhandled exception on update db')
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
        _set_task_progress(100)
    finally:  
        print('Finished updating databases')
        _set_task_progress(100)
        #at this point would provide the user with an option to refresh the page, instead of forcing the reload
        
def check_caches():
    try:
        job = get_current_job()
        _set_task_progress(0)
        #get headers Etag to check for cache version
        r_gloves = requests.get('https://bad-api-assignment.reaktor.com/v2/products/gloves')
        gloves_query = Caches.query.filter_by(name='Gloves').first()
        if r_gloves.headers['Etag'] != gloves_query['id']:
            #it needs to be updated
            pass
            
        r_beanies = requests.get('https://bad-api-assignment.reaktor.com/v2/products/beanies')
        beanies_query = Caches.query.filter_by(name='Beanies').first()
        if r_beanies.headers['Etag'] != beanies_query['id']:
            #it needs to be updated
            pass
            
        r_facemasks = requests.get('https://bad-api-assignment.reaktor.com/v2/products/facemasks')
        facemasks_query = Caches.query.filter_by(name='Facemasks').first()
        if r_facemasks.headers['Etag'] != facemasks_query['id']:
            #it needs to be updated
            pass
            
        manu_names = Manufacturer.query.all()
        for name in manu_names:
            url = 'https://bad-api-assignment.reaktor.com/v2/availability/' + name
            m_request = requests.get(url)
            cache_query = Caches.query.filter_by(name=name).first()
            if m_request.headers['Etag'] != cache_query['id']:
                #it needs to be updated
                pass
    except:
        print('Unhandled exception on checking caches')
        _set_task_progress(100)
    finally:
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
        print(job.meta['progress'])
        time.sleep(1)
    job.meta['progress'] = 100
    job.save_meta()
    print('Task completed')