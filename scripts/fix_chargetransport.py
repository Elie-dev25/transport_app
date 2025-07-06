from app import create_app
from app.database import db
from app.models.utilisateur import Utilisateur
from app.models.chargetransport import Chargetransport

app = create_app()
with app.app_context():
    # Vérifie que chaque utilisateur CHARGE a une entrée dans chargetransport
    users = Utilisateur.query.filter_by(role='CHARGE').all()
    for user in users:
        chargeur = Chargetransport.query.filter_by(chargetransport_id=user.utilisateur_id).first()
        if not chargeur:
            # Crée l'entrée manquante
            new_chargeur = Chargetransport(chargetransport_id=user.utilisateur_id, utilisateur_id=user.utilisateur_id)
            db.session.add(new_chargeur)
            print(f"Ajouté dans chargetransport: utilisateur_id={user.utilisateur_id}, nom={user.nom_utilisateur}")
        else:
            print(f"Déjà présent: utilisateur_id={user.utilisateur_id}, nom={user.nom_utilisateur}")
    db.session.commit()
print("Vérification et correction terminées.")
