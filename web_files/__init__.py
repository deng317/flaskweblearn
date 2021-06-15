from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
app.config['SECRET_KEY']='05b4d05c7c13e6ead61539a283042249'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_message_category ="success"
login_manager.login_message=u"不好意思，这个是会员界面，请登录后查看。"
login_manager.login_view='login'
login_manager.session_protection='strong'

app.config['MAIL_SERVER']=os.environ.get('MAIL_HOST')
app.config['MAIL_PORT']=465
app.config['MAIL_USE_TLS']=False
app.config['MAIL_USE_SSL']=True
app.config['MAIL_USERNAME']=os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD']=os.environ.get('MAIL_USERPASSWD')
mail=Mail(app)

app.config

from web_files import routes