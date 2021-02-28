from flask import render_template, jsonify, request, redirect, session, url_for, current_app, g
from app import db
from app.models import Product, Task
from app.build_database import init_db
from app.main import bp
from rq import get_current_job
from datetime import timedelta


@bp.before_app_first_request
def before_app_first_request():
    print('this should only get printed once') #deploy does it twice
    #should check if there are some previous tasks in queue in RQ, as on local that seems to be a possibility. And flush them out. 
    q_jobs = current_app.task_queue.jobs
    print('q_jobs: {}'.format(q_jobs))
    current_app.task_queue.delete(delete_jobs=True)
     
    
    session['recreate'] = False    
    session['refresh'] = False
    session['startup'] = True
    if 'category' not in session:
        session['category'] = 'Gloves'
    session['task_name'] = 'Unknown'
    session['tasks'] = '0'
    session['update'] = False
    
    #otherwise it would still show old "cached" tables, even though the database is being created in the background
    #db.drop_all()
    #db.create_all()
    #does this cause more harm than good?
    
    #calling the initial creation of databases with 'False' in order to force the database creation for the first request of the app
    print ('Starting the initial database creation')
    create(False)
                
@bp.before_request
def before_request():
    
    # try to get current task, it might be locked at certain points
    try:
        tasks = Task.query.filter_by(id=session['tasks']).first()
        if tasks:
            if tasks.name == 'CreateDb' and tasks.complete == True and session['task_name'] != 'DONE':
                session['refresh'] = True
            if tasks.name == 'CacheCheck' and tasks.complete == True:
                #print('Cache check is done')
                #print(tasks)
                if tasks.recreate == True:
                    session['recreate'] = True
    except:
        #if locked use the job id and name in session 
        job = current_app.task_queue.fetch_job(session['tasks'])
        if session['task_name'] == 'CreateDb' and job.get_status() == 'Finished':
            session['refresh'] = True
        if session['task_name'] == 'CacheCheck' and job.get_status() == 'Finished':
            pass
    try:
        tasks = Task.query.filter_by(complete=False).first()
        print('current task is: {}'.format(tasks.name))
        session['tasks'] = tasks.id
        session['task_name'] = tasks.name
    except:
        pass

    
    if session['startup'] == True:
        session['refresh'] = True
    #print('refresh is: {}'.format(session['refresh']))
    
    #could do a periodic check here to see if a job is stuck in queue?
    q_jobs = current_app.task_queue.jobs
    if q_jobs:
        print(q_jobs)
        for job in q_jobs:
            print(job)

#trying a one "page" solution for now, instead of having separate pages for all three categories
#could just as well make three different endpoints for all the categories, which currently just redirect to this instead
@bp.route('/')
@bp.route('/index')
def index():
    if 'category' in session:
        category = session['category']
    else:
        category = 'Gloves'
    #this might be pointless atm
    #print ('category: {}'.format(category))
        
    recreate = session['recreate']
    #print ('recreate : {}'.format(recreate))

    # try to get products table, it might be locked at certain points
    try:
        products = Product.query.filter_by(category=category.lower()).all()
    except:
        products = []
    # try to get current task, it might be locked at certain points
    try:
        tasks = Task.query.filter_by(complete=False).first()
        if tasks:
            session['tasks'] = tasks.id
            session['task_name'] = tasks.name
            if tasks.name == 'CacheCheck':
                tasks = []
    except:
        tasks = []
        print('last task id: {}'.format(session['tasks']))
        job = current_app.task_queue.fetch_job(session['tasks'])
        if job:
            print('progress: {}'.format(job.meta['progress']))

    #tasks sometimes becomes None during the whole process, due to database being locked. 
    #should maybe save a reference to it elsewhere (like session) and when it fails, load it from there? Thus having at least the old values/data instead of nothing
    # another option seems to be committing more often. But it slows down the whole process ridiculously. So rather suffer the missing flash/info caused by locked db
    # while updating, it is found again as complete
    
    
    try:
        print('all tasks: {}'.format (Task.query.all()))
    except:
        pass
    
    return render_template('index.html', title='Reaktor Warehouse', category=category, products=products, tasks=tasks, recreate=recreate)

#change category, redirect to index
@bp.route('/switch_category/<string:category>')
def switch_category(category):
    session['category'] = category
    return redirect(url_for('main.index'))
    
@bp.route('/gloves')
def gloves():
    return redirect(url_for('main.switch_category', category='Gloves'))
    
@bp.route('/facemasks')
def facemasks():
    return redirect(url_for('main.switch_category', category='Facemasks'))
    
@bp.route('/beanies')
def beanies():
    return redirect(url_for('main.switch_category', category='Beanies'))

@bp.route('/progress')
def progress():
    #print('progress is being called from ajax')
    job = current_app.task_queue.fetch_job(session['tasks'])
    refresh = session['refresh']
    recreate = session['recreate']
    #recreate = True
    if job:
        if refresh == True:
            session['refresh'] = False
            session['startup'] = False
            session['task_name'] = 'DONE'
        return jsonify({
            'id': job.id,
            'data': int(job.meta['progress']),
            'refresh': refresh,
            'recreate': recreate})
    else:
        return jsonify({
            'id': 0,
            'data': 0,
            'refresh': refresh,
            'recreate': recreate})

#this could be abused, would ideally need a better solution for this     
#but also for this purpose it could be run to see how long it takes to get up and running and that everything still works after recreate       
@bp.route('/recreate')
def recreate():
    create(False)
    return redirect(url_for('main.index'))

def create(voluntary):
    q_jobs = current_app.task_queue.jobs
    print('q_jobs: {}'.format(q_jobs))
    if q_jobs:
        for job in q_jobs:
            job.cancel()
    current_app.task_queue.empty()
    current_app.task_queue.delete(delete_jobs=True)
    print('queueing database initialization')
    if voluntary == False:
        session['recreate'] = False
        rq_job = current_app.task_queue.enqueue('app.tasks.create_db', at_front=True)

#RQ sometimes doesn't start the scheduled jobs, could be an issue in RQ_win?
#need a solution for this, other than restarting RQ
#hard to reproduce
def update():
    print('queueing an update job')
    # don't want to do it immediately since, the API will probably take a moment to work correctly anyway, but don't want to wait too long. Also wondering if starting it too fast might be causing it to get stuck?
    rq_job = current_app.task_queue.enqueue_in(timedelta(seconds=7), 'app.tasks.update_db', at_front=True)
    
def caches():
    print('queueing a cache checking job')
    #for testing using less time than should, but considering the 5 minute cache time. Every 2.5 (150 seconds) mins might be reasonable? or even slower. 2.5 to 5 minutes will always check the cache once, faster than 2.5 will check the same cache more than once
    rq_job = current_app.task_queue.enqueue_in(timedelta(seconds=150), 'app.tasks.check_caches')
    
    q_jobs = current_app.task_queue.jobs
    print('q_jobs: {}'.format(q_jobs)) 
    # was returning [] even though a task was just added before it
    # could be that something was just stuck in the RQ_win settings etc, as restarting the console that I'm running it in started showing something in this...
