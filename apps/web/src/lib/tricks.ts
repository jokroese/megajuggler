export type Trick = {
  id: string;
  title: string;
  source_url: string;
  object_count: number | null;
  siteswap: string | null;
  difficulty: number | null;
  prerequisites: string[];
  description: string | null;
};

export type TrickBuckets = {
  known: Trick[];
  learnable: Trick[];
  blocked: Trick[];
};

export type DifficultyFilter = "all" | "easy" | "medium" | "hard";

export type TrickFilters = {
  query: string;
  objectCount: number | "all";
  difficulty: DifficultyFilter;
};

export const DEFAULT_TRICK_FILTERS: TrickFilters = {
  query: "",
  objectCount: "all",
  difficulty: "all",
};

export function bucketTricks(tricks: Trick[], knownIds: Set<string>): TrickBuckets {
  const known: Trick[] = [];
  const learnable: Trick[] = [];
  const blocked: Trick[] = [];

  for (const trick of tricks) {
    if (knownIds.has(trick.id)) {
      known.push(trick);
      continue;
    }

    const hasAllPrerequisites = trick.prerequisites.every((id) => knownIds.has(id));
    if (hasAllPrerequisites) {
      learnable.push(trick);
    } else {
      blocked.push(trick);
    }
  }

  return { known, learnable, blocked };
}

export function filterTricks(tricks: Trick[], filters: TrickFilters): Trick[] {
  const query = filters.query.trim().toLowerCase();

  return tricks.filter((trick) => {
    if (query && !matchesQuery(trick, query)) {
      return false;
    }

    if (filters.objectCount !== "all" && trick.object_count !== filters.objectCount) {
      return false;
    }

    return matchesDifficulty(trick, filters.difficulty);
  });
}

export function trickTitleById(tricks: Trick[]): Map<string, string> {
  return new Map(tricks.map((trick) => [trick.id, trick.title]));
}

export function prerequisiteTitles(trick: Trick, titles: Map<string, string>): string[] {
  return trick.prerequisites.map((id) => titles.get(id) ?? id);
}

export function missingPrerequisiteIds(trick: Trick, knownIds: Set<string>): string[] {
  return trick.prerequisites.filter((id) => !knownIds.has(id));
}

export function unlockCountsByTrickId(tricks: Trick[]): Map<string, number> {
  const unlockCounts = new Map<string, number>();

  for (const trick of tricks) {
    for (const prerequisiteId of trick.prerequisites) {
      unlockCounts.set(prerequisiteId, (unlockCounts.get(prerequisiteId) ?? 0) + 1);
    }
  }

  return unlockCounts;
}

export function availableObjectCounts(tricks: Trick[]): number[] {
  return [
    ...new Set(tricks.map((trick) => trick.object_count).filter((value) => value !== null)),
  ].toSorted((left, right) => left - right);
}

export function animationUrl(trick: Trick, extension: "webm" | "mp4"): string {
  return `/data/media/loj/${trick.id}.${extension}`;
}

export function descriptionPreview(description: string | null, maxLength = 220): string | null {
  if (!description) {
    return null;
  }

  const normalised = description.replace(/\s+/g, " ").trim();
  if (!normalised || normalised.length <= maxLength) {
    return normalised || null;
  }

  const truncated = normalised.slice(0, maxLength);
  const lastSpace = truncated.lastIndexOf(" ");
  return `${truncated.slice(0, lastSpace > 0 ? lastSpace : maxLength)}…`;
}

function matchesQuery(trick: Trick, query: string): boolean {
  return (
    trick.title.toLowerCase().includes(query) ||
    trick.id.toLowerCase().includes(query) ||
    (trick.object_count !== null && `${trick.object_count} ball`.includes(query)) ||
    (trick.object_count !== null && `${trick.object_count} balls`.includes(query)) ||
    (trick.siteswap?.toLowerCase().includes(query) ?? false)
  );
}

function matchesDifficulty(trick: Trick, difficulty: DifficultyFilter): boolean {
  if (difficulty === "all") {
    return true;
  }

  if (trick.difficulty === null) {
    return false;
  }

  if (difficulty === "easy") {
    return trick.difficulty <= 3;
  }

  if (difficulty === "medium") {
    return trick.difficulty >= 4 && trick.difficulty <= 6;
  }

  return trick.difficulty >= 7;
}
