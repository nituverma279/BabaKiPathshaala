from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
# from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import logging
import os
from logging.handlers import RotatingFileHandler
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask('__name__')

csrf = CSRFProtect(app)
app.config.from_object('geniusapp.config.DevelopmentConfig')
db = SQLAlchemy(app,session_options={"expire_on_commit": False})

# migrate = Migrate(app, db)
# manager = Manager(app)
# manager.add_command('db', MigrateCommand)

logging.basicConfig(filename='info.log', level=logging.ERROR)
logHandler = RotatingFileHandler('info.log', maxBytes=100000, backupCount=1)
formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
logHandler.setLevel(logging.INFO)
app.logger.setLevel(logging.INFO)
logHandler.setFormatter(formatter)
app.logger.addHandler(logHandler)

login_manager = LoginManager()
login_manager.login_view='login'
login_manager.init_app(app)
login_manager.session_protection = "None"
login_manager.login_view = "login"
login_manager.login_message = "Please Log In"
login_manager.login_message_category = "danger"


import geniusapp.admin.controller
import geniusapp.admin.reportController
import geniusapp.error.controller
import geniusapp.home.controller
import geniusapp.package.controller
import geniusapp.security.controller
import geniusapp.dashboard.controller
import geniusapp.dashboard.subscription
import geniusapp.dashboard.demoController
import geniusapp.dashboard.memberController
import geniusapp.dashboard.seminarControllery
import geniusapp.dashboard.chat
import geniusapp.userDashborad.userDashboardController
