from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, reqparse
from models.teams import TeamsModel
from models.matches import MatchesModel
from models.competitions import CompetitionsModel
from models.competitions import sports_list, categories_list
from lock import lock
auth = HTTPBasicAuth()


class Competition(Resource):

    @classmethod
    def get(cls, id=None):
        with lock.lock:
            # Necessitem l'identificador de la competició a mostrar.
            if id is None:
                return {'message': "Must specify competition id".format(id)}, 400
            competition = CompetitionsModel.get_by_id(id)
            if competition:
                return competition.json(), 200
            else:
                return {'message': "Competition does not exist"}, 404

    @classmethod
    @auth.login_required(role='admin')
    def post(cls, id=None):
        with lock.lock:
            # Creem la nova competició
            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str, required=True, help="This field cannot be left blank")
            parser.add_argument('category', required=True, type=str, help="This field cannot be left blank")
            parser.add_argument('sport', required=True, type=str, help="This field cannot be left blank")
            parser.add_argument('teams', type=int, action='append')
            parser.add_argument('matches', type=int, action='append')
            info = parser.parse_args()

            if info['sport'] not in sports_list:
                return {"message": "Sport doesn't exist"}, 500

            if info['category'] not in categories_list:
                return {"message": "Category doesn't exist"}, 500

            try:
                new_competition = CompetitionsModel(info['name'], info['category'], info['sport'])
                for team_id in info['teams']:
                    team = TeamsModel.get_by_id(team_id)
                    if team is None:
                        return {"message": "Some teams don't exist"}, 500
                    else:
                        new_competition.teams.append(team)

                for match_id in info['matches']:
                    match = MatchesModel.get_by_id(match_id)
                    if match.competition:
                        return {"message": f"Match with id {match.id} is already in one competition"}, 500
                    new_competition.teams.append(match.local)
                    new_competition.teams.append(match.visitor)
                    match.competition = new_competition

                    if match is None:
                        return {"message": "Some matches don't exist"}, 500
                    else:
                        new_competition.matches.append(match)

                # Un cop fets els checks previs, si arribem aquí tot és correcte. Afegim la competició
                new_competition.save_to_db()
                return {'message': "Competition with id [{}] added successfully".format(new_competition.id)}, 201
            except:
                return {"message": "An error occurred inserting the competition."}, 500

    @classmethod
    @auth.login_required(role='admin')
    def delete(cls, id=None):
        with lock.lock:
            # Si no ens passen id, enviem un missatge d'error
            if id is None:
                return {'message': "Must specify competition id"}, 400

            competition = CompetitionsModel.get_by_id(id)
            if competition:
                try:
                    competition.delete_from_db()
                    return {"message": f"competition with id [{id}] deleted successfully"}, 200
                except:
                    return {"message": "An error occurred deleting the competition."}, 500

            else:
                # Si no trobem l'equip, retornem 404
                return {'message': "Competition does not exist"}, 404

    @classmethod
    @auth.login_required(role='admin')
    def put(cls, id=None):
        with lock.lock:
            # Creem la nova competició
            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str)
            parser.add_argument('category', type=str)
            parser.add_argument('sport', type=str)
            info = parser.parse_args()

            if id is None:
                return {'message': "Must specify competition id"}, 400
            else:
                competition = CompetitionsModel.query.get(id)
                if competition:
                    if info['name'] is not None:
                        competition.name = info['name']
                    if info['category'] is not None:
                        competition.category = info['category']
                    if info['sport'] is not None:
                        competition.category = info['sport']
                    try:
                        competition.save_to_db()
                        return {'message': "Competition with id [{}] was modified successfully".format(id)}, 201
                    except:
                        return {"message": "An error occurred updating the competition."}, 500

            return cls.post(id)


class Competitions(Resource):

    @classmethod
    def get(cls):
        return {'competitions': [competition.json() for competition in CompetitionsModel.get_all()]}, 200
