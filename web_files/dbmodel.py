from datetime import datetime
from web_files import db,login_manager,app
from itsdangerous import TimedJSONWebSignatureSerializer as serializer
from flask_login import UserMixin

@login_manager.user_loader
def load_user(userID):
    return User.query.get(int(userID))


class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(30),nullable=False)
    email = db.Column(db.String(100),unique = True,nullable = False)
    image = db.Column(db.String(120),nullable = False,default = 'default.jpg')
    password = db.Column(db.String(100),nullable = False)
    posts = db.relationship('Post',backref = 'author',lazy = True)
    pictures = db.relationship('Picture',backref = 'author',lazy = True)

    def get_reset_token(self,expirs_seconds = 600):
        s= serializer(app.config['SECRET_KEY'],expirs_seconds)
        return s.dumps({'userid':self.id}).decode('utf-8')
    
    @staticmethod
    def verify_token(token):
        s= serializer(app.config['SECRET_KEY'])
        try:
            userid = s.loads(token)['userid']
            return User.query.get(userid)
        except:
            return None
        

    def __repr__(self):
        return f"User({self.id},{self.username},{self.email},{self.image})"

class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    post_title =db.Column(db.String(100),nullable=False)
    post_time = db.Column(db.DateTime,nullable=False,default=datetime.now)
    post_content = db.Column(db.Text,nullable = False)

    userID = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Post({self.post_time},{self.post_title})"

class Picture(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    picture_name =db.Column(db.String(100),nullable=False)
    upload_time = db.Column(db.DateTime,nullable=False,default=datetime.now)
    picture_content = db.Column(db.Text,nullable = False)
    picture_path = db.Column(db.String(120),nullable = False)

    userID = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Picture({self.upload_time},{self.picture_name},{self.picture_content})"