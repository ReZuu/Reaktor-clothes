from flask import render_template, jsonify, request, redirect
from app import db, app
from app.models import Product
from app.build_database import init_db

#for checking how long it was been since last visit/build, if more than 5 minutes. Would call database to update itself. Would need to store last visit time. Some kind of a timer might be simpler/better, especially if you don't know the exact refresh time? Otherwise would have to ping it more often to see if it has changed.
@app.before_request
def before_request():
    #check if the Product database exits, if not initiate it with build_database init_db()
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
    #check which category is checked and render page accordingly. g.var for this should work perfectly
    category = "Gloves"
    
    #make sure the product database is populated and then pass it on to the render_template
    products = Product.query.all()
        
    # products = [
        # {"id":"4826cde687cf433f527cec34","type":"gloves","name":"DALKOL BRIGHT FLOWER","color":["green"],"price":36,"manufacturer":"abiplos"},
        # {"id":"e1d8c2ac13d739789eba2cab","type":"gloves","name":"ÖISAKUP GREEN NORMAL","color":["white"],"price":739,"manufacturer":"niksleh"},
        # {"id":"35b1ad69b78aa704c228317","type":"beanies","name":"KOLDALUP ANIMAL FANTASY","color":["blue"],"price":97,"manufacturer":"abiplos"},
        # {"id":"5c5055eee6b16cea65a747eb","type":"beanies","name":"JEKOL TYRANNUS","color":["blue"],"price":39,"manufacturer":"umpante"},
        # {"id":"8933428407db522031c7","type":"facemasks","name":"ILAKMO LIGHT BRIGHT","color":["white"],"price":78,"manufacturer":"laion"},
        # {"id":"88b60730ece62ce0b288600","type":"facemasks","name":"REVDALLEA SWEET","color":["white"],"price":108,"manufacturer":"laion"}
    # ]
    
    return render_template('index.html', title='Reaktor Warehouse', category=category, products=products)

#change category, redirect to index. Don't think I need these, g.var for category might be simpler.
@app.route('/switch_category')
def switch_category():
    pass

