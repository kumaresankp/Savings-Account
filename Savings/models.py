from datetime import datetime,date
from Savings import db,login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    # posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Account(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),autoincrement=True)
    account_number = db.Column(db.String(20))
    balance = db.Column(db.Float)
    user = db.relationship('User', backref=db.backref('account', lazy=True))

    def __repr__(self):
            return f"Account('{self.account_number}', '{self.balance}')"

    def get_user(self):
        return User.query.get(self.id)


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    request_type = db.Column(db.String(10))
    amount = db.Column(db.Float)
    status = db.Column(db.String(10),default='Pending')
    transanct_date = db.Column(db.Date, default=date.today)

    # def __init__(self, transaction_date):
    #     self.transaction_date = transaction_date

