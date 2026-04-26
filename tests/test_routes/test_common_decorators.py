"""Tests for app.routes.common decorators - exercises error/redirect branches.

Goal: cover all the flash/redirect branches added when extracting message constants
(MSG_SESSION_EXPIREE, MSG_INCOHERENCE_SESSION, MSG_VEUILLEZ_CONNECTER, MSG_ACCES_REFUSE).
"""
import pytest
from flask import Flask, session
from flask_login import LoginManager, login_user, logout_user, UserMixin

from app.routes.common import (
    role_required,
    admin_or_responsable,
    read_only_access,
    superviseur_access,
    business_action_required,
    admin_business_action,
)


class _DummyUser(UserMixin):
    def __init__(self, uid='1'):
        self.id = uid
        self.utilisateur_id = uid

    def get_id(self):
        return self.id


@pytest.fixture
def mini_app():
    """Minimal Flask app with login manager and stub auth.login route."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    lm = LoginManager(app)
    lm.login_view = 'auth.login'
    USERS = {}

    @lm.user_loader
    def _load(uid):
        return USERS.get(uid)

    # Stub login endpoint required by url_for('auth.login')
    @app.route('/login')
    def auth_login():
        return 'login_page'

    # Bind blueprint name 'auth' for url_for lookup
    app.view_functions['auth.login'] = app.view_functions['auth_login']
    app.url_map._rules_by_endpoint['auth.login'] = app.url_map._rules_by_endpoint['auth_login']

    # Test routes wrapping each decorator
    @app.route('/role-admin')
    @role_required('ADMIN')
    def role_admin_view():
        return 'ok'

    @app.route('/admin-resp')
    @admin_or_responsable
    def admin_resp_view():
        return 'ok'

    @app.route('/readonly')
    @read_only_access('ADMIN', 'SUPERVISEUR')
    def readonly_view():
        return 'ok'

    @app.route('/super')
    @superviseur_access
    def super_view():
        return 'ok'

    @app.route('/biz')
    @business_action_required('ADMIN')
    def biz_view():
        return 'ok'

    @app.route('/admin-biz')
    @admin_business_action
    def admin_biz_view():
        return 'ok'

    @app.route('/_login_user/<uid>')
    def _login_user(uid):
        u = _DummyUser(uid)
        USERS[uid] = u
        login_user(u)
        return 'logged'

    @app.route('/_set_session/<uid>/<role>')
    def _set_session(uid, role):
        session['user_id'] = uid
        session['user_role'] = role
        return 'set'

    return app


@pytest.fixture
def cli(mini_app):
    return mini_app.test_client()


def _follow(resp):
    return resp.status_code


# ---------- role_required ----------

class TestRoleRequired:
    def test_unauthenticated_redirects(self, cli):
        # No login, no session -> MSG_VEUILLEZ_CONNECTER branch
        resp = cli.get('/role-admin')
        assert resp.status_code == 302

    def test_session_missing_after_login(self, cli):
        cli.get('/_login_user/1')  # authenticated but no session keys
        resp = cli.get('/role-admin')
        assert resp.status_code == 302

    def test_session_incoherence(self, cli):
        cli.get('/_login_user/1')
        cli.get('/_set_session/999/ADMIN')  # session uid != current_user uid
        resp = cli.get('/role-admin')
        assert resp.status_code == 302

    def test_role_mismatch_logs_unauthorized(self, cli):
        cli.get('/_login_user/1')
        cli.get('/_set_session/1/CHARGE')  # not ADMIN
        resp = cli.get('/role-admin')
        assert resp.status_code == 302

    def test_authorized_passes(self, cli):
        cli.get('/_login_user/1')
        cli.get('/_set_session/1/ADMIN')
        resp = cli.get('/role-admin')
        assert resp.status_code == 200


# ---------- admin_or_responsable ----------

class TestAdminOrResponsable:
    def test_unauthenticated(self, cli):
        resp = cli.get('/admin-resp')
        assert resp.status_code == 302

    def test_session_missing(self, cli):
        cli.get('/_login_user/1')
        resp = cli.get('/admin-resp')
        assert resp.status_code == 302

    def test_session_incoherence(self, cli):
        cli.get('/_login_user/1')
        cli.get('/_set_session/999/ADMIN')
        resp = cli.get('/admin-resp')
        assert resp.status_code == 302

    def test_role_not_allowed(self, cli):
        cli.get('/_login_user/1')
        cli.get('/_set_session/1/SUPERVISEUR')
        resp = cli.get('/admin-resp')
        assert resp.status_code == 302

    def test_admin_ok(self, cli):
        cli.get('/_login_user/1')
        cli.get('/_set_session/1/ADMIN')
        resp = cli.get('/admin-resp')
        assert resp.status_code == 200


# ---------- read_only_access ----------

class TestReadOnlyAccess:
    def test_no_session(self, cli):
        resp = cli.get('/readonly')
        assert resp.status_code == 302

    def test_role_denied(self, cli):
        cli.get('/_set_session/1/CHARGE')
        resp = cli.get('/readonly')
        assert resp.status_code == 302

    def test_role_ok(self, cli):
        cli.get('/_set_session/1/ADMIN')
        resp = cli.get('/readonly')
        assert resp.status_code == 200


# ---------- superviseur_access ----------

class TestSuperviseurAccess:
    def test_unauthenticated(self, cli):
        resp = cli.get('/super')
        assert resp.status_code == 302

    def test_session_missing(self, cli):
        cli.get('/_login_user/1')
        resp = cli.get('/super')
        assert resp.status_code == 302

    def test_session_incoherence(self, cli):
        cli.get('/_login_user/1')
        cli.get('/_set_session/999/SUPERVISEUR')
        resp = cli.get('/super')
        assert resp.status_code == 302

    def test_role_denied(self, cli):
        cli.get('/_login_user/1')
        cli.get('/_set_session/1/CHARGE')
        resp = cli.get('/super')
        assert resp.status_code == 302

    def test_super_ok(self, cli):
        cli.get('/_login_user/1')
        cli.get('/_set_session/1/SUPERVISEUR')
        resp = cli.get('/super')
        assert resp.status_code == 200


# ---------- business_action_required ----------

class TestBusinessActionRequired:
    def test_no_session(self, cli):
        resp = cli.get('/biz')
        assert resp.status_code == 302

    def test_role_not_in_list(self, cli):
        cli.get('/_set_session/1/SUPERVISEUR')
        resp = cli.get('/biz')
        assert resp.status_code == 302

    def test_explicit_superviseur_denied(self, cli):
        # First wrap superviseur into allowed roles to hit second branch
        # Need to define a new view; reuse with role 'SUPERVISEUR' allowed
        # We'll register a dynamic route here is non-trivial; rely on test_role_not_in_list
        # plus test below
        cli.get('/_set_session/1/ADMIN')
        resp = cli.get('/biz')
        assert resp.status_code == 200


def test_business_action_blocks_supervisor_when_in_role_list(mini_app):
    """Cover the explicit SUPERVISEUR-block branch of business_action_required."""
    @mini_app.route('/biz-super')
    @business_action_required('ADMIN', 'SUPERVISEUR')
    def biz_super_view():
        return 'ok'
    cli = mini_app.test_client()
    cli.get('/_set_session/1/SUPERVISEUR')
    resp = cli.get('/biz-super')
    assert resp.status_code == 302  # blocked despite role being in the list


# ---------- admin_business_action ----------

class TestAdminBusinessAction:
    def test_no_session(self, cli):
        resp = cli.get('/admin-biz')
        assert resp.status_code == 302

    def test_role_not_admin_or_responsable(self, cli):
        cli.get('/_set_session/1/CHARGE')
        resp = cli.get('/admin-biz')
        assert resp.status_code == 302

    def test_admin_ok(self, cli):
        cli.get('/_set_session/1/ADMIN')
        resp = cli.get('/admin-biz')
        assert resp.status_code == 200
