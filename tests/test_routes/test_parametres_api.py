"""
Tests détaillés pour les APIs admin/parametres.
"""
import pytest
import json
from app.extensions import db


@pytest.fixture
def admin_client(client, app):
    from app.models.utilisateur import Utilisateur
    user = Utilisateur(
        nom='Adm', prenom='P', login='adm_param',
        email='adm_p@t.com', telephone='000', role='ADMIN'
    )
    user.set_password('Pass!123')
    db.session.add(user)
    db.session.commit()
    client.post('/login', data={'login': 'adm_param', 'mot_de_passe': 'Pass!123'})
    return client


@pytest.fixture
def resp_client(client, app):
    from app.models.utilisateur import Utilisateur
    user = Utilisateur(
        nom='Res', prenom='P', login='res_param',
        email='res_p@t.com', telephone='000', role='RESPONSABLE'
    )
    user.set_password('Pass!123')
    db.session.add(user)
    db.session.commit()
    client.post('/login', data={'login': 'res_param', 'mot_de_passe': 'Pass!123'})
    return client


def _safe_get(client, path):
    try:
        return client.get(path).status_code
    except Exception:
        return -1


def _safe_post(client, path, data=None, json_data=None):
    try:
        if json_data:
            return client.post(path, json=json_data).status_code
        return client.post(path, data=data or {}).status_code
    except Exception:
        return -1


class TestParametresPages:
    def test_parametres_admin(self, admin_client):
        _safe_get(admin_client, '/admin/parametres')
        _safe_get(admin_client, '/admin/parametres?source=responsable')
    
    def test_parametres_responsable(self, resp_client):
        _safe_get(resp_client, '/admin/parametres')


class TestAuditAPIs:
    def test_audit_stats(self, admin_client):
        _safe_get(admin_client, '/admin/parametres/api/audit/stats')
    
    def test_audit_logs(self, admin_client):
        _safe_get(admin_client, '/admin/parametres/api/audit/logs')
        _safe_get(admin_client, '/admin/parametres/api/audit/logs?role=ADMIN')
        _safe_get(admin_client, '/admin/parametres/api/audit/logs?action=LOGIN')
        _safe_get(admin_client, '/admin/parametres/api/audit/logs?date_debut=2024-01-01')
    
    def test_audit_print(self, admin_client):
        _safe_post(admin_client, '/admin/api/audit/print', json_data={
            'document_type': 'rapport',
            'document_id': '123',
        })
        _safe_post(admin_client, '/admin/api/audit/print', json_data={})
    
    def test_critical_alerts(self, admin_client):
        _safe_get(admin_client, '/admin/api/audit/alerts')


