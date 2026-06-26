export type Trick = {
  id: string;
  title: string;
  source_url: string;
  object_count: number | null;
  siteswap: string | null;
  difficulty: number | null;
  prerequisites: string[];
};

export type TrickBuckets = {
  known: Trick[];
  learnable: Trick[];
  blocked: Trick[];
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

export function trickTitleById(tricks: Trick[]): Map<string, string> {
  return new Map(tricks.map((trick) => [trick.id, trick.title]));
}
