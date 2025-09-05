from app.database import db
from sqlalchemy import Enum

class DocumentBusUdM(db.Model):
    __tablename__ = 'document_bus_udm'

    document_id = db.Column(db.Integer, primary_key=True)
    numero_bus_udm = db.Column(db.String(50), db.ForeignKey('bus_udm.numero'), nullable=False)
    type_document = db.Column(
        Enum(
            'VISITE_TECHNIQUE',
            'ASSURANCE_VIGNETTE',
            'TAXE_STATIONNEMENT',
            'TAXE_PUBLICITAIRE',
            'CARTE_GRISE',
            name='typedocumentenum'
        ),
        nullable=False
    )
    date_debut = db.Column(db.Date, nullable=False)
    date_expiration = db.Column(db.Date, nullable=True)

    # No fichier_url nor commentaire as per current requirements

    def __repr__(self):
        return f"<DocumentBusUdM {self.type_document} {self.numero_bus_udm}>"
