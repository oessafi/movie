function normalizeLineEndings(text) {
  return String(text || "")
    .replace(/^\uFEFF/, "")
    .replace(/\r\n/g, "\n")
    .replace(/\r/g, "\n");
}

function convertSrtToVtt(srtContent) {
  const normalized = normalizeLineEndings(srtContent);
  const lines = normalized.split("\n");
  const output = ["WEBVTT", ""];

  for (let index = 0; index < lines.length; index += 1) {
    const currentLine = lines[index];
    const nextLine = lines[index + 1] || "";
    const trimmed = currentLine.trim();

    if (/^\d+$/.test(trimmed) && /-->/.test(nextLine)) {
      continue;
    }

    output.push(currentLine.replace(/(\d{2}:\d{2}:\d{2}),(\d{3})/g, "$1.$2"));
  }

  return `${output.join("\n").trimEnd()}\n`;
}

function normalizeVttContent(vttContent) {
  const normalized = normalizeLineEndings(vttContent).trim();
  if (normalized.startsWith("WEBVTT")) {
    return `${normalized}\n`;
  }

  return `WEBVTT\n\n${normalized}\n`;
}

module.exports = {
  convertSrtToVtt,
  normalizeVttContent,
};
