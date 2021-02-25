from flask import render_template, jsonify, request, redirect, session, url_for, current_app, g
from app import db
from app.models import Product, Task
from app.build_database import init_db
from app.main import bp


@bp.before_app_first_request
def before_app_first_request():
    #should maybe check if there are some previous tasks in queue in RQ, as on local that seems to be a possibility. And flush them out. 
    

    #job = current_app.task_queue.enqueue('app.tasks.example', 23)
    rq_job = current_app.task_queue.enqueue('app.tasks.create_db')


#trying a one page solution for now, instead of having separate pages for all three categories
#could just as well make three different versions of the same page for different categories, but extra work for no reason?
@bp.route('/')
@bp.route('/index')
def index():
    if 'category' in session:
        category = session['category']
    else:
        category = 'Gloves'

    #category = g.category # doesn't seem to work

    
    products = Product.query.filter_by(category=category.lower()).all()
    tasks = Task.query.filter_by(complete=False).first()
    if tasks:
        print('task progress: {}'.format (tasks.get_progress()))
    
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
    jobid = request.args.get('jobid', type=string)
    task = Task.query.filter_by(id=jobid).first()
    if task:
        return jsonify(task.get_progress())
    return jsonify(50)
    
@bp.route('/progress2')
def progress2():
    jobid = request.values.get('jobid')
    print('progress2 called')
    print(jobid)
    if jobid:
        job = Task.query.filter_by(id=jobid).first()
        print('job progress in ajax')
        print(job.get_progress())
        return jsonify(job.get_progress())
    
@bp.route('/ajax')
def ajax():
    print('ajax polling test')
    
@bp.route('/test')
def test():
    print ('ajax test')
    time = requests.args.get('test', type=string)
    if not time:
        return jsonify({status: 'error: incorrect parameters'})
    val = 50
    return jsonify({status: 'success', data: val})