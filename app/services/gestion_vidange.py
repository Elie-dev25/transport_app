from app.database import db
from app.models.bus_udm import BusUdM
from app.models.vidange import Vidange
from datetime import datetime

# Capacités par type d'huile (km)
OIL_CAPACITY_KM = {
    'Quartz 5000 20W-50': 5000,
    'Quartz 7000 10W-40': 7000,
    'Quartz 9000 5W-40': 9000,
    'Rubia TIR 7400 15W-40': 7400,
    'Rubia TIR 9900 FE 5W-30': 9900,
    'Rubia Fleet HD 400 15W-40': 400,
}


def get_vidange_history(numero_bus_udm=None, date_debut=None, date_fin=None):
    query = Vidange.query.join(BusUdM, Vidange.bus_udm_id == BusUdM.id)
    if numero_bus_udm:
        query = query.filter(BusUdM.numero == numero_bus_udm)
    if date_debut:
        query = query.filter(Vidange.date_vidange >= date_debut)
    if date_fin:
        query = query.filter(Vidange.date_vidange <= date_fin)
    # Tri: du plus récent au moins récent (date décroissante)
    return query.order_by(Vidange.date_vidange.desc()).all()


def compute_voyant(bus: BusUdM) -> str:
    """Calcule le voyant (green/orange/red) pour l'état vidange du bus."""
    voyant = 'green'
    if bus.kilometrage is not None and bus.km_critique_huile is not None:
        reste = bus.km_critique_huile - bus.kilometrage
        # Seuil orange basé sur 10% de l'intervalle lié au type d'huile.
        type_huile = getattr(bus, 'type_huile', None)
        intervalle = OIL_CAPACITY_KM.get(type_huile, 600)
        seuil_orange = 0.1 * intervalle
        if reste <= 0:
            return 'red'
        if reste <= seuil_orange:
            return 'orange'
    return voyant


def build_bus_vidange_list():
    """Retourne la liste des bus formatée pour l'écran vidange avec le voyant calculé."""
    bus_list = BusUdM.query.order_by(BusUdM.numero).all()
    result = []
    for bus in bus_list:
        result.append({
            'id': bus.id,
            'numero': bus.numero,
            'kilometrage': bus.kilometrage,
            'km_critique_huile': bus.km_critique_huile,
            'date_derniere_vidange': bus.date_derniere_vidange,
            'voyant': compute_voyant(bus)
        })
    return result


def enregistrer_vidange_common(data: dict) -> dict:
    """
    Valide les entrées, enregistre une vidange et met à jour le bus associé.
    Retourne un payload dict prêt pour jsonify.
    Lève ValueError (400) pour erreurs de validation et LookupError (404) si bus introuvable.
    """
    bus_udm_id = data.get('bus_udm_id')
    kilometrage = data.get('kilometrage')
    type_huile = data.get('type_huile')
    remarque = data.get('remarque')

    if not all([bus_udm_id, kilometrage, type_huile]):
        raise ValueError('Champs manquants.')

    # Cast et validations
    bus_udm_id_int = int(bus_udm_id)
    km_int = int(kilometrage)
    if km_int < 0:
        raise ValueError('Le kilométrage ne peut pas être négatif.')
    type_clean = (type_huile or '').strip()
    if type_clean not in OIL_CAPACITY_KM:
        raise ValueError("Type d'huile invalide. Veuillez choisir un type supporté.")

    bus = BusUdM.query.get(bus_udm_id_int)
    if not bus:
        raise LookupError('Bus introuvable.')

    # Autoriser égalité: le kilométrage saisi doit être supérieur ou égal au kilométrage actuel
    if bus.kilometrage is not None and km_int < bus.kilometrage:
        raise ValueError(f'Le kilométrage saisi ({km_int} km) doit être supérieur ou égal au kilométrage actuel ({bus.kilometrage} km).')

    # Persister la vidange
    vidange = Vidange(
        bus_udm_id=bus_udm_id_int,
        date_vidange=datetime.utcnow().date(),
        kilometrage=km_int,
        type_huile=type_clean,
        remarque=remarque
    )
    db.session.add(vidange)

    # Mettre à jour le bus: ajuster aussi le niveau carburant si le kilométrage évolue
    try:
        from app.services.trajet_service import update_autocontrol_after_km_change  # import local pour éviter les cycles
        prev_km = bus.kilometrage
        update_autocontrol_after_km_change(bus, km_int, prev_km)
    except Exception:
        # En cas d'échec (ex. import), on continue sans bloquer la vidange
        pass
    bus.kilometrage = km_int
    bus.type_huile = type_clean
    # Définir le km critique selon la capacité du type d'huile saisi
    bus.km_critique_huile = km_int + OIL_CAPACITY_KM.get(type_clean, 600)
    bus.date_derniere_vidange = datetime.utcnow().date()

    db.session.commit()

    voyant = compute_voyant(bus)
    return {
        'success': True,
        'bus_updated': {
            'id': bus.id,
            'numero': bus.numero,
            'kilometrage': bus.kilometrage,
            'km_critique_huile': bus.km_critique_huile,
            'date_derniere_vidange': bus.date_derniere_vidange.strftime('%d/%m/%Y'),
            'voyant': voyant
        }
    }
