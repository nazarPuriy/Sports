import flask_restful
from flask_restful import Resource, reqparse
from models.accounts import AccountsModel, auth
from flask import g
from lock import lock

class Account(Resource):

    @classmethod
    @auth.login_required(role=['admin', 'user'])
    def get(cls, username=None):

        with lock.lock:
            if not username:
                return {'message': "Must specify username"}, 400
            if username != g.user.username and g.user.is_admin == 0:
                return {'message': "User and token must match"}, 400
            account = AccountsModel.get_by_name(username)
            if not account:
                return {'message': "Account doesn't exist"}, 404

            return account.json(), 200

    @classmethod
    def post(cls, username=None):
        with lock.lock:
            parser = reqparse.RequestParser()
            parser.add_argument('password', type=str, help="This field cannot be left blank", required=True)
            parser.add_argument('is_admin', type=bool)
            parser.add_argument('available_money', type=int)
            if username is None:
                parser.add_argument('username', type=str, help="This field cannot be left blank", required=True)

            info = parser.parse_args()

            if username is None:
                username = info['username']

            account = AccountsModel(username)

            if info['is_admin'] is not None:
                account.is_admin = info['is_admin']

            if info['available_money'] is not None:
                account.available_money = info['available_money']

            account.hash_password(info['password'])

            try:
                account.save_to_db()
            except:
                return {"message": "An error occurred inserting the user."}, 500

            return {'message': "User with name [{}] added successfully".format(account.username)}, 201

    @classmethod
    @auth.login_required(role=['user', 'admin'])
    def delete(cls, username=None):
        with lock.lock:
            if not username:
                return {'message': "Must specify username"}, 400
            if username != g.user.username and g.user.is_admin == 0:
                return {'message': "User and token must match"}, 400

            account = AccountsModel.get_by_name(username)
            if not account:
                return {'message': "Account does not exist"}, 404

            try:
                account.delete_from_db()
                return {"message": f"User [{username}] deleted successfully"}, 200
            except:
                return {"message": "An error occurred deleting the team."}, 500


class AccountsList(Resource):

    @classmethod
    @auth.login_required(role='admin')
    def get(cls):
        with lock.lock:
            return {'accounts': [account.json() for account in AccountsModel.query.all()]}, 200
