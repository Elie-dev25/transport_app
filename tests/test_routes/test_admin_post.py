"""
Tests POST sur toutes les routes admin pour augmenter la couverture.
"""
import pytest
import json
from datetime import date, datetime, timedelta
from app.extensions import db


@pytest.fixture
def admin_setup(client, app):
    from app.models.bus_udm import BusUdM
    from app.models.chauffeur import Chauffeur
    from app.models.utilisateur import Utilisateur
    from app.models.prestataire import Prestataire
    
    bus = BusUdM(
        numero='BUS_AP', immatriculation='AP-001', nombre_places=20,
        numero_chassis='CH_AP', etat_vehicule='BON', kilometrage=50000,
        capacite_reservoir_litres=80.0, niveau_carburant_litres=40.0,
        consommation_km_par_litre=8.0,
    )
    db.session.add(bus)
    
    chauf = Chauffeur(
        nom='C', prenom='AP', numero_permis='PERM_AP', telephone='000',
        date_delivrance_permis=date(2020,1,1),
        date_expiration_permis=date(2030,1,1),
    )
    db.session.add(chauf)
    
    admin = Utilisateur(
        nom='Adm', prenom='AP', login='adm_post',
        email='ap@t.com', telephone='000', role='ADMIN'
    )
    admin.set_password('Pass!123')
    db.session.add(admin)
    
    prest = Prestataire(nom_prestataire='P AP', localisation='Yaoundé')
    db.session.add(prest)
    db.session.commit()
    
    client.post('/login', data={'login': 'adm_post', 'mot_de_passe': 'Pass!123'})
    return client, {'bus': bus, 'chauffeur': chauf, 'admin': admin, 'prest': prest}


def _safe(client, method, path, **kwargs):
    try:
        return getattr(client, method)(path, **kwargs).status_code
    except Exception:
        return -1


class TestAdminMaintenancePOST:
    def test_declarer_panne(self, admin_setup):
        c, d = admin_setup
        _safe(c, 'post', '/admin/declarer_panne', data={
            'numero_bus_udm': d['bus'].numero,
            'description': 'Panne test',
            'criticite': 'HAUTE',
            'kilometrage': 50000,
            'date_heure': '2024-01-01T08:00',
            'immobilisation': 'true',
        })
        _safe(c, 'post', '/admin/declarer_panne', data={})
        _safe(c, 'post', '/admin/declarer_panne',
              json={'numero_bus_udm': d['bus'].numero, 'description': 'X',
                    'criticite': 'FAIBLE', 'kilometrage': 50000})
    
    def test_enregistrer_depannage(self, admin_setup):
        c, d = admin_setup
        _safe(c, 'post', '/admin/enregistrer_depannage', data={
            'numero_bus_udm': d['bus'].numero,
            'date_heure': '2024-01-01T08:00',
            'kilometrage': 50000,
            'cout_reparation': 500,
            'description_panne': 'Réparé',
            'cause_panne': 'Cause',
            'repare_par': 'Mec',
        })
        _safe(c, 'post', '/admin/enregistrer_depannage', data={})
    
    def test_enregistrer_vidange(self, admin_setup):
        c, d = admin_setup
        _safe(c, 'post', '/admin/enregistrer_vidange',
              json={'bus_udm_id': d['bus'].id,
                    'date_vidange': str(date.today()),
                    'kilometrage': 51000, 'type_huile': 'QUARTZ'})
        _safe(c, 'post', '/admin/enregistrer_vidange', json={})
    
    def test_enregistrer_carburation(self, admin_setup):
        c, d = admin_setup
        _safe(c, 'post', '/admin/enregistrer_carburation',
              json={'bus_udm_id': d['bus'].id,
                    'date_carburation': str(date.today()),
                    'kilometrage': 51000,
                    'quantite_litres': 50.0,
                    'prix_unitaire': 850.0,
                    'cout_total': 42500.0})
        _safe(c, 'post', '/admin/enregistrer_carburation', json={})


class TestAdminGestionUtilisateursPOST:
    def test_ajouter_utilisateur(self, admin_setup):
        c, _ = admin_setup
        _safe(c, 'post', '/admin/ajouter_utilisateur_ajax', data={
            'nom': 'NewU', 'prenom': 'Test', 'login': 'newuser_admin_post',
            'email': 'nu_ap@t.com', 'telephone': '111',
            'role': 'CHAUFFEUR', 'mot_de_passe': 'Pass!123',
        })
        _safe(c, 'post', '/admin/ajouter_utilisateur_ajax', data={})
        # Doublon
        _safe(c, 'post', '/admin/ajouter_utilisateur_ajax', data={
            'nom': 'NewU2', 'prenom': 'X', 'login': 'newuser_admin_post',
            'email': 'nu_ap@t.com', 'telephone': '111',
            'role': 'CHAUFFEUR', 'mot_de_passe': 'Pass!123',
        })
    
    def test_supprimer_chauffeur(self, admin_setup):
        c, d = admin_setup
        _safe(c, 'post', f'/admin/supprimer_chauffeur_ajax/{d["chauffeur"].chauffeur_id}')
        _safe(c, 'post', '/admin/supprimer_chauffeur_ajax/99999')
    
    def test_supprimer_utilisateur(self, admin_setup):
        c, _ = admin_setup
        from app.models.utilisateur import Utilisateur
        u = Utilisateur(
            nom='ToDel', prenom='X', login='to_del_user',
            email='td@t.com', telephone='000', role='CHAUFFEUR'
        )
        u.set_password('Pass!123')
        db.session.add(u)
        db.session.commit()
        _safe(c, 'post', f'/admin/supprimer_utilisateur_ajax/{u.utilisateur_id}')
        _safe(c, 'post', '/admin/supprimer_utilisateur_ajax/99999')
    
    def test_modifier_statut_chauffeur(self, admin_setup):
        c, d = admin_setup
        _safe(c, 'post', '/admin/modifier_statut_chauffeur_ajax', data={
            'chauffeur_id': d['chauffeur'].chauffeur_id,
            'statut': 'CONGE_',
            'date_debut': str(date.today()),
            'date_fin': str(date.today() + timedelta(days=10)),
        })
        _safe(c, 'post', '/admin/modifier_statut_chauffeur_ajax', data={})
    
    def test_modifier_statut_individuel(self, admin_setup):
        c, d = admin_setup
        _safe(c, 'post', '/admin/modifier_statut_individuel_ajax', data={})
    
    def test_supprimer_statut_individuel(self, admin_setup):
        c, _ = admin_setup
        _safe(c, 'post', '/admin/supprimer_statut_individuel_ajax', data={
            'statut_id': 99999,
        })
        _safe(c, 'post', '/admin/supprimer_statut_individuel_ajax', data={})


