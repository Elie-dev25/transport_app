#!/usr/bin/env python3
"""
Script d'optimisation des performances pour Transport UdM
Identifie et corrige les problèmes de performance
"""

import os
import time
from datetime import datetime, date, timedelta

# Configuration pour le développement
os.environ['FLASK_ENV'] = 'development'

def analyze_query_performance():
    """Analyse les performances des requêtes SQL"""
    print("🔍 ANALYSE DES PERFORMANCES SQL")
    print("=" * 50)
    
    from app import create_app
    from app.database import db
    from app.models.bus_udm import BusUdM
    from app.models.trajet import Trajet
    from app.models.utilisateur import Utilisateur
    from app.services.query_service import QueryService
    
    app = create_app()
    
    with app.app_context():
        # Test 1: Requêtes de base
        print("1. Test des requêtes de base...")
        
        start_time = time.time()
        bus_count = BusUdM.query.count()
        bus_time = time.time() - start_time
        print(f"   - Bus count: {bus_count} ({bus_time:.3f}s)")
        
        start_time = time.time()
        user_count = Utilisateur.query.count()
        user_time = time.time() - start_time
        print(f"   - Users count: {user_count} ({user_time:.3f}s)")
        
        start_time = time.time()
        trajet_count = Trajet.query.count()
        trajet_time = time.time() - start_time
        print(f"   - Trajets count: {trajet_count} ({trajet_time:.3f}s)")
        
        # Test 2: Requêtes complexes
        print("\n2. Test des requêtes complexes...")
        
        start_time = time.time()
        active_buses = QueryService.get_active_buses()
        active_buses_time = time.time() - start_time
        print(f"   - Active buses: {len(active_buses)} ({active_buses_time:.3f}s)")
        
        start_time = time.time()
        today_trajets = QueryService.get_trajets_by_date(date.today())
        today_trajets_time = time.time() - start_time
        print(f"   - Today trajets: {len(today_trajets)} ({today_trajets_time:.3f}s)")
        
        # Test 3: Requêtes avec jointures
        print("\n3. Test des requêtes avec jointures...")
        
        start_time = time.time()
        # Requête avec jointure explicite (plus efficace)
        trajets_with_bus = db.session.query(Trajet).join(BusUdM, Trajet.numero_bus_udm == BusUdM.numero).limit(10).all()
        join_time = time.time() - start_time
        print(f"   - Trajets with bus (JOIN): {len(trajets_with_bus)} ({join_time:.3f}s)")
        
        # Analyse des résultats
        print("\n📊 ANALYSE DES PERFORMANCES:")
        total_time = bus_time + user_time + trajet_time + active_buses_time + today_trajets_time + join_time
        print(f"   - Temps total: {total_time:.3f}s")
        
        if total_time > 1.0:
            print("   ⚠️  Performances lentes détectées")
            return False
        else:
            print("   ✅ Performances acceptables")
            return True

def analyze_static_files():
    """Analyse les fichiers statiques"""
    print("\n🎨 ANALYSE DES FICHIERS STATIQUES")
    print("=" * 50)
    
    import os
    from pathlib import Path
    
    css_dir = Path("app/static/css")
    js_dir = Path("app/static/js")
    
    # Analyser les fichiers CSS
    css_files = list(css_dir.glob("*.css"))
    total_css_size = sum(f.stat().st_size for f in css_files)
    print(f"📄 CSS: {len(css_files)} fichiers, {total_css_size/1024:.1f} KB")
    
    large_css = [f for f in css_files if f.stat().st_size > 10000]  # > 10KB
    if large_css:
        print("   ⚠️  Fichiers CSS volumineux:")
        for f in large_css:
            print(f"      - {f.name}: {f.stat().st_size/1024:.1f} KB")
    
    # Analyser les fichiers JS
    js_files = list(js_dir.glob("*.js"))
    total_js_size = sum(f.stat().st_size for f in js_files)
    print(f"📄 JS: {len(js_files)} fichiers, {total_js_size/1024:.1f} KB")
    
    large_js = [f for f in js_files if f.stat().st_size > 10000]  # > 10KB
    if large_js:
        print("   ⚠️  Fichiers JS volumineux:")
        for f in large_js:
            print(f"      - {f.name}: {f.stat().st_size/1024:.1f} KB")
    
    # Recommandations
    print("\n💡 RECOMMANDATIONS:")
    if total_css_size > 50000:  # > 50KB
        print("   - Considérer la minification CSS")
    if total_js_size > 50000:  # > 50KB
        print("   - Considérer la minification JS")
    if len(css_files) > 10:
        print("   - Considérer la concaténation CSS")
    if len(js_files) > 10:
        print("   - Considérer la concaténation JS")

def check_database_indexes():
    """Vérifier les index de base de données"""
    print("\n🗄️  ANALYSE DES INDEX DE BASE DE DONNÉES")
    print("=" * 50)
    
    from app import create_app
    from app.database import db
    
    app = create_app()
    
    with app.app_context():
        # Vérifier les tables principales
        tables_to_check = [
            'utilisateur',
            'bus_udm', 
            'trajet',
            'chauffeur',
            'panne_bus_udm',
            'carburation',
            'vidange'
        ]
        
        print("📋 Tables analysées:")
        for table in tables_to_check:
            try:
                # Requête pour obtenir les index (SQLite)
                result = db.session.execute(f"PRAGMA index_list({table})")
                indexes = result.fetchall()
                print(f"   - {table}: {len(indexes)} index")
            except Exception as e:
                print(f"   - {table}: Erreur - {e}")
        
        # Recommandations d'index
        print("\n💡 RECOMMANDATIONS D'INDEX:")
        print("   - trajet.date_heure_depart (pour les filtres par date)")
        print("   - trajet.numero_bus_udm (pour les jointures)")
        print("   - utilisateur.login (pour l'authentification)")
        print("   - bus_udm.etat_vehicule (pour les filtres de statut)")

def main():
    """Fonction principale d'analyse des performances"""
    print("🚀 ANALYSE COMPLÈTE DES PERFORMANCES")
    print("Transport UdM - Optimisation")
    print("=" * 60)
    
    try:
        # Tests de performance
        sql_ok = analyze_query_performance()
        analyze_static_files()
        check_database_indexes()
        
        # Résumé
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DE L'ANALYSE")
        print("=" * 60)
        
        if sql_ok:
            print("✅ Performances SQL: Acceptables")
        else:
            print("⚠️  Performances SQL: À optimiser")
        
        print("\n💡 PROCHAINES ÉTAPES:")
        print("1. Implémenter la mise en cache")
        print("2. Optimiser les requêtes lentes")
        print("3. Minifier les assets CSS/JS")
        print("4. Ajouter des index de base de données")
        print("5. Implémenter la compression gzip")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
