const { normalizeLanguageCode, pickRequestedLanguages } = require("../utils/languages");
const { assertValidImdbId, createHttpError, toBoolean } = require("../utils/validation");
const { removeFileQuietly } = require("../utils/fileSystem");

function createSubtitlesController(service) {
  return {
    async getSubtitles(req, res, next) {
      try {
        const imdbId = String(req.params.imdbId || "").trim();
        assertValidImdbId(imdbId);

        const subtitles = await service.getLocalSubtitles(imdbId);
        res.json(subtitles);
      } catch (error) {
        next(error);
      }
    },

    async fetchSubtitles(req, res, next) {
      try {
        const imdbId = String(req.params.imdbId || "").trim();
        assertValidImdbId(imdbId);

        const languages = pickRequestedLanguages(req.body?.languages);
        const provider = String(req.body?.provider || "subdl").trim().toLowerCase();
        const subtitles = await service.fetchMissingSubtitles(imdbId, languages, provider);
        res.json(subtitles);
      } catch (error) {
        next(error);
      }
    },

    async uploadSubtitle(req, res, next) {
      try {
        const imdbId = String(req.params.imdbId || "").trim();
        assertValidImdbId(imdbId);

        if (!req.file) {
          throw createHttpError(400, "A subtitle file is required.");
        }

        const languageCode = normalizeLanguageCode(req.body?.languageCode);
        if (!languageCode) {
          throw createHttpError(400, "languageCode must be one of ar, fr or en.");
        }

        const subtitles = await service.ingestManualSubtitle({
          imdbId,
          languageCode,
          sourcePath: req.file.path,
          originalName: req.file.originalname,
          isDefault: toBoolean(req.body?.isDefault),
        });

        res.status(201).json(subtitles);
      } catch (error) {
        await removeFileQuietly(req.file?.path);
        next(error);
      }
    },
  };
}

module.exports = createSubtitlesController;
