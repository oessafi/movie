const path = require("path");
const { randomUUID } = require("crypto");
const multer = require("multer");
const { ensureDirectory } = require("../utils/fileSystem");
const { isAllowedManualUploadExtension } = require("../utils/validation");

function createUploadMiddleware(config) {
  const storage = multer.diskStorage({
    destination(req, file, callback) {
      ensureDirectory(config.tempDir)
        .then(() => callback(null, config.tempDir))
        .catch((error) => callback(error));
    },
    filename(req, file, callback) {
      callback(null, `${randomUUID()}${path.extname(file.originalname).toLowerCase()}`);
    },
  });

  return multer({
    storage,
    limits: {
      fileSize: config.maxSubtitleSizeBytes,
    },
    fileFilter(req, file, callback) {
      if (!isAllowedManualUploadExtension(file.originalname)) {
        callback(new Error("Only .srt and .vtt files are allowed for manual uploads."));
        return;
      }

      callback(null, true);
    },
  });
}

module.exports = createUploadMiddleware;
