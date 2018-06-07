from . import app


class BaseConfig:
    DEBUG = True
    DEVELOPMENT = True


class TestConfig(BaseConfig):
    SECRET_KEY = "test"
    DATABASE = app.instance_path + '/flask.sqlite'


class ProdConfig(BaseConfig):
    SECRET_KEY = "are-you-fucking-retarded"
