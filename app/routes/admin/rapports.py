from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import func, extract, and_, or_
from datetime import datetime, timedelta
from app.models.trajet import Trajet
from app.models.aed import AED
from app.models.chauffeur import Chauffeur
from app.models.carburation import Carburation
from app.models.panne_aed import PanneAED
from app.models.vidange import Vidange
from app.models.prestataire import Prestataire
from app.extensions import db

# Enregistrer les routes dans le blueprint admin principal
from . import bp

@bp.route('/rapports')
def rapports():
    """Page principale des rapports"""
    return render_template('rapports.html')

@bp.route('/api/rapports/test')
def test_rapports_data():
    """API de test avec données factices pour vérifier le fonctionnement"""
    data = {
        'performance_chauffeurs': [
            {'nom': 'Dupont Jean', 'nb_trajets': 15, 'taux_ponctualite': 95.5},
            {'nom': 'Martin Paul', 'nb_trajets': 12, 'taux_ponctualite': 88.2}
        ],
        'performance_prestataires': [
            {'nom_agence': 'Charter Express', 'nb_trajets': 8, 'satisfaction': 4.2},
            {'nom_agence': 'Noblesse Transport', 'nb_trajets': 5, 'satisfaction': 3.8}
        ],
        'suivi_kilometrage': [
            {'numero': 'AED001', 'kilometrage_actuel': 45000, 'derniere_vidange': '2024-01-01'},
            {'numero': 'AED002', 'kilometrage_actuel': 38000, 'derniere_vidange': '2024-02-10'}
        ],
        'utilisation_bus': [
            {'numero': 'AED001', 'nb_trajets': 45},
            {'numero': 'AED002', 'nb_trajets': 36}
        ],
        'couts_carburant': {
            'par_bus': [
                {'numero': 'AED001', 'cout_total': 1250.50},
                {'numero': 'AED002', 'cout_total': 980.75}
            ],
            'cout_global': 2231.25
        },
        'consommation_moyenne': [
            {'numero': 'AED001', 'consommation_theorique': 11.5, 'consommation_moyenne': 12.5},
            {'numero': 'AED002', 'consommation_theorique': 11.0, 'consommation_moyenne': 11.8}
        ],
        'budget_maintenance': {
            'par_criticite': [
                {'criticite': 'URGENT', 'nb_pannes': 5},
                {'criticite': 'MODERE', 'nb_pannes': 9}
            ],
            'par_bus': [
                {'numero': 'AED001', 'cout': 3200},
                {'numero': 'AED002', 'cout': 4600}
            ]
        },
        'roi_bus': [
            {'numero': 'AED001', 'cout_carburant': 1250.50, 'nb_trajets': 45},
            {'numero': 'AED002', 'cout_carburant': 980.75, 'nb_trajets': 36}
        ],
        'historique_pannes': [
            {'numero_aed': 'AED001', 'date_heure': '2024-01-15 10:30', 'description': 'Problème moteur', 'criticite': 'URGENT', 'immobilisation': True},
            {'numero_aed': 'AED002', 'date_heure': '2024-01-10 14:20', 'description': 'Pneu crevé', 'criticite': 'MODERE', 'immobilisation': False}
        ],
        'planning_vidanges': [
            {'numero': 'AED001', 'kilometrage_actuel': 45000, 'km_critique': 50000, 'km_restants': 5000, 'derniere_vidange': '2024-01-01', 'urgence': 'Modere'},
            {'numero': 'AED002', 'kilometrage_actuel': 38000, 'km_critique': 40000, 'km_restants': 2000, 'derniere_vidange': '2024-02-10', 'urgence': 'Urgent'}
        ],
        'periode': 'test'
    }
    
    print("Debug: API de test appelée avec succès")
    return jsonify(data)

