import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'B\xb2?.\xdf\x9f\xa7m\xf8\x8a%,\xf7\xc4\xfa\x91'

    """ Qlicknnpay online payment details of production"""
    MERCHANT_ID = '10457'
    API = 'vhXWhuQZ8rbW'

    """ Qlicknnpay online payment details of sandbox"""
    # MERCHANT_ID = '10195'
    # API = 'vJsYt2TuZjqk'
    

class ProductionConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/geniuseduonline?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE=20
    SQLALCHEMY_POOL_TIMEOUT=600

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Onmobile@localhost/geniuseduonline?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:janmejay@localhost/geniusedu'
    SQLALCHEMY_TRACK_MODIFICATIONS = False