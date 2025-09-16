print("Test simple")
try:
    from app.services.dashboard_service import DashboardService
    print("DashboardService OK")
except Exception as e:
    print(f"Erreur DashboardService: {e}")

try:
    from app.forms.constants import FormChoices
    print("FormChoices OK")
except Exception as e:
    print(f"Erreur FormChoices: {e}")

try:
    from app.constants import AppConstants
    print("AppConstants OK")
except Exception as e:
    print(f"Erreur AppConstants: {e}")

print("Test terminé")
