import { useEffect, useRef, useState } from "react";
import Hls from "hls.js";
import { fetchSubtitles, getSubtitles, toAbsoluteAssetUrl } from "../api/subtitlesApi";

const DEFAULT_LANGUAGES = ["ar", "fr", "en"];

function isHlsSource(videoUrl) {
  return /\.m3u8($|\?)/i.test(videoUrl || "");
}

export default function MoviePlayer({ imdbId, videoUrl, posterUrl, refreshKey = 0 }) {
  const videoRef = useRef(null);
  const [subtitles, setSubtitles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const videoElement = videoRef.current;
    if (!videoElement || !videoUrl) {
      return undefined;
    }

    let hlsInstance = null;
    if (isHlsSource(videoUrl)) {
      if (videoElement.canPlayType("application/vnd.apple.mpegurl")) {
        videoElement.src = videoUrl;
      } else if (Hls.isSupported()) {
        hlsInstance = new Hls();
        hlsInstance.loadSource(videoUrl);
        hlsInstance.attachMedia(videoElement);
      } else {
        setError("This browser cannot play HLS streams.");
      }
    } else {
      videoElement.src = videoUrl;
    }

    return () => {
      if (hlsInstance) {
        hlsInstance.destroy();
      }
    };
  }, [videoUrl]);

  useEffect(() => {
    let cancelled = false;

    async function loadSubtitles() {
      if (!imdbId) {
        return;
      }

      setLoading(true);
      setError("");
      setMessage("");

      try {
        let results = await getSubtitles(imdbId);
        if (!results.length) {
          results = await fetchSubtitles(imdbId, DEFAULT_LANGUAGES, "subdl");
          if (!cancelled && results.length) {
            setMessage("Subtitles were fetched from the backend.");
          }
        }

        if (!cancelled) {
          setSubtitles(results);
          if (!results.length) {
            setMessage("No subtitles are available for this title yet.");
          }
        }
      } catch (requestError) {
        if (!cancelled) {
          setError(requestError.message || "Unable to load subtitles.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadSubtitles();

    return () => {
      cancelled = true;
    };
  }, [imdbId, refreshKey]);

  return (
    <section className="player-card">
      <div className="player-header">
        <div>
          <p className="eyebrow">Movie Player</p>
          <h2>IMDb {imdbId}</h2>
        </div>
        {loading ? <span className="badge">Loading subtitles...</span> : null}
      </div>

      <video ref={videoRef} controls poster={posterUrl} className="movie-player">
        {!isHlsSource(videoUrl) ? <source src={videoUrl} type="video/mp4" /> : null}
        {subtitles.map((subtitle) => (
          <track
            key={subtitle.language_code}
            kind="subtitles"
            src={toAbsoluteAssetUrl(subtitle.file_url)}
            srcLang={subtitle.language_code}
            label={subtitle.language_label}
            default={subtitle.is_default}
          />
        ))}
      </video>

      {error ? <p className="panel-message panel-message--error">{error}</p> : null}
      {!error && message ? <p className="panel-message">{message}</p> : null}

      <div className="subtitle-list">
        {subtitles.length ? (
          subtitles.map((subtitle) => (
            <span key={subtitle.language_code} className="subtitle-pill">
              {subtitle.language_label}
            </span>
          ))
        ) : (
          <span className="subtitle-pill subtitle-pill--muted">No subtitle track yet</span>
        )}
      </div>
    </section>
  );
}
