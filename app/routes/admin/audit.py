"""
Routes pour la consultation des logs d'audit
Permet de voir qui fait quoi et quand
"""

from flask import render_template, request, jsonify
from app.routes.common import admin_or_responsable
from app.utils.audit_logger import get_audit_logs, get_role_statistics
from . import bp

@bp.route('/audit')
@admin_or_responsable
def audit_logs():
    """
    Page de consultation des logs d'audit
    Accessible uniquement aux ADMIN et RESPONSABLE
    """
    # Paramètres de filtrage
    role_filter = request.args.get('role', '')
    action_filter = request.args.get('action', '')
    limit = int(request.args.get('limit', 100))
    
    # Récupérer les logs avec filtres
    logs = get_audit_logs(
        limit=limit,
        role_filter=role_filter if role_filter else None,
        action_filter=action_filter if action_filter else None
    )
    
    # Récupérer les statistiques
    stats = get_role_statistics()
    
    return render_template(
        'admin/audit.html',
        logs=logs,
        stats=stats,
        role_filter=role_filter,
        action_filter=action_filter,
        limit=limit,
        active_page='audit'
    )

@bp.route('/audit/api/stats')
@admin_or_responsable
def audit_stats_api():
    """
    API pour récupérer les statistiques d'audit en JSON
    """
    stats = get_role_statistics()
    return jsonify(stats)

@bp.route('/audit/api/logs')
@admin_or_responsable
def audit_logs_api():
    """
    API pour récupérer les logs d'audit en JSON
    """
    role_filter = request.args.get('role')
    action_filter = request.args.get('action')
    limit = int(request.args.get('limit', 50))
    
    logs = get_audit_logs(
        limit=limit,
        role_filter=role_filter,
        action_filter=action_filter
    )
    
    return jsonify({
        'logs': logs,
        'count': len(logs)
    })