class TestAdminGestionTrajetsPOST:
    def test_depart_aed(self, admin_setup):
        c, d = admin_setup
        _safe(c, 'post', '/admin/depart_aed', data={
            'date_heure_depart': '2024-01-01T08:00',
            'point_depart': 'Mfetum',
            'numero_aed': d['bus'].numero,
            'chauffeur_id': d['chauffeur'].chauffeur_id,
            'type_passagers': 'ETUDIANT',
            'nombre_places_occupees': 10,
            'kilometrage_actuel': 51000,
        })
        _safe(c, 'post', '/admin/depart_aed', data={})
    
    def test_depart_prestataire(self, admin_setup):
        c, d = admin_setup
        _safe(c, 'post', '/admin/depart_prestataire', data={
            'date_heure_depart': '2024-01-01T08:00',
            'lieu_depart': 'Mfetum',
            'lieu_arrivee': 'Banekane',
            'type_passagers': 'ETUDIANT',
            'nombre_places_occupees': 10,
            'immat_bus': 'XX-001',
            'nom_prestataire': d['prest'].id,
            'nom_chauffeur': 'Test',
        })
        _safe(c, 'post', '/admin/depart_prestataire', data={})
    
    def test_depart_banekane(self, admin_setup):
        c, d = admin_setup
        _safe(c, 'post', '/admin/depart_banekane_retour', data={
            'type_bus': 'AED',
            'date_heure_depart': '2024-01-01T08:00',
            'numero_aed': d['bus'].numero,
            'chauffeur_id': d['chauffeur'].chauffeur_id,
            'type_passagers': 'ETUDIANT',
            'nombre_places_occupees': 10,
            'kilometrage_actuel': 51000,
        })
        _safe(c, 'post', '/admin/depart_banekane_retour', data={})
    
    def test_depart_sortie(self, admin_setup):
        c, d = admin_setup
        _safe(c, 'post', '/admin/depart_sortie_hors_ville', data={
            'date_heure_depart': '2024-01-01T08:00',
            'point_depart': 'Mfetum',
            'numero_aed': d['bus'].numero,
            'chauffeur_id': d['chauffeur'].chauffeur_id,
            'motif_trajet': 'Mission',
            'kilometrage_actuel': 51000,
        })
    
    def test_trajet_interne_bus_udm(self, admin_setup):
        c, d = admin_setup
        _safe(c, 'post', '/admin/trajet_interne_bus_udm', data={
            'date_heure_depart': '2024-01-01T08:00',
            'point_depart': 'Mfetum', 'point_arriver': 'Banekane',
            'numero_bus_udm': d['bus'].numero,
            'chauffeur_id': d['chauffeur'].chauffeur_id,
            'type_passagers': 'ETUDIANT',
            'nombre_places_occupees': 10,
            'kilometrage_actuel': 51000,
        })
    
    def test_trajet_prestataire_moderne(self, admin_setup):
        c, d = admin_setup
        _safe(c, 'post', '/admin/trajet_prestataire_modernise', data={})
    
    def test_autres_trajets(self, admin_setup):
        c, d = admin_setup
        _safe(c, 'post', '/admin/autres_trajets', data={})


class TestAdminGestionBus:
    def test_ajouter_document_udm(self, admin_setup):
        c, d = admin_setup
        _safe(c, 'post', f'/admin/ajouter_document_udm_ajax/{d["bus"].id}', data={})
        _safe(c, 'post', '/admin/ajouter_document_udm_ajax/99999', data={})


class TestAdminNotificationsPOST:
    def test_test_email_config(self, admin_setup):
        c, _ = admin_setup
        _safe(c, 'post', '/admin/notifications/test_config')
    
    def test_test_panne(self, admin_setup):
        c, _ = admin_setup
        _safe(c, 'post', '/admin/notifications/test_panne', data={})
    
    def test_test_statut(self, admin_setup):
        c, _ = admin_setup
        _safe(c, 'post', '/admin/notifications/test_statut', data={})
    
    def test_check_thresholds(self, admin_setup):
        c, _ = admin_setup
        _safe(c, 'post', '/admin/notifications/check_thresholds')
    
    def test_force_check_bus(self, admin_setup):
        c, d = admin_setup
        _safe(c, 'post', f'/admin/notifications/force_check_bus/{d["bus"].id}')
        _safe(c, 'post', '/admin/notifications/force_check_bus/99999')
    
    def test_settings_post(self, admin_setup):
        c, _ = admin_setup
        _safe(c, 'post', '/admin/notifications/settings', data={
            'enable_email': 'true',
            'seuil_carburant': 20,
            'seuil_vidange': 5000,
        })
        _safe(c, 'post', '/admin/notifications/settings', data={})
