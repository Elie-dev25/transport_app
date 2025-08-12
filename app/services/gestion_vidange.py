from app.extensions import db
from app.models.aed import AED
from app.models.vidange import Vidange

def get_vidange_history(numero_aed=None):
    query = Vidange.query.join(AED, Vidange.aed_id == AED.id)
    if numero_aed:
        query = query.filter(AED.numero == numero_aed)
    return query.order_by(Vidange.date_vidange.desc()).all()
