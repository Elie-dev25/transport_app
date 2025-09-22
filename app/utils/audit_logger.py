"""
Système d'audit intelligent pour tracer les actions critiques des utilisateurs
- Filtre les actions importantes uniquement
- Logs séparés par rôle (6 fichiers distincts)
- Actions critiques : Auth, CRUD, Admin, Erreurs, Config
"""

import logging
import os
from datetime import datetime
from flask import session, request
from functools import wraps
from enum import Enum

class AuditActionType(Enum):
    """Types d'actions critiques à auditer"""
    # Authentification
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGOUT = "LOGOUT"
    SESSION_EXPIRED = "SESSION_EXPIRED"

    # Accès ressources sensibles
    SENSITIVE_ACCESS = "SENSITIVE_ACCESS"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"

    # CRUD Operations
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

    # Actions d'administration
    USER_CREATED = "USER_CREATED"
    USER_ROLE_CHANGED = "USER_ROLE_CHANGED"
    USER_DELETED = "USER_DELETED"
    PERMISSION_GRANTED = "PERMISSION_GRANTED"

    # Erreurs système
    SYSTEM_ERROR = "SYSTEM_ERROR"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"

    # Configuration
    CONFIG_CHANGED = "CONFIG_CHANGED"
    SYSTEM_MAINTENANCE = "SYSTEM_MAINTENANCE"

class AuditLevel(Enum):
    """Niveaux de criticité des actions"""
    LOW = "LOW"           # Actions normales (consultation)
    MEDIUM = "MEDIUM"     # Actions importantes (CRUD)
    HIGH = "HIGH"         # Actions critiques (Admin, Auth)
    CRITICAL = "CRITICAL" # Erreurs système, violations sécurité

# Configuration des loggers par rôle
ROLE_LOGGERS = {}

def setup_role_audit_loggers():
    """Configure un logger séparé pour chaque rôle"""

    # Créer le dossier logs s'il n'existe pas
    logs_dir = 'logs/audit'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Les 6 rôles de l'application
    roles = ['ADMIN', 'RESPONSABLE', 'SUPERVISEUR', 'CHARGE', 'CHAUFFEUR', 'MECANICIEN']

    for role in roles:
        logger_name = f'audit_{role.lower()}'
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

        # Éviter la duplication des handlers
        if not logger.handlers:
            # Handler pour fichier spécifique au rôle
            handler = logging.FileHandler(
                os.path.join(logs_dir, f'audit_{role.lower()}.log'),
                encoding='utf-8'
            )

            # Format détaillé pour l'audit
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

            # Empêcher la propagation vers le logger racine
            logger.propagate = False

        ROLE_LOGGERS[role] = logger

    return ROLE_LOGGERS

# Initialiser les loggers par rôle
setup_role_audit_loggers()

def is_critical_action(action_type):
    """Détermine si une action doit être auditée"""
    critical_actions = {
        # Authentification
        AuditActionType.LOGIN_SUCCESS,
        AuditActionType.LOGIN_FAILED,
        AuditActionType.LOGOUT,
        AuditActionType.SESSION_EXPIRED,

        # CRUD sur données importantes
        AuditActionType.CREATE,
        AuditActionType.UPDATE,
        AuditActionType.DELETE,

        # Administration
        AuditActionType.USER_CREATED,
        AuditActionType.USER_ROLE_CHANGED,
        AuditActionType.USER_DELETED,
        AuditActionType.PERMISSION_GRANTED,

        # Accès sensibles
        AuditActionType.SENSITIVE_ACCESS,
        AuditActionType.UNAUTHORIZED_ACCESS,

        # Erreurs système
        AuditActionType.SYSTEM_ERROR,
        AuditActionType.SECURITY_VIOLATION,

        # Configuration
        AuditActionType.CONFIG_CHANGED,
        AuditActionType.SYSTEM_MAINTENANCE
    }

    # Convertir string en enum si nécessaire
    if isinstance(action_type, str):
        try:
            action_type = AuditActionType(action_type)
        except ValueError:
            return False

    return action_type in critical_actions

