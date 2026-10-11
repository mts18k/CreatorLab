# CreatorLab 1.1 — correctif interface

## Lancement sur Windows
1. Installe Python 3.10 ou plus récent depuis https://www.python.org/downloads/ si nécessaire.
2. Décompresse ce dossier.
3. Double-clique sur `lancer_creatorlab.bat`.
4. Le lanceur met à jour Streamlit et ses dépendances, nettoie le cache, puis ouvre le site sur `http://localhost:8503`.

## Si l'erreur React `removeChild` continue
- Ferme les anciens serveurs CreatorLab (fenêtres noires) avec `Ctrl+C`.
- Ouvre `http://localhost:8503` dans une fenêtre privée Chrome (`Ctrl+Maj+N`) ou dans Edge.
- Désactive les extensions de traduction, de correction grammaticale, de thèmes ou de modification de page pour ce test.

## Données
Les brouillons et le planning sont enregistrés localement dans `data/creatorlab_state.json`. Une clé API OpenAI, si utilisée, ne doit pas être partagée ni téléversée sur GitHub.
