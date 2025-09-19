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

from datetime import datetime
from typing import Tuple, Optional

from app.database import db
from app.models.trajet import Trajet
from app.models.bus_udm import BusUdM
from app.models.prestataire import Prestataire
from app.models.chargetransport import Chargetransport


# Paramètre global par défaut: autonomie (km par litre). Peut être surchargé par bus.
AUTONOMIE_KM_PAR_LITRE = 8.0


def update_autocontrol_after_km_change(bus_udm: BusUdM, new_km: int, prev_km: Optional[int]) -> None:
    """
    Met à jour automatiquement le niveau de carburant estimé en fonction du delta kilométrique.
    - Utilise la consommation spécifique du bus (bus_udm.consommation_km_par_litre) si définie,
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
    if getattr(bus_udm, 'consommation_km_par_litre', None):
        try:
            autonomie = float(bus_udm.consommation_km_par_litre)
        except (TypeError, ValueError):
            autonomie = None
    # 2) Sinon, calculer à partir des capacités si disponibles: km plein / litres réservoir
    if autonomie is None and getattr(bus_udm, 'capacite_plein_carburant', None) and getattr(bus_udm, 'capacite_reservoir_litres', None):
        try:
            km_plein = float(bus_udm.capacite_plein_carburant)
            litres = float(bus_udm.capacite_reservoir_litres)
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
    if hasattr(bus_udm, 'niveau_carburant_litres') and bus_udm.niveau_carburant_litres is not None:
        consommation_l = float(delta) / autonomie
        nouveau_niveau = (bus_udm.niveau_carburant_litres or 0.0) - consommation_l
        # Clamp entre 0 et capacité réservoir si connue
        try:
            cap = float(bus_udm.capacite_reservoir_litres) if getattr(bus_udm, 'capacite_reservoir_litres', None) else None
        except (TypeError, ValueError):
            cap = None
        if nouveau_niveau < 0:
            nouveau_niveau = 0.0
        if cap and cap > 0:
            nouveau_niveau = min(nouveau_niveau, cap)
        bus_udm.niveau_carburant_litres = round(nouveau_niveau, 3)
        # Recalculer le km critique carburant à partir du niveau courant
        # Priorité: consommation spécifique -> capacités plein / réservoir -> constante globale
        km_par_litre = None
        if getattr(bus_udm, 'consommation_km_par_litre', None):
            try:
                km_par_litre = float(bus_udm.consommation_km_par_litre)
            except (TypeError, ValueError):
                km_par_litre = None
        if km_par_litre is None and getattr(bus_udm, 'capacite_plein_carburant', None) and getattr(bus_udm, 'capacite_reservoir_litres', None):
            try:
                km_plein = float(bus_udm.capacite_plein_carburant)
                litres = float(bus_udm.capacite_reservoir_litres)
                if km_plein > 0 and litres and litres > 0:
                    km_par_litre = km_plein / litres
            except (TypeError, ValueError, ZeroDivisionError):
                km_par_litre = None
        if km_par_litre is None:
            km_par_litre = float(AUTONOMIE_KM_PAR_LITRE)
        # Mettre à jour l'odomètre critique carburant
        try:
            bus_udm.km_critique_carburant = round(float(newv) + (bus_udm.niveau_carburant_litres * km_par_litre), 3)
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
        # Refus si le Bus UdM est défaillant
        bus_udm = BusUdM.query.filter_by(numero=form.numero_aed.data).first()
        if bus_udm and getattr(bus_udm, 'etat_vehicule', None) == 'DEFAILLANT':
            return False, f"Le bus UdM {bus_udm.numero} est immobilisé (DEFAILLANT) et ne peut pas être utilisé pour un trajet."
        trajet = Trajet(
            type_trajet='UDM_INTERNE',
            date_heure_depart=form.date_heure_depart.data,
            point_depart=form.point_depart.data,
            type_passagers=form.type_passagers.data,
            nombre_places_occupees=form.nombre_places_occupees.data,
            chauffeur_id=form.chauffeur_id.data,
            numero_bus_udm=form.numero_aed.data,
            immat_bus=None,
            enregistre_par=user.utilisateur_id,
        )
        db.session.add(trajet)

        # Mettre à jour le kilométrage du véhicule Bus UdM sélectionné s'il est fourni dans le form
        if hasattr(form, 'kilometrage_actuel') and form.kilometrage_actuel.data is not None:
            bus_udm = BusUdM.query.filter_by(numero=form.numero_aed.data).first()
            if bus_udm:
                prev_km = bus_udm.kilometrage
                new_km = form.kilometrage_actuel.data
                # Validation: le nouvel odomètre ne doit pas être inférieur à l'ancien
                try:
                    if prev_km is not None and int(new_km) < int(prev_km):
                        db.session.rollback()
                        return False, f"Kilométrage invalide: {new_km} < {prev_km}."
                except (TypeError, ValueError):
                    db.session.rollback()
                    return False, "Kilométrage invalide."
                update_autocontrol_after_km_change(bus_udm, new_km, prev_km)
                bus_udm.kilometrage = new_km
                db.session.add(bus_udm)

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
        # Refus si le Bus UdM est défaillant
        bus_udm = BusUdM.query.filter_by(numero=form.numero_aed.data).first()
        if bus_udm and getattr(bus_udm, 'etat_vehicule', None) == 'DEFAILLANT':
            return False, f"Le bus UdM {bus_udm.numero} est immobilisé (DEFAILLANT) et ne peut pas être utilisé pour un trajet."
        trajet = Trajet(
            type_trajet='AUTRE',
            date_heure_depart=form.date_heure_depart.data,
            point_depart=form.point_depart.data,
            type_passagers=None,  # NULL pour les sorties hors ville
            nombre_places_occupees=None,  # NULL pour les sorties hors ville
            chauffeur_id=form.chauffeur_id.data,
            numero_bus_udm=form.numero_aed.data,
            immat_bus=None,
            enregistre_par=user.utilisateur_id,
            motif=form.motif_trajet.data,
        )
        db.session.add(trajet)

        # Mettre à jour le kilométrage du véhicule Bus UdM
        if hasattr(form, 'kilometrage_actuel') and form.kilometrage_actuel.data is not None:
            bus_udm = BusUdM.query.filter_by(numero=form.numero_aed.data).first()
            if bus_udm:
                prev_km = bus_udm.kilometrage
                new_km = form.kilometrage_actuel.data
                # Validation: le nouvel odomètre ne doit pas être inférieur à l'ancien
                try:
                    if prev_km is not None and int(new_km) < int(prev_km):
                        db.session.rollback()
                        return False, f"Kilométrage invalide: {new_km} < {prev_km}."
                except (TypeError, ValueError):
                    db.session.rollback()
                    return False, "Kilométrage invalide."
                update_autocontrol_after_km_change(bus_udm, new_km, prev_km)
                bus_udm.kilometrage = new_km
                db.session.add(bus_udm)

        db.session.commit()
        return True, 'Sortie hors de la ville (AED) enregistrée avec succès.'
    except Exception as e:
        db.session.rollback()
        return False, f'Erreur : {e}'


def enregistrer_depart_prestataire(data, user) -> Tuple[bool, str]:
    """
    Enregistre un départ de bus prestataire
    """
    try:
        _ensure_chargetransport_for_user(user.utilisateur_id)
        
        # Extraction et validation des données
        date_str = data.get('date_heure_depart')
        point_depart = data.get('lieu_depart')
        type_passagers = data.get('type_passagers')
        places_occupees = data.get('nombre_places_occupees')
        immat_bus = data.get('immat_bus')
        prestataire_id = data.get('nom_prestataire')
        nom_chauffeur = data.get('nom_chauffeur')
        
        if not date_str:
            return False, "Date et heure de départ requises"
        
        # Conversion de la date
        try:
            date_dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            return False, "Format de date invalide"
        
        if not all([point_depart, type_passagers, places_occupees, immat_bus, prestataire_id, nom_chauffeur]):
            return False, "Tous les champs obligatoires doivent être remplis"
        
        # Conversion du nombre de places et prestataire_id
        try:
            places_occupees = int(places_occupees)
            prestataire_id = int(prestataire_id)
        except (ValueError, TypeError):
            return False, "Nombre de places ou prestataire invalide"
        
        # Debug: afficher les données reçues
        print(f"DEBUG - Données reçues: {dict(data)}")
        print(f"DEBUG - prestataire_id: {prestataire_id}, nom_chauffeur: {nom_chauffeur}")
        
        # Création du trajet
        trajet = Trajet(
            type_trajet='PRESTATAIRE',
            prestataire_id=prestataire_id,
            date_heure_depart=date_dt,
            point_depart=point_depart,
            type_passagers=type_passagers,
            nombre_places_occupees=places_occupees,
            chauffeur_id=None,
            immat_bus=immat_bus,
            nom_chauffeur=nom_chauffeur,
            enregistre_par=user.utilisateur_id,
        )
        
        # Ajout du point d'arrivée si fourni
        point_arriver = data.get('lieu_arrivee')
        if point_arriver:
            trajet.point_arriver = point_arriver
        
        print(f"DEBUG - Trajet créé: {trajet}")
        print(f"DEBUG - Avant db.session.add")
        
        db.session.add(trajet)
        
        print(f"DEBUG - Avant db.session.commit")
        db.session.commit()
        
        print(f"DEBUG - Trajet enregistré avec ID: {trajet.trajet_id}")
        
        return True, f"Trajet prestataire enregistré avec succès (ID: {trajet.trajet_id})"
        
    except Exception as e:
        print(f"DEBUG - Erreur: {str(e)}")
        db.session.rollback()
        return False, f"Erreur lors de l'enregistrement : {str(e)}"


def enregistrer_depart_banekane_retour(form, user) -> Tuple[bool, str]:
    """
    Enregistrer un départ de Banekane (retour) via formulaire Flask-WTF validé.
    Gère les deux cas: type_bus == 'AED' ou Prestataire.
    """
    try:
        _ensure_chargetransport_for_user(user.utilisateur_id)
        type_bus = getattr(form, 'type_bus').data
        if type_bus == 'AED':
            # Refus si le Bus UdM est défaillant
            bus_udm = BusUdM.query.filter_by(numero=form.numero_aed.data).first()
            if bus_udm and getattr(bus_udm, 'etat_vehicule', None) == 'DEFAILLANT':
                return False, f"Le bus UdM {bus_udm.numero} est immobilisé (DEFAILLANT) et ne peut pas être utilisé pour un trajet."
            trajet = Trajet(
                type_trajet='UDM_INTERNE',
                date_heure_depart=form.date_heure_depart.data,
                point_depart='Banekane',
                type_passagers=form.type_passagers.data,
                nombre_places_occupees=form.nombre_places_occupees.data,
                chauffeur_id=form.chauffeur_id.data,
                numero_bus_udm=form.numero_aed.data,
                immat_bus=None,
                enregistre_par=user.utilisateur_id,
            )
            db.session.add(trajet)
            # MAJ kilométrage si fourni
            if hasattr(form, 'kilometrage_actuel') and form.kilometrage_actuel.data is not None:
                bus_udm = BusUdM.query.filter_by(numero=form.numero_aed.data).first()
                if bus_udm:
                    prev_km = bus_udm.kilometrage
                    new_km = form.kilometrage_actuel.data
                    # Validation: le nouvel odomètre ne doit pas être inférieur à l'ancien
                    try:
                        if prev_km is not None and int(new_km) < int(prev_km):
                            db.session.rollback()
                            return False, f"Kilométrage invalide: {new_km} < {prev_km}."
                    except (TypeError, ValueError):
                        db.session.rollback()
                        return False, "Kilométrage invalide."
                    update_autocontrol_after_km_change(bus_udm, new_km, prev_km)
                    bus_udm.kilometrage = new_km
                    db.session.add(bus_udm)
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
                type_trajet='PRESTATAIRE',
                date_heure_depart=form.date_heure_depart.data,
                point_depart='Banekane',
                type_passagers='ETUDIANT',
                nombre_places_occupees=form.nombre_places_occupees.data,
                chauffeur_id=None,
                numero_bus_udm=None,
                immat_bus=immat_bus_value,
                enregistre_par=user.utilisateur_id,
            )
            db.session.add(trajet)
            db.session.commit()
            return True, 'Départ de Banekane (retour) enregistré !'
    except Exception as e:
        db.session.rollback()
        return False, f'Erreur : {e}'


# ========================================
# NOUVEAUX SERVICES MODERNISÉS
# ========================================

def enregistrer_trajet_interne_bus_udm(form, user) -> Tuple[bool, str]:
    """
    Enregistrer un trajet interne avec bus UdM (remplace enregistrer_depart_aed).
    Champs attendus: lieu_depart, point_arriver, type_passagers, nombre_places_occupees,
    chauffeur_id, numero_bus_udm, kilometrage_actuel, date_heure_depart.
    """
    try:
        _ensure_chargetransport_for_user(user.utilisateur_id)

        # Refus si le Bus UdM est défaillant
        bus_udm = BusUdM.query.filter_by(numero=form.numero_bus_udm.data).first()
        if bus_udm and getattr(bus_udm, 'etat_vehicule', None) == 'DEFAILLANT':
            return False, f"Le bus UdM {bus_udm.numero} est immobilisé (DEFAILLANT) et ne peut pas être utilisé pour un trajet."

        trajet = Trajet(
            type_trajet='UDM_INTERNE',
            date_heure_depart=form.date_heure_depart.data,
            point_depart=form.lieu_depart.data,
            point_arriver=form.point_arriver.data,  # Nom correct selon votre DB
            type_passagers=form.type_passagers.data,
            nombre_places_occupees=form.nombre_places_occupees.data,
            chauffeur_id=form.chauffeur_id.data,
            numero_bus_udm=form.numero_bus_udm.data,
            immat_bus=None,
            enregistre_par=user.utilisateur_id,
        )
        db.session.add(trajet)

        # Mettre à jour le kilométrage du véhicule Bus UdM
        if hasattr(form, 'kilometrage_actuel') and form.kilometrage_actuel.data is not None:
            bus_udm = BusUdM.query.filter_by(numero=form.numero_bus_udm.data).first()
            if bus_udm:
                prev_km = bus_udm.kilometrage
                new_km = form.kilometrage_actuel.data
                # Validation: le nouvel odomètre ne doit pas être inférieur à l'ancien
                try:
                    if prev_km is not None and int(new_km) < int(prev_km):
                        db.session.rollback()
                        return False, f"Kilométrage invalide: {new_km} < {prev_km}."
                except (TypeError, ValueError):
                    db.session.rollback()
                    return False, "Kilométrage invalide."
                update_autocontrol_after_km_change(bus_udm, new_km, prev_km)
                bus_udm.kilometrage = new_km
                db.session.add(bus_udm)

        db.session.commit()
        return True, f'Trajet interne Bus UdM enregistré avec succès ({form.lieu_depart.data} → {form.point_arriver.data}).'
    except Exception as e:
        db.session.rollback()
        return False, f'Erreur lors de l\'enregistrement : {str(e)}'


def enregistrer_trajet_prestataire_modernise(form, user) -> Tuple[bool, str]:
    """
    Enregistrer un trajet avec bus prestataire (version modernisée).
    Champs attendus: lieu_depart, point_arriver, nom_prestataire, immat_bus, etc.
    """
    try:
        _ensure_chargetransport_for_user(user.utilisateur_id)

        # Debug: afficher les données reçues du formulaire
        print(f"DEBUG MODERNISE - Form data:")
        print(f"  - nom_prestataire: {form.nom_prestataire.data}")
        print(f"  - nom_chauffeur_prestataire: {form.nom_chauffeur_prestataire.data}")
        print(f"  - immat_bus: {form.immat_bus.data}")
        print(f"  - lieu_depart: {form.lieu_depart.data}")
        print(f"  - point_arriver: {form.point_arriver.data}")
        print(f"  - type_passagers: {form.type_passagers.data}")
        print(f"  - nombre_places_occupees: {form.nombre_places_occupees.data}")

        trajet = Trajet(
            type_trajet='PRESTATAIRE',
            prestataire_id=form.nom_prestataire.data,
            date_heure_depart=form.date_heure_depart.data,
            point_depart=form.lieu_depart.data,
            point_arriver=form.point_arriver.data,  # Nom correct selon votre DB
            type_passagers=form.type_passagers.data,
            nombre_places_occupees=form.nombre_places_occupees.data,
            chauffeur_id=None,
            numero_bus_udm=None,
            immat_bus=form.immat_bus.data,
            nom_chauffeur=form.nom_chauffeur_prestataire.data,
            enregistre_par=user.utilisateur_id,
        )
        
        print(f"DEBUG MODERNISE - Trajet créé: {trajet}")
        print(f"DEBUG MODERNISE - Avant db.session.add")
        
        db.session.add(trajet)
        
        print(f"DEBUG MODERNISE - Avant db.session.commit")
        db.session.commit()
        
        print(f"DEBUG MODERNISE - Trajet enregistré avec ID: {trajet.trajet_id}")
        
        return True, f'Trajet prestataire enregistré avec succès (ID: {trajet.trajet_id}) - {form.lieu_depart.data} → {form.point_arriver.data}'
    except Exception as e:
        print(f"DEBUG MODERNISE - Erreur: {str(e)}")
        db.session.rollback()
        return False, f'Erreur lors de l\'enregistrement : {str(e)}'


def enregistrer_autres_trajets(form, user) -> Tuple[bool, str]:
    """
    Enregistrer un autre trajet (remplace sortie hors ville).
    Champs attendus: lieu_depart, point_arriver, motif_trajet, chauffeur_id,
    numero_bus_udm, kilometrage_actuel, date_heure_depart.
    """
    try:
        _ensure_chargetransport_for_user(user.utilisateur_id)

        # Refus si le Bus UdM est défaillant
        bus_udm = BusUdM.query.filter_by(numero=form.numero_bus_udm.data).first()
        if bus_udm and getattr(bus_udm, 'etat_vehicule', None) == 'DEFAILLANT':
            return False, f"Le bus UdM {bus_udm.numero} est immobilisé (DEFAILLANT) et ne peut pas être utilisé pour un trajet."

        # Option B: Considérer les "autres trajets" comme des trajets internes Bus UdM
        # pour qu'ils apparaissent dans le rapport Bus UdM (type_trajet = 'UDM_INTERNE')
        trajet = Trajet(
            type_trajet='UDM_INTERNE',
            date_heure_depart=form.date_heure_depart.data,
            point_depart=form.lieu_depart.data,
            point_arriver=form.point_arriver.data,  # Nom correct selon votre DB
            type_passagers=None,  # Peut rester NULL si non applicable
            nombre_places_occupees=None,  # Peut rester NULL si non applicable
            chauffeur_id=form.chauffeur_id.data,
            numero_bus_udm=form.numero_bus_udm.data,
            immat_bus=None,
            enregistre_par=user.utilisateur_id,
            motif=form.motif_trajet.data,
        )
        db.session.add(trajet)

        # Mettre à jour le kilométrage du véhicule Bus UdM
        if hasattr(form, 'kilometrage_actuel') and form.kilometrage_actuel.data is not None:
            bus_udm = BusUdM.query.filter_by(numero=form.numero_bus_udm.data).first()
            if bus_udm:
                prev_km = bus_udm.kilometrage
                new_km = form.kilometrage_actuel.data
                # Validation: le nouvel odomètre ne doit pas être inférieur à l'ancien
                try:
                    if prev_km is not None and int(new_km) < int(prev_km):
                        db.session.rollback()
                        return False, f"Kilométrage invalide: {new_km} < {prev_km}."
                except (TypeError, ValueError):
                    db.session.rollback()
                    return False, "Kilométrage invalide."
                update_autocontrol_after_km_change(bus_udm, new_km, prev_km)
                bus_udm.kilometrage = new_km
                db.session.add(bus_udm)

        db.session.commit()
        return True, f'Autre trajet (Bus UdM) enregistré avec succès ({form.lieu_depart.data} → {form.point_arriver.data}).'
    except Exception as e:
        db.session.rollback()
        return False, f'Erreur lors de l\'enregistrement : {str(e)}'
