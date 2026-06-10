require("dotenv").config();

const express = require("express");
const cors = require("cors");
const rateLimit = require("express-rate-limit");
const config = require("./config");
const createUploadMiddleware = require("./middleware/upload");
const OpenSubtitlesProvider = require("./providers/openSubtitlesProvider");
const SubDLProvider = require("./providers/subdlProvider");
const createSubtitlesRouter = require("./routes/subtitles");
const SubtitleService = require("./services/SubtitleService");
const SubtitleRepository = require("./storage/subtitleRepository");

async function createApp() {
  const repository = new SubtitleRepository(config.dataFile);
  const service = new SubtitleService({
    config,
    repository,
    providers: {
      subdl: new SubDLProvider(config),
      opensubtitles: new OpenSubtitlesProvider(config),
    },
  });

  await service.init();

  const app = express();
  app.use(cors());
  app.use(express.json({ limit: "512kb" }));
  app.use(express.urlencoded({ extended: true }));

  app.use(
    "/subtitles",
    express.static(config.subtitlesDir, {
      setHeaders(response, filePath) {
        if (filePath.endsWith(".vtt")) {
          response.setHeader("Content-Type", "text/vtt; charset=utf-8");
        }
      },
    }),
  );

  app.get("/health", (req, res) => {
    res.json({ ok: true });
  });

  const fetchRateLimiter = rateLimit({
    windowMs: 60 * 1000,
    max: 10,
    standardHeaders: true,
    legacyHeaders: false,
    message: {
      error: "Too many subtitle fetch attempts. Please retry in a minute.",
    },
  });

  const controller = require("./controllers/subtitlesController")(service);
  const upload = createUploadMiddleware(config);
  app.use("/api", createSubtitlesRouter({ controller, upload, fetchRateLimiter }));

  app.use((error, req, res, next) => {
    const status = error.status || 500;
    res.status(status).json({
      error: error.message || "Unexpected subtitle service error.",
    });
  });

  return app;
}

module.exports = createApp;
