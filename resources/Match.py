from flask_restful import Resource, reqparse
from models.teams import TeamsModel
from models.matches import MatchesModel
from models.competitions import CompetitionsModel
from models.accounts import auth
from datetime import datetime
from lock import lock


class Match(Resource):
    @classmethod
    @auth.login_required(role='admin')
    def create_add_match(cls, date, price, local_id, visitor_id, total_available_tickets, competition_id=-1):
        with lock.lock:
            if local_id == visitor_id:
                return {"message": "Local id must be different from visitor id"}, 500
            new_match = MatchesModel(datetime.strptime(date, "%Y-%m-%d"), price, total_available_tickets)
            local = TeamsModel.get_by_id(local_id)
            visitor = TeamsModel.get_by_id(visitor_id)
            if local and visitor:
                new_match.local = local
                new_match.visitor = visitor
                if competition_id != -1:
                    competition = CompetitionsModel.get_by_id(competition_id)
                    if competition:
                        new_match.competition = competition
                    else:
                        return {"message": "Competition doesn't exist"}, 500
                # Un cop fets els checks previs, si arribem aquí tot és correcte. Afegim la id a l'equip i aquest a la llista
                try:
                    new_match.save_to_db()
                    return {'message': "Match with id [{}] added successfully".format(new_match.id)}, 201
                except:
                    return {"message": "An error occurred inserting the match."}, 500

            else:
                return {"message": "Local or visitor team doesn't exist"}, 500

    @classmethod
    def get(cls, id=None):
        with lock.lock:
            # Necessitem l'identificador del partit a mostrar.
            if id is None:
                return {'message': "Must specify match id"}, 400

            match = MatchesModel.get_by_id(id)
            if match:
                return match.json(), 200
            else:
                return {'message': "match does not exist"}, 404

    @classmethod
    @auth.login_required(role='admin')
    def post(cls, id=None):
        with lock.lock:

            # TODO poder especificar id
            # Creem el nou match
            parser = reqparse.RequestParser()
            parser.add_argument('local_id', type=int, required=True, help="This field cannot be left blank")
            parser.add_argument('visitor_id', type=int, required=True, help="This field cannot be left blank")
            parser.add_argument('date', type=str, required=True, help="This field cannot be left blank")
            parser.add_argument('price', type=float, required=True, help="This field cannot be left blank")
            parser.add_argument('total_available_tickets', type=int, required=True, help="This field cannot be left blank")
            parser.add_argument('competition_id', type=int, required=False)
            info = parser.parse_args()
            if info['competition_id'] is not None:
                return cls.create_add_match(info['date'], info['price'], info['local_id'], info['visitor_id'], info['total_available_tickets'],
                                            info['competition_id'])
            else:
                return cls.create_add_match(info['date'], info['price'], info['local_id'], info['visitor_id'], info['total_available_tickets'])

    @classmethod
    @auth.login_required(role='admin')
    def delete(cls, id=None):
        with lock.lock:
            # Si no ens passen id, enviem un missatge d'error
            if id is None:
                return {'message': "Must specify match id"}, 400

            # Recorrem els partits per veure quin eliminar
            match = MatchesModel.get_by_id(id)
            if match:
                try:
                    match.delete_from_db()
                    return {"message": f"Match with id [{id}] deleted successfully"}, 200
                except:
                    return {"message": "An error occurred deleting the match."}, 500

            else:
                # Si no trobem l'equip, retornem 404
                return {'message': "Match does not exist"}, 404

    @classmethod
    @auth.login_required(role='admin')
    def put(cls, id=None):
        with lock.lock:
            # Creem el nou partit
            parser = reqparse.RequestParser()
            parser.add_argument('local_id', type=int, help="This field cannot be left blank")
            parser.add_argument('visitor_id', type=int, help="This field cannot be left blank")
            parser.add_argument('date', type=str, help="This field cannot be left blank")
            parser.add_argument('price', type=float, help="This field cannot be left blank")
            parser.add_argument('total_available_tickets', type=int, help="This field cannot be left blank")
            parser.add_argument('competition_id', type=int, required=False)
            info = parser.parse_args()
            if id is None:
                return {'message': "Must specify match id"}, 400
            else:
                match = MatchesModel.get_by_id(id)
                if match:
                    if info['date'] is not None:
                        match.date = datetime.strptime(info['date'], "%Y-%m-%d")
                    if info['price'] is not None:
                        match.price = info['price']
                    if info['total_available_tickets'] is not None:
                        match.total_available_tickets = info['total_available_tickets']
                    if info['local_id'] is not None:
                        local = TeamsModel.get_by_id(info['local_id'])
                        if local:
                            match.local = local
                        else:
                            return {"message": "Local team doesn't exist"}, 500
                    if info['visitor_id'] is not None:
                        visitor = TeamsModel.get_by_id(info['visitor_id'])
                        if visitor:
                            match.visitor = visitor
                        else:
                            return {"message": "Visitor team doesn't exist"}, 500
                    if info['competition_id'] is not None:
                        competition = CompetitionsModel.get_by_id(info['competition_id'])
                        if competition:
                            match.competition = competition
                        else:
                            return {"message": "Competition team doesn't exist"}, 500

                    if match.local.id == match.visitor.id:
                        return {"message": "Local id must be different from visitor id"}, 500

                    try:
                        match.save_to_db()
                        return {'message': "Match with id [{}] was modified successfully".format(id)}, 201
                    except:
                        return {"message": "An error occurred updating the match."}, 500

                # Si el partit no existeix, l'afegim
                else:
                    if info['date'] is not None and info['date'] is not None and info['price'] is not None and info[
                        'visitor_id'] is not None:

                        if info['competition_id'] is not None:
                            return cls.create_add_match(info['date'], info['price'], info['local_id'], info['visitor_id'],
                                                        info['competition_id'])
                        else:
                            return cls.create_add_match(info['date'], info['price'], info['local_id'], info['visitor_id'])

                    else:
                        return {'message': "No match found with specified id and the information is not complete".format(
                            id)}, 500


