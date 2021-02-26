import time, sys, requests, json
from rq import get_current_job
from app import create_app, db
from app.models import Task, Product, Caches, Manufacturer
from app.build_database import init_db, fill_stock
from app.main.routes import update, caches, create
from flask import g, current_app

app = create_app()
app.app_context().push()

# rqworker --with-scheduler -w rq_win.WindowsWorker warehouse-tasks

def create_db():
    try:
        job = get_current_job()
        print('Creating databases')
        print('Job id: {}'.format(job.id))
        task = Task(id=job.get_id(), name='CreateDb', description='Creating product databases - progress: ', complete=False)
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
        manu_fails = Manufacturer.query.filter_by(received=False).all()
        if manu_fails:
            print ('manu fails are: {}'.format(manu_fails))
            update()
        caches()
    
def update_db():
    try:
        job = get_current_job()
        print('Updating databases')
        print('Current job: {}'.format(job.id))
        task = Task(id=job.get_id(), name='UpdatingDb', description='Updating product databases - progress: ', complete=False)
        _set_task_progress(0)
        
        db.session.add(task)
        db.session.commit()
        fill_stock(job)
    except:
        print('Unhandled exception on update db')
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
        _set_task_progress(100)
    finally:  
        print('Finished updating databases')
        _set_task_progress(100)
        #at this point would provide the user with an option to refresh the page, instead of forcing the reload
        manu_fails = Manufacturer.query.filter_by(received=False).all()
        if manu_fails:
            print ('manu fails are: {}'.format(manu_fails))
            update()
        
def check_caches():
    try:
        isUpToDate = True
        print ('Checking cache versions')
        job = get_current_job()
        task = Task(id=job.get_id(), name='CacheCheck', description='Checking server caches for newer versions', complete=False)
        _set_task_progress(0)
        db.session.add(task)
        db.session.commit()
        
        print('cache task commited')
        #get headers Etag to check for cache version
        r_gloves = requests.get('https://bad-api-assignment.reaktor.com/v2/products/gloves')
        gloves_query = Caches.query.filter_by(name='Gloves').first()
        if r_gloves.headers['Etag'] != gloves_query.id:
            #it needs to be updated
            isUpToDate = False
            
        r_beanies = requests.get('https://bad-api-assignment.reaktor.com/v2/products/beanies')
        beanies_query = Caches.query.filter_by(name='Beanies').first()
        if r_beanies.headers['Etag'] != beanies_query.id:
            #it needs to be updated
            isUpToDate = False
            
        r_facemasks = requests.get('https://bad-api-assignment.reaktor.com/v2/products/facemasks')
        facemasks_query = Caches.query.filter_by(name='Facemasks').first()
        if r_facemasks.headers['Etag'] != facemasks_query.id:
            #it needs to be updated
            isUpToDate = False
        
        print('cache products checked')
        manu_names = Manufacturer.query.all()
        #this is only checking for failed manufacturers, need to add all of the names to the list to be sure
        for manu in manu_names:
            print('checking cache for {}'.format(manu.name))
            url = 'https://bad-api-assignment.reaktor.com/v2/availability/' + manu.name
            m_request = requests.get(url)
            m_json = json.loads(m_request.text)
            
            if m_json['response'] != '[]':
                cache_query = Caches.query.filter_by(name=manu.name).first()
                if m_request.headers['Etag'] != cache_query.id:
                    #it needs to be updated
                    isUpToDate = False
        print('manufacturers checked')
    except:
        print('Unhandled exception on checking caches')
        _set_task_progress(100)
    finally:
        print('Finished checking caches')
        _set_task_progress(100)
        if isUpToDate == False:
            print('There are new products available')
            #need to initialize the database again, but this should be voluntary?
            create(True)
        else:
            print('Everything is up to date')
            #caches()

def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        
        if progress >= 100:
            task.complete = True
        db.session.commit()
   
def example(seconds=23):
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