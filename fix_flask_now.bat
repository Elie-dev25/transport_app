@echo off
echo 🚀 CORRECTION IMMEDIATE DE FLASK
echo ================================

echo 1. Desactivation de l'environnement virtuel...
call deactivate 2>nul

echo 2. Suppression de l'ancien environnement virtuel...
if exist venv rmdir /s /q venv

echo 3. Creation d'un nouvel environnement virtuel...
python -m venv venv

echo 4. Activation du nouvel environnement...
call venv\Scripts\activate.bat

echo 5. Mise a jour de pip...
python -m pip install --upgrade pip

echo 6. Installation des versions compatibles...
pip install Werkzeug==2.3.7
pip install Flask==2.3.3
pip install WTForms==3.0.1
pip install Flask-WTF==1.1.1
pip install SQLAlchemy==2.0.23
pip install Flask-SQLAlchemy==3.0.5
pip install Flask-Login==0.6.3
pip install PyMySQL==1.1.0
pip install ldap3==2.9.1
pip install python-dateutil==2.8.2

echo 7. Test de l'installation...
python -c "import flask; print('✅ Flask', flask.__version__, 'installe avec succes')"

echo 8. Test de l'application...
python -c "from app import create_app; app = create_app(); print('✅ Application creee avec succes')"

echo.
echo 🎉 CORRECTION TERMINEE!
echo Vous pouvez maintenant executer: python run.py
pause
