from app.extensions import db

class Vidange(db.Model):
    __tablename__ = 'vidange'
    id = db.Column(db.Integer, primary_key=True)
    aed_id = db.Column(db.Integer, db.ForeignKey('aed.id'), nullable=False)
    date_vidange = db.Column(db.Date, nullable=False)
    kilometrage = db.Column(db.Integer, nullable=False)
    type_huile = db.Column(db.String(64), nullable=True)
    remarque = db.Column(db.String(256), nullable=True)

    aed = db.relationship('AED', backref=db.backref('vidanges', lazy=True))
