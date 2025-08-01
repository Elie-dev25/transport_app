from app.database import db
from sqlalchemy import Enum
from datetime import date

class DocumentAED(db.Model):
    __tablename__ = 'document_aed'

    document_id = db.Column(db.Integer, primary_key=True)
    numero_aed = db.Column(db.String(50), db.ForeignKey('aed.numero'), nullable=False)
    type_document = db.Column(
        Enum(
            'ASSURANCE',
            'VISITE_TECHNIQUE',
            'VIGNETTE',
            'FICHE_TECHNIQUE',
            'CARTE_GRISE',
            name='typedocumentenum'
        ),
        nullable=False
    )
    date_debut = db.Column(db.Date, nullable=False)
    date_expiration = db.Column(db.Date, nullable=True)

    # No fichier_url nor commentaire as per current requirements

    def __repr__(self):
        return f"<DocumentAED {self.type_document} {self.numero_aed}>"
