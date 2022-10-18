from db import db


class MatchesModel(db.Model):
    __tablename__ = 'matches'
    __table_args__ = (db.UniqueConstraint('local_id', 'visitor_id', 'date'),)

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_available_tickets = db.Column(db.Integer, nullable=False)

    local_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    visitor_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey("competitions.id"), nullable=True)

    local = db.relationship("TeamsModel", foreign_keys=[local_id],
                            backref=db.backref("matchesL", cascade="all, delete-orphan"))
    visitor = db.relationship("TeamsModel", foreign_keys=[visitor_id],
                              backref=db.backref("matchesV", cascade="all, delete-orphan"))
    competition = db.relationship("CompetitionsModel", foreign_keys=[competition_id], backref=db.backref("matches"))

    def __init__(self, date, price, total_available_tickets):
        self.date = date
        self.price = price
        self.total_available_tickets = total_available_tickets

    def json(self):
        competition_name = "Not in a competition"
        if self.competition:
            competition_name = self.competition.name
        return {'id': self.id, 'date': self.date.isoformat(), 'price': self.price, 'local': self.local.json(),
                'visitor': self.visitor.json(), 'competition': competition_name, 'total_available_tickets': self.total_available_tickets, 'competition_id': self.competition_id}

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

    @classmethod
    def get_by_local_visitor_and_date(cls, local_req, visitor_req, date_req, price_req):
        if price_req:
            return cls.query.filter_by(local_id=local_req, visitor_id=visitor_req, date=date_req, price=price_req)
        else:
            return cls.query.filter_by(local_id=local_req, visitor_id=visitor_req, date=date_req)
