from app.database import db
from sqlalchemy import Enum

class Affectation(db.Model):
    __tablename__ = 'affectation'

    affectation_id = db.Column(db.Integer, primary_key=True)
    type_affectation = db.Column(
        Enum('EN_SEMAINE', 'WEEK_END', 'PERMANENCE', 'CONGE', name='type_affectation_enum'),
        nullable=False
    )
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    chauffeur_id = db.Column(db.Integer, db.ForeignKey('chauffeur.chauffeur_id'), nullable=False)
    planifie_par = db.Column(db.Integer, db.ForeignKey('utilisateur.utilisateur_id'), nullable=True)

    chauffeur = db.relationship('Chauffeur', backref=db.backref('affectations', lazy=True))
    planificateur = db.relationship('Utilisateur', backref=db.backref('affectations_planifiees', lazy=True), foreign_keys=[planifie_par])

    def __repr__(self):
        return f"<Affectation {self.affectation_id} {self.type_affectation}>"