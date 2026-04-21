import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from flask_bootstrap import Bootstrap5

db = SQLAlchemy()                              # Created, but NOT bound to any app yet
login_manager = LoginManager()
login_manager.login_view = 'auth.login'        # Blueprint-prefixed route name (from Part 4/5)
migrate = Migrate()
bootstrap = Bootstrap5()

def create_app(config_class=Config):
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.decks.routes import bp as decks_bp
    app.register_blueprint(decks_bp, url_prefix='/decks')

    from app.main.routes import bp as main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app

from app import models