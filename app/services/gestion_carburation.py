from app.database import db
from app.models.aed import AED
from datetime import datetime


def get_carburation_history(numero_aed=None, date_debut=None, date_fin=None):
    """Retourne l'historique des carburations, trié du plus récent au moins récent.
    date_debut et date_fin sont des objets date optionnels pour filtrer l'intervalle.
    """
    # Import local pour éviter les imports circulaires
    from app.models.carburation import Carburation

    query = Carburation.query.join(AED, Carburation.aed_id == AED.id)
    if numero_aed:
        query = query.filter(AED.numero == numero_aed)
    if date_debut:
        query = query.filter(Carburation.date_carburation >= date_debut)
    if date_fin:
        query = query.filter(Carburation.date_carburation <= date_fin)
    # Tri: du plus récent au moins récent (date décroissante)
    return query.order_by(Carburation.date_carburation.desc()).all()


def compute_voyant_carburant(bus: AED) -> str:
    """Calcule le voyant (green/orange/red) pour l'état carburant du bus."""
    voyant = 'green'
    if bus.kilometrage is not None and bus.km_critique_carburant is not None:
        # Reste d'autonomie (km) avant le seuil critique
        reste = bus.km_critique_carburant - bus.kilometrage
        # Seuil orange = 10% de l'autonomie totale (si connue). Fallback: 10% du reste courant.
        seuil_orange = None
        try:
            capacite_km = float(getattr(bus, 'capacite_plein_carburant', 0) or 0)
        except (TypeError, ValueError):
            capacite_km = 0.0
        if capacite_km > 0:
            seuil_orange = 0.1 * capacite_km
        else:
            # Essayer d'inférer via km/L et capacité réservoir
            try:
                cap_res_l = float(getattr(bus, 'capacite_reservoir_litres', 0) or 0)
            except (TypeError, ValueError):
                cap_res_l = 0.0
            km_par_litre = None
            if cap_res_l > 0 and capacite_km > 0:
                km_par_litre = capacite_km / cap_res_l
            # Fallback: 10% du reste si on ne peut rien déduire de plus stable
            seuil_orange = 0.1 * reste if km_par_litre is None else 0.1 * (km_par_litre * cap_res_l)

        if reste <= 0:
            return 'red'
        if seuil_orange is not None and reste <= seuil_orange:
            return 'orange'
    return voyant


def build_bus_carburation_list():
    """Retourne la liste des bus formatée pour l'écran carburation avec le voyant calculé."""
    bus_list = AED.query.order_by(AED.numero).all()
    result = []
    for bus in bus_list:
        km_restant_carburant = None
        if bus.kilometrage is not None and bus.km_critique_carburant is not None:
            km_restant_carburant = bus.km_critique_carburant - bus.kilometrage
        
        result.append({
            'id': bus.id,
            'numero': bus.numero,
            'immatriculation': getattr(bus, 'immatriculation', None),
            'kilometrage': bus.kilometrage,
            'capacite_plein_carburant': bus.capacite_plein_carburant,
            'km_critique_carburant': round(bus.km_critique_carburant, 3) if bus.km_critique_carburant is not None else None,
            'km_restant_carburant': km_restant_carburant,
            'niveau_carburant_litres': round(getattr(bus, 'niveau_carburant_litres', 0.0), 3) if getattr(bus, 'niveau_carburant_litres', None) is not None else None,
            'voyant': compute_voyant_carburant(bus)
        })
    return result


