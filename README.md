# Movie Explorer Python

Projet Python simple pour rechercher des films, séries ou jeux avec l'API OMDb.

## Fonctionnalités

- Recherche par titre
- Filtre par type : film, série, jeu ou tous
- Affichage des posters
- Détails complets : année, genre, durée, acteurs, résumé, notes
- Favoris sauvegardés localement dans `favorites.json`
- Prêt pour déploiement Streamlit Cloud, Render ou Docker

## Installation locale

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Installe les dépendances :

```bash
pip install -r requirements.txt
```

Crée le fichier `.env` :

```bash
copy .env.example .env
```

Sur macOS/Linux :

```bash
cp .env.example .env
```

Puis modifie `.env` :

```env
OMDB_API_KEY=ta_cle_api_ici
```

Tu peux utiliser la clé que tu as déjà obtenue depuis OMDb. Par sécurité, ne mets pas ta clé directement dans le code et ne publie pas `.env` sur GitHub.

## Lancement

```bash
streamlit run app.py
```

Puis ouvre l'adresse affichée dans le terminal, souvent :

```text
http://localhost:8501
```

## Déploiement sur Streamlit Cloud

1. Mets le projet sur GitHub.
2. Va sur Streamlit Cloud.
3. Crée une nouvelle application.
4. Sélectionne le fichier `app.py`.
5. Dans **Settings > Secrets**, ajoute :

```toml
OMDB_API_KEY = "ta_cle_api_ici"
```

6. Déploie l'application.

## Déploiement sur Render

1. Mets le projet sur GitHub.
2. Crée un Web Service sur Render.
3. Build command :

```bash
pip install -r requirements.txt
```

4. Start command :

```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

5. Ajoute une variable d'environnement :

```text
OMDB_API_KEY=ta_cle_api_ici
```

## Structure

```text
movie_explorer_python/
├── app.py
├── omdb_client.py
├── favorites.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── Procfile
├── runtime.txt
├── Dockerfile
└── .streamlit/
    ├── config.toml
    └── secrets.toml.example
```

## Remarque importante

La clé API ne doit pas être visible dans le dépôt GitHub public. Utilise toujours `.env`, Streamlit Secrets ou les variables d'environnement de Render.
