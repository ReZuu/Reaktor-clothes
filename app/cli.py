import os
import click

def register(app):
    @app.cli.group()
    def database():
        pass
        
    @database.command()
    def init():
        pass
        
    @database.command()
    def update():
        pass