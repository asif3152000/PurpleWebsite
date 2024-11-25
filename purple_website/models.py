from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from purple_website import db,login_manager,app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return userstable.query.get(int(user_id))

class userstable(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    designation = db.Column(db.String(120),nullable=False,default='user')
    password = db.Column(db.String(60), nullable=False)

    def get_reset_token(self,expires_sec=1800):
        s= Serializer(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s= Serializer(app.config['SECRET_KEY'])
        try:
            user_id=s.loads(token)['user_id']
        except:
            return None
        return userstable.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class productstable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    image_file = db.Column(db.String(20), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellertable.id'), nullable=False)  # Foreign key to seller
    status = db.Column(db.String, default="available",nullable=False)  # Foreign key to seller
    seller = db.relationship('sellertable', backref='products')  # Relationship to access seller from product

class adminstable(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


class sellertable(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userstable.id'), nullable=False)  # Foreign key to Registertable
    storename = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Default to current time
    storedescription = db.Column(db.String, nullable=False)
    status = db.Column(db.String(20), default='active')    
    # Relationship to Registertable
    user = db.relationship('userstable', backref=db.backref('storename', lazy=True))
