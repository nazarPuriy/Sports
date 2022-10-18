from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, reqparse
from lock import lock
from models.competitions import CompetitionsModel
from models.matches import MatchesModel
from models.teams import TeamsModel
auth = HTTPBasicAuth()



class Team(Resource):

    @classmethod
    def get(cls, id=None):
        with lock.lock:
            # Necessitem l'identificador de l'equip a mostrar.
            if id is None:
                return {'message': "Must specify team id"}, 400

            team = TeamsModel.get_by_id(id)
            if team:
                return team.json(), 200
            else:
                return {'message': "team does not exist"}, 404

    @classmethod
    @auth.login_required(role='admin')
    def post(cls, id=None):
        with lock.lock:
            # Creem el nou equip
            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str, required=True, help="This field cannot be left blank")
            parser.add_argument('country', type=str, required=True, help="This field cannot be left blank")
            name = parser.parse_args()['name']
            country = parser.parse_args()['country']

            # TODO poder especificar id
            new_team = TeamsModel(name, country)
            # Un cop fets els checks previs, si arribem aquí tot és correcte. Afegim la id a l'equip i aquest a la llista
            try:
                new_team.save_to_db()
                return {'message': "Team with id [{}] added successfully".format(new_team.id)}, 201
            except:
                return {"message": "An error occurred inserting the team."}, 500

    @classmethod
    @auth.login_required(role='admin')
    def delete(cls, id=None):
        with lock.lock:
            # Si no ens passen id, enviem un missatge d'error
            if id is None:
                return {'message': "Must specify team id"}, 400

            team = TeamsModel.get_by_id(id)
            if team:
                try:
                    team.delete_from_db()
                    return {"message": f"Team with id [{id}] deleted successfully"}, 200
                except Exception as e:
                    return {"message": "An error occurred deleting the team."}, 500

            else:
                # Si no trobem l'equip, retornem 404
                return {'message': "Team does not exist"}, 404

    @classmethod
    @auth.login_required(role='admin')
    def put(cls, id=None):
        with lock.lock:
            # Creem el nou equip
            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str)
            parser.add_argument('country', type=str)
            info = parser.parse_args()

            if id is None:
                return {'message': "Must specify team id"}, 400
            else:
                team = TeamsModel.get_by_id(id)
                if team:
                    if info['name'] is not None:
                        team.name = info['name']
                    if info['country'] is not None:
                        team.country = info['country']
                    try:
                        team.save_to_db()
                        return {'message': "Team with id [{}] was modified successfully".format(id)}, 201
                    except:
                        return {"message": "An error occurred updating the team."}, 500
                # Si l'equip no existeix l'afegim
                else:
                    if 'name' in info.keys() and 'country' in info.keys():
                        new_team = TeamsModel(info['name'], info['country'])
                        try:
                            new_team.save_to_db()
                            return {'message': "Team with id [{}] added successfully".format(id)}, 201
                        except:
                            return {"message": "An error occurred inserting the team."}, 500
                    else:
                        return {'message': "No team found with specified id and the information is not complete".format(
                            id)}, 500


class Teams(Resource):

    @classmethod
    def get(cls):
        with lock.lock:
            return {'teams': [team.json() for team in TeamsModel.get_all()]}, 200


class CompetitionTeamsList(Resource):

    @classmethod
    def get(cls, id):
        with lock.lock:
            competition = CompetitionsModel.get_by_id(id)
            if not competition:
                return {'message': "Competition does not exist"}, 404

            return [team.json() for team in competition.teams], 200


class MatchTeamsList(Resource):

    @classmethod
    def get(cls, id):
        with lock.lock:
            match = MatchesModel.get_by_id(id)
            if not match:
                return {'message': "Match does not exist"}, 404

            return [match.local.json(), match.visitor.json()], 200


class CompetitionTeams(Resource):

    @classmethod
    def get(cls, id_competition, id_team=None):
        with lock.lock:
            team = TeamsModel.get_by_id(id_team)
            if not team:
                return {'message': "Team does not exist"}, 404

            competition = CompetitionsModel.get_by_id(id_competition)
            if not competition:
                return {'message': "Competition does not exist"}, 404

            if team not in competition.teams:
                return {'message': "Team does not participate in competition"}, 404

            return team.json(), 200

    @classmethod
    @auth.login_required(role='admin')
    def post(cls, id_competition, id_team=None):
        with lock.lock:
            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str, required=True, help="This field cannot be left blank")
            parser.add_argument('country', type=str, required=False)
            name_req = parser.parse_args()['name']
            country_req = parser.parse_args()['country']

            if id_team:
                team = TeamsModel.get_by_id(id_team)

            else:
                team = TeamsModel.get_by_name_and_country(name_req, country_req)

            if not team:
                return {'message': "Team does not exist"}, 404

            if team.name != name_req or (country_req and country_req != team.country):
                return {'message': "Teams do not match"}, 409

            competition = CompetitionsModel.get_by_id(id_competition)
            if not competition:
                return {'message': "Competition does not exist"}, 404

            if team in competition.teams:
                return {'message': "Team already participates in competition"}, 409

            competition.teams.append(team)
            competition.save_to_db()
            return {'message': "Team with id [{}] added to competition with id [{}]".format(team.id, competition.id)}, 201

    @classmethod
    @auth.login_required(role='admin')
    def delete(cls, id_competition, id_team=None):
        with lock.lock:
            if id_team:
                team = TeamsModel.get_by_id(id_team)
            else:
                return {'message': "Must specify team id"}, 400

            if not team:
                return {'message': "Team does not exist"}, 404

            competition = CompetitionsModel.get_by_id(id_competition)
            if not competition:
                return {'message': "Competition does not exist"}, 404

            if team not in competition.teams:
                return {'message': "Team does not participate in competition"}, 404

            competition.teams.remove(team)
            competition.save_to_db()
            return {'message': "Team with id [{}] removed from competition with id [{}]".format(team.id,
                                                                                                competition.id)}, 200
