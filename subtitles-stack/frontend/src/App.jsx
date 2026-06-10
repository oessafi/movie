import { useState } from "react";
import AdminSubtitleManager from "./components/AdminSubtitleManager";
import MoviePlayer from "./components/MoviePlayer";

const SAMPLE_MOVIE = {
  imdbId: "tt1757678",
  videoUrl:
    import.meta.env.VITE_SAMPLE_VIDEO_URL || "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
  posterUrl:
    import.meta.env.VITE_SAMPLE_POSTER_URL || "https://dummyimage.com/960x540/111111/ffffff&text=IMDb+tt1757678",
};

export default function App() {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">Streaming subtitle demo</p>
        <h1>Backend-managed subtitles by IMDb ID</h1>
        <p className="hero-copy">
          This React example calls the Express subtitle backend, pulls Arabic/French/English tracks,
          and displays them in an HTML5 or HLS player without exposing provider API keys.
        </p>
      </section>

      <section className="layout">
        <MoviePlayer
          imdbId={SAMPLE_MOVIE.imdbId}
          videoUrl={SAMPLE_MOVIE.videoUrl}
          posterUrl={SAMPLE_MOVIE.posterUrl}
          refreshKey={refreshKey}
        />
        <AdminSubtitleManager imdbId={SAMPLE_MOVIE.imdbId} onRefresh={() => setRefreshKey((value) => value + 1)} />
      </section>
    </main>
  );
}
