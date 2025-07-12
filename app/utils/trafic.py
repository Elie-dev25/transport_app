"""Utility functions to compute real-time traffic statistics for dashboards."""
from datetime import date, datetime as dt, time
from typing import Dict

from app.database import db
from app.models.trajet import Trajet


def daily_student_trafic(target_date: date | None = None) -> Dict[str, int]:
    """Return traffic numbers for student passengers for the given day.

    Keys returned:
        - arrives: total number of student passengers transported to campus that day.
        - partis: placeholder for number of student passengers who left the campus (0 for now).
        - present: arrives - partis.

    Args:
        target_date: day to compute stats for. Defaults to today.
    """
    if target_date is None:
        target_date = date.today()

    start_dt = dt.combine(target_date, time.min)
    end_dt = dt.combine(target_date, time.max)

    arrives = (
        db.session.query(db.func.coalesce(db.func.sum(Trajet.nombre_places_occupees), 0))
        .filter(
            Trajet.type_passagers == 'ETUDIANT',
            Trajet.point_depart.in_(['Mfetum', 'Ancienne mairie']),
            Trajet.date_heure_depart.between(start_dt, end_dt)
        )
        .scalar()
    )

    # Départs (étudiants enregistrés comme départ de Banekane)
    partis = (
        db.session.query(db.func.coalesce(db.func.sum(Trajet.nombre_places_occupees), 0))
        .filter(
            Trajet.type_passagers == 'ETUDIANT',
            Trajet.point_depart == 'Banekane',
            Trajet.date_heure_depart.between(start_dt, end_dt)
        )
        .scalar()
    )

    present = arrives - partis

    return {
        'arrives': int(arrives or 0),
        'partis': int(partis),
        'present': int(present),
    }
