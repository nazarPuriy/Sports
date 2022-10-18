from flask_restful import Resource, reqparse
from models.accounts import AccountsModel
from lock import lock


class Login(Resource):

    @classmethod
    def post(cls):
        with lock.lock:
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, required=True, help="This field cannot be left blank")
            parser.add_argument('password', type=str, required=True, help="This field cannot be left blank")
            data = parser.parse_args()

            username = data['username']
            password = data['password']

            account: AccountsModel = AccountsModel.get_by_name(username)
            if not account:
                return {'message': "User not found"}, 404

            if not account.verify_password(password):
                return {'message': "Incorrect password"}, 400

            token = account.generate_auth_token()
            return {'token': token}, 200
