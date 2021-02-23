from flask import render_template, jsonify, request, redirect, session, url_for
from app import db, app
from app.models import Product
from app.build_database import init_db


#for checking how long it was been since last visit/build, if more than 5 minutes. Would call database to update itself. Would need to store last visit time. Some kind of a timer might be simpler/better, especially if you don't know the exact refresh time? Otherwise would have to ping it more often to see if it has changed.
@app.before_request
def before_request():
    #check if the Product database exits/has anything, if not initiate it with build_database init_db()
    #g.category = 'Gloves'
    products = Product.query.all()
    if len(products) == 0:
        init_db(Product)
    #otherwise check for creation/update time and update the database
    pass

#trying a one page solution for now, instead of having separate pages for all three categories
#could just as well make three different versions of the same page for different categories, but extra work for no reason?
@app.route('/')
@app.route('/index')
def index():
    if 'category' in session:
        category = session['category']
    else:
        category = 'Gloves'


    #make sure the product database is populated and then pass it on to the render_template
    #products = Product.query.all()
    products = Product.query.filter_by(category=category.lower()).all()
    
    
    return render_template('index.html', title='Reaktor Warehouse', category=category, products=products)

#change category, redirect to index. Don't think I need these, g.var for category might be simpler.
@app.route('/switch_category/<string:category>')
def switch_category(category):
    session['category'] = category
    return redirect(url_for('index'))

