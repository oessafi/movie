const path = require("path");
const { URL } = require("url");

const SUBTITLE_EXTENSIONS = new Set([".srt", ".vtt", ".zip"]);
const MANUAL_UPLOAD_EXTENSIONS = new Set([".srt", ".vtt"]);

function createHttpError(status, message) {
  const error = new Error(message);
  error.status = status;
  return error;
}

function assertValidImdbId(imdbId) {
  if (!/^tt\d{7,10}$/.test(String(imdbId || "").trim())) {
    throw createHttpError(400, "Invalid IMDb ID. Expected a value like tt1757678.");
  }
}

function assertSafeDownloadUrl(urlString) {
  let parsedUrl;

  try {
    parsedUrl = new URL(urlString);
  } catch (error) {
    throw createHttpError(400, "The subtitle provider returned an invalid download URL.");
  }

  if (!["http:", "https:"].includes(parsedUrl.protocol)) {
    throw createHttpError(400, "Only HTTP and HTTPS subtitle downloads are allowed.");
  }
}

function isAllowedSubtitleExtension(fileName) {
  return SUBTITLE_EXTENSIONS.has(path.extname(String(fileName || "")).toLowerCase());
}

function isAllowedManualUploadExtension(fileName) {
  return MANUAL_UPLOAD_EXTENSIONS.has(path.extname(String(fileName || "")).toLowerCase());
}

function toBoolean(value) {
  return ["1", "true", "yes", "on"].includes(String(value || "").trim().toLowerCase());
}

module.exports = {
  assertSafeDownloadUrl,
  assertValidImdbId,
  createHttpError,
  isAllowedManualUploadExtension,
  isAllowedSubtitleExtension,
  toBoolean,
};
