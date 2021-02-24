from flask import render_template, jsonify, request, redirect, session, url_for, current_app
from app import db
from app.models import Product, get_tasks_in_progress
from app.build_database import init_db, empty_db
from app.main import bp


#for checking how long it was been since last visit/build, if more than 5 minutes. Would call database to update itself. Would need to store last visit time. Some kind of a timer might be simpler/better, especially if you don't know the exact refresh time? Otherwise would have to ping it more often to see if it has changed.
@bp.before_request
def before_request():
    #check if the Product database exits/has anything, if not initiate it with build_database init_db(). 
    #Need to start this is a background task for it to work on deploy
    products = Product.query.all()
    if len(products) == 0:
        #init_db(Product)
        #job = current_app.task_queue.enqueue(func=init_db(Product))
        job = current_app.task_queue.enqueue('app.tasks.create_db')
    #have to also check for creation time and based on that re-create it or update it. 
    #with rq jobs can actually schedule them to run at intervals
    
    #using this temporarely for forcing the re-creation of the databases
    #init_db(Product)
    #job = current_app.task_queue.enqueue(init_db(Product))
    #job = current_app.task_queue.enqueue('app.tasks.example', 23)
    # if session['job'] is None:
        # session['job'] = 0
    job = current_app.task_queue.enqueue('app.tasks.create_db')
    #session['job'] = job.get_id()
    
    pass

#trying a one page solution for now, instead of having separate pages for all three categories
#could just as well make three different versions of the same page for different categories, but extra work for no reason?
@bp.route('/')
@bp.route('/index')
def index():
    if 'category' in session:
        category = session['category']
    else:
        category = 'Gloves'


    #make sure the product database is populated and then pass it on to the render_template with the selected category
    products = Product.query.filter_by(category=category.lower()).all()
    
    return render_template('index.html', title='Reaktor Warehouse', category=category, products=products, tasks=get_tasks_in_progress())

#change category, redirect to index. Don't think I need these, g.var for category might be simpler.
@bp.route('/switch_category/<string:category>')
def switch_category(category):
    session['category'] = category
    return redirect(url_for('main.index'))