def get_action_level(action_type):
    """Détermine le niveau de criticité d'une action"""
    if isinstance(action_type, str):
        try:
            action_type = AuditActionType(action_type)
        except ValueError:
            return AuditLevel.LOW

    critical_levels = {
        # CRITICAL - Sécurité et erreurs système
        AuditActionType.LOGIN_FAILED: AuditLevel.CRITICAL,
        AuditActionType.UNAUTHORIZED_ACCESS: AuditLevel.CRITICAL,
        AuditActionType.SECURITY_VIOLATION: AuditLevel.CRITICAL,
        AuditActionType.SYSTEM_ERROR: AuditLevel.CRITICAL,

        # HIGH - Administration et authentification
        AuditActionType.LOGIN_SUCCESS: AuditLevel.HIGH,
        AuditActionType.LOGOUT: AuditLevel.HIGH,
        AuditActionType.USER_CREATED: AuditLevel.HIGH,
        AuditActionType.USER_ROLE_CHANGED: AuditLevel.HIGH,
        AuditActionType.USER_DELETED: AuditLevel.HIGH,
        AuditActionType.CONFIG_CHANGED: AuditLevel.HIGH,
        AuditActionType.SYSTEM_MAINTENANCE: AuditLevel.HIGH,

        # MEDIUM - CRUD et accès sensibles
        AuditActionType.CREATE: AuditLevel.MEDIUM,
        AuditActionType.UPDATE: AuditLevel.MEDIUM,
        AuditActionType.DELETE: AuditLevel.MEDIUM,
        AuditActionType.SENSITIVE_ACCESS: AuditLevel.MEDIUM,

        # LOW - Autres
        AuditActionType.SESSION_EXPIRED: AuditLevel.LOW,
        AuditActionType.PERMISSION_GRANTED: AuditLevel.LOW,
    }

    return critical_levels.get(action_type, AuditLevel.LOW)

def log_critical_action(action_type, resource_type=None, resource_id=None, details=None, success=True, error_message=None):
    """
    Log intelligent - N'enregistre que les actions critiques

    Args:
        action_type: Type d'action (AuditActionType enum ou string)
        resource_type: Type de ressource (bus, chauffeur, trajet, etc.)
        resource_id: ID de la ressource concernée
        details: Détails supplémentaires
        success: Succès ou échec de l'action
        error_message: Message d'erreur si applicable
    """
    try:
        # Vérifier si l'action doit être auditée
        if not is_critical_action(action_type):
            return  # Ne pas logger les actions non critiques

        # Récupérer les informations de session
        user_id = session.get('user_id', 'SYSTEM')
        user_role = session.get('user_role', 'UNKNOWN')

        # Récupérer les informations de requête
        ip_address = request.remote_addr if request else 'UNKNOWN'
        user_agent = request.headers.get('User-Agent', 'UNKNOWN') if request else 'UNKNOWN'

        # Déterminer le niveau de criticité
        level = get_action_level(action_type)

        # Construire le message de log structuré
        log_parts = [
            f"USER:{user_id}",
            f"ROLE:{user_role}",
            f"ACTION:{action_type.value if hasattr(action_type, 'value') else action_type}",
            f"LEVEL:{level.value}",
            f"SUCCESS:{success}",
            f"IP:{ip_address}"
        ]

        if resource_type:
            log_parts.append(f"RESOURCE:{resource_type}")
        if resource_id:
            log_parts.append(f"RESOURCE_ID:{resource_id}")
        if details:
            log_parts.append(f"DETAILS:{details}")
        if error_message:
            log_parts.append(f"ERROR:{error_message}")

        log_message = " | ".join(log_parts)

        # Logger dans le fichier spécifique au rôle
        role_logger = ROLE_LOGGERS.get(user_role)
        if role_logger:
            if level == AuditLevel.CRITICAL:
                role_logger.error(log_message)
            elif level == AuditLevel.HIGH:
                role_logger.warning(log_message)
            else:
                role_logger.info(log_message)
        else:
            # Fallback vers un logger générique si rôle inconnu
            logging.info(f"UNKNOWN_ROLE | {log_message}")

    except Exception as e:
        # En cas d'erreur de logging, ne pas faire planter l'application
        logging.error(f"Erreur lors du logging d'audit: {str(e)}")

