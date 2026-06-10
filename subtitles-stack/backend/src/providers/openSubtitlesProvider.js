const axios = require("axios");
const { getLanguageMeta, normalizeLanguageCode, pickRequestedLanguages } = require("../utils/languages");

class OpenSubtitlesProvider {
  constructor(config) {
    this.baseUrl = config.opensubtitlesBaseUrl;
    this.apiKey = config.opensubtitlesApiKey;
    this.userAgent = config.opensubtitlesUserAgent;
  }

  isConfigured() {
    return Boolean(this.apiKey && this.userAgent);
  }

  headers() {
    return {
      "Api-Key": this.apiKey,
      "Content-Type": "application/json",
      "User-Agent": this.userAgent,
    };
  }

  async search(imdbId, languages) {
    if (!this.isConfigured()) {
      return [];
    }

    const requestedLanguages = pickRequestedLanguages(languages);
    const imdbNumericId = imdbId.replace(/^tt/, "");
    const response = await axios.get(`${this.baseUrl}/subtitles`, {
      headers: this.headers(),
      params: {
        imdb_id: imdbNumericId,
        languages: requestedLanguages.join(","),
        order_by: "download_count",
        order_direction: "desc",
      },
      timeout: 15000,
    });

    const items = Array.isArray(response.data?.data) ? response.data.data : [];
    const bestByLanguage = new Map();

    for (const item of items) {
      const attributes = item?.attributes || {};
      const files = Array.isArray(attributes.files) ? attributes.files : [];
      const primaryFile = files[0] || {};
      const languageCode = normalizeLanguageCode(attributes.language || attributes.iso639 || primaryFile.language);

      if (!languageCode || !requestedLanguages.includes(languageCode) || !primaryFile.file_id) {
        continue;
      }

      const candidate = {
        provider: "opensubtitles",
        imdbId,
        languageCode,
        languageLabel: getLanguageMeta(languageCode)?.label || attributes.language || languageCode,
        fileName: primaryFile.file_name || `${imdbId}.${languageCode}.srt`,
        providerMetadata: {
          fileId: primaryFile.file_id,
        },
        sourceDownloadUrl: attributes.url || null,
        score: Number(attributes.download_count || 0),
      };

      const current = bestByLanguage.get(languageCode);
      if (!current || candidate.score > current.score) {
        bestByLanguage.set(languageCode, candidate);
      }
    }

    return Array.from(bestByLanguage.values());
  }

  async getDownloadResult(result) {
    const fileId = result?.providerMetadata?.fileId;
    if (!fileId) {
      throw new Error("OpenSubtitles did not return a downloadable file id.");
    }

    const response = await axios.post(
      `${this.baseUrl}/download`,
      { file_id: fileId },
      {
        headers: this.headers(),
        timeout: 15000,
      },
    );

    if (!response.data?.link) {
      throw new Error("OpenSubtitles did not return a download link.");
    }

    return {
      downloadUrl: response.data.link,
      fileName: response.data.file_name || result.fileName || `${result.imdbId}.${result.languageCode}.srt`,
    };
  }
}

module.exports = OpenSubtitlesProvider;
