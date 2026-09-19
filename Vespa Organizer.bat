@echo off
REM Lance l'application sans rien construire. Necessite Python installe.
REM Placez ce fichier a cote de vespa_organizer.py.
REM Astuce : clic droit -> Envoyer vers -> Bureau (creer un raccourci),
REM puis sur le raccourci : Proprietes -> Changer d'icone -> vespa.ico

cd /d "%~dp0"
where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw vespa_organizer.py
) else (
    start "" py -w vespa_organizer.py
)