@bp.route('/api/rapports/data')
def get_rapports_data():
    """API pour récupérer toutes les données des rapports"""
    try:
        periode = request.args.get('periode', 'jour')  # jour, semaine, mois, annee
        
        # Calculer les dates selon la période
        now = datetime.now()
        if periode == 'jour':
            date_debut = now.replace(hour=0, minute=0, second=0, microsecond=0)
            date_fin = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif periode == 'semaine':
            date_debut = now - timedelta(days=now.weekday())
            date_debut = date_debut.replace(hour=0, minute=0, second=0, microsecond=0)
            date_fin = date_debut + timedelta(days=6, hours=23, minutes=59, seconds=59)
        elif periode == 'mois':
            date_debut = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                date_fin = now.replace(year=now.year+1, month=1, day=1) - timedelta(seconds=1)
            else:
                date_fin = now.replace(month=now.month+1, day=1) - timedelta(seconds=1)
        else:  # annee
            date_debut = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            date_fin = now.replace(month=12, day=31, hour=23, minute=59, second=59)

        # Debug: vérifier les données disponibles
        print(f"Debug: Période demandée: {periode}")
        print(f"Debug: Date début: {date_debut}, Date fin: {date_fin}")
        
        performance_chauffeurs = get_performance_chauffeurs(date_debut, date_fin)
        performance_prestataires = get_performance_prestataires(date_debut, date_fin)
        suivi_kilometrage = get_suivi_kilometrage()
        
        print(f"Debug: Chauffeurs trouvés: {len(performance_chauffeurs)}")
        print(f"Debug: Prestataires trouvés: {len(performance_prestataires)}")
        print(f"Debug: Bus AED trouvés: {len(suivi_kilometrage)}")
        
        data = {
            'performance_chauffeurs': performance_chauffeurs,
            'performance_prestataires': performance_prestataires,
            'suivi_kilometrage': suivi_kilometrage,
            'utilisation_bus': get_utilisation_bus(date_debut, date_fin),
            'couts_carburant': get_couts_carburant(),
            'consommation_moyenne': get_consommation_moyenne(),
            'budget_maintenance': get_budget_maintenance(),
            'roi_bus': get_roi_bus(),
            'historique_pannes': get_historique_pannes(),
            'planning_vidanges': get_planning_vidanges(),
            'periode': periode
        }
        
        return jsonify(data)
    
    except Exception as e:
        print(f"Erreur API rapports: {e}")
        return jsonify({
            'error': str(e),
            'performance_chauffeurs': [],
            'performance_prestataires': [],
            'suivi_kilometrage': [],
            'utilisation_bus': [],
            'couts_carburant': {'par_bus': [], 'cout_global': 0},
            'consommation_moyenne': [],
            'budget_maintenance': {'par_criticite': [], 'par_bus': []},
            'roi_bus': [],
            'historique_pannes': [],
            'planning_vidanges': [],
            'periode': periode
        })

def get_performance_chauffeurs(date_debut, date_fin):
    """Performance des chauffeurs (nombre de trajets)"""
    performance = db.session.query(
        Chauffeur.nom,
        Chauffeur.prenom,
        func.count(Trajet.trajet_id).label('nb_trajets')
    ).join(
        Trajet, Chauffeur.chauffeur_id == Trajet.chauffeur_id
    ).filter(
        and_(
            Trajet.date_heure_depart >= date_debut,
            Trajet.date_heure_depart <= date_fin
        )
    ).group_by(
        Chauffeur.chauffeur_id, Chauffeur.nom, Chauffeur.prenom
    ).order_by(
        func.count(Trajet.trajet_id).desc()
    ).all()
    
    return [
        {
            'nom': f"{p.nom} {p.prenom}",
            'nb_trajets': p.nb_trajets
        }
        for p in performance
    ]

def get_performance_prestataires(date_debut, date_fin):
    """Performance des prestataires (nombre de trajets)"""
    performance = db.session.query(
        Prestataire.nom_agence,
        func.count(Trajet.trajet_id).label('nb_trajets')
    ).join(
        Trajet, Prestataire.immatriculation == Trajet.immat_bus
    ).filter(
        and_(
            Trajet.date_heure_depart >= date_debut,
            Trajet.date_heure_depart <= date_fin
        )
    ).group_by(
        Prestataire.nom_agence
    ).order_by(
        func.count(Trajet.trajet_id).desc()
    ).all()
    
    return [
        {
            'nom_agence': p.nom_agence,
            'nb_trajets': p.nb_trajets
        }
        for p in performance
    ]

def get_suivi_kilometrage():
    """Évolution du kilométrage par bus"""
    buses = db.session.query(AED).all()
    
    return [
        {
            'numero': bus.numero,
            'kilometrage_actuel': bus.kilometrage or 0,
            'immatriculation': bus.immatriculation
        }
        for bus in buses
    ]

def get_utilisation_bus(date_debut, date_fin):
    """Taux d'utilisation par véhicule"""
    # Nombre total de trajets par bus AED
    utilisation_aed = db.session.query(
        AED.numero,
        AED.immatriculation,
        func.count(Trajet.trajet_id).label('nb_trajets')
    ).outerjoin(
        Trajet, AED.numero == Trajet.numero_aed
    ).filter(
        or_(
            Trajet.date_heure_depart.is_(None),
            and_(
                Trajet.date_heure_depart >= date_debut,
                Trajet.date_heure_depart <= date_fin
            )
        )
    ).group_by(
        AED.numero, AED.immatriculation
    ).all()
    
    return [
        {
            'numero': u.numero,
            'immatriculation': u.immatriculation,
            'nb_trajets': u.nb_trajets,
            'type': 'AED'
        }
        for u in utilisation_aed
    ]

def get_couts_carburant():
    """Évolution des dépenses carburant"""
    # Coûts par bus
    couts_par_bus = db.session.query(
        AED.numero,
        func.sum(Carburation.cout_total).label('cout_total'),
        func.sum(Carburation.quantite_litres).label('quantite_totale')
    ).join(
        Carburation, AED.id == Carburation.aed_id
    ).group_by(
        AED.numero
    ).all()
    
    # Coût total global
    cout_global = db.session.query(
        func.sum(Carburation.cout_total).label('cout_total_global')
    ).scalar() or 0
    
    return {
        'par_bus': [
            {
                'numero': c.numero,
                'cout_total': float(c.cout_total or 0),
                'quantite_totale': float(c.quantite_totale or 0)
            }
            for c in couts_par_bus
        ],
        'cout_global': float(cout_global)
    }

