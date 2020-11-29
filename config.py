import datetime


class Config(object):
    ENV = 'production'
    SECRET_KEY = None
    SESSION_COOKIE_SECURE = True
    DEBUG = False


class DevelopmentConfig(Config):
    ENV = 'development'
    SECRET_KEY = r'b$2b$12$j7IQog.NYRWgjfRB4j5Fxu'
    SESSION_COOKIE_SECURE = False
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=1)


class ProductionConfig(Config):
    pass


class TestingConfig(Config):
    pass
