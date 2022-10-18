from db import db

categories_list = ("Senior", "Junior")
sports_list = ("Volleyball", "Football", "Basketball", "Futsal")
teams_in_competitions = db.Table("teams_in_competitions",
                                 db.Column("id", db.Integer, primary_key=True),
                                 db.Column("team_id", db.Integer, db.ForeignKey("teams.id")),
                                 db.Column("competition_id", db.Integer, db.ForeignKey("competitions.id")))

# TODO treure-ho??
"""
matches_in_competitions = db.Table("matches_in_competitions",
                                   db.Column("id", db.Integer, primary_key=True),
                                   db.Column("matches_id", db.Integer, db.ForeignKey("matches.id")),
                                   db.Column("competition_id", db.Integer, db.ForeignKey("competitions.id")))
"""


class CompetitionsModel(db.Model):
    __tablename__ = 'competitions'
    __table_args__ = (db.UniqueConstraint('name', 'category', 'sport'),)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    category = db.Column(db.Enum(*categories_list, name='categories_types'), nullable=False)
    sport = db.Column(db.Enum(*sports_list, name='sports_types'), nullable=False)
    teams = db.relationship("TeamsModel", secondary=teams_in_competitions, backref=db.backref("competitions"))

    def __init__(self, name, category, sport):
        self.name = name
        self.category = category
        self.sport = sport

    def json(self):
        return {'id': self.id, 'name': self.name, 'category': self.category, 'sport': self.sport,
                'teams': [team.json() for team in self.teams], 'matches': [match.json() for match in self.matches]}

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_all(cls):
        return cls.query.all()

