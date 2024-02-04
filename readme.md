## Moteur de recherche

## Description

### Crawler

1. Aller sur un site
2. Récupérer l'ensemble des informations importantes
3. Récupérer l'ensemble des liens
4. Stockage en base de données
5. Recommencer avec un lien en attente

Limite : l'utilisation de la librairie BeautifulSoup ne permet pas de récupérer le contenu des sites webs chargés dynamiquement en javascript. Ceux-ci seront donc mal référencés.

### Moteur de recherche

## Installation

- Installer Python

Installer les librairies suivantes : 
```bash
pip install sqlalchemy
pip install beautifulsoup4
pip install python-dotenv
pip install nltk
pip install requests
```
A la racine du projet créer un fichier .env permettant de stocker les variables d'environnement. Exemple :
```bash
DB_SERVER=localhost
DB_PORT=5432
DB_USER=postgres
DB_PWD=admin
DB_BASE=search-engine