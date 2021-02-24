from flask import render_template, jsonify, request, redirect, session, url_for, current_app, g
from app import db
from app.models import Product, get_tasks_in_progress
from app.build_database import init_db
from app.main import bp

#for checking how long it was been since last visit/build, if more than 5 minutes. Would call database to update itself. Would need to store last visit time. Some kind of a timer might be simpler/better, especially if you don't know the exact refresh time? Otherwise would have to ping it more often to see if it has changed.
@bp.before_app_first_request
def before_app_first_request():
    #Would ideally check for creation time and based on that re-create it or update it. 
    #with rq jobs can actually schedule them to run at intervals
    

    #init_db(Product)
    #job = current_app.task_queue.enqueue(init_db(Product))
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

    #make sure the product database is populated and then pass it on to the render_template with the selected category
    products = Product.query.filter_by(category=category.lower()).all()
    
    return render_template('index.html', title='Reaktor Warehouse', category=category, products=products, tasks=get_tasks_in_progress())

#change category, redirect to index. Don't think I need these, g.var for category might be simpler.
@bp.route('/switch_category/<string:category>')
def switch_category(category):
    session['category'] = category
    g.category = category
    return redirect(url_for('main.index'))

