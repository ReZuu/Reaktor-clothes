from flask import render_template, jsonify, request
from app import db, app


@app.route('/')
@app.route('/index')
def index():
    #check which category is checked and render page accordingly
    category = "Gloves"
    products = [
        {"id":"4826cde687cf433f527cec34","type":"gloves","name":"DALKOL BRIGHT FLOWER","color":["green"],"price":36,"manufacturer":"abiplos"},
        {"id":"e1d8c2ac13d739789eba2cab","type":"gloves","name":"ÖISAKUP GREEN NORMAL","color":["white"],"price":739,"manufacturer":"niksleh"},
        {"id":"35b1ad69b78aa704c228317","type":"beanies","name":"KOLDALUP ANIMAL FANTASY","color":["blue"],"price":97,"manufacturer":"abiplos"},
        {"id":"5c5055eee6b16cea65a747eb","type":"beanies","name":"JEKOL TYRANNUS","color":["blue"],"price":39,"manufacturer":"umpante"},
        {"id":"8933428407db522031c7","type":"facemasks","name":"ILAKMO LIGHT BRIGHT","color":["white"],"price":78,"manufacturer":"laion"},
        {"id":"88b60730ece62ce0b288600","type":"facemasks","name":"REVDALLEA SWEET","color":["white"],"price":108,"manufacturer":"laion"}
    ]
    
    return render_template('index.html', title='Reaktor Warehouse', category=category, products=products)

@app.route('/<category>')
def get_category():
    #get product listing based on category
    #https://bad-api-assignment.reaktor.com/v2/products/<category>
    pass
    
@app.route('/<manufacturer>')
def get_manufacturer():
    #get manufacturer availability
    #https://bad-api-assignment.reaktor.com/v2/aivalibility/<manufacturer>
    pass