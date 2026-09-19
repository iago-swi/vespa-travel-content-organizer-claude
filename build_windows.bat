@echo off
REM =====================================================================
REM  Vespa Travel Content Organizer - construction de l'application
REM  Windows portable (un seul .exe, aucune installation requise).
REM
REM  A executer UNE FOIS, sur le PC Windows, dans le dossier qui contient
REM  vespa_organizer.py et vespa.ico. Le resultat est place dans dist\.
REM =====================================================================

setlocal
cd /d "%~dp0"

echo.
echo === Verification de Python ===
where py >nul 2>nul
if %errorlevel%==0 (set PY=py) else (set PY=python)
%PY% --version || (
    echo.
    echo Python est introuvable. Installez-le depuis python.org
    echo en cochant "Add python.exe to PATH".
    pause & exit /b 1
)

echo.
echo === Installation de PyInstaller ===
%PY% -m pip install --upgrade pyinstaller || (echo Echec pip & pause & exit /b 1)

echo.
echo === Construction ===
%PY% -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "Vespa Organizer" ^
    --icon vespa.ico ^
    --add-data "vespa.ico;." ^
    --noconfirm ^
    --clean ^
    vespa_organizer.py || (echo Echec de la construction & pause & exit /b 1)

echo.
echo =====================================================================
echo  Termine.
echo.
echo  L'application se trouve ici :
echo      %cd%\dist\Vespa Organizer.exe
echo.
echo  C'est un fichier unique et portable : copiez-le ou vous voulez,
echo  y compris sur une cle USB. Aucune installation, aucun Python
echo  necessaire sur la machine qui l'execute.
echo.
echo  Premier lancement : Windows SmartScreen peut afficher un
echo  avertissement (l'executable n'est pas signe). Cliquez sur
echo  "Informations complementaires" puis "Executer quand meme".
echo  Cela n'arrive qu'une fois.
echo.
echo  Pour l'epingler a la barre des taches : lancez-le, puis clic
echo  droit sur son icone dans la barre des taches, "Epingler".
echo =====================================================================
echo.
pause
