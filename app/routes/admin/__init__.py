from flask import Blueprint

# Création du blueprint principal pour l'administrateur
bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import des sous-modules pour enregistrer les routes
from . import dashboard
from . import gestion_bus
from . import gestion_trajets
from . import rapports
from . import maintenance
from . import gestion_utilisateurs
from . import parametres
from . import utils