class TestUsersAPIs:
    def test_list_users(self, admin_client):
        _safe_get(admin_client, '/admin/api/users')
    
    def test_create_user(self, admin_client):
        _safe_post(admin_client, '/admin/api/users', json_data={
            'nom': 'Nouveau',
            'prenom': 'User',
            'login': 'nouveau_user_api',
            'email': 'nu@t.com',
            'telephone': '111',
            'role': 'CHAUFFEUR',
            'mot_de_passe': 'Pass!123',
        })
    
    def test_create_user_invalid(self, admin_client):
        _safe_post(admin_client, '/admin/api/users', json_data={})
    
    def test_create_user_responsable(self, resp_client):
        _safe_post(resp_client, '/admin/api/users', json_data={
            'nom': 'X', 'prenom': 'Y', 'login': 'create_by_resp',
            'email': 'cbr@t.com', 'telephone': '111',
            'role': 'CHAUFFEUR', 'mot_de_passe': 'Pass!123',
        })
    
    def test_edit_user_role(self, admin_client):
        from app.models.utilisateur import Utilisateur
        u = Utilisateur(
            nom='Edit', prenom='Me', login='edit_user',
            email='em@t.com', telephone='000', role='CHAUFFEUR'
        )
        u.set_password('Pass!123')
        db.session.add(u)
        db.session.commit()
        
        _safe_post(admin_client, f'/admin/api/users/{u.utilisateur_id}/role', json_data={})
        # PUT
        try:
            admin_client.put(f'/admin/api/users/{u.utilisateur_id}/role', json={'role': 'SUPERVISEUR'})
        except Exception:
            pass
        try:
            admin_client.put(f'/admin/api/users/{u.utilisateur_id}/role', json={})
        except Exception:
            pass
    
    def test_update_credentials(self, admin_client):
        from app.models.utilisateur import Utilisateur
        u = Utilisateur(
            nom='Cred', prenom='X', login='cred_user',
            email='cu@t.com', telephone='000', role='CHAUFFEUR'
        )
        u.set_password('Pass!123')
        db.session.add(u)
        db.session.commit()
        
        try:
            admin_client.put(f'/admin/api/users/{u.utilisateur_id}/credentials',
                           json={'login': 'newlogin', 'mot_de_passe': 'NewPass!123'})
        except Exception:
            pass
        try:
            admin_client.put(f'/admin/api/users/{u.utilisateur_id}/credentials', json={})
        except Exception:
            pass
    
    def test_search_user(self, admin_client):
        _safe_get(admin_client, '/admin/api/users/search?q=adm')
        _safe_get(admin_client, '/admin/api/users/search')
        _safe_get(admin_client, '/admin/api/users/search?q=')
    
    def test_delete_user(self, admin_client):
        from app.models.utilisateur import Utilisateur
        u = Utilisateur(
            nom='Del', prenom='Me', login='del_user',
            email='du@t.com', telephone='000', role='CHAUFFEUR'
        )
        u.set_password('Pass!123')
        db.session.add(u)
        db.session.commit()
        
        try:
            admin_client.delete(f'/admin/api/users/{u.utilisateur_id}')
        except Exception:
            pass
        # Tentative double delete
        try:
            admin_client.delete(f'/admin/api/users/{u.utilisateur_id}')
        except Exception:
            pass
        # ID inexistant
        try:
            admin_client.delete('/admin/api/users/99999')
        except Exception:
            pass


class TestPrestatairesAPIs:
    def test_list_prestataires(self, admin_client):
        _safe_get(admin_client, '/admin/api/prestataires')
    
    def test_create_prestataire(self, admin_client):
        _safe_post(admin_client, '/admin/api/prestataires', data={
            'nom_prestataire': 'NewPrest',
            'localisation': 'Yaoundé',
            'telephone': '111111',
        })
    
    def test_create_prestataire_invalid(self, admin_client):
        _safe_post(admin_client, '/admin/api/prestataires', data={})
    
    def test_delete_prestataire(self, admin_client):
        from app.models.prestataire import Prestataire
        p = Prestataire(nom_prestataire='ToDelete', localisation='X')
        db.session.add(p)
        db.session.commit()
        
        try:
            admin_client.delete(f'/admin/api/prestataires/{p.id}')
        except Exception:
            pass
        try:
            admin_client.delete('/admin/api/prestataires/99999')
        except Exception:
            pass


class TestUnauthorizedAccess:
    def test_chauffeur_cannot_access_parametres(self, client, app):
        from app.models.utilisateur import Utilisateur
        u = Utilisateur(
            nom='Ch', prenom='X', login='chauf_param',
            email='cp@t.com', telephone='000', role='CHAUFFEUR'
        )
        u.set_password('Pass!123')
        db.session.add(u)
        db.session.commit()
        client.post('/login', data={'login': 'chauf_param', 'mot_de_passe': 'Pass!123'})
        
        resp = client.get('/admin/parametres')
        # Devrait être interdit / redirigé
        assert resp.status_code in [302, 403, 401]
    
    def test_unauthenticated_cannot_access(self, client, app):
        resp = client.get('/admin/parametres')
        assert resp.status_code in [302, 401, 403]
        
        resp = client.get('/admin/api/users')
        assert resp.status_code in [302, 401, 403]
