from flask import render_template, jsonify, request, redirect, session, url_for, current_app, g
from app import db
from app.models import Product, Task
from app.build_database import init_db
from app.main import bp
from rq import get_current_job
from rq.job import Job
from datetime import timedelta


@bp.before_app_first_request
def before_app_first_request():
    #should check if there are some previous tasks in queue in RQ, as on local that seems to be a possibility. And flush them out. 
    q_jobs = current_app.task_queue.jobs
    print('q_jobs: {}'.format(q_jobs))
    current_app.task_queue.empty() 
    #this doesn't help since the RQ worker needs to be on and it starts doing the queue immediately, when it gets turned on. 
    
    #should maybe drop the previous databases here?
    
    #calling the initial creation of databases with 'False' in order to force the database creation for the first request of the app
    create(False)


#trying a one page solution for now, instead of having separate pages for all three categories
#could just as well make three different versions of the same page for different categories, but extra work for no reason?
@bp.route('/')
@bp.route('/index')
def index():
    if 'category' in session:
        category = session['category']
    else:
        category = 'Gloves'

    # try to get products table, it might be locked at certain points
    try:
        products = Product.query.filter_by(category=category.lower()).all()
    except:
        products = []
    # try to get current task, it might be locked at certain points
    try:
        tasks = Task.query.filter_by(complete=False).first()
        session['tasks'] = tasks.id
        if tasks:
            print('task progress: {}'.format (tasks.get_progress()))
        if tasks.name == 'CacheCheck':
            tasks = []
    except:
        tasks = []

    try:
        test = current_app.task_queue.fetch_job(session['tasks'])
        print('test id : {}'.format(test.id))
    except:
        pass
    #tasks sometimes becomes None during the whole process, due to database being locked. 
    #should maybe save a reference to it elsewhere (like session) and when it fails, load it from there? Thus having at least the old values/data instead of nothing
    # another option seems to be committing more often. But it slows down the whole process ridiculously. So rather suffer the missing flash/info caused by locked db
    # while updating, it is found again as complete
    
    
    try:
        print('all tasks: {}'.format (Task.query.all()))
    except:
        pass
    
    return render_template('index.html', title='Reaktor Warehouse', category=category, products=products, tasks=tasks)

#change category, redirect to index. Don't think I need these, g.var for category might be simpler.
@bp.route('/switch_category/<string:category>')
def switch_category(category):
    session['category'] = category
    g.category = category
    return redirect(url_for('main.index'))

@bp.route('/progress')
def progress():
    print('progress is being called from ajax')
    try:
        jobid = Task.query.filter_by(complete=False).first()
    except: 
        jobid = None
    if jobid:
        print('found job task')
        return jsonify({
            'name': jobid.name,
            'id': jobid.id,
            'data': jobid.get_progress()})
    else:
        print('no job task, fetching job')
        job = current_app.task_queue.fetch_job(session['tasks'])
        return jsonify({
            'id': job.id,
            'data': job.meta['progress']})

def create(voluntary):
    print('queueing database initialization')
    if voluntary == False:
        rq_job = current_app.task_queue.enqueue('app.tasks.create_db')
    else:
        #flash a message with link to update? 
        #rq_job = current_app.task_queue.enqueue('app.tasks.create_db')
        pass

#RQ sometimes doesn't start the scheduled jobs, could be an issue in RQ_win?    
def update():
    print('queueing an update job')
    # don't want to do it immediately since, the API will probably take a moment to work correctly anyway
    rq_job = current_app.task_queue.enqueue_in(timedelta(seconds=5), 'app.tasks.update_db')
    
def caches():
    print('queueing a cache checking job')
    #for testing using less time than should, but considering the 5 minute cache time. Every 2.5 (150 seconds) mins might be reasonable? or even slower.
    rq_job = current_app.task_queue.enqueue_in(timedelta(seconds=15), 'app.tasks.check_caches')
    #q_jobs = current_app.task_queue.jobs
    q_jobs = current_app.task_queue
    print('q_jobs: {}'.format(q_jobs)) # is returning [] even though a task was just added before it
    # could be that something was just stuck in the RQ_win settings etc, as restarting the console that I'm running it in started showing something in this...
    