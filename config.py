import datetime


class Config(object):
    ENV = 'production'
    SECRET_KEY = None
    SESSION_COOKIE_SECURE = True
    DEBUG = False
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=31)


    USE_SESSION_FOR_NEXT = False

    UPLOADS_FOLDER = None
    IMAGES_FOLDER = None
    AUDIOS_FOLDER = None
    ALLOWED_IMAGES_EXTENSIONS = None
    ALLOWED_AUDIOS_EXTENSIONS = None


class DevelopmentConfig(Config):
    ENV = 'development'
    SECRET_KEY = 'Yep_this_supose_to_be_a_secret'
    SESSION_COOKIE_SECURE = False
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=1)

    USE_SESSION_FOR_NEXT = False

    UPLOADS_FOLDER = '/home/wachadev/Programming/Python/brocat/brocat/uploads/'
    IMAGES_FOLDER = UPLOADS_FOLDER + 'images/'
    AUDIOS_FOLDER = UPLOADS_FOLDER + 'audios/'
    ALLOWED_IMAGES_EXTENSIONS = frozenset({'jpg', 'jpeg', 'svg', 'png'})
    ALLOWED_AUDIOS_EXTENSIONS = frozenset({'mp3', 'wav', 'ogg', 'oga', 'flac'})


class ProductionConfig(Config):
    ENV = 'production'
    SECRET_KEY = b'60a5a167df9ff636d318c374aa76ca94dfc163bd7ad9e489'
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    pass
