from flask import Flask


def create_app():
    app = Flask(__name__)
    
    with app.app_context():
        if app.config['ENV'] == 'development':
            app.config.from_object('config.DevelopmentConfig')
        elif app.config['ENV'] == 'production':
            app.config.from_object('config.ProductionConfig')
        else:
            app.config.from_object('config.TestingConfig')

        from brocat.database import init_db
        init_db()

        from flask_login import LoginManager
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'main.login'
        login_manager.login_message = 'You need to login first.'

        from brocat.models import User
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        from brocat.views import main as main_blueprint
        app.register_blueprint(main_blueprint)

    return app
