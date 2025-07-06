from app import create_app
from app.database import db
from app.models.utilisateur import Utilisateur

app = create_app()
with app.app_context():
    users = Utilisateur.query.filter((Utilisateur.nom_utilisateur == None) | (Utilisateur.nom_utilisateur == "")).all()
    for user in users:
        # Met à jour le nom si possible, ici on met le login comme nom par défaut
        user.nom_utilisateur = user.login
        print(f"Utilisateur {user.login} corrigé avec nom_utilisateur = {user.login}")
    db.session.commit()
print("Correction terminée.")