# Fonction de compatibilité avec l'ancien système
def log_user_action(action_type, action_name, details=None):
    """
    Fonction de compatibilité avec l'ancien système
    Filtre automatiquement les actions non critiques
    """
    # Mapper les anciens types vers les nouveaux
    action_mapping = {
        'CREATION': AuditActionType.CREATE,
        'MODIFICATION': AuditActionType.UPDATE,
        'SUPPRESSION': AuditActionType.DELETE,
        'ACTION_ADMIN': AuditActionType.SENSITIVE_ACCESS,
        'CONSULTATION': None,  # Ne plus logger les consultations simples
    }

    mapped_action = action_mapping.get(action_type)
    if mapped_action is None:
        return  # Ne pas logger cette action

    # Extraire le type de ressource du nom de fonction
    resource_type = None
    if 'bus' in action_name.lower():
        resource_type = 'bus'
    elif 'chauffeur' in action_name.lower():
        resource_type = 'chauffeur'
    elif 'trajet' in action_name.lower():
        resource_type = 'trajet'
    elif 'user' in action_name.lower():
        resource_type = 'utilisateur'

    log_critical_action(
        action_type=mapped_action,
        resource_type=resource_type,
        details=f"Function: {action_name} | {details}" if details else f"Function: {action_name}"
    )

