class Config():
    SECRET_KEY = '6d8c5faf6f00d8ed8e52c74e1cbe695115c6d18e5acd7ec7626b016408580cae'

class developmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'alfonso'
    MYSQL_DB = 'dgt_app'

class productionConfig(Config):
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'alfonso'
    MYSQL_DB = 'dgt_app'


config = {
    'development': developmentConfig,
    'production': productionConfig
}

