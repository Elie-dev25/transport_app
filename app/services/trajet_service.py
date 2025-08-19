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


# Paramètre global par défaut: autonomie (km par litre). Peut être surchargé par bus.
AUTONOMIE_KM_PAR_LITRE = 8.0


def update_autocontrol_after_km_change(aed: AED, new_km: int, prev_km: Optional[int]) -> None:
    """
    Met à jour automatiquement le niveau de carburant estimé en fonction du delta kilométrique.
    - Utilise la consommation spécifique du bus (aed.consommation_km_par_litre) si définie,
      sinon la constante globale AUTONOMIE_KM_PAR_LITRE.
    - Ne modifie pas les seuils critiques (km_critique_*), qui sont exprimés en km.
    """
    if new_km is None:
        return
    try:
        prev = int(prev_km) if prev_km is not None else None
        newv = int(new_km)
    except (TypeError, ValueError):
        return
    if prev is None:
        return
    delta = newv - prev
    if delta <= 0:
        return

    # Déterminer l'autonomie (km par litre)
    autonomie = None
    # 1) Consommation spécifique si définie
    if getattr(aed, 'consommation_km_par_litre', None):
        try:
            autonomie = float(aed.consommation_km_par_litre)
        except (TypeError, ValueError):
            autonomie = None
    # 2) Sinon, calculer à partir des capacités si disponibles: km plein / litres réservoir
    if autonomie is None and getattr(aed, 'capacite_plein_carburant', None) and getattr(aed, 'capacite_reservoir_litres', None):
        try:
            km_plein = float(aed.capacite_plein_carburant)
            litres = float(aed.capacite_reservoir_litres)
            if km_plein > 0 and litres and litres > 0:
                autonomie = km_plein / litres
        except (TypeError, ValueError, ZeroDivisionError):
            autonomie = None
    # 3) Repli sur la constante globale
    if autonomie is None:
        autonomie = float(AUTONOMIE_KM_PAR_LITRE)

    if autonomie <= 0:
        return

    # Mettre à jour le niveau de carburant (si suivi activé)
    if hasattr(aed, 'niveau_carburant_litres') and aed.niveau_carburant_litres is not None:
        consommation_l = float(delta) / autonomie
        nouveau_niveau = (aed.niveau_carburant_litres or 0.0) - consommation_l
        # Clamp entre 0 et capacité réservoir si connue
        try:
            cap = float(aed.capacite_reservoir_litres) if getattr(aed, 'capacite_reservoir_litres', None) else None
        except (TypeError, ValueError):
            cap = None
        if nouveau_niveau < 0:
            nouveau_niveau = 0.0
        if cap and cap > 0:
            nouveau_niveau = min(nouveau_niveau, cap)
        aed.niveau_carburant_litres = round(nouveau_niveau, 3)
        # Recalculer le km critique carburant à partir du niveau courant
        # Priorité: consommation spécifique -> capacités plein / réservoir -> constante globale
        km_par_litre = None
        if getattr(aed, 'consommation_km_par_litre', None):
            try:
                km_par_litre = float(aed.consommation_km_par_litre)
            except (TypeError, ValueError):
                km_par_litre = None
        if km_par_litre is None and getattr(aed, 'capacite_plein_carburant', None) and getattr(aed, 'capacite_reservoir_litres', None):
            try:
                km_plein = float(aed.capacite_plein_carburant)
                litres = float(aed.capacite_reservoir_litres)
                if km_plein > 0 and litres and litres > 0:
                    km_par_litre = km_plein / litres
            except (TypeError, ValueError, ZeroDivisionError):
                km_par_litre = None
        if km_par_litre is None:
            km_par_litre = float(AUTONOMIE_KM_PAR_LITRE)
        # Mettre à jour l'odomètre critique carburant
        try:
            aed.km_critique_carburant = round(float(newv) + (aed.niveau_carburant_litres * km_par_litre), 3)
        except Exception:
            # En cas d'erreur de conversion, ne pas casser le flux
            pass


