const STORAGE_KEY = "megajuggler:known-tricks:v1";

export type ProgressExport = {
  version: 1;
  exportedAt: string;
  knownTrickIds: string[];
};

export function loadKnownIds(): Set<string> {
  if (typeof localStorage === "undefined") {
    return new Set();
  }

  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return new Set();
  }

  try {
    return parseKnownIds(raw);
  } catch {
    return new Set();
  }
}

export function saveKnownIds(ids: Set<string>): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...ids].sort()));
}

export function createProgressExport(ids: Set<string>, exportedAt = new Date()): ProgressExport {
  return {
    version: 1,
    exportedAt: exportedAt.toISOString(),
    knownTrickIds: [...ids].sort(),
  };
}

export function serialiseProgress(ids: Set<string>, exportedAt = new Date()): string {
  return `${JSON.stringify(createProgressExport(ids, exportedAt), null, 2)}\n`;
}

export function parseProgressImport(raw: string): Set<string> {
  const parsed: unknown = JSON.parse(raw);

  if (isProgressExport(parsed)) {
    return new Set(parsed.knownTrickIds);
  }

  if (Array.isArray(parsed)) {
    return idsFromUnknownArray(parsed);
  }

  throw new Error("Progress file must contain a Megajuggler progress export.");
}

function parseKnownIds(raw: string): Set<string> {
  const parsed: unknown = JSON.parse(raw);

  if (Array.isArray(parsed)) {
    return idsFromUnknownArray(parsed);
  }

  if (isProgressExport(parsed)) {
    return new Set(parsed.knownTrickIds);
  }

  return new Set();
}

function idsFromUnknownArray(values: unknown[]): Set<string> {
  return new Set(values.filter((value) => typeof value === "string"));
}

function isProgressExport(value: unknown): value is ProgressExport {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const candidate = value as Partial<ProgressExport>;
  return (
    candidate.version === 1 &&
    typeof candidate.exportedAt === "string" &&
    Array.isArray(candidate.knownTrickIds) &&
    candidate.knownTrickIds.every((id) => typeof id === "string")
  );
}
