const LANGUAGE_CATALOG = {
  ar: { code: "ar", label: "العربية" },
  fr: { code: "fr", label: "Français" },
  en: { code: "en", label: "English" },
};

const LANGUAGE_ALIASES = {
  ar: "ar",
  ara: "ar",
  arabic: "ar",
  العربية: "ar",
  fr: "fr",
  fra: "fr",
  fre: "fr",
  french: "fr",
  francais: "fr",
  français: "fr",
  en: "en",
  eng: "en",
  english: "en",
};

function normalizeLanguageCode(value) {
  if (!value) {
    return null;
  }

  const normalized = String(value).trim().toLowerCase();
  return LANGUAGE_ALIASES[normalized] || null;
}

function getLanguageMeta(languageCode) {
  const normalized = normalizeLanguageCode(languageCode);
  return normalized ? LANGUAGE_CATALOG[normalized] : null;
}

function pickRequestedLanguages(languages) {
  const rawValues = Array.isArray(languages) && languages.length ? languages : Object.keys(LANGUAGE_CATALOG);
  const result = [];
  const seen = new Set();

  for (const value of rawValues) {
    const normalized = normalizeLanguageCode(value);
    if (!normalized || seen.has(normalized)) {
      continue;
    }

    seen.add(normalized);
    result.push(normalized);
  }

  return result.length ? result : Object.keys(LANGUAGE_CATALOG);
}

module.exports = {
  LANGUAGE_CATALOG,
  getLanguageMeta,
  normalizeLanguageCode,
  pickRequestedLanguages,
};
