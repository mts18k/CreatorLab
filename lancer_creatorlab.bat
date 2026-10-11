@echo off
setlocal
cd /d "%~dp0"
title CreatorLab - Correctif interface
 echo =====================================
 echo     CREATORLAB - LANCEMENT CORRIGE
 echo =====================================
where python >nul 2>nul
if errorlevel 1 (
  echo Python n'est pas installe ou pas ajoute au PATH.
  echo Installe Python depuis https://www.python.org/downloads/
  echo Choisis Python 3.10 ou plus recent et coche l'ajout au PATH.
  pause
  exit /b 1
)
echo.
echo Mise a jour de Streamlit et des dependances...
python -m pip install --upgrade pip
python -m pip install --upgrade -r requirements.txt
if errorlevel 1 (
  echo.
  echo Echec de l'installation. Verifie la connexion Internet puis relance.
  pause
  exit /b 1
)
echo.
echo Nettoyage du cache Streamlit...
python -m streamlit cache clear
 echo.
 echo Ouverture de CreatorLab sur http://localhost:8503
 echo Si Chrome affiche encore une erreur, ouvre Edge ou une fenetre privee.
 echo Pour arreter le serveur, reviens ici puis fais Ctrl+C.
 echo.
python -m streamlit run app.py --server.port 8503
pause
