from db import db
from passlib.apps import custom_app_context as pwd_context
from jwt import encode, decode, ExpiredSignatureError, InvalidSignatureError
import time
from flask_httpauth import HTTPBasicAuth
from jwt import encode, decode
from flask import g, current_app

auth = HTTPBasicAuth()


class AccountsModel(db.Model):
    __tablename__ = 'accounts'

    username = db.Column(db.String(30), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    # 0 not admin/ 1 is admin
    is_admin = db.Column(db.Integer, nullable=False)
    available_money = db.Column(db.Float)

    def __init__(self, username, available_money=0, is_admin=False):
        self.username = username
        self.available_money = available_money
        self.is_admin = is_admin
        self.password = 'test'

    def json(self):
        if (self.is_admin):
            admin = "Si"
        else:
            admin = "No"
        return {'username': self.username, 'admin': admin, 'money': self.available_money}

    @classmethod
    def get_by_name(cls, username):
        return cls.query.get(username)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def generate_auth_token(self, expiration=6000):
        return encode(
            {"username": self.username, "exp": int(time.time()) + expiration},
            current_app.secret_key,
            algorithm="HS256"
        )

    @classmethod
    def verify_auth_token(cls, token):
        try:
            data = decode(token, current_app.secret_key, algorithms=["HS256"])
        except ExpiredSignatureError:
            return None  # expired token
        except InvalidSignatureError:
            return None  # invalid token

        user = cls.query.filter_by(username=data['username']).first()

        return user


class OrdersModel(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), db.ForeignKey('accounts.username'), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)
    tickets_bought = db.Column(db.Integer, nullable=False)

    match = db.relationship("MatchesModel", foreign_keys=[match_id],
                            backref=db.backref("orders", cascade="all, delete-orphan"))

    account = db.relationship("AccountsModel", foreign_keys=[username],
                              backref=db.backref("orders", cascade="all, delete-orphan"))

    def __init__(self, username=None, match_id=None, quantity=1):
        self.match_id = match_id
        self.username = username
        self.tickets_bought = quantity

    def json(self):
        return {'id': self.id, 'username': self.username, 'match_id': self.match_id,
                'tickets_bought': self.tickets_bought}


@auth.verify_password
def verify_password(token, password):
    try:
        data = decode(token, secret_key, algorithms=["HS256"])
    except:
        return False

    if data['exp'] < time.time():
        return False

    user = AccountsModel.get_by_name(data['username'])
    if user:
        g.user = user
        return user


@auth.get_user_roles
def get_user_roles(user: AccountsModel):
    roles = [['user'], ['admin']]
    return roles[user.is_admin]