def get_consommation_moyenne():
    """Analyse de la consommation par km"""
    consommation = db.session.query(
        AED.numero,
        AED.consommation_km_par_litre,
        func.avg(Carburation.quantite_litres).label('conso_moyenne')
    ).join(
        Carburation, AED.id == Carburation.aed_id
    ).group_by(
        AED.numero, AED.consommation_km_par_litre
    ).all()
    
    return [
        {
            'numero': c.numero,
            'consommation_theorique': float(c.consommation_km_par_litre or 0),
            'consommation_moyenne': float(c.conso_moyenne or 0)
        }
        for c in consommation
    ]

def get_budget_maintenance():
    """Coûts des pannes et réparations"""
    # Nombre de pannes par criticité
    pannes_par_criticite = db.session.query(
        PanneAED.criticite,
        func.count(PanneAED.id).label('nb_pannes')
    ).group_by(
        PanneAED.criticite
    ).all()
    
    # Pannes par bus
    pannes_par_bus = db.session.query(
        PanneAED.numero_aed,
        func.count(PanneAED.id).label('nb_pannes'),
        func.sum(func.case([(PanneAED.immobilisation == True, 1)], else_=0)).label('nb_immobilisations')
    ).group_by(
        PanneAED.numero_aed
    ).all()
    
    return {
        'par_criticite': [
            {
                'criticite': p.criticite,
                'nb_pannes': p.nb_pannes
            }
            for p in pannes_par_criticite
        ],
        'par_bus': [
            {
                'numero_aed': p.numero_aed,
                'nb_pannes': p.nb_pannes,
                'nb_immobilisations': p.nb_immobilisations
            }
            for p in pannes_par_bus
        ]
    }

def get_roi_bus():
    """Rentabilité de chaque véhicule (estimation basée sur utilisation vs coûts)"""
    # Calcul simplifié : nb trajets vs coûts carburant
    roi_data = db.session.query(
        AED.numero,
        func.count(Trajet.trajet_id).label('nb_trajets'),
        func.coalesce(func.sum(Carburation.cout_total), 0).label('cout_carburant')
    ).outerjoin(
        Trajet, AED.numero == Trajet.numero_aed
    ).outerjoin(
        Carburation, AED.id == Carburation.aed_id
    ).group_by(
        AED.numero
    ).all()
    
    return [
        {
            'numero': r.numero,
            'nb_trajets': r.nb_trajets,
            'cout_carburant': float(r.cout_carburant),
            'ratio_efficacite': r.nb_trajets / max(float(r.cout_carburant), 1)  # Éviter division par 0
        }
        for r in roi_data
    ]

def get_historique_pannes():
    """Fréquence et criticité des pannes par bus"""
    pannes = db.session.query(
        PanneAED.numero_aed,
        PanneAED.criticite,
        PanneAED.date_heure,
        PanneAED.description,
        PanneAED.immobilisation
    ).order_by(
        PanneAED.date_heure.desc()
    ).limit(50).all()  # Limiter aux 50 dernières pannes
    
    return [
        {
            'numero_aed': p.numero_aed,
            'criticite': p.criticite,
            'date_heure': p.date_heure.strftime('%Y-%m-%d %H:%M'),
            'description': p.description,
            'immobilisation': p.immobilisation
        }
        for p in pannes
    ]

def get_planning_vidanges():
    """Prochaines vidanges dues"""
    # Bus nécessitant une vidange (basé sur le kilométrage critique)
    buses_vidange = db.session.query(
        AED.numero,
        AED.kilometrage,
        AED.km_critique_huile,
        func.max(Vidange.date_vidange).label('derniere_vidange')
    ).outerjoin(
        Vidange, AED.id == Vidange.aed_id
    ).group_by(
        AED.numero, AED.kilometrage, AED.km_critique_huile
    ).all()
    
    planning = []
    for bus in buses_vidange:
        if bus.km_critique_huile and bus.kilometrage:
            km_restants = bus.km_critique_huile - bus.kilometrage
            if km_restants <= 1000:  # Alerte si moins de 1000 km
                planning.append({
                    'numero': bus.numero,
                    'kilometrage_actuel': bus.kilometrage,
                    'km_critique': bus.km_critique_huile,
                    'km_restants': km_restants,
                    'derniere_vidange': bus.derniere_vidange.strftime('%Y-%m-%d') if bus.derniere_vidange else 'Aucune',
                    'urgence': 'CRITIQUE' if km_restants <= 500 else 'ATTENTION'
                })
    
    return sorted(planning, key=lambda x: x['km_restants'])