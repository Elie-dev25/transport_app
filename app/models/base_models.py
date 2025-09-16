"""
Modèles de base pour éliminer la duplication
Phase 3 - Classes de base et mixins pour les modèles
"""

from datetime import datetime
from app.database import db


class BaseModel(db.Model):
    """
    Classe de base abstraite pour tous les modèles
    Contient les champs communs et méthodes utilitaires
    """
    __abstract__ = True
    
    # Champs de métadonnées communs
    created_at = db.Column(
        db.DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        comment='Date de création de l\'enregistrement'
    )
    
    updated_at = db.Column(
        db.DateTime, 
        nullable=False, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        comment='Date de dernière modification'
    )
    
    # Champ optionnel pour soft delete
    is_active = db.Column(
        db.Boolean, 
        nullable=False, 
        default=True,
        comment='Indique si l\'enregistrement est actif'
    )
    
    def save(self):
        """Sauvegarde l'objet en base"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self, soft_delete=True):
        """
        Supprime l'objet (soft delete par défaut)
        
        Args:
            soft_delete: Si True, marque comme inactif. Si False, supprime physiquement.
        """
        if soft_delete:
            self.is_active = False
            self.save()
        else:
            db.session.delete(self)
            db.session.commit()
    
    def to_dict(self, exclude_fields=None):
        """
        Convertit l'objet en dictionnaire
        
        Args:
            exclude_fields: Liste des champs à exclure
        """
        exclude_fields = exclude_fields or []
        result = {}
        
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                # Convertir les dates en string pour JSON
                if isinstance(value, datetime):
                    value = value.isoformat()
                result[column.name] = value
        
        return result
    
    @classmethod
    def get_active(cls):
        """Retourne tous les enregistrements actifs"""
        return cls.query.filter_by(is_active=True)
    
    @classmethod
    def get_by_id(cls, id_value):
        """Récupère un enregistrement par son ID"""
        return cls.query.get(id_value)
    
    def __repr__(self):
        """Représentation générique"""
        class_name = self.__class__.__name__
        if hasattr(self, 'id'):
            return f"<{class_name} id={self.id}>"
        elif hasattr(self, f"{class_name.lower()}_id"):
            id_field = f"{class_name.lower()}_id"
            return f"<{class_name} id={getattr(self, id_field)}>"
        else:
            return f"<{class_name}>"


class UserRoleMixin:
    """
    Mixin pour les modèles de rôles utilisateur
    Élimine la duplication des FK vers utilisateur
    """
    
    @classmethod
    def create_user_role_fields(cls, role_name):
        """
        Crée les champs standard pour un rôle utilisateur
        
        Args:
            role_name: Nom du rôle (ex: 'administrateur', 'chauffeur')
        """
        # ID du rôle (FK vers utilisateur)
        id_field_name = f"{role_name}_id"
        setattr(cls, id_field_name, db.Column(
            db.Integer, 
            db.ForeignKey('utilisateur.utilisateur_id', ondelete='CASCADE', onupdate='CASCADE'), 
            primary_key=True,
            comment=f'ID du {role_name} (FK vers utilisateur)'
        ))
        
        # Relation vers utilisateur
        setattr(cls, 'utilisateur', db.relationship(
            'Utilisateur', 
            backref=role_name.lower(), 
            uselist=False,
            cascade='all, delete-orphan',
            single_parent=True
        ))
    
    def get_user_info(self):
        """Retourne les informations utilisateur associées"""
        if hasattr(self, 'utilisateur') and self.utilisateur:
            return {
                'nom': self.utilisateur.nom,
                'prenom': self.utilisateur.prenom,
                'login': self.utilisateur.login,
                'role': self.utilisateur.role,
                'email': getattr(self.utilisateur, 'email', None)
            }
        return None
    
    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        if hasattr(self, 'utilisateur') and self.utilisateur:
            return f"{self.utilisateur.prenom} {self.utilisateur.nom}"
        return "Utilisateur inconnu"


class PermisDriverMixin:
    """
    Mixin pour les modèles avec permis de conduire
    Élimine la duplication des champs de permis
    """
    
    numero_permis = db.Column(
        db.String(50), 
        nullable=False, 
        unique=True,
        comment='Numéro du permis de conduire'
    )
    
    date_delivrance_permis = db.Column(
        db.Date, 
        nullable=False,
        comment='Date de délivrance du permis'
    )
    
    date_expiration_permis = db.Column(
        db.Date, 
        nullable=False,
        comment='Date d\'expiration du permis'
    )
    
    def is_permis_valid(self):
        """Vérifie si le permis est encore valide"""
        from datetime import date
        return self.date_expiration_permis >= date.today()
    
    def days_until_expiration(self):
        """Retourne le nombre de jours avant expiration du permis"""
        from datetime import date
        if self.is_permis_valid():
            return (self.date_expiration_permis - date.today()).days
        return 0
    
    def get_permis_info(self):
        """Retourne les informations du permis"""
        return {
            'numero': self.numero_permis,
            'date_delivrance': self.date_delivrance_permis.isoformat() if self.date_delivrance_permis else None,
            'date_expiration': self.date_expiration_permis.isoformat() if self.date_expiration_permis else None,
            'is_valid': self.is_permis_valid(),
            'days_until_expiration': self.days_until_expiration()
        }


class ContactInfoMixin:
    """
    Mixin pour les modèles avec informations de contact
    """
    
    telephone = db.Column(
        db.String(30), 
        nullable=True,
        comment='Numéro de téléphone'
    )
    
    email = db.Column(
        db.String(120), 
        nullable=True,
        comment='Adresse email'
    )
    
    adresse = db.Column(
        db.Text, 
        nullable=True,
        comment='Adresse postale'
    )
    
    def get_contact_info(self):
        """Retourne les informations de contact"""
        return {
            'telephone': self.telephone,
            'email': self.email,
            'adresse': self.adresse
        }


class VehicleMixin:
    """
    Mixin pour les modèles de véhicules
    Élimine la duplication des champs véhicule
    """
    
    numero = db.Column(
        db.String(20), 
        nullable=False, 
        unique=True,
        comment='Numéro d\'identification du véhicule'
    )
    
    immatriculation = db.Column(
        db.String(20), 
        nullable=True,
        comment='Plaque d\'immatriculation'
    )
    
    marque = db.Column(
        db.String(50), 
        nullable=True,
        comment='Marque du véhicule'
    )
    
    modele = db.Column(
        db.String(50), 
        nullable=True,
        comment='Modèle du véhicule'
    )
    
    annee = db.Column(
        db.Integer, 
        nullable=True,
        comment='Année de fabrication'
    )
    
    nombre_places = db.Column(
        db.Integer, 
        nullable=False, 
        default=50,
        comment='Nombre de places assises'
    )
    
    kilometrage = db.Column(
        db.Integer, 
        nullable=False, 
        default=0,
        comment='Kilométrage actuel'
    )
    
    def get_vehicle_info(self):
        """Retourne les informations du véhicule"""
        return {
            'numero': self.numero,
            'immatriculation': self.immatriculation,
            'marque': self.marque,
            'modele': self.modele,
            'annee': self.annee,
            'nombre_places': self.nombre_places,
            'kilometrage': self.kilometrage
        }
    
    def update_kilometrage(self, nouveau_km):
        """Met à jour le kilométrage si supérieur à l'actuel"""
        if nouveau_km > self.kilometrage:
            self.kilometrage = nouveau_km
            self.save()
            return True
        return False


# Fonctions utilitaires pour créer des modèles dynamiquement
def create_user_role_model(role_name, additional_fields=None):
    """
    Factory pour créer des modèles de rôles utilisateur
    
    Args:
        role_name: Nom du rôle (ex: 'superviseur')
        additional_fields: Dictionnaire de champs supplémentaires
    """
    additional_fields = additional_fields or {}
    
    class_name = role_name.capitalize()
    table_name = role_name.lower()
    
    # Créer la classe dynamiquement
    attrs = {
        '__tablename__': table_name,
        '__repr__': lambda self: f"<{class_name} id={getattr(self, f'{role_name}_id')}>"
    }
    
    # Ajouter les champs supplémentaires
    attrs.update(additional_fields)
    
    # Créer la classe
    model_class = type(class_name, (BaseModel, UserRoleMixin), attrs)
    
    # Créer les champs de rôle utilisateur
    model_class.create_user_role_fields(role_name)
    
    return model_class