def enregistrer_depart_aed(form, user) -> Tuple[bool, str]:
    """
    Enregistrer un départ AED (formulaire Flask-WTF validé).
    - Met à jour le kilométrage AED si fourni.
    - Utilise user.utilisateur_id comme 'enregistre_par'.
    """
    try:
        _ensure_chargetransport_for_user(user.utilisateur_id)
        # Refus si l'AED est défaillant
        aed_bus = AED.query.filter_by(numero=form.numero_aed.data).first()
        if aed_bus and getattr(aed_bus, 'etat_vehicule', None) == 'DEFAILLANT':
            return False, f"Le bus AED {aed_bus.numero} est immobilisé (DEFAILLANT) et ne peut pas être utilisé pour un trajet."
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
                prev_km = aed.kilometrage
                new_km = form.kilometrage_actuel.data
                # Validation: le nouvel odomètre ne doit pas être inférieur à l'ancien
                try:
                    if prev_km is not None and int(new_km) < int(prev_km):
                        db.session.rollback()
                        return False, f"Kilométrage invalide: {new_km} < {prev_km}."
                except (TypeError, ValueError):
                    db.session.rollback()
                    return False, "Kilométrage invalide."
                update_autocontrol_after_km_change(aed, new_km, prev_km)
                aed.kilometrage = new_km
                db.session.add(aed)

        db.session.commit()
        return True, 'Départ AED enregistré avec succès.'
    except Exception as e:
        db.session.rollback()
        return False, f'Erreur : {e}'


def enregistrer_depart_sortie_hors_ville(form, user) -> Tuple[bool, str]:
    """
    Enregistrer un départ AED pour une sortie hors de la ville (formulaire Flask-WTF validé).
    Champs attendus: point_depart, chauffeur_id, numero_aed, destination, motif,
    kilometrage_actuel, date_heure_depart.
    """
    try:
        _ensure_chargetransport_for_user(user.utilisateur_id)
        # Refus si l'AED est défaillant
        aed_bus = AED.query.filter_by(numero=form.numero_aed.data).first()
        if aed_bus and getattr(aed_bus, 'etat_vehicule', None) == 'DEFAILLANT':
            return False, f"Le bus AED {aed_bus.numero} est immobilisé (DEFAILLANT) et ne peut pas être utilisé pour un trajet."
        trajet = Trajet(
            date_heure_depart=form.date_heure_depart.data,
            point_depart=form.point_depart.data,
            type_passagers=None,  # NULL pour les sorties hors ville
            nombre_places_occupees=None,  # NULL pour les sorties hors ville
            chauffeur_id=form.chauffeur_id.data,
            numero_aed=form.numero_aed.data,
            immat_bus=None,
            enregistre_par=user.utilisateur_id,
            destination=form.destination.data,
            motif=form.motif.data,
        )
        db.session.add(trajet)

        # Mettre à jour le kilométrage du véhicule AED
        if hasattr(form, 'kilometrage_actuel') and form.kilometrage_actuel.data is not None:
            aed = AED.query.filter_by(numero=form.numero_aed.data).first()
            if aed:
                prev_km = aed.kilometrage
                new_km = form.kilometrage_actuel.data
                # Validation: le nouvel odomètre ne doit pas être inférieur à l'ancien
                try:
                    if prev_km is not None and int(new_km) < int(prev_km):
                        db.session.rollback()
                        return False, f"Kilométrage invalide: {new_km} < {prev_km}."
                except (TypeError, ValueError):
                    db.session.rollback()
                    return False, "Kilométrage invalide."
                update_autocontrol_after_km_change(aed, new_km, prev_km)
                aed.kilometrage = new_km
                db.session.add(aed)

        db.session.commit()
        return True, 'Sortie hors de la ville (AED) enregistrée avec succès.'
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
            # Refus si l'AED est défaillant
            aed_bus = AED.query.filter_by(numero=form.numero_aed.data).first()
            if aed_bus and getattr(aed_bus, 'etat_vehicule', None) == 'DEFAILLANT':
                return False, f"Le bus AED {aed_bus.numero} est immobilisé (DEFAILLANT) et ne peut pas être utilisé pour un trajet."
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
                    prev_km = aed.kilometrage
                    new_km = form.kilometrage_actuel.data
                    # Validation: le nouvel odomètre ne doit pas être inférieur à l'ancien
                    try:
                        if prev_km is not None and int(new_km) < int(prev_km):
                            db.session.rollback()
                            return False, f"Kilométrage invalide: {new_km} < {prev_km}."
                    except (TypeError, ValueError):
                        db.session.rollback()
                        return False, "Kilométrage invalide."
                    update_autocontrol_after_km_change(aed, new_km, prev_km)
                    aed.kilometrage = new_km
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
