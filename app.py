from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask import render_template
from flask_migrate import Migrate

from resources.Login import Login
from resources.Team import Team, Teams, CompetitionTeamsList, MatchTeamsList, CompetitionTeams
from resources.Match import Match, Matches, TeamMatchesList, CompetitionMatchesList, CompetitionMatch
from resources.Competition import Competition, Competitions
from resources.Order import Order, OrdersList
from resources.Account import Account, AccountsList
from db import db
from decouple import config as config_decouple
from config import config

app = Flask(__name__)
environment = config['development']
if config_decouple('PRODUCTION', cast=bool, default=False):
  environment = config['production']

app.config.from_object(environment)

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)
CORS(app, resources={r'/*': {'origins': '*'}})


@app.route('/')
def render_vue():
    return render_template("index.html")


# TODO el retorn dels data es amb dies amb hora pero afegim nomes hora?

api.add_resource(Team, '/team/<int:id>/', '/team/')
api.add_resource(Teams, '/teams/')
api.add_resource(Match, '/match/<int:id>/', '/match/')
api.add_resource(Matches, '/matches/')
api.add_resource(Competition, '/competition/<int:id>/', '/competition/')
api.add_resource(Competitions, '/competitions/')

# Aquests es demanaven abans però no a la versió actualitzada, els deixem per si de cas
api.add_resource(CompetitionTeamsList, '/competition/<int:id>/teams/')
api.add_resource(CompetitionTeams, '/competition/<int:id_competition>/team/<int:id_team>/',
                 '/competition/<int:id_competition>/team/')  # s'ha canviat per team per a no tenir urls ambigües

api.add_resource(CompetitionMatchesList, '/competition/<int:id>/matches/')

api.add_resource(CompetitionMatch, '/competition/<int:id_match>/match/',
                 '/competition/<int:id_competition>/match/<int:id_match>/')

api.add_resource(TeamMatchesList, '/team/<int:id>/matches/')
api.add_resource(MatchTeamsList, '/match/<int:id>/teams/')

api.add_resource(Order, '/order/<string:username>/')
api.add_resource(OrdersList, '/orders/', '/orders/<string:username>/')

api.add_resource(Account, '/account/<string:username>/', '/account/')
api.add_resource(AccountsList, '/accounts/')

api.add_resource(Login, '/login/')

if __name__ == '__main__':
    app.run(port=5000, debug=True)




# TODO creo que se puede quitar el last / i en http llamas igual sin el last /
