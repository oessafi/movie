import { useState } from "react";
import { fetchSubtitles, uploadSubtitle } from "../api/subtitlesApi";

const LANGUAGE_OPTIONS = [
  { value: "ar", label: "العربية" },
  { value: "fr", label: "Français" },
  { value: "en", label: "English" },
];

export default function AdminSubtitleManager({ imdbId, onRefresh }) {
  const [provider, setProvider] = useState("subdl");
  const [languageCode, setLanguageCode] = useState("ar");
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleFetchClick() {
    setBusy(true);
    setMessage("");
    setError("");

    try {
      await fetchSubtitles(imdbId, ["ar", "fr", "en"], provider);
      setMessage("Subtitle fetch completed.");
      onRefresh?.();
    } catch (requestError) {
      setError(requestError.message || "Unable to fetch subtitles.");
    } finally {
      setBusy(false);
    }
  }

  async function handleUploadSubmit(event) {
    event.preventDefault();
    if (!file) {
      setError("Pick a .srt or .vtt file first.");
      return;
    }

    setBusy(true);
    setMessage("");
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("languageCode", languageCode);
      await uploadSubtitle(imdbId, formData);
      setFile(null);
      setMessage("Manual subtitle uploaded.");
      onRefresh?.();
    } catch (requestError) {
      setError(requestError.message || "Unable to upload the subtitle.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <aside className="admin-panel">
      <p className="eyebrow">Admin</p>
      <h3>Manage subtitles</h3>

      <label className="field">
        <span>Provider</span>
        <select value={provider} onChange={(event) => setProvider(event.target.value)}>
          <option value="subdl">SubDL</option>
          <option value="opensubtitles">OpenSubtitles</option>
        </select>
      </label>

      <button className="primary-button" type="button" onClick={handleFetchClick} disabled={busy}>
        Récupérer les sous-titres
      </button>

      <form onSubmit={handleUploadSubmit} className="upload-form">
        <label className="field">
          <span>Language</span>
          <select value={languageCode} onChange={(event) => setLanguageCode(event.target.value)}>
            {LANGUAGE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Manual upload (.srt / .vtt)</span>
          <input
            type="file"
            accept=".srt,.vtt"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
          />
        </label>

        <button className="secondary-button" type="submit" disabled={busy}>
          Upload subtitle
        </button>
      </form>

      {error ? <p className="panel-message panel-message--error">{error}</p> : null}
      {!error && message ? <p className="panel-message">{message}</p> : null}
    </aside>
  );
}
