from db import db
from flask_restful import Resource, reqparse
from models.accounts import AccountsModel, OrdersModel, auth
from models.matches import MatchesModel
from flask import g
from lock import lock

class Order(Resource):

    @classmethod
    @auth.login_required(role=['admin', 'user'])
    def get(cls, username=None):
        with lock.lock:
            if username is None and g.user.role == 1:
                return [order.json() for order in OrdersModel.query.all()], 200
            else:
                if username != g.user.username and g.user.role == 0:
                    if username != g.user.username:
                        return {'message': "User and token must match"}, 400

                account = AccountsModel.query.get(username)
                if account is None:
                    return {'message': "Not a real username"}, 404
                return {'orders': [order.json() for order in account.orders]}, 200

    @classmethod
    @auth.login_required(role='user')
    def post(cls, username):
        with lock.lock:

            if username is None:
                return {'message': "Must specify username"}, 400

            if username != g.user.username:
                return {'message': "User and token must match"}, 400

            # Demanen una llista de
            parser = reqparse.RequestParser()
            parser.add_argument('match_id', type=int, help="This field cannot be left blank", required=True)
            parser.add_argument('tickets_bought', type=int, help="This field cannot be left blank", required=True)
            info = parser.parse_args()

            # Anem a comprovar que l'ordre pot ser realitzada
            account = AccountsModel.get_by_name(username)
            if not account:
                return {'message': "User doesn't exist"}, 404

            match = MatchesModel.get_by_id(info['match_id'])
            if not match:
                return {'message': "Match doesn't exist"}, 404

            if account.available_money < info['tickets_bought'] * match.price:
                return {"message": "User doesn't have enough money"}, 500
            if match.total_available_tickets < info['tickets_bought']:
                return {"message": "There are not enough tickets left"}, 500

            match.total_available_tickets = match.total_available_tickets - info['tickets_bought']
            account.available_money = account.available_money - info['tickets_bought'] * match.price
            new_order = OrdersModel(quantity=info['tickets_bought'])
            new_order.match = match
            new_order.account = account
            try:
                db.session.add(new_order)
                db.session.commit()
                return new_order.json(), 201
            except:
                return {"message": "An error occurred saving the order."}, 500

    # TODO acabar això?
    @classmethod
    def delete(cls, id=None):
        return {'message': "Not implemented yet"}, 500

    @classmethod
    def put(cls, id=None):
        return {'message': "Not implemented yet"}, 500


class OrdersList(Resource):

    @classmethod
    @auth.login_required(role='admin')
    def get(cls, username=None):
        with lock.lock:
            if username is None:
                return [order.json() for order in OrdersModel.query.all()], 200
            else:
                account = AccountsModel.query.get(username)
                if account is None:
                    return {'message': "Not a real username"}, 404
                return {'orders': [order.json() for order in account.orders]}, 200

    @classmethod
    @auth.login_required(role='user')
    def post(cls, username=None):
        with lock.lock:
            if username is None:
                return {'message': "Must specify username"}, 400

            if username != g.user.username:
                return {'message': "User and token must match"}, 400

            # Demanen una llista de matches i quantitats
            parser = reqparse.RequestParser()
            parser.add_argument('matches', type=int, action='append', required=True, help='match ids required')
            parser.add_argument('quantities', type=int, action='append', required=True, help='match quantities required')
            info = parser.parse_args()

            # Anem a comprovar que l'ordre pot ser realitzada
            account = AccountsModel.query.get(username)
            if not account:
                return {'message': "User doesn't exist"}, 404

            for match_id, quantity in zip(info['matches'], info['quantities']):

                if quantity <= 0:
                    return {'message': "All ticket quantities must be positive"}, 400

                match = MatchesModel.query.get(match_id)
                if not match:
                    return {'message': "Some matches don't exist"}, 404

                account.available_money = account.available_money - quantity * match.price
                match.total_available_tickets = match.total_available_tickets - quantity
                new_order = OrdersModel(quantity=quantity)
                new_order.account = account
                new_order.match = match

                if match.total_available_tickets < 0:
                    return {"message": "There are not enough tickets left for some matches"}, 500

                if account.available_money < 0:
                    return {"message": "User doesn't have enough money"}, 500

            try:
                db.session.add(account)
                db.session.commit()
                return {"message": "Orders added successfully"}, 201
            except:
                db.session.rollback()
                return {"message": "An error occurred saving the orders."}, 500




