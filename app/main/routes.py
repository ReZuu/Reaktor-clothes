from flask import render_template, jsonify, request, redirect, session, url_for, current_app, g
from app import db
from app.models import Product, Task
from app.build_database import init_db
from app.main import bp
from rq import get_current_job
from datetime import timedelta


@bp.before_app_first_request
def before_app_first_request():
    #should check if there are some previous tasks in queue in RQ, as on local that seems to be a possibility. And flush them out. 
    q_jobs = current_app.task_queue.jobs
    print('q_jobs: {}'.format(q_jobs))
    current_app.task_queue.empty() 
    #this doesn't help since the RQ worker needs to be on and it starts doing the queue immediately, when it gets turned on.    
    
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
    create(False)
                
@bp.before_request
def before_request():
    
    # try to get current task, it might be locked at certain points
    try:
        tasks = Task.query.filter_by(id=session['tasks']).first()
        if tasks:
            if tasks.name == 'CreateDb' and tasks.complete == True and session['task_name'] != 'DONE':
                session['refresh'] = True
            job = current_app.task_queue.fetch_job(session['tasks'])
            if session['task_name'] == 'CreateDb' and job.get_status() == 'Finished':
                session['refresh'] = True
    except:
        #if locked use the job id and name in session 
        job = current_app.task_queue.fetch_job(session['tasks'])
        if session['task_name'] == 'CreateDb' and job.get_status() == 'Finished':
            session['refresh'] = True

    try:
        tasks = Task.query.filter_by(complete=False).first()
        print('current task is: {}'.format(tasks.name))
        session['tasks'] = tasks.id
        session['task_name'] = tasks.name
    except:
        pass

    
    if session['startup'] == True:
        session['refresh'] = True
    print('refresh is: {}'.format(session['refresh']))


#trying a one page solution for now, instead of having separate pages for all three categories
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
    print ('recreate : {}'.format(recreate))

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

#change category, redirect to index. Don't think I need these, g.var for category might be simpler.
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
    if job:
        if refresh == True:
            session['refresh'] = False
            session['startup'] = False
            session['task_name'] = 'DONE'
        return jsonify({
            'id': job.id,
            'data': int(job.meta['progress']),
            'refresh': refresh})
    else:
        return jsonify({
            'id': 0,
            'data': 0,
            'refresh': refresh})
            
@bp.route('/recreate')
def recreate():
    # should just stop all current tasks and empty the queue first?
    create(False)

def create(voluntary):
    q_jobs = current_app.task_queue.jobs
    print('q_jobs: {}'.format(q_jobs))
    current_app.task_queue.empty() 
    print('queueing database initialization')
    if voluntary == False:
        session['recreate'] = False
        rq_job = current_app.task_queue.enqueue('app.tasks.create_db')
        session['refresh'] = True
        session['startup'] = True
    else:
        #flash a message with link to update? 
        #session['recreate'] = True
        #session['refresh'] = True
        pass
        #cause an event for ajax to refresh the flash msg?

#RQ sometimes doesn't start the scheduled jobs, could be an issue in RQ_win?   
def update():
    print('queueing an update job')
    # don't want to do it immediately since, the API will probably take a moment to work correctly anyway
    rq_job = current_app.task_queue.enqueue_in(timedelta(seconds=5), 'app.tasks.update_db')
    
def caches():
    print('queueing a cache checking job')
    #for testing using less time than should, but considering the 5 minute cache time. Every 2.5 (150 seconds) mins might be reasonable? or even slower.
    rq_job = current_app.task_queue.enqueue_in(timedelta(seconds=15), 'app.tasks.check_caches')
    
    q_jobs = current_app.task_queue.jobs
    print('q_jobs: {}'.format(q_jobs)) 
    # was returning [] even though a task was just added before it
    # could be that something was just stuck in the RQ_win settings etc, as restarting the console that I'm running it in started showing something in this...
