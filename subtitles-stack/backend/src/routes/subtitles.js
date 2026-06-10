const express = require("express");

function createSubtitlesRouter({ controller, upload, fetchRateLimiter }) {
  const router = express.Router();

  router.get("/movies/:imdbId/subtitles", controller.getSubtitles);
  router.post("/movies/:imdbId/subtitles/fetch", fetchRateLimiter, controller.fetchSubtitles);
  router.post("/movies/:imdbId/subtitles/upload", upload.single("file"), controller.uploadSubtitle);

  return router;
}

module.exports = createSubtitlesRouter;
