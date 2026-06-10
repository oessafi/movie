const fs = require("fs");
const fsp = require("fs/promises");
const path = require("path");
const { randomUUID } = require("crypto");
const { pipeline } = require("stream/promises");
const axios = require("axios");
const unzipper = require("unzipper");
const { convertSrtToVtt, normalizeVttContent } = require("../utils/convertSrtToVtt");
const { ensureDirectory, fileExists, removeFileQuietly } = require("../utils/fileSystem");
const { getLanguageMeta, pickRequestedLanguages } = require("../utils/languages");
const { assertSafeDownloadUrl, createHttpError, isAllowedSubtitleExtension } = require("../utils/validation");

class SubtitleService {
  constructor({ config, repository, providers }) {
    this.config = config;
    this.repository = repository;
    this.providers = providers;
  }

  async init() {
    await Promise.all([
      ensureDirectory(this.config.publicDir),
      ensureDirectory(this.config.subtitlesDir),
      ensureDirectory(this.config.tempDir),
      this.repository.init(),
    ]);
  }

  async getLocalSubtitles(imdbId) {
    const records = await this.repository.findByImdbId(imdbId);
    const subtitles = [];

    for (const record of records) {
      if (await fileExists(record.local_path)) {
        subtitles.push({
          language_code: record.language_code,
          language_label: record.language_label,
          file_url: record.file_url,
          is_default: Boolean(record.is_default),
        });
      }
    }

    return subtitles.sort((left, right) => {
      if (left.is_default !== right.is_default) {
        return left.is_default ? -1 : 1;
      }

      return left.language_code.localeCompare(right.language_code);
    });
  }

  async fetchMissingSubtitles(imdbId, languages, providerName = "subdl") {
    const requestedLanguages = pickRequestedLanguages(languages);
    const localSubtitles = await this.getLocalSubtitles(imdbId);
    const localLanguages = new Set(localSubtitles.map((subtitle) => subtitle.language_code));
    const missingLanguages = requestedLanguages.filter((languageCode) => !localLanguages.has(languageCode));

    if (!missingLanguages.length) {
      return localSubtitles;
    }

    const searchResults = await this.fetchProviderResults(imdbId, missingLanguages, providerName);
    const importErrors = [];

    for (const languageCode of missingLanguages) {
      const match = searchResults.find((item) => item.languageCode === languageCode);
      if (!match) {
        continue;
      }

      try {
        await this.ingestProviderResult(imdbId, languageCode, match);
      } catch (error) {
        importErrors.push(`${languageCode}: ${error.message}`);
      }
    }

    const finalSubtitles = await this.getLocalSubtitles(imdbId);
    if (!finalSubtitles.length && importErrors.length) {
      throw createHttpError(502, `Unable to import subtitles. ${importErrors.join(" | ")}`);
    }

    return finalSubtitles;
  }

  async fetchProviderResults(imdbId, languages, providerName) {
    if (providerName === "subdl") {
      return this.searchSubDL(imdbId, languages);
    }

    if (providerName === "opensubtitles") {
      return this.searchOpenSubtitles(imdbId, languages);
    }

    throw createHttpError(400, "Unsupported subtitle provider. Use subdl or opensubtitles.");
  }

  async searchSubDL(imdbId, languages) {
    return this.providers.subdl.search(imdbId, languages);
  }

  async searchOpenSubtitles(imdbId, languages) {
    return this.providers.opensubtitles.search(imdbId, languages);
  }

  detectExtension(fileName, contentType) {
    const extension = path.extname(String(fileName || "")).toLowerCase();
    if ([".srt", ".vtt", ".zip"].includes(extension)) {
      return extension;
    }

    if (String(contentType || "").includes("zip")) {
      return ".zip";
    }

    if (String(contentType || "").includes("vtt")) {
      return ".vtt";
    }

    return ".srt";
  }

  async downloadSubtitle(result) {
    const provider = this.providers[result.provider];
    if (!provider) {
      throw new Error(`No provider registered for ${result.provider}.`);
    }

    const download = await provider.getDownloadResult(result);
    assertSafeDownloadUrl(download.downloadUrl);

    await ensureDirectory(this.config.tempDir);

    const extension = this.detectExtension(download.fileName, null);
    const targetPath = path.join(this.config.tempDir, `${randomUUID()}${extension}`);
    const response = await axios.get(download.downloadUrl, {
      responseType: "stream",
      timeout: 30000,
      maxBodyLength: this.config.maxSubtitleSizeBytes,
      maxContentLength: this.config.maxSubtitleSizeBytes,
    });

    let transferredBytes = 0;
    response.data.on("data", (chunk) => {
      transferredBytes += chunk.length;
      if (transferredBytes > this.config.maxSubtitleSizeBytes) {
        response.data.destroy(createHttpError(413, "Subtitle file is larger than the allowed limit."));
      }
    });

    await pipeline(response.data, fs.createWriteStream(targetPath));

    return {
      filePath: targetPath,
      fileName: download.fileName,
      sourceDownloadUrl: download.downloadUrl,
    };
  }

