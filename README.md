# Movie Explorer Python

Projet Python simple pour rechercher des films, séries ou jeux avec l'API OMDb.

## Fonctionnalités

- Recherche par titre
- Filtre par type : film, série, jeu ou tous
- Affichage des posters
- Détails complets : année, genre, durée, acteurs, résumé, notes
- Favoris sauvegardés localement dans `favorites.json`
- Lecteur vidéo intégré avec sous-titres `.vtt` configurables par film dans `player_sources.json`
- Statut de connexion affiché dans la navbar
- Mode SSO sans interface personnalisée dans l'app via headers compatibles Keycloak
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
OMDB_API_KEYS=cle_1,cle_2,cle_3

# ou version simple
OMDB_API_KEY=ta_cle_api_ici
```

Tu peux utiliser la clé que tu as déjà obtenue depuis OMDb. Par sécurité, ne mets pas ta clé directement dans le code et ne publie pas `.env` sur GitHub.

## Authentification Keycloak sans interface

Cette app peut fonctionner derrière Keycloak sans écran de login dans Streamlit.
Le principe est le suivant :

1. Keycloak gère la connexion en dehors de l'app.
2. Un proxy (par exemple `oauth2-proxy`, Nginx, Traefik, Caddy) transmet un header de confiance.
3. Streamlit lit ce header et affiche l'état de connexion dans la navbar.

Exemple de configuration locale :

```env
AUTH_MODE=header
AUTH_REQUIRED=true
AUTH_HEADER_CANDIDATES=x-auth-request-email,x-auth-request-user,x-forwarded-email,x-forwarded-user
```

Pour du développement local sans proxy, tu peux simuler un utilisateur :

```env
AUTH_DEV_USER=dev@example.com
```

Si `AUTH_REQUIRED=true` et qu'aucun header utilisateur n'est transmis, l'app se bloque volontairement.

## Lancement

```bash
streamlit run app.py
```

Puis ouvre l'adresse affichée dans le terminal, souvent :

```text
http://localhost:8501
```

## Lecture avec sous-titres

1. Ouvre un film puis clique sur `Regarder`.
2. Dans `Configurer la vidéo et les sous-titres`, colle une URL vidéo directe comme `https://.../movie.mp4`.
3. Ajoute si besoin une URL de sous-titre WebVTT comme `https://.../subtitle-fr.vtt`.
4. Enregistre, puis lance la lecture dans le lecteur intégré.

Remarques :

- Le lecteur HTML5 fonctionne surtout avec des URLs directes lisibles par le navigateur, par exemple MP4 ou WebM.
- Les sous-titres doivent être au format `.vtt`.
- La vidéo et le fichier `.vtt` doivent être accessibles depuis le navigateur et autoriser le chargement cross-origin si elles viennent d'un autre domaine.

## Déploiement sur Streamlit Cloud

1. Mets le projet sur GitHub.
2. Va sur Streamlit Cloud.
3. Crée une nouvelle application.
4. Sélectionne le fichier `app.py`.
5. Dans **Settings > Secrets**, ajoute :

```toml
OMDB_API_KEYS = ["cle_1", "cle_2", "cle_3"]

# ou version simple
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
OMDB_API_KEYS=cle_1,cle_2,cle_3

# ou version simple
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
