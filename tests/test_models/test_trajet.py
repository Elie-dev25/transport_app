"""Tests pour le modèle Trajet."""
import pytest
from datetime import datetime, date
from app.models.trajet import Trajet
from app.models.bus_udm import BusUdM
from app.extensions import db


class TestTrajet:
    def test_create_trajet(self, app):
        bus = BusUdM(numero='BUS_TR1', immatriculation='TR-001', nombre_places=20,
                     numero_chassis='CHASSIS_TR1', etat_vehicule='BON')
        db.session.add(bus)
        db.session.commit()
        trajet = Trajet(
            type_trajet='UDM_INTERNE',
            date_heure_depart=datetime.now(),
            point_depart='Mfetum',
            point_arriver='Banekane',
            numero_bus_udm='BUS_TR1',
            type_passagers='ETUDIANT',
            nombre_places_occupees=15,
        )
        db.session.add(trajet)
        db.session.commit()
        assert trajet.trajet_id is not None
        assert trajet.point_arriver == 'Banekane'
    
    def test_trajet_repr(self, app):
        trajet = Trajet(
            type_trajet='AUTRE',
            date_heure_depart=datetime(2024, 1, 1, 8, 0),
            point_depart='Mfetum',
            point_arriver='Test',
            motif='Mission',
        )
        db.session.add(trajet)
        db.session.commit()
        assert 'Trajet' in repr(trajet)
    
    def test_trajet_prestataire(self, app):
        from app.models.prestataire import Prestataire
        prest = Prestataire(nom_prestataire='Test Prest', localisation='Yaoundé')
        db.session.add(prest)
        db.session.commit()
        
        trajet = Trajet(
            type_trajet='PRESTATAIRE',
            date_heure_depart=datetime.now(),
            point_depart='Ancienne Mairie',
            point_arriver='Banekane',
            prestataire_id=prest.id,
            immat_bus='XX-999-YY',
            nom_chauffeur='Chauffeur Externe',
        )
        db.session.add(trajet)
        db.session.commit()
        assert trajet.prestataire_id == prest.id
    
    def test_trajet_query(self, app):
        for i in range(3):
            t = Trajet(
                type_trajet='UDM_INTERNE',
                date_heure_depart=datetime.now(),
                point_depart='Mfetum',
                point_arriver=f'Dest{i}',
            )
            db.session.add(t)
        db.session.commit()
        assert Trajet.query.count() == 3
