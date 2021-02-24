import time, sys, requests, json
from rq import get_current_job
from app import create_app, db
from app.models import Task, Product
from app.build_database import init_db, fill_stock
from flask import g

app = create_app()
app.app_context().push()

def create_db():
    try:
        job = get_current_job()
        print('Creating databases')
        task = Task(id=job.get_id(), name='Create db')
        db.session.add(task)
        init_db(job)
        
    except:
        print('Unhandled exception on creating db')
        g.isDbCreating = False
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        print('Finished creating databases')
        g.isDbCreating = False
        _set_task_progress(100)
    
def update_db():
    try:
        g.isDbUpdating = True
        job = get_current_job()
        print('Updating databases')
        task = Task(id=job.get_id(), name='Updating db')
        db.session.add(task)
        fill_stock(job)
    except:
        print('Unhandled exception on update db')
        g.isDbUpdating = False
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:  
        print('Finished updating databases')
        g.isDbUpdating = False
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