def _ensure_chargetransport_for_user(user_id: int) -> None:
    """Hotfix: ensure a Chargetransport row exists for the given utilisateur_id.
    Required while DB FK enregistre_par -> chargetransport.chargetransport_id is in place.
    """
    ct = Chargetransport.query.get(user_id)
    if not ct:
        ct = Chargetransport(chargetransport_id=user_id)
        db.session.add(ct)
        # flush so PK exists for FK reference without committing early
        db.session.flush()

from datetime import datetime as dt
from typing import Tuple, Optional

from app.database import db
from app.models.trajet import Trajet
from app.models.aed import AED
from app.models.prestataire import Prestataire
from app.models.chargetransport import Chargetransport


def enregistrer_depart_aed(form, user) -> Tuple[bool, str]:
    """
    Enregistrer un départ AED (formulaire Flask-WTF validé).
    - Met à jour le kilométrage AED si fourni.
    - Utilise user.utilisateur_id comme 'enregistre_par'.
    """
    try:
        _ensure_chargetransport_for_user(user.utilisateur_id)
        trajet = Trajet(
            date_heure_depart=form.date_heure_depart.data,
            point_depart=form.point_depart.data,
            type_passagers=form.type_passagers.data,
            nombre_places_occupees=form.nombre_places_occupees.data,
            chauffeur_id=form.chauffeur_id.data,
            numero_aed=form.numero_aed.data,
            immat_bus=None,
            enregistre_par=user.utilisateur_id,
        )
        db.session.add(trajet)

        # Mettre à jour le kilométrage du véhicule AED sélectionné s'il est fourni dans le form
        if hasattr(form, 'kilometrage_actuel') and form.kilometrage_actuel.data is not None:
            aed = AED.query.filter_by(numero=form.numero_aed.data).first()
            if aed:
                aed.kilometrage = form.kilometrage_actuel.data
                db.session.add(aed)

        db.session.commit()
        return True, 'Départ AED enregistré avec succès.'
    except Exception as e:
        db.session.rollback()
        return False, f'Erreur : {e}'


def enregistrer_depart_prestataire(data, user) -> Tuple[bool, str]:
    """
    Enregistrer un départ Bus Agence à partir de request.form (soumission AJAX).
    data: MultiDict (request.form) contenant les champs nécessaires.
    """
    try:
        _ensure_chargetransport_for_user(user.utilisateur_id)
        date_heure_depart = data.get('date_heure_depart')
        point_depart = data.get('point_depart')
        # Accepter à la fois 'nom_agence' et 'nom_prestataire' selon le template
        nom_agence = data.get('nom_agence') or data.get('nom_prestataire')
        immat_bus = data.get('immat_bus')
        nom_chauffeur = data.get('nom_chauffeur')
        type_passagers = data.get('type_passagers', 'ETUDIANT')
        places_occupees = data.get('nombre_places_occupees', type=int) if hasattr(data, 'get') else int(data.get('nombre_places_occupees') or 0)
        places_occupees = places_occupees or 0

        if not all([date_heure_depart, point_depart, nom_agence, immat_bus, nom_chauffeur]):
            return False, 'Tous les champs sont obligatoires.'

        date_dt = dt.strptime(date_heure_depart, '%Y-%m-%dT%H:%M')

        # Insérer ou mettre à jour Bus Agence
        bus = Prestataire.query.get(immat_bus)
        if not bus:
            bus = Prestataire(
                immatriculation=immat_bus,
                nom_prestataire=nom_agence,
                nombre_places=50,
                nom_chauffeur=nom_chauffeur,
            )
            db.session.add(bus)
        else:
            bus.nom_prestataire = nom_agence
            bus.nombre_places = 50
            bus.nom_chauffeur = nom_chauffeur

        trajet = Trajet(
            date_heure_depart=date_dt,
            point_depart=point_depart,
            type_passagers=type_passagers,
            nombre_places_occupees=places_occupees,
            chauffeur_id=None,
            immat_bus=immat_bus,
            enregistre_par=user.utilisateur_id,
        )
        db.session.add(trajet)
        db.session.commit()
        return True, 'Départ Prestataire enregistré !'
    except Exception as e:
        db.session.rollback()
        return False, f'Erreur : {e}'


def enregistrer_depart_banekane_retour(form, user) -> Tuple[bool, str]:
    """
    Enregistrer un départ de Banekane (retour) via formulaire Flask-WTF validé.
    Gère les deux cas: type_bus == 'AED' ou Prestataire.
    """
    try:
        _ensure_chargetransport_for_user(user.utilisateur_id)
        type_bus = getattr(form, 'type_bus').data
        if type_bus == 'AED':
            trajet = Trajet(
                date_heure_depart=form.date_heure_depart.data,
                point_depart='Banekane',
                type_passagers=form.type_passagers.data,
                nombre_places_occupees=form.nombre_places_occupees.data,
                chauffeur_id=form.chauffeur_id.data,
                numero_aed=form.numero_aed.data,
                immat_bus=None,
                enregistre_par=user.utilisateur_id,
            )
            db.session.add(trajet)
            # MAJ kilométrage si fourni
            if hasattr(form, 'kilometrage_actuel') and form.kilometrage_actuel.data is not None:
                aed = AED.query.filter_by(numero=form.numero_aed.data).first()
                if aed:
                    aed.kilometrage = form.kilometrage_actuel.data
                    db.session.add(aed)
            db.session.commit()
            return True, 'Départ de Banekane (retour) enregistré et kilométrage mis à jour !'
        else:
            immat = form.immat_bus.data.strip() if getattr(form, 'immat_bus', None) else ''
            immat_bus_value: Optional[str] = None
            if immat:
                bus = Prestataire.query.get(immat)
                if not bus:
                    bus = Prestataire(
                        immatriculation=immat,
                        nom_prestataire=form.nom_agence.data,
                        nombre_places=form.nombre_places_occupees.data or 50,
                        nom_chauffeur=form.nom_chauffeur_agence.data or '',
                    )
                    db.session.add(bus)
                else:
                    bus.nom_prestataire = form.nom_agence.data
                    bus.nombre_places = form.nombre_places_occupees.data or bus.nombre_places
                    bus.nom_chauffeur = form.nom_chauffeur_agence.data or bus.nom_chauffeur
                immat_bus_value = immat

            trajet = Trajet(
                date_heure_depart=form.date_heure_depart.data,
                point_depart='Banekane',
                type_passagers='ETUDIANT',
                nombre_places_occupees=form.nombre_places_occupees.data,
                chauffeur_id=None,
                numero_aed=None,
                immat_bus=immat_bus_value,
                enregistre_par=user.utilisateur_id,
            )
            db.session.add(trajet)
            db.session.commit()
            return True, 'Départ de Banekane (retour) enregistré !'
    except Exception as e:
        db.session.rollback()
        return False, f'Erreur : {e}'
