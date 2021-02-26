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
    #should maybe check if there are some previous tasks in queue in RQ, as on local that seems to be a possibility. And flush them out. 
    q_jobs = current_app.task_queue.jobs
    print('q_jobs: {}'.format(q_jobs))
    current_app.task_queue.empty() #this doesn't help since the RQ worker needs to be on and it starts doing the queue immediately
    
    #job = current_app.task_queue.enqueue('app.tasks.example', 23)
    #rq_job = current_app.task_queue.enqueue('app.tasks.create_db')
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

    # try to get products table, it might be locked in certain points
    try:
        products = Product.query.filter_by(category=category.lower()).all()
    except:
        products = []
    # try to get current task, it might be locked in certain points
    try:
        tasks = Task.query.filter_by(complete=False).first()
    except:
        tasks = []
        
    try:
        test = current_app.task_queue.fetch_job(tasks['id'])
        print(test.id)
    except:
        pass
        
    #tasks sometimes becomes None during the whole process...
    # while updating, it is found again as complete
    # tasks 
    if tasks:
        print('task progress: {}'.format (tasks.get_progress()))
        if tasks.name == 'CacheCheck':
            tasks = []
    print('all tasks: {}'.format (Task.query.all()))
    
    return render_template('index.html', title='Reaktor Warehouse', category=category, products=products, tasks=tasks)

#change category, redirect to index. Don't think I need these, g.var for category might be simpler.
@bp.route('/switch_category/<string:category>')
def switch_category(category):
    session['category'] = category
    g.category = category
    return redirect(url_for('main.index'))

@bp.route('/progress')
def progress():
    print('progress is being called')
    jobid = request.args.get('jobid', type=str)
    print('jobid from ajax: {}'.format(jobid))
    if jobid:
        job = Task.query.filter_by(id=jobid).first()
        print('job progress in ajax')
        print(job.get_progress())
        
        return jsonify({
            'name': job.name,
            'data': job.get_progress()})

def create(voluntary):
    print('queueing database initialization')
    if voluntary == False:
        rq_job = current_app.task_queue.enqueue('app.tasks.create_db')
    else:
        #flash a message with link to update? 
        #rq_job = current_app.task_queue.enqueue('app.tasks.create_db')
        pass
    
def update():
    print('queueing an update job')
    # don't want to do it immediately since, the API will probably take a moment to work correctly anyway
    rq_job = current_app.task_queue.enqueue_in(timedelta(seconds=10), 'app.tasks.update_db')
    
def caches():
    print('queueing a cache checking job')
    #for testing using less time than should, but considering the 5 minute cache time. Every 2.5 (150 seconds) mins might be reasonable? or even slower.
    rq_job = current_app.task_queue.enqueue_in(timedelta(seconds=15), 'app.tasks.check_caches')
    q_jobs = current_app.task_queue.jobs
    print('q_jobs: {}'.format(q_jobs)) # is returning [] even though a task was just added before it
    #should first check if there is already a cache job queued, as not to spam them
    