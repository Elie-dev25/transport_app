from app.database import db

class FuelAlertState(db.Model):
    __tablename__ = 'fuel_alert_state'
    id = db.Column(db.Integer, primary_key=True)
    aed_id = db.Column(db.Integer, db.ForeignKey('aed.id'), unique=True, nullable=False)
    # Dernier seuil notifié: 10, 25, 50 ou None
    last_threshold = db.Column(db.Integer, nullable=True)

    aed = db.relationship('AED', backref=db.backref('fuel_alert_state', uselist=False))
