const API_BASE_URL = import.meta.env.VITE_SUBTITLE_API_BASE_URL || "http://localhost:4000";

function buildUrl(path) {
  return `${API_BASE_URL}${path}`;
}

async function parseJsonResponse(response) {
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || "Subtitle request failed.");
  }
  return payload;
}

export function toAbsoluteAssetUrl(fileUrl) {
  if (!fileUrl) {
    return "";
  }

  if (/^https?:\/\//i.test(fileUrl)) {
    return fileUrl;
  }

  return buildUrl(fileUrl);
}

export async function getSubtitles(imdbId) {
  const response = await fetch(buildUrl(`/api/movies/${imdbId}/subtitles`));
  return parseJsonResponse(response);
}

export async function fetchSubtitles(imdbId, languages = ["ar", "fr", "en"], provider = "subdl") {
  const response = await fetch(buildUrl(`/api/movies/${imdbId}/subtitles/fetch`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ languages, provider }),
  });

  return parseJsonResponse(response);
}

export async function uploadSubtitle(imdbId, formData) {
  const response = await fetch(buildUrl(`/api/movies/${imdbId}/subtitles/upload`), {
    method: "POST",
    body: formData,
  });

  return parseJsonResponse(response);
}
