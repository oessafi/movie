const fs = require("fs/promises");
const path = require("path");
const { ensureDirectory, fileExists } = require("../utils/fileSystem");

class SubtitleRepository {
  constructor(dataFilePath) {
    this.dataFilePath = dataFilePath;
  }

  async init() {
    await ensureDirectory(path.dirname(this.dataFilePath));
    if (!(await fileExists(this.dataFilePath))) {
      await fs.writeFile(this.dataFilePath, "[]\n", "utf8");
    }
  }

  async readAll() {
    await this.init();

    const raw = await fs.readFile(this.dataFilePath, "utf8");

    try {
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    } catch (error) {
      return [];
    }
  }

  async writeAll(records) {
    await this.init();
    await fs.writeFile(this.dataFilePath, `${JSON.stringify(records, null, 2)}\n`, "utf8");
  }

  async findByImdbId(imdbId) {
    const records = await this.readAll();
    return records.filter((record) => record.imdb_id === imdbId);
  }

  async upsert(record) {
    const now = new Date().toISOString();
    const records = await this.readAll();
    const recordIndex = records.findIndex(
      (entry) => entry.imdb_id === record.imdb_id && entry.language_code === record.language_code,
    );

    if (recordIndex >= 0) {
      const existing = records[recordIndex];
      records[recordIndex] = {
        ...existing,
        ...record,
        created_at: existing.created_at || record.created_at || now,
        updated_at: now,
      };
    } else {
      records.push({
        ...record,
        created_at: record.created_at || now,
        updated_at: record.updated_at || now,
      });
    }

    await this.writeAll(records);
    return record;
  }
}

module.exports = SubtitleRepository;
