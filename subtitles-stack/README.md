# Subtitle Stack

Backend Express + frontend React pour récupérer, convertir et servir des sous-titres par `imdb_id` sans exposer les clés API côté client.

## Structure

```text
subtitles-stack/
├── backend/
│   ├── data/subtitles.json
│   ├── public/subtitles/
│   ├── src/
│   └── .env.example
├── frontend/
│   ├── src/
│   └── .env.example
└── README.md
```

## 1. Ajouter les clés API

Dans `subtitles-stack/backend` :

```bash
copy .env.example .env
```

Puis remplis :

```env
PORT=4000
SUBDL_API_KEY=your_subdl_key
OPENSUBTITLES_API_KEY=your_opensubtitles_key
OPENSUBTITLES_USER_AGENT=MovieExplorerSubtitles/1.0
MAX_SUBTITLE_SIZE_BYTES=5242880
```

Dans `subtitles-stack/frontend` :

```bash
copy .env.example .env
```

## 2. Installer et lancer le backend

```bash
cd subtitles-stack/backend
npm install
npm run dev
```

Le backend démarre par défaut sur `http://localhost:4000`.

Endpoints disponibles :

- `GET /api/movies/:imdbId/subtitles`
- `POST /api/movies/:imdbId/subtitles/fetch`
- `POST /api/movies/:imdbId/subtitles/upload`

## 3. Tester la récupération des sous-titres

Exemple avec `tt1757678` :

```bash
curl -X POST http://localhost:4000/api/movies/tt1757678/subtitles/fetch ^
  -H "Content-Type: application/json" ^
  -d "{\"languages\":[\"ar\",\"fr\",\"en\"],\"provider\":\"subdl\"}"
```

Puis vérifie les pistes disponibles :

```bash
curl http://localhost:4000/api/movies/tt1757678/subtitles
```

Si tout se passe bien, les fichiers convertis sont écrits dans :

```text
backend/public/subtitles/tt1757678/ar.vtt
backend/public/subtitles/tt1757678/fr.vtt
backend/public/subtitles/tt1757678/en.vtt
```

## 4. Lancer et afficher le lecteur React

```bash
cd subtitles-stack/frontend
npm install
npm run dev
```

Le composant principal est `src/components/MoviePlayer.jsx`.

Props attendues :

- `imdbId`
- `videoUrl`
- `posterUrl`

Exemple minimal :

```jsx
<MoviePlayer
  imdbId="tt1757678"
  videoUrl="https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
  posterUrl="https://dummyimage.com/960x540/111111/ffffff&text=IMDb+tt1757678"
/>
```

Le panneau admin `src/components/AdminSubtitleManager.jsx` ajoute :

- un bouton `Récupérer les sous-titres`
- un upload manuel `.srt` / `.vtt`

## Notes d’intégration

- Le backend garde les clés API uniquement côté serveur.
- Les conversions `.srt -> .vtt` sont faites avant stockage public.
- Le stockage “base de données” est volontairement simple via `backend/data/subtitles.json`, pour être facilement remplacé par SQLite, Postgres ou MongoDB.
- L’adaptateur `OpenSubtitles` suit la structure officielle `GET /subtitles` puis `POST /download`.
- L’adaptateur `SubDL` a été isolé dans un provider dédié pour pouvoir ajuster facilement le mapping si ton compte ou ton plan SubDL renvoie des champs légèrement différents.
