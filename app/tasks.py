import time, sys, requests, json
from rq import get_current_job
from app import create_app, db
from app.models import Task, Product
from app.build_database import init_db, get_stock, html_parse

app = create_app()
app.app_context().push()

def create_db():
    try:
        job = get_current_job()
        print('Creating databases')
        task = Task(id=job.get_id(), name='Create db')
        db.session.add(task)
        init_db(Product, job)
        
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
        print(job.meta['progress'])
        time.sleep(1)
    job.meta['progress'] = 100
    job.save_meta()
    print('Task completed')