class Matches(Resource):

    @classmethod
    def get(cls):
        with lock.lock:
            return {'matches': [match.json() for match in MatchesModel.get_all()]}, 200


class TeamMatchesList(Resource):

    @classmethod
    def get(cls, id):
        with lock.lock:
            team = TeamsModel.get_by_id(id)
            if not team:
                return {'message': "Team does not exist"}, 404

            return [match.json() for match in team.matchesL + team.matchesV], 200


class CompetitionMatchesList(Resource):

    @classmethod
    def get(cls, id):
        with lock.lock:
            competition = CompetitionsModel.get_by_id(id)
            if not competition:
                return {'message': "Competition does not exist"}, 404

            return [match.json() for match in competition.matches], 200


# TODO comprovar que tot funcioni bé
class CompetitionMatch(Resource):

    @classmethod
    def get(cls, id_competition, id_match=None):
        with lock.lock:
            if id_match is None:
                return {'message': "Must specify match id"}, 400

            match = MatchesModel.get_by_id(id_match)
            if not match:
                return {'message': "Match does not exist"}, 404

            competition = CompetitionsModel.get_by_id(id_competition)
            if not competition:
                return {'message': "Competition does not exist"}, 404

            if match not in competition.matches:
                return {'message': "Match not in competition"}, 404

        return match.json(), 200

    @classmethod
    @auth.login_required(role='admin')
    def post(cls, id_competition, id_match=None):
        with lock.lock:
            parser = reqparse.RequestParser()
            parser.add_argument('local_id', type=int, required=True, help="This field cannot be left blank")
            parser.add_argument('visitor_id', type=int, required=True, help="This field cannot be left blank")
            parser.add_argument('date', type=str, required=True, help="This field cannot be left blank")
            parser.add_argument('price', type=float, required=False)
            info = parser.parse_args()

            local_req = info.local_id
            visitor_req = info.visitor_id
            date_req = info.date
            price_req = info.price

            if id_match:
                match = MatchesModel.get_by_id(id_match)

            else:
                match = MatchesModel.get_by_local_visitor_and_date(local_req, visitor_req, date_req, price_req)

            if not match:
                return {'message': "Match does not exist"}, 404

            if match.local_id != local_req or match.visitor_id != visitor_req or match.date != date_req or (
                    price_req and match.price != price_req):
                return {'message': "Matches do not match"}, 409

            competition = CompetitionsModel.get_by_id(id_competition)
            if not competition:
                return {'message': "Competition does not exist"}, 404

            if match in competition.teams:
                return {'message': "Match already in competition"}, 409

            competition.teams.append(match)
            competition.save_to_db()
            return {'message': "Match with id [{}] added to competition with id [{}]".format(match.id, competition.id)}, 201

    @classmethod
    @auth.login_required(role='admin')
    def delete(cls, id_competition, id_match=None):
        with lock.lock:
            if id_match:
                match = MatchesModel.get_by_id(id_match)
            else:
                return {'message': "Must specify match id"}, 400

            if not match:
                return {'message': "Match does not exist"}, 404

            competition = CompetitionsModel.get_by_id(id_competition)
            if not competition:
                return {'message': "Competition does not exist"}, 404

            if match not in competition.matches:
                return {'message': "Match not in competition"}, 404

            competition.matches.remove(match)
            competition.save_to_db()
            return {'message': "Match with id [{}] removed from competition with id [{}]".format(match.id,
                                                                                                 competition.id)}, 200
