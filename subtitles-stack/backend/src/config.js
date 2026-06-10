const path = require("path");

const rootDir = process.cwd();

module.exports = {
  rootDir,
  port: Number(process.env.PORT || 4000),
  publicDir: path.join(rootDir, "public"),
  subtitlesDir: path.join(rootDir, "public", "subtitles"),
  tempDir: path.join(rootDir, "tmp"),
  dataFile: path.join(rootDir, "data", "subtitles.json"),
  maxSubtitleSizeBytes: Number(process.env.MAX_SUBTITLE_SIZE_BYTES || 5 * 1024 * 1024),
  subdlBaseUrl: process.env.SUBDL_BASE_URL || "https://api.subdl.com/api/v1",
  opensubtitlesBaseUrl: process.env.OPENSUBTITLES_BASE_URL || "https://api.opensubtitles.com/api/v1",
  subdlApiKey: process.env.SUBDL_API_KEY || "",
  opensubtitlesApiKey: process.env.OPENSUBTITLES_API_KEY || "",
  opensubtitlesUserAgent: process.env.OPENSUBTITLES_USER_AGENT || "MovieExplorerSubtitles/1.0",
};
