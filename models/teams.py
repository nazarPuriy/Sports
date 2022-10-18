from db import db


class TeamsModel(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    country = db.Column(db.String(30), nullable=False)

    def __init__(self, name, country):
        self.name = name
        self.country = country

    def json(self):
        return {'id': self.id, 'name': self.name, 'country': self.country}

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
    def get_by_name_and_country(cls, name, country):
        if country:
            return cls.query.filter_by(name=name, country=country).first()
        else:
            return cls.query.filter_by(name=name).first()
