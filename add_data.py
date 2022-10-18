from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.teams import TeamsModel
from models.matches import MatchesModel
from models.competitions import CompetitionsModel
import data
from datetime import datetime

import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.init_app(app)

teams = []
matches = []
competitions = []

for competition in data.competitions:
    competitionModel = CompetitionsModel(name=competition["name"], category=competition["category"],
                                         sport=competition["sport"])
    competitions.append(competitionModel)

for match in data.matches:
    matchModel = MatchesModel(date=datetime.strptime(match["date"], "%Y-%m-%d"), price=match["price"])
    matches.append(matchModel)

for team in data.teams:
    teamModel = TeamsModel(name=team["name"], country=team["country"])
    teams.append(teamModel)

# Relationships
for match in matches:
    local = teams[random.randint(0,len(teams)-1)]
    visitor = teams[random.randint(0,len(teams)-1)]

    # Assign local and visitor for the current match
    match.local = local
    match.visitor = visitor

    random_competition = competitions[random.randint(0,len(competitions))]
    # Assign the competition to the match
    match.competition = random_competition
    random_competition.matches.append(match)
    random_competition.teams.append(local)
    random_competition.teams.append(visitor)

db.session.add_all(teams)
db.session.add_all(matches)
db.session.add_all(competitions)
db.session.commit()