  async extractZipIfNeeded(filePath) {
    const extension = path.extname(filePath).toLowerCase();
    if (extension !== ".zip") {
      return {
        extractedPath: filePath,
        format: extension.replace(".", "") || "srt",
      };
    }

    const archive = await unzipper.Open.file(filePath);
    const entries = archive.files.filter(
      (entry) => !entry.path.endsWith("/") && [".srt", ".vtt"].includes(path.extname(entry.path).toLowerCase()),
    );

    if (!entries.length) {
      throw createHttpError(422, "The subtitle ZIP does not contain a .srt or .vtt file.");
    }

    entries.sort((left, right) => {
      const leftExtension = path.extname(left.path).toLowerCase();
      const rightExtension = path.extname(right.path).toLowerCase();
      if (leftExtension !== rightExtension) {
        return leftExtension === ".vtt" ? -1 : 1;
      }

      return left.path.length - right.path.length;
    });

    const selected = entries[0];
    const extractedPath = path.join(this.config.tempDir, `${randomUUID()}${path.extname(selected.path).toLowerCase()}`);
    await pipeline(selected.stream(), fs.createWriteStream(extractedPath));

    return {
      extractedPath,
      format: path.extname(selected.path).replace(".", ""),
    };
  }

  convertSrtToVtt(srtContent) {
    return convertSrtToVtt(srtContent);
  }

  async saveVttFile(imdbId, languageCode, content) {
    const movieDirectory = path.join(this.config.subtitlesDir, imdbId);
    const localPath = path.join(movieDirectory, `${languageCode}.vtt`);

    await ensureDirectory(movieDirectory);
    await fsp.writeFile(localPath, content, "utf8");

    return {
      fileUrl: `/subtitles/${imdbId}/${languageCode}.vtt`,
      localPath,
    };
  }

  async saveSubtitleToDb(data) {
    return this.repository.upsert(data);
  }

  async readSubtitleAsVtt(filePath, format) {
    const raw = await fsp.readFile(filePath, "utf8");
    if (format === "vtt") {
      return normalizeVttContent(raw);
    }

    return this.convertSrtToVtt(raw);
  }

  async ingestProviderResult(imdbId, languageCode, result) {
    let downloadedFile = null;
    let extractedFile = null;

    try {
      downloadedFile = await this.downloadSubtitle(result);
      extractedFile = await this.extractZipIfNeeded(downloadedFile.filePath);
      const vttContent = await this.readSubtitleAsVtt(extractedFile.extractedPath, extractedFile.format);
      const savedFile = await this.saveVttFile(imdbId, languageCode, vttContent);
      const languageMeta = getLanguageMeta(languageCode);

      await this.saveSubtitleToDb({
        id: `${imdbId}:${languageCode}`,
        imdb_id: imdbId,
        movie_id: null,
        language_code: languageCode,
        language_label: languageMeta?.label || languageCode,
        provider: result.provider,
        original_format: extractedFile.format,
        file_url: savedFile.fileUrl,
        local_path: savedFile.localPath,
        source_download_url: downloadedFile.sourceDownloadUrl || result.sourceDownloadUrl || null,
        is_default: languageCode === "ar",
      });
    } finally {
      await removeFileQuietly(extractedFile?.extractedPath);
      await removeFileQuietly(downloadedFile?.filePath);
    }
  }

  async ingestManualSubtitle({ imdbId, languageCode, sourcePath, originalName, isDefault = false }) {
    const extension = path.extname(String(originalName || "")).toLowerCase();
    if (![".srt", ".vtt"].includes(extension)) {
      throw createHttpError(400, "Only .srt and .vtt uploads are allowed.");
    }

    const vttContent = await this.readSubtitleAsVtt(sourcePath, extension.replace(".", ""));
    const savedFile = await this.saveVttFile(imdbId, languageCode, vttContent);
    const languageMeta = getLanguageMeta(languageCode);

    await this.saveSubtitleToDb({
      id: `${imdbId}:${languageCode}`,
      imdb_id: imdbId,
      movie_id: null,
      language_code: languageCode,
      language_label: languageMeta?.label || languageCode,
      provider: "manual",
      original_format: extension.replace(".", ""),
      file_url: savedFile.fileUrl,
      local_path: savedFile.localPath,
      source_download_url: null,
      is_default: Boolean(isDefault),
    });

    await removeFileQuietly(sourcePath);
    return this.getLocalSubtitles(imdbId);
  }
}

module.exports = SubtitleService;
