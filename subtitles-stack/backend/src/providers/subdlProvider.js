const axios = require("axios");
const { getLanguageMeta, normalizeLanguageCode, pickRequestedLanguages } = require("../utils/languages");

function extractSubtitlesArray(payload) {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (Array.isArray(payload?.subtitles)) {
    return payload.subtitles;
  }

  if (Array.isArray(payload?.data?.subtitles)) {
    return payload.data.subtitles;
  }

  if (Array.isArray(payload?.data)) {
    return payload.data;
  }

  if (Array.isArray(payload?.results)) {
    return payload.results;
  }

  return [];
}

class SubDLProvider {
  constructor(config) {
    this.baseUrl = config.subdlBaseUrl;
    this.apiKey = config.subdlApiKey;
  }

  isConfigured() {
    return Boolean(this.apiKey);
  }

  async search(imdbId, languages) {
    if (!this.isConfigured()) {
      return [];
    }

    const requestedLanguages = pickRequestedLanguages(languages);
    const response = await axios.get(`${this.baseUrl}/subtitles`, {
      params: {
        api_key: this.apiKey,
        imdb_id: imdbId,
        languages: requestedLanguages.join(","),
      },
      timeout: 15000,
    });

    const items = extractSubtitlesArray(response.data);
    const bestByLanguage = new Map();

    for (const item of items) {
      const languageCode = normalizeLanguageCode(
        item?.language_code || item?.lang || item?.language || item?.lang_code || item?.iso639,
      );

      if (!languageCode || !requestedLanguages.includes(languageCode)) {
        continue;
      }

      const candidate = {
        provider: "subdl",
        imdbId,
        languageCode,
        languageLabel: getLanguageMeta(languageCode)?.label || item?.language || languageCode,
        fileName:
          item?.file_name || item?.filename || item?.name || item?.release_name || `${imdbId}.${languageCode}.zip`,
        downloadUrl: item?.download_url || item?.file_url || item?.link || item?.url || null,
        sourceDownloadUrl: item?.download_url || item?.file_url || item?.link || item?.url || null,
        score: Number(item?.downloads || item?.download_count || item?.score || 0),
      };

      if (!candidate.downloadUrl) {
        continue;
      }

      const current = bestByLanguage.get(languageCode);
      if (!current || candidate.score > current.score) {
        bestByLanguage.set(languageCode, candidate);
      }
    }

    return Array.from(bestByLanguage.values());
  }

  async getDownloadResult(result) {
    if (!result.downloadUrl) {
      throw new Error("SubDL did not return a direct subtitle download URL.");
    }

    return {
      downloadUrl: result.downloadUrl,
      fileName: result.fileName || `${result.imdbId}.${result.languageCode}.zip`,
    };
  }
}

module.exports = SubDLProvider;
