"""
Tests pour le modèle Chauffeur.
"""
import pytest
from datetime import date, timedelta
from app.models.chauffeur import Chauffeur
from app.database import db


class TestChauffeur:
    """Tests pour le modèle Chauffeur."""
    
    def test_create_chauffeur(self, app):
        """Test de création d'un chauffeur."""
        with app.app_context():
            chauffeur = Chauffeur(
                nom='Martin',
                prenom='Pierre',
                numero_permis='PERM123456',
                telephone='0612345678',
                date_delivrance_permis=date(2020, 1, 15),
                date_expiration_permis=date(2030, 1, 15)
            )
            db.session.add(chauffeur)
            db.session.commit()
            
            assert chauffeur.chauffeur_id is not None
            assert chauffeur.nom == 'Martin'
            assert chauffeur.prenom == 'Pierre'
            assert chauffeur.numero_permis == 'PERM123456'
    
    def test_chauffeur_repr(self, app):
        """Test de la représentation string du chauffeur."""
        with app.app_context():
            chauffeur = Chauffeur(
                nom='Durand',
                prenom='Marie',
                numero_permis='PERM789012',
                telephone='0698765432',
                date_delivrance_permis=date(2019, 6, 1),
                date_expiration_permis=date(2029, 6, 1)
            )
            db.session.add(chauffeur)
            db.session.commit()
            
            repr_str = repr(chauffeur)
            assert 'Durand' in repr_str
            assert 'Marie' in repr_str
    
    def test_nom_complet_property(self, app):
        """Test de la propriété nom_complet."""
        with app.app_context():
            chauffeur = Chauffeur(
                nom='Dupont',
                prenom='Jean',
                numero_permis='PERM111111',
                telephone='0600000001',
                date_delivrance_permis=date(2018, 3, 10),
                date_expiration_permis=date(2028, 3, 10)
            )
            
            assert chauffeur.nom_complet == 'Jean Dupont'
    
    def test_get_full_info(self, app):
        """Test de la méthode get_full_info."""
        with app.app_context():
            date_deliv = date(2021, 5, 20)
            date_exp = date(2031, 5, 20)
            
            chauffeur = Chauffeur(
                nom='Bernard',
                prenom='Sophie',
                numero_permis='PERM222222',
                telephone='0600000002',
                date_delivrance_permis=date_deliv,
                date_expiration_permis=date_exp
            )
            db.session.add(chauffeur)
            db.session.commit()
            
            info = chauffeur.get_full_info()
            
            assert info['nom'] == 'Bernard'
            assert info['prenom'] == 'Sophie'
            assert info['nom_complet'] == 'Sophie Bernard'
            assert info['numero_permis'] == 'PERM222222'
            assert info['telephone'] == '0600000002'
            assert info['date_delivrance_permis'] == date_deliv
            assert info['date_expiration_permis'] == date_exp
            assert info['id'] == chauffeur.chauffeur_id
    
    def test_is_permis_expire_valid(self, app):
        """Test d'un permis non expiré."""
        with app.app_context():
            future_date = date.today() + timedelta(days=365)
            
            chauffeur = Chauffeur(
                nom='Test',
                prenom='Valid',
                numero_permis='PERM333333',
                telephone='0600000003',
                date_delivrance_permis=date(2020, 1, 1),
                date_expiration_permis=future_date
            )
            
            assert chauffeur.is_permis_expire() is False
    
    def test_is_permis_expire_expired(self, app):
        """Test d'un permis expiré."""
        with app.app_context():
            past_date = date.today() - timedelta(days=30)
            
            chauffeur = Chauffeur(
                nom='Test',
                prenom='Expired',
                numero_permis='PERM444444',
                telephone='0600000004',
                date_delivrance_permis=date(2015, 1, 1),
                date_expiration_permis=past_date
            )
            
            assert chauffeur.is_permis_expire() is True
    
    def test_is_permis_expire_today(self, app):
        """Test d'un permis expirant aujourd'hui."""
        with app.app_context():
            today = date.today()
            
            chauffeur = Chauffeur(
                nom='Test',
                prenom='Today',
                numero_permis='PERM555555',
                telephone='0600000005',
                date_delivrance_permis=date(2020, 1, 1),
                date_expiration_permis=today
            )
            
            # Un permis expirant aujourd'hui est considéré comme expiré
            assert chauffeur.is_permis_expire() is True
    
    def test_chauffeur_telephone_required(self, app):
        """Test que le téléphone est obligatoire."""
        with app.app_context():
            chauffeur = Chauffeur(
                nom='Test',
                prenom='NoPhone',
                numero_permis='PERM666666',
                date_delivrance_permis=date(2020, 1, 1),
                date_expiration_permis=date(2030, 1, 1)
                # telephone manquant
            )
            db.session.add(chauffeur)
            
            with pytest.raises(Exception):
                db.session.commit()
    
    def test_chauffeur_query_by_nom(self, app):
        """Test de requête par nom."""
        with app.app_context():
            chauffeur1 = Chauffeur(
                nom='Recherche',
                prenom='Test1',
                numero_permis='PERM777771',
                telephone='0600000007',
                date_delivrance_permis=date(2020, 1, 1),
                date_expiration_permis=date(2030, 1, 1)
            )
            chauffeur2 = Chauffeur(
                nom='Autre',
                prenom='Test2',
                numero_permis='PERM777772',
                telephone='0600000008',
                date_delivrance_permis=date(2020, 1, 1),
                date_expiration_permis=date(2030, 1, 1)
            )
            db.session.add_all([chauffeur1, chauffeur2])
            db.session.commit()
            
            results = Chauffeur.query.filter_by(nom='Recherche').all()
            assert len(results) == 1
            assert results[0].prenom == 'Test1'
    
    def test_multiple_chauffeurs(self, app):
        """Test de création de plusieurs chauffeurs."""
        with app.app_context():
            for i in range(5):
                chauffeur = Chauffeur(
                    nom=f'Chauffeur{i}',
                    prenom=f'Prenom{i}',
                    numero_permis=f'PERM88888{i}',
                    telephone=f'060000010{i}',
                    date_delivrance_permis=date(2020, 1, 1),
                    date_expiration_permis=date(2030, 1, 1)
                )
                db.session.add(chauffeur)
            
            db.session.commit()
            
            count = Chauffeur.query.count()
            assert count == 5
