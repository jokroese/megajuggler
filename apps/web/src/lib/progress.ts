const STORAGE_KEY = "megajuggler:known-tricks:v1";

export function loadKnownIds(): Set<string> {
  if (typeof localStorage === "undefined") {
    return new Set();
  }

  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return new Set();
  }

  try {
    const parsed: unknown = JSON.parse(raw);
    return new Set(
      Array.isArray(parsed) ? parsed.filter((value) => typeof value === "string") : [],
    );
  } catch {
    return new Set();
  }
}

export function saveKnownIds(ids: Set<string>): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...ids].sort()));
}