# Fonction pour nettoyer l'ancien système
def cleanup_old_audit_system():
    """Supprime l'ancien fichier audit.log s'il existe"""
    try:
        old_audit_file = os.path.join('logs', 'audit.log')
        if os.path.exists(old_audit_file):
            # Créer une sauvegarde avant suppression
            backup_file = os.path.join('logs', f'audit_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            os.rename(old_audit_file, backup_file)
            logging.info(f"Ancien fichier audit.log sauvegardé vers {backup_file}")
        return True
    except Exception as e:
        logging.error(f"Erreur lors du nettoyage de l'ancien système d'audit: {str(e)}")
        return False

# Nettoyer automatiquement au démarrage
cleanup_old_audit_system()

def audit_action(action_type, resource_type=None, track_errors=True):
    """
    Décorateur intelligent pour logger automatiquement les actions critiques

    Usage:
        @audit_action(AuditActionType.CREATE, 'bus')
        def create_bus():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            success = True
            error_message = None
            result = None

            try:
                # Exécuter la fonction
                result = func(*args, **kwargs)
                return result

            except Exception as e:
                success = False
                error_message = str(e)
                if track_errors:
                    log_system_error(
                        error_type=f"Function: {func.__name__}",
                        error_message=error_message,
                        context=f"Args: {args}, Kwargs: {kwargs}"
                    )
                raise  # Re-lever l'exception

            finally:
                # Logger l'action seulement si c'est critique
                if is_critical_action(action_type):
                    # Essayer d'extraire l'ID de la ressource du résultat
                    resource_id = None
                    if result and hasattr(result, 'id'):
                        resource_id = result.id
                    elif result and isinstance(result, dict) and 'id' in result:
                        resource_id = result['id']

                    log_critical_action(
                        action_type=action_type,
                        resource_type=resource_type or func.__name__.replace('create_', '').replace('update_', '').replace('delete_', ''),
                        resource_id=resource_id,
                        details=f"Function: {func.__name__}",
                        success=success,
                        error_message=error_message
                    )
        return wrapper
    return decorator

def smart_audit(resource_type):
    """
    Décorateur ultra-intelligent qui détecte automatiquement le type d'action
    basé sur le nom de la fonction

    Usage:
        @smart_audit('bus')
        def create_bus():  # Détecte automatiquement CREATE
            pass

        @smart_audit('chauffeur')
        def update_chauffeur():  # Détecte automatiquement UPDATE
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Détecter le type d'action basé sur le nom de fonction
            func_name = func.__name__.lower()

            if func_name.startswith('create_') or func_name.startswith('add_'):
                action_type = AuditActionType.CREATE
            elif func_name.startswith('update_') or func_name.startswith('modify_') or func_name.startswith('edit_'):
                action_type = AuditActionType.UPDATE
            elif func_name.startswith('delete_') or func_name.startswith('remove_'):
                action_type = AuditActionType.DELETE
            elif func_name.startswith('login'):
                action_type = AuditActionType.LOGIN_SUCCESS
            elif func_name.startswith('logout'):
                action_type = AuditActionType.LOGOUT
            else:
                # Si on ne peut pas détecter, ne pas auditer
                return func(*args, **kwargs)

            # Utiliser le décorateur audit_action
            return audit_action(action_type, resource_type, track_errors=True)(func)(*args, **kwargs)

        return wrapper
    return decorator

def get_audit_logs(limit=100, role_filter=None, action_filter=None, level_filter=None):
    """
    Récupère les logs d'audit depuis les fichiers séparés par rôle

    Args:
        limit: Nombre maximum de logs à retourner
        role_filter: Filtrer par rôle (ADMIN, RESPONSABLE, etc.)
        action_filter: Filtrer par type d'action
        level_filter: Filtrer par niveau (LOW, MEDIUM, HIGH, CRITICAL)

    Returns:
        Liste des logs d'audit triés par date (plus récent en premier)
    """
    try:
        logs_dir = 'logs/audit'
        if not os.path.exists(logs_dir):
            return []

        all_logs = []
        roles_to_check = [role_filter] if role_filter else ['ADMIN', 'RESPONSABLE', 'SUPERVISEUR', 'CHARGE', 'CHAUFFEUR', 'MECANICIEN']

        for role in roles_to_check:
            log_file = os.path.join(logs_dir, f'audit_{role.lower()}.log')
            if not os.path.exists(log_file):
                continue

            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Appliquer les filtres
                    if action_filter and f"ACTION:{action_filter}" not in line:
                        continue
                    if level_filter and f"LEVEL:{level_filter}" not in line:
                        continue

                    # Extraire la date pour le tri
                    try:
                        date_part = line.split(' | ')[0]
                        log_datetime = datetime.strptime(date_part, '%Y-%m-%d %H:%M:%S')
                        all_logs.append((log_datetime, line))
                    except:
                        # Si parsing de date échoue, ajouter quand même
                        all_logs.append((datetime.min, line))

            except Exception as e:
                logging.error(f"Erreur lecture fichier {log_file}: {str(e)}")
                continue

        # Trier par date (plus récent en premier) et limiter
        all_logs.sort(key=lambda x: x[0], reverse=True)
        return [log[1] for log in all_logs[:limit]]

    except Exception as e:
        logging.error(f"Erreur lors de la lecture des logs d'audit: {str(e)}")
        return []

def get_role_audit_logs(role, limit=50, action_filter=None, level_filter=None):
    """
    Récupère les logs d'audit pour un rôle spécifique

    Args:
        role: Rôle à consulter (ADMIN, RESPONSABLE, etc.)
        limit: Nombre maximum de logs
        action_filter: Filtrer par type d'action
        level_filter: Filtrer par niveau

    Returns:
        Liste des logs pour ce rôle
    """
    try:
        logs_dir = 'logs/audit'
        log_file = os.path.join(logs_dir, f'audit_{role.lower()}.log')

        if not os.path.exists(log_file):
            return []

        logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Prendre les dernières lignes (plus récentes)
        recent_lines = lines[-limit*2:] if len(lines) > limit*2 else lines

        for line in reversed(recent_lines):  # Plus récent en premier
            line = line.strip()
            if not line:
                continue

            # Appliquer les filtres
            if action_filter and f"ACTION:{action_filter}" not in line:
                continue
            if level_filter and f"LEVEL:{level_filter}" not in line:
                continue

            logs.append(line)

            if len(logs) >= limit:
                break

        return logs

    except Exception as e:
        logging.error(f"Erreur lors de la lecture des logs pour {role}: {str(e)}")
        return []

def get_role_statistics():
    """
    Génère des statistiques détaillées sur les actions par rôle

    Returns:
        Dictionnaire avec les statistiques par rôle incluant les niveaux de criticité
    """
    try:
        stats = {}
        roles = ['ADMIN', 'RESPONSABLE', 'SUPERVISEUR', 'CHARGE', 'CHAUFFEUR', 'MECANICIEN']

        for role in roles:
            logs = get_role_audit_logs(role, limit=500)  # Analyser les 500 dernières actions par rôle

            role_stats = {
                'total': len(logs),
                'actions': {},
                'levels': {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0},
                'success_rate': 0,
                'recent_activity': []
            }

            successful_actions = 0

            for log in logs:
                try:
                    # Extraire l'action
                    if 'ACTION:' in log:
                        action_part = log.split('ACTION:')[1].split('|')[0].strip()
                        if action_part not in role_stats['actions']:
                            role_stats['actions'][action_part] = 0
                        role_stats['actions'][action_part] += 1

                    # Extraire le niveau
                    if 'LEVEL:' in log:
                        level_part = log.split('LEVEL:')[1].split('|')[0].strip()
                        if level_part in role_stats['levels']:
                            role_stats['levels'][level_part] += 1

                    # Extraire le succès
                    if 'SUCCESS:True' in log:
                        successful_actions += 1

                    # Ajouter à l'activité récente (5 dernières)
                    if len(role_stats['recent_activity']) < 5:
                        try:
                            date_part = log.split(' | ')[0]
                            action_part = log.split('ACTION:')[1].split('|')[0].strip() if 'ACTION:' in log else 'Unknown'
                            role_stats['recent_activity'].append({
                                'date': date_part,
                                'action': action_part
                            })
                        except:
                            pass

                except Exception as e:
                    continue

            # Calculer le taux de succès
            if role_stats['total'] > 0:
                role_stats['success_rate'] = round((successful_actions / role_stats['total']) * 100, 1)

            stats[role] = role_stats

        return stats

    except Exception as e:
        logging.error(f"Erreur lors du calcul des statistiques: {str(e)}")
        return {}

def get_critical_alerts(hours=24):
    """
    Récupère les alertes critiques des dernières heures

    Args:
        hours: Nombre d'heures à analyser

    Returns:
        Liste des alertes critiques
    """
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        alerts = []

        # Chercher dans tous les fichiers de logs
        for role in ['ADMIN', 'RESPONSABLE', 'SUPERVISEUR', 'CHARGE', 'CHAUFFEUR', 'MECANICIEN']:
            logs = get_role_audit_logs(role, limit=100, level_filter='CRITICAL')

            for log in logs:
                try:
                    # Extraire la date
                    date_part = log.split(' | ')[0]
                    log_datetime = datetime.strptime(date_part, '%Y-%m-%d %H:%M:%S')

                    if log_datetime >= cutoff_time:
                        alerts.append({
                            'timestamp': date_part,
                            'role': role,
                            'log': log,
                            'severity': 'CRITICAL'
                        })
                except:
                    continue

        # Trier par date (plus récent en premier)
        alerts.sort(key=lambda x: x['timestamp'], reverse=True)
        return alerts

    except Exception as e:
        logging.error(f"Erreur lors de la récupération des alertes: {str(e)}")
        return []

# ===== FONCTIONS SPÉCIALISÉES POUR ACTIONS CRITIQUES =====

# 1. AUTHENTIFICATION
def log_login_success(user_id, user_role, details=None):
    """Log une connexion réussie"""
    log_critical_action(
        action_type=AuditActionType.LOGIN_SUCCESS,
        resource_type='session',
        resource_id=user_id,
        details=f"Role: {user_role} | {details}" if details else f"Role: {user_role}",
        success=True
    )

def log_login_failed(username, reason=None):
    """Log une tentative de connexion échouée"""
    log_critical_action(
        action_type=AuditActionType.LOGIN_FAILED,
        resource_type='session',
        resource_id=username,
        details=f"Reason: {reason}" if reason else "Authentication failed",
        success=False,
        error_message=reason
    )

def log_logout(user_id, user_role):
    """Log une déconnexion"""
    log_critical_action(
        action_type=AuditActionType.LOGOUT,
        resource_type='session',
        resource_id=user_id,
        details=f"Role: {user_role}",
        success=True
    )

def log_session_expired(user_id, user_role):
    """Log une expiration de session"""
    log_critical_action(
        action_type=AuditActionType.SESSION_EXPIRED,
        resource_type='session',
        resource_id=user_id,
        details=f"Role: {user_role}",
        success=True
    )

# 2. CRUD OPERATIONS
def log_creation(entity_type, entity_id=None, details=None):
    """Log une création d'entité"""
    log_critical_action(
        action_type=AuditActionType.CREATE,
        resource_type=entity_type.lower(),
        resource_id=entity_id,
        details=details,
        success=True
    )

def log_modification(entity_type, entity_id=None, old_values=None, new_values=None):
    """Log une modification d'entité avec détails des changements"""
    change_details = []
    if old_values and new_values:
        for key in new_values:
            if key in old_values and old_values[key] != new_values[key]:
                change_details.append(f"{key}: {old_values[key]} → {new_values[key]}")

    details = f"Changes: {', '.join(change_details)}" if change_details else "Modified"

    log_critical_action(
        action_type=AuditActionType.UPDATE,
        resource_type=entity_type.lower(),
        resource_id=entity_id,
        details=details,
        success=True
    )

def log_suppression(entity_type, entity_id=None, details=None):
    """Log une suppression d'entité"""
    log_critical_action(
        action_type=AuditActionType.DELETE,
        resource_type=entity_type.lower(),
        resource_id=entity_id,
        details=details,
        success=True
    )

# 3. ACTIONS D'ADMINISTRATION
def log_user_created(new_user_id, new_user_role, created_by_role):
    """Log la création d'un nouvel utilisateur"""
    log_critical_action(
        action_type=AuditActionType.USER_CREATED,
        resource_type='utilisateur',
        resource_id=new_user_id,
        details=f"New role: {new_user_role} | Created by: {created_by_role}",
        success=True
    )

def log_user_role_changed(user_id, old_role, new_role):
    """Log un changement de rôle utilisateur"""
    log_critical_action(
        action_type=AuditActionType.USER_ROLE_CHANGED,
        resource_type='utilisateur',
        resource_id=user_id,
        details=f"Role changed: {old_role} → {new_role}",
        success=True
    )

def log_user_deleted(deleted_user_id, deleted_user_role):
    """Log la suppression d'un utilisateur"""
    log_critical_action(
        action_type=AuditActionType.USER_DELETED,
        resource_type='utilisateur',
        resource_id=deleted_user_id,
        details=f"Deleted role: {deleted_user_role}",
        success=True
    )

# 4. ACCÈS RESSOURCES SENSIBLES
def log_sensitive_access(resource_type, resource_id=None, action_description=None):
    """Log l'accès à une ressource sensible"""
    log_critical_action(
        action_type=AuditActionType.SENSITIVE_ACCESS,
        resource_type=resource_type,
        resource_id=resource_id,
        details=action_description,
        success=True
    )

def log_unauthorized_access(attempted_resource, attempted_action):
    """Log une tentative d'accès non autorisé"""
    log_critical_action(
        action_type=AuditActionType.UNAUTHORIZED_ACCESS,
        resource_type=attempted_resource,
        details=f"Attempted: {attempted_action}",
        success=False,
        error_message="Access denied - insufficient permissions"
    )

# 5. ERREURS SYSTÈME
def log_system_error(error_type, error_message, context=None):
    """Log une erreur système"""
    log_critical_action(
        action_type=AuditActionType.SYSTEM_ERROR,
        resource_type='system',
        details=f"Error type: {error_type} | Context: {context}" if context else f"Error type: {error_type}",
        success=False,
        error_message=error_message
    )

def log_security_violation(violation_type, details=None):
    """Log une violation de sécurité"""
    log_critical_action(
        action_type=AuditActionType.SECURITY_VIOLATION,
        resource_type='security',
        details=f"Violation: {violation_type} | {details}" if details else f"Violation: {violation_type}",
        success=False,
        error_message=f"Security violation: {violation_type}"
    )

# 6. CONFIGURATION
def log_config_changed(config_type, old_value=None, new_value=None):
    """Log un changement de configuration"""
    change_detail = f"{old_value} → {new_value}" if old_value and new_value else "Configuration modified"
    log_critical_action(
        action_type=AuditActionType.CONFIG_CHANGED,
        resource_type='configuration',
        resource_id=config_type,
        details=change_detail,
        success=True
    )

def log_system_maintenance(maintenance_type, details=None):
    """Log une opération de maintenance système"""
    log_critical_action(
        action_type=AuditActionType.SYSTEM_MAINTENANCE,
        resource_type='system',
        details=f"Maintenance: {maintenance_type} | {details}" if details else f"Maintenance: {maintenance_type}",
        success=True
    )

# 7. IMPRESSION DE DOCUMENTS
def log_document_printed(document_type, document_id=None, details=None):
    """Log l'impression d'un document"""
    log_critical_action(
        action_type=AuditActionType.SENSITIVE_ACCESS,
        resource_type='document',
        resource_id=f"{document_type}_{document_id}" if document_id else document_type,
        details=f"Document printed: {document_type} | {details}" if details else f"Document printed: {document_type}",
        success=True
    )

# Fonction de compatibilité (ne plus logger les consultations simples)
def log_consultation(page_name):
    """Fonction de compatibilité - ne log plus les consultations simples"""
    pass  # Les consultations simples ne sont plus auditées
