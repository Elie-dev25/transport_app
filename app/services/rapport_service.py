"""
Service de génération de rapports réutilisable
Export CSV, PDF et données pour tous les rôles
"""

import io
import csv
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
from sqlalchemy import func, and_

from app.database import db
from app.models.trajet import Trajet
from app.models.bus_udm import BusUdM
from app.models.panne_bus_udm import PanneBusUdM
from app.models.vidange import Vidange
from app.models.carburation import Carburation

# Import optionnel de reportlab pour l'export PDF
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class RapportService:
    """Service pour la génération de rapports"""
    
    @staticmethod
    def get_rapport_trajets(date_debut: date = None, date_fin: date = None, 
                           type_trajet: str = None) -> Dict[str, Any]:
        """
        Génère un rapport des trajets
        Utilisable par : ADMIN, SUPERVISEUR, CHARGE
        """
        if not date_debut:
            date_debut = date.today().replace(day=1)  # Début du mois
        if not date_fin:
            date_fin = date.today()
        
        # Requête de base
        query = Trajet.query.filter(
            func.date(Trajet.date_heure_depart) >= date_debut,
            func.date(Trajet.date_heure_depart) <= date_fin
        )
        
        if type_trajet:
            query = query.filter(Trajet.type_trajet == type_trajet)
        
        trajets = query.order_by(Trajet.date_heure_depart.desc()).all()
        
        # Statistiques
        total_trajets = len(trajets)
        total_etudiants = sum(t.nombre_places_occupees for t in trajets if t.type_passagers == 'ETUDIANT')
        total_km = sum(t.distance_km for t in trajets if t.distance_km)
        
        # Répartition par type
        repartition_type = {}
        for trajet in trajets:
            type_t = trajet.type_trajet
            if type_t not in repartition_type:
                repartition_type[type_t] = 0
            repartition_type[type_t] += 1
        
        # Données détaillées
        trajets_data = []
        for trajet in trajets:
            bus = BusUdM.query.get(trajet.bus_udm_id) if trajet.bus_udm_id else None
            trajets_data.append({
                'id': trajet.id,
                'date_heure_depart': trajet.date_heure_depart,
                'point_depart': trajet.point_depart,
                'point_arrivee': trajet.point_arrivee,
                'type_trajet': trajet.type_trajet,
                'type_passagers': trajet.type_passagers,
                'nombre_places_occupees': trajet.nombre_places_occupees,
                'distance_km': trajet.distance_km,
                'bus_numero': bus.numero if bus else None,
                'bus_immatriculation': bus.immatriculation if bus else None,
                'chauffeur_nom': trajet.chauffeur.nom if trajet.chauffeur else None
            })
        
        return {
            'periode': {
                'debut': date_debut,
                'fin': date_fin
            },
            'statistiques': {
                'total_trajets': total_trajets,
                'total_etudiants': total_etudiants,
                'total_km': total_km,
                'repartition_type': repartition_type
            },
            'trajets': trajets_data
        }
    
    @staticmethod
    def get_rapport_maintenance(date_debut: date = None, date_fin: date = None) -> Dict[str, Any]:
        """
        Génère un rapport de maintenance
        Utilisable par : ADMIN, SUPERVISEUR, CHARGE, MECANICIEN
        """
        if not date_debut:
            date_debut = date.today().replace(day=1)
        if not date_fin:
            date_fin = date.today()
        
        # Pannes
        pannes = PanneBusUdM.query.filter(
            func.date(PanneBusUdM.date_heure) >= date_debut,
            func.date(PanneBusUdM.date_heure) <= date_fin
        ).order_by(PanneBusUdM.date_heure.desc()).all()
        
        # Vidanges
        vidanges = Vidange.query.filter(
            Vidange.date_vidange >= date_debut,
            Vidange.date_vidange <= date_fin
        ).order_by(Vidange.date_vidange.desc()).all()
        
        # Carburations
        carburations = Carburation.query.filter(
            Carburation.date_carburation >= date_debut,
            Carburation.date_carburation <= date_fin
        ).order_by(Carburation.date_carburation.desc()).all()
        
        # Statistiques
        total_pannes = len(pannes)
        pannes_critiques = len([p for p in pannes if p.criticite == 'HAUTE'])
        pannes_resolues = len([p for p in pannes if p.resolue])
        
        total_vidanges = len(vidanges)
        total_carburations = len(carburations)
        cout_carburant = sum(c.cout_total for c in carburations)
        
        return {
            'periode': {
                'debut': date_debut,
                'fin': date_fin
            },
            'statistiques': {
                'total_pannes': total_pannes,
                'pannes_critiques': pannes_critiques,
                'pannes_resolues': pannes_resolues,
                'taux_resolution': round((pannes_resolues / total_pannes * 100) if total_pannes > 0 else 0, 1),
                'total_vidanges': total_vidanges,
                'total_carburations': total_carburations,
                'cout_carburant': cout_carburant
            },
            'pannes': [RapportService._format_panne_rapport(p) for p in pannes],
            'vidanges': [RapportService._format_vidange_rapport(v) for v in vidanges],
            'carburations': [RapportService._format_carburation_rapport(c) for c in carburations]
        }
    
    @staticmethod
    def export_trajets_csv(trajets_data: List[Dict[str, Any]]) -> Tuple[str, str]:
        """
        Exporte les trajets en CSV
        Utilisable par : ADMIN, SUPERVISEUR, CHARGE
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # En-têtes
        headers = [
            'Date/Heure', 'Point Départ', 'Point Arrivée', 'Type Trajet',
            'Type Passagers', 'Places Occupées', 'Distance (km)',
            'Bus N°', 'Immatriculation', 'Chauffeur'
        ]
        writer.writerow(headers)
        
        # Données
        for trajet in trajets_data:
            writer.writerow([
                trajet['date_heure_depart'].strftime('%d/%m/%Y %H:%M') if trajet['date_heure_depart'] else '',
                trajet['point_depart'] or '',
                trajet['point_arrivee'] or '',
                trajet['type_trajet'] or '',
                trajet['type_passagers'] or '',
                trajet['nombre_places_occupees'] or 0,
                trajet['distance_km'] or 0,
                trajet['bus_numero'] or '',
                trajet['bus_immatriculation'] or '',
                trajet['chauffeur_nom'] or ''
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        filename = f"trajets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return csv_content, filename
    
    @staticmethod
    def export_maintenance_csv(maintenance_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Exporte les données de maintenance en CSV
        Utilisable par : ADMIN, SUPERVISEUR, CHARGE, MECANICIEN
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Section Pannes
        writer.writerow(['=== PANNES ==='])
        headers_pannes = [
            'Date/Heure', 'Bus N°', 'Immatriculation', 'Description',
            'Criticité', 'Immobilisation', 'Résolue', 'Enregistré par'
        ]
        writer.writerow(headers_pannes)
        
        for panne in maintenance_data['pannes']:
            writer.writerow([
                panne['date_heure'].strftime('%d/%m/%Y %H:%M') if panne['date_heure'] else '',
                panne['numero_bus_udm'] or '',
                panne['immatriculation'] or '',
                panne['description'] or '',
                panne['criticite'] or '',
                'Oui' if panne['immobilisation'] else 'Non',
                'Oui' if panne['resolue'] else 'Non',
                panne['enregistre_par'] or ''
            ])
        
        writer.writerow([])  # Ligne vide
        
        # Section Vidanges
        writer.writerow(['=== VIDANGES ==='])
        headers_vidanges = [
            'Date', 'Bus N°', 'Immatriculation', 'Kilométrage', 'Type Huile', 'Remarque'
        ]
        writer.writerow(headers_vidanges)
        
        for vidange in maintenance_data['vidanges']:
            writer.writerow([
                vidange['date_vidange'].strftime('%d/%m/%Y') if vidange['date_vidange'] else '',
                vidange['bus_numero'] or '',
                vidange['bus_immatriculation'] or '',
                vidange['kilometrage'] or 0,
                vidange['type_huile'] or '',
                vidange['remarque'] or ''
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        filename = f"maintenance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return csv_content, filename
    
    @staticmethod
    def export_trajets_pdf(trajets_data: List[Dict[str, Any]]) -> Tuple[bytes, str]:
        """
        Exporte les trajets en PDF
        Utilisable par : ADMIN, SUPERVISEUR, CHARGE
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab non disponible pour l'export PDF")
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Titre
        title = Paragraph("Rapport des Trajets", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Informations générales
        info = Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles['Normal'])
        story.append(info)
        story.append(Spacer(1, 20))
        
        # Tableau des trajets
        if trajets_data:
            data = [['Date/Heure', 'Départ', 'Arrivée', 'Type', 'Places', 'Distance']]
            
            for trajet in trajets_data[:50]:  # Limiter à 50 pour éviter les pages trop longues
                data.append([
                    trajet['date_heure_depart'].strftime('%d/%m %H:%M') if trajet['date_heure_depart'] else '',
                    trajet['point_depart'][:15] if trajet['point_depart'] else '',
                    trajet['point_arrivee'][:15] if trajet['point_arrivee'] else '',
                    trajet['type_trajet'][:10] if trajet['type_trajet'] else '',
                    str(trajet['nombre_places_occupees'] or 0),
                    f"{trajet['distance_km'] or 0} km"
                ])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
        
        doc.build(story)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        filename = f"trajets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return pdf_content, filename
    
    # ==================== MÉTHODES UTILITAIRES ====================
    
    @staticmethod
    def _format_panne_rapport(panne: PanneBusUdM) -> Dict[str, Any]:
        """Formate une panne pour les rapports"""
        return {
            'id': panne.id,
            'date_heure': panne.date_heure,
            'numero_bus_udm': panne.numero_bus_udm,
            'immatriculation': panne.immatriculation,
            'description': panne.description,
            'criticite': panne.criticite,
            'immobilisation': panne.immobilisation,
            'resolue': panne.resolue,
            'enregistre_par': panne.enregistre_par
        }
    
    @staticmethod
    def _format_vidange_rapport(vidange: Vidange) -> Dict[str, Any]:
        """Formate une vidange pour les rapports"""
        bus = BusUdM.query.get(vidange.bus_udm_id)
        return {
            'id': vidange.id,
            'date_vidange': vidange.date_vidange,
            'bus_numero': bus.numero if bus else None,
            'bus_immatriculation': bus.immatriculation if bus else None,
            'kilometrage': vidange.kilometrage,
            'type_huile': vidange.type_huile,
            'remarque': vidange.remarque
        }
    
    @staticmethod
    def _format_carburation_rapport(carburation: Carburation) -> Dict[str, Any]:
        """Formate une carburation pour les rapports"""
        bus = BusUdM.query.get(carburation.bus_udm_id)
        return {
            'id': carburation.id,
            'date_carburation': carburation.date_carburation,
            'bus_numero': bus.numero if bus else None,
            'bus_immatriculation': bus.immatriculation if bus else None,
            'quantite_litres': carburation.quantite_litres,
            'prix_unitaire': carburation.prix_unitaire,
            'cout_total': carburation.cout_total
        }
