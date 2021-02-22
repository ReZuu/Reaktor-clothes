from app import db, app
from app.models import Product, Manufacturer


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Product': Product, 'Manufacturer': Manufacturer}

#app = create_app()