"""
Utilitaires pour la gestion des routes et templates selon les rôles
"""

from flask import request
from flask_login import current_user


def get_base_template_for_role(role=None, source=None):
    """
    Retourne le template de base approprié selon le rôle de l'utilisateur
    
    Args:
        role: Rôle spécifique à utiliser (optionnel)
        source: Source de la requête (ex: 'responsable')
    
    Returns:
        str: Chemin vers le template de base approprié
    """
    # Priorité au paramètre source
    if source == 'responsable':
        return 'roles/responsable/_base_responsable.html'
    
    # Utiliser le rôle fourni ou celui de l'utilisateur connecté
    user_role = role or (current_user.role if current_user.is_authenticated else None)
    
    template_mapping = {
        'ADMIN': 'roles/admin/_base_admin.html',
        'RESPONSABLE': 'roles/responsable/_base_responsable.html',
        'SUPERVISEUR': 'roles/superviseur/_base_superviseur.html',
        'CHARGE': 'roles/charge_transport/_base_charge.html',
        'CHAUFFEUR': 'roles/chauffeur/_base_chauffeur.html',
        'MECANICIEN': 'roles/mecanicien/_base_mecanicien.html'
    }
    
    return template_mapping.get(user_role, 'roles/admin/_base_admin.html')


def get_template_context_for_role():
    """
    Retourne le contexte de template approprié selon le rôle de l'utilisateur
    
    Returns:
        dict: Contexte avec les variables appropriées
    """
    source = request.args.get('source', '')
    
    context = {
        'use_responsable_base': False,
        'superviseur_mode': False,
        'base_template': None
    }
    
    if source == 'responsable' or (current_user.is_authenticated and current_user.role == 'RESPONSABLE'):
        context['use_responsable_base'] = True
        context['base_template'] = 'roles/responsable/_base_responsable.html'
    elif current_user.is_authenticated and current_user.role == 'SUPERVISEUR':
        context['superviseur_mode'] = True
        context['base_template'] = 'roles/superviseur/_base_superviseur.html'
    elif current_user.is_authenticated and current_user.role == 'CHARGE':
        context['base_template'] = 'roles/charge_transport/_base_charge.html'
    elif current_user.is_authenticated and current_user.role == 'MECANICIEN':
        context['base_template'] = 'roles/mecanicien/_base_mecanicien.html'
    elif current_user.is_authenticated and current_user.role == 'CHAUFFEUR':
        context['base_template'] = 'roles/chauffeur/_base_chauffeur.html'
    else:
        context['base_template'] = 'roles/admin/_base_admin.html'
    
    return context


def get_redirect_url_for_role(endpoint, **kwargs):
    """
    Retourne l'URL de redirection appropriée selon le rôle de l'utilisateur
    
    Args:
        endpoint: Endpoint de base (ex: 'bus', 'rapports')
        **kwargs: Arguments supplémentaires pour l'URL
    
    Returns:
        str: URL de redirection appropriée
    """
    if not current_user.is_authenticated:
        return f'/admin/{endpoint}'
    
    role_prefixes = {
        'ADMIN': 'admin',
        'RESPONSABLE': 'responsable',
        'SUPERVISEUR': 'superviseur',
        'CHARGE': 'charge_transport',
        'CHAUFFEUR': 'chauffeur',
        'MECANICIEN': 'mecanicien'
    }
    
    prefix = role_prefixes.get(current_user.role, 'admin')
    
    # Construire l'URL avec les paramètres
    url = f'/{prefix}/{endpoint}'
    if kwargs:
        params = '&'.join([f'{k}={v}' for k, v in kwargs.items()])
        url += f'?{params}'
    
    return url


def is_responsable_context():
    """
    Vérifie si le contexte actuel est celui d'un responsable
    
    Returns:
        bool: True si c'est un contexte responsable
    """
    source = request.args.get('source', '')
    return (source == 'responsable' or 
            (current_user.is_authenticated and current_user.role == 'RESPONSABLE'))


def add_role_context_to_template_vars(**template_vars):
    """
    Ajoute automatiquement les variables de contexte de rôle aux variables de template
    
    Args:
        **template_vars: Variables de template existantes
    
    Returns:
        dict: Variables de template avec contexte de rôle ajouté
    """
    context = get_template_context_for_role()
    template_vars.update(context)
    return template_vars
