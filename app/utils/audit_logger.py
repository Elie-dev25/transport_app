"""
Système de logging et d'audit pour tracer les actions des utilisateurs
Permet de distinguer les actions ADMIN vs RESPONSABLE
"""

import logging
import os
from datetime import datetime
from flask import session, request
from functools import wraps

# Configuration du logger d'audit
def setup_audit_logger():
    """Configure le logger d'audit avec rotation des fichiers"""
    
    # Créer le dossier logs s'il n'existe pas
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Configuration du logger d'audit
    audit_logger = logging.getLogger('audit')
    audit_logger.setLevel(logging.INFO)
    
    # Éviter la duplication des handlers
    if not audit_logger.handlers:
        # Handler pour fichier d'audit
        audit_handler = logging.FileHandler(
            os.path.join(logs_dir, 'audit.log'),
            encoding='utf-8'
        )
        
        # Format détaillé pour l'audit
        audit_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        audit_handler.setFormatter(audit_formatter)
        audit_logger.addHandler(audit_handler)
    
    return audit_logger

# Logger d'audit global
audit_logger = setup_audit_logger()

def log_user_action(action_type, action_name, details=None):
    """
    Log une action utilisateur avec tous les détails nécessaires
    
    Args:
        action_type: Type d'action (CONSULTATION, CREATION, MODIFICATION, SUPPRESSION)
        action_name: Nom de l'action (ex: "creation_bus", "modification_trajet")
        details: Détails supplémentaires (optionnel)
    """
    try:
        # Récupérer les informations de session
        user_id = session.get('user_id', 'INCONNU')
        user_role = session.get('user_role', 'INCONNU')
        
        # Récupérer les informations de requête
        ip_address = request.remote_addr if request else 'INCONNU'
        user_agent = request.headers.get('User-Agent', 'INCONNU') if request else 'INCONNU'
        
        # Construire le message de log
        log_message = (
            f"USER:{user_id} | ROLE:{user_role} | ACTION:{action_type} | "
            f"FUNCTION:{action_name} | IP:{ip_address}"
        )
        
        if details:
            log_message += f" | DETAILS:{details}"
        
        # Logger l'action
        audit_logger.info(log_message)
        
    except Exception as e:
        # En cas d'erreur de logging, ne pas faire planter l'application
        logging.error(f"Erreur lors du logging d'audit: {str(e)}")

def audit_action(action_type, details=None):
    """
    Décorateur pour logger automatiquement les actions
    
    Usage:
        @audit_action('CREATION', 'Nouveau bus créé')
        def create_bus():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Logger l'action avant exécution
            log_user_action(action_type, func.__name__, details)
            
            # Exécuter la fonction
            result = func(*args, **kwargs)
            
            return result
        return wrapper
    return decorator

def get_audit_logs(limit=100, role_filter=None, action_filter=None):
    """
    Récupère les logs d'audit avec filtres optionnels
    
    Args:
        limit: Nombre maximum de logs à retourner
        role_filter: Filtrer par rôle (ADMIN, RESPONSABLE, etc.)
        action_filter: Filtrer par type d'action
    
    Returns:
        Liste des logs d'audit
    """
    try:
        logs_file = os.path.join('logs', 'audit.log')
        if not os.path.exists(logs_file):
            return []
        
        logs = []
        with open(logs_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Prendre les dernières lignes (plus récentes)
        recent_lines = lines[-limit:] if len(lines) > limit else lines
        
        for line in reversed(recent_lines):  # Plus récent en premier
            line = line.strip()
            if not line:
                continue
            
            # Appliquer les filtres
            if role_filter and f"ROLE:{role_filter}" not in line:
                continue
            if action_filter and f"ACTION:{action_filter}" not in line:
                continue
            
            logs.append(line)
        
        return logs
        
    except Exception as e:
        logging.error(f"Erreur lors de la lecture des logs d'audit: {str(e)}")
        return []

def get_role_statistics():
    """
    Génère des statistiques sur les actions par rôle
    
    Returns:
        Dictionnaire avec les statistiques par rôle
    """
    try:
        logs = get_audit_logs(limit=1000)  # Analyser les 1000 dernières actions
        
        stats = {
            'ADMIN': {'total': 0, 'actions': {}},
            'RESPONSABLE': {'total': 0, 'actions': {}},
            'SUPERVISEUR': {'total': 0, 'actions': {}},
            'AUTRES': {'total': 0, 'actions': {}}
        }
        
        for log in logs:
            # Extraire le rôle et l'action
            if 'ROLE:' in log and 'ACTION:' in log:
                try:
                    role_part = log.split('ROLE:')[1].split('|')[0].strip()
                    action_part = log.split('ACTION:')[1].split('|')[0].strip()
                    
                    # Catégoriser le rôle
                    role_key = role_part if role_part in ['ADMIN', 'RESPONSABLE', 'SUPERVISEUR'] else 'AUTRES'
                    
                    # Compter les actions
                    stats[role_key]['total'] += 1
                    if action_part not in stats[role_key]['actions']:
                        stats[role_key]['actions'][action_part] = 0
                    stats[role_key]['actions'][action_part] += 1
                    
                except:
                    continue
        
        return stats
        
    except Exception as e:
        logging.error(f"Erreur lors du calcul des statistiques: {str(e)}")
        return {}

# Fonctions utilitaires pour les actions courantes
def log_creation(entity_type, entity_id=None):
    """Log une création d'entité"""
    details = f"{entity_type}"
    if entity_id:
        details += f" (ID: {entity_id})"
    log_user_action('CREATION', f'create_{entity_type.lower()}', details)

def log_modification(entity_type, entity_id=None):
    """Log une modification d'entité"""
    details = f"{entity_type}"
    if entity_id:
        details += f" (ID: {entity_id})"
    log_user_action('MODIFICATION', f'update_{entity_type.lower()}', details)

def log_suppression(entity_type, entity_id=None):
    """Log une suppression d'entité"""
    details = f"{entity_type}"
    if entity_id:
        details += f" (ID: {entity_id})"
    log_user_action('SUPPRESSION', f'delete_{entity_type.lower()}', details)

def log_consultation(page_name):
    """Log une consultation de page"""
    log_user_action('CONSULTATION', f'view_{page_name}', f"Page: {page_name}")
