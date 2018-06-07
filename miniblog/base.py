import os
from . import app
from .config import TestConfig, ProdConfig
from .database import initApp
from .auth import blueprint

app.config.from_object(TestConfig)

if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path)

initApp()

app.register_blueprint(blueprint)

@app.route('/config')
def getConfig():
    return str(dict(app.config))


@app.route('/index')
def index():
    return "Hello World!!"
