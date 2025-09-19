from app.database import db
from datetime import datetime

class ChauffeurStatut(db.Model):
    __tablename__ = 'chauffeur_statut'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chauffeur_id = db.Column(db.Integer, db.ForeignKey('chauffeur.chauffeur_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    statut = db.Column(db.Enum('CONGE', 'PERMANENCE', 'SERVICE_WEEKEND', 'SERVICE_SEMAINE', name='statut_chauffeur'), nullable=False)
    lieu = db.Column(db.Enum('CUM', 'CAMPUS', 'CONJOINTEMENT', name='lieu_chauffeur_statut'), nullable=False, default='CUM')
    date_debut = db.Column(db.DateTime, nullable=False)
    date_fin = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Colonne présente en base

    # Relation avec Chauffeur
    chauffeur = db.relationship('Chauffeur', backref=db.backref('statuts', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self) -> str:
        return f"<ChauffeurStatut id={self.id} chauffeur_id={self.chauffeur_id} statut={self.statut}>"

    def to_dict(self):
        """Convertir en dictionnaire pour JSON"""
        result = {
            'id': self.id,
            'chauffeur_id': self.chauffeur_id,
            'statut': self.statut,
            'lieu': self.lieu,
            'date_debut': self.date_debut.isoformat() if self.date_debut else None,
            'date_fin': self.date_fin.isoformat() if self.date_fin else None
        }
        # Formats lisibles (jj/mm/aaaa)
        try:
            if self.date_debut:
                result['date_debut_formatted'] = self.date_debut.strftime('%d/%m/%Y')
            if self.date_fin:
                result['date_fin_formatted'] = self.date_fin.strftime('%d/%m/%Y')
        except Exception:
            # En cas de problème de strftime (valeur None, etc.), ignorer sans casser l'API
            pass
        # Ajouter created_at si la colonne existe
        if hasattr(self, 'created_at') and self.created_at:
            result['created_at'] = self.created_at.isoformat()
            try:
                result['created_at_formatted'] = self.created_at.strftime('%d/%m/%Y')
            except Exception:
                pass
        return result

    @staticmethod
    def check_overlap(chauffeur_id, date_debut, date_fin, statut, exclude_id=None):
        """
        Vérifier les chevauchements selon les règles:
        - Si statut = CONGE: aucun chevauchement avec n'importe quel statut
        - Sinon: aucun chevauchement avec CONGE uniquement
        """
        query = ChauffeurStatut.query.filter(
            ChauffeurStatut.chauffeur_id == chauffeur_id,
            db.not_(db.or_(
                ChauffeurStatut.date_fin <= date_debut,
                ChauffeurStatut.date_debut >= date_fin
            ))
        )
        
        if exclude_id:
            query = query.filter(ChauffeurStatut.id != exclude_id)
        
        if statut == 'CONGE':
            # CONGE ne peut chevaucher avec aucun statut
            conflicting_statuts = query.all()
        else:
            # Les autres statuts ne peuvent chevaucher qu'avec CONGE
            conflicting_statuts = query.filter(ChauffeurStatut.statut == 'CONGE').all()
        
        return conflicting_statuts

    @staticmethod
    def get_current_statuts(chauffeur_id):
        """Récupérer les statuts actuels d'un chauffeur"""
        # Utiliser l'heure locale de l'application (Option A)
        # Hypothèse: le serveur/app tourne en GMT+1 comme demandé par l'utilisateur.
        # Si le serveur est en UTC, privilégier datetime.utcnow() OU convertir l'entrée en UTC côté enregistrement.
        db_now = datetime.now()
        statuts = ChauffeurStatut.query.filter(
            ChauffeurStatut.chauffeur_id == chauffeur_id,
            ChauffeurStatut.date_debut <= db_now,
            ChauffeurStatut.date_fin >= db_now
        ).all()
        
        # Debug: log pour vérifier
        import logging
        logging.info(f"[get_current_statuts] chauffeur_id={chauffeur_id}, using DB NOW(), found {len(statuts)} statuts")
        for s in statuts:
            logging.info(f"  - Statut: {s.statut}, début: {s.date_debut}, fin: {s.date_fin}")
        
        return statuts