def enregistrer_carburation_common(data: dict) -> dict:
    """
    Valide les entrées, enregistre une carburation et met à jour le bus associé.
    Retourne un payload dict prêt pour jsonify.
    Lève ValueError (400) pour erreurs de validation et LookupError (404) si bus introuvable.
    """
    # Import local pour éviter les imports circulaires
    from app.models.carburation import Carburation
    
    aed_id = data.get('aed_id')
    kilometrage = data.get('kilometrage')
    quantite_litres = data.get('quantite_litres')
    prix_unitaire = data.get('prix_unitaire')
    cout_total = data.get('cout_total')
    remarque = data.get('remarque')

    if not all([aed_id, kilometrage, quantite_litres, prix_unitaire]):
        raise ValueError('Champs manquants.')

    # Cast et validations
    aed_id_int = int(aed_id)
    km_int = int(kilometrage)
    quantite_float = float(quantite_litres)
    prix_float = float(prix_unitaire)
    cout_float = float(cout_total) if cout_total else quantite_float * prix_float
    # Arrondir le coût total à 3 décimales
    cout_float = round(cout_float, 3)
    
    if km_int < 0:
        raise ValueError('Le kilométrage ne peut pas être négatif.')
    if quantite_float <= 0:
        raise ValueError('La quantité doit être positive.')
    if prix_float <= 0:
        raise ValueError('Le prix unitaire doit être positif.')

    bus = AED.query.get(aed_id_int)
    if not bus:
        raise LookupError('Bus introuvable.')

    if bus.kilometrage is not None and km_int < bus.kilometrage:
        raise ValueError(f'Le kilométrage saisi ({km_int} km) doit être supérieur ou égal au kilométrage actuel ({bus.kilometrage} km).')

    # Persister la carburation
    carburation = Carburation(
        aed_id=aed_id_int,
        date_carburation=datetime.utcnow().date(),
        kilometrage=km_int,
        quantite_litres=quantite_float,
        prix_unitaire=prix_float,
        cout_total=cout_float,
        remarque=remarque
    )
    db.session.add(carburation)

    # Mettre à jour le bus (kilométrage, niveau carburant et portée jusqu'au seuil critique)
    bus.kilometrage = km_int

    # 1) Mettre à jour le niveau de carburant (L)
    try:
        capacite_reservoir = float(getattr(bus, 'capacite_reservoir_litres', 0) or 0)
    except (TypeError, ValueError):
        capacite_reservoir = 0.0
    prev_niveau = getattr(bus, 'niveau_carburant_litres', None)
    base = float(prev_niveau) if prev_niveau is not None else 0.0
    nouveau_niveau = base + quantite_float
    if capacite_reservoir > 0:
        nouveau_niveau = min(nouveau_niveau, capacite_reservoir)
    if hasattr(bus, 'niveau_carburant_litres'):
        bus.niveau_carburant_litres = round(nouveau_niveau, 3)

    # 2) Estimer km/L
    try:
        capacite_km_full = float(getattr(bus, 'capacite_plein_carburant', 0) or 0)
    except (TypeError, ValueError):
        capacite_km_full = 0.0
    km_par_litre_defaut = 8.0  # valeur par défaut si on ne peut pas déduire
    if capacite_km_full > 0 and capacite_reservoir > 0:
        km_par_litre = capacite_km_full / capacite_reservoir
    else:
        km_par_litre = km_par_litre_defaut

    # 3) Déterminer le km critique carburant à partir du niveau courant
    autonomie_estimee = (nouveau_niveau * km_par_litre)
    bus.km_critique_carburant = round(km_int + autonomie_estimee, 3)

    db.session.commit()

    km_restant_carburant = (bus.km_critique_carburant - bus.kilometrage) if bus.km_critique_carburant else None
    if km_restant_carburant is not None:
        km_restant_carburant = round(km_restant_carburant, 3)
    voyant = compute_voyant_carburant(bus)
    
    return {
        'success': True,
        'bus_updated': {
            'id': bus.id,
            'numero': bus.numero,
            'kilometrage': bus.kilometrage,
            'km_critique_carburant': bus.km_critique_carburant,
            'km_restant_carburant': km_restant_carburant,
            'niveau_carburant_litres': getattr(bus, 'niveau_carburant_litres', None),
            'voyant': voyant
        }
    }
