"""
Service pour la gestion centralisée des formulaires
Évite la duplication de code d'initialisation des formulaires
Version étendue - Phase 1 Refactoring
"""

from typing import List, Tuple, Optional, Any
from app.models.chauffeur import Chauffeur
from app.models.bus_udm import BusUdM
from app.models.prestataire import Prestataire
from app.services.query_service import QueryService


class FormService:
    """Service pour initialiser les formulaires avec les données dynamiques"""
    
    @staticmethod
    def populate_trajet_form_choices(form, bus_filter: str = 'BON_ONLY'):
        """
        Peuple les choix dynamiques pour les formulaires de trajets
        Version étendue utilisant QueryService pour éviter duplication

        Args:
            form: Formulaire à peupler
            bus_filter: 'BON_ONLY' (défaut), 'ALL', ou 'ACTIVE'
        """
        try:
            # Choix des chauffeurs (utilise QueryService)
            if hasattr(form, 'chauffeur_id'):
                form.chauffeur_id.choices = QueryService.get_chauffeur_choices()

            # Choix des bus UdM selon le filtre
            bus_choices = FormService._get_bus_choices(bus_filter)

            if hasattr(form, 'numero_bus_udm'):
                form.numero_bus_udm.choices = bus_choices

            # Choix des bus UdM (ancien nom pour compatibilité)
            if hasattr(form, 'numero_aed'):
                form.numero_aed.choices = bus_choices

            # Choix des prestataires (utilise QueryService)
            prestataire_choices = QueryService.get_prestataire_choices()

            if hasattr(form, 'prestataire_id'):
                form.prestataire_id.choices = prestataire_choices

            # Choix des prestataires (nom alternatif)
            if hasattr(form, 'nom_prestataire'):
                form.nom_prestataire.choices = prestataire_choices

        except Exception as e:
            # En cas d'erreur, initialiser avec des listes vides
            FormService._set_empty_choices(form)
            print(f"Erreur lors du peuplement des choix du formulaire: {e}")

    @staticmethod
    def populate_multiple_forms(*forms, bus_filter: str = 'BON_ONLY'):
        """
        Peuple plusieurs formulaires en une seule fois
        Évite les appels multiples et optimise les requêtes
        """
        for form in forms:
            if form:
                FormService.populate_trajet_form_choices(form, bus_filter)

    @staticmethod
    def _get_bus_choices(bus_filter: str) -> List[Tuple[str, str]]:
        """Retourne les choix de bus selon le filtre"""
        if bus_filter == 'BON_ONLY':
            buses = QueryService.get_active_buses()
        elif bus_filter == 'ALL':
            buses = QueryService.get_all_buses()
        else:  # 'ACTIVE' ou autre
            buses = QueryService.get_active_buses()

        return [(b.numero, b.numero) for b in buses]

    @staticmethod
    def _set_empty_choices(form):
        """Initialise les choix avec des listes vides en cas d'erreur"""
        empty_fields = ['chauffeur_id', 'numero_bus_udm', 'numero_aed', 'prestataire_id', 'nom_prestataire']
        for field_name in empty_fields:
            if hasattr(form, field_name):
                getattr(form, field_name).choices = []
    
    @staticmethod
    def get_bus_choices(filter_type: str = 'BON_ONLY'):
        """
        Retourne les choix de bus disponibles
        Utilise QueryService pour éviter duplication
        """
        try:
            return FormService._get_bus_choices(filter_type)
        except Exception:
            return []

    @staticmethod
    def get_chauffeur_choices():
        """
        Retourne les choix de chauffeurs disponibles
        Utilise QueryService pour éviter duplication
        """
        try:
            return QueryService.get_chauffeur_choices()
        except Exception:
            return []

    @staticmethod
    def get_prestataire_choices():
        """
        Retourne les choix de prestataires disponibles
        Utilise QueryService pour éviter duplication
        """
        try:
            return QueryService.get_prestataire_choices()
        except Exception:
            return []

    @staticmethod
    def populate_form_with_data(form, data: dict):
        """
        Peuple un formulaire avec des données
        Utile pour l'édition d'enregistrements existants
        """
        for field_name, value in data.items():
            if hasattr(form, field_name):
                field = getattr(form, field_name)
                field.data = value

    @staticmethod
    def validate_form_with_choices(form, bus_filter: str = 'BON_ONLY') -> Tuple[bool, dict]:
        """
        Valide un formulaire après avoir peuplé ses choix
        Retourne (is_valid, errors)
        """
        try:
            # Peupler les choix avant validation
            FormService.populate_trajet_form_choices(form, bus_filter)

            # Valider
            is_valid = form.validate()
            errors = form.errors if not is_valid else {}

            return is_valid, errors

        except Exception as e:
            return False, {'form_error': f'Erreur de validation: {str(e)}'}

    @staticmethod
    def get_form_choices_data() -> dict:
        """
        Retourne toutes les données de choix en une seule fois
        Optimise les requêtes pour les pages avec plusieurs formulaires
        """
        try:
            return {
                'chauffeurs': QueryService.get_chauffeur_choices(),
                'buses_bon': FormService._get_bus_choices('BON_ONLY'),
                'buses_all': FormService._get_bus_choices('ALL'),
                'prestataires': QueryService.get_prestataire_choices()
            }
        except Exception as e:
            print(f"Erreur lors de la récupération des choix: {e}")
            return {
                'chauffeurs': [],
                'buses_bon': [],
                'buses_all': [],
                'prestataires': []
            }
