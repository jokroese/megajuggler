import { describe, expect, test } from "vitest";
import {
  availableObjectCounts,
  bucketTricks,
  DEFAULT_TRICK_FILTERS,
  filterTricks,
  missingPrerequisiteIds,
  type Trick,
  unlockCountsByTrickId,
} from "./tricks";

const tricks: Trick[] = [
  {
    id: "cascade",
    title: "Cascade",
    source_url: "https://example.com/cascade",
    category: "Three Ball Patterns",
    object_count: 3,
    siteswap: "3",
    difficulty: 1,
    prerequisites: [],
    animation_gif_url: "https://example.com/cascade.gif",
    animation_webm_url: null,
    animation_mp4_url: null,
    tutorial_urls: [],
    description_preview: "The Cascade is the most basic three ball pattern.",
  },
  {
    id: "reverse-cascade",
    title: "Reverse Cascade",
    source_url: "https://example.com/reverse-cascade",
    category: "Three Ball Patterns",
    object_count: 3,
    siteswap: "3",
    difficulty: 2,
    prerequisites: ["cascade"],
    animation_gif_url: null,
    animation_webm_url: null,
    animation_mp4_url: null,
    tutorial_urls: [],
    description_preview: null,
  },
  {
    id: "als-slide",
    title: "Al's Slide",
    source_url: "https://example.com/als-slide",
    category: "Three Ball Patterns",
    object_count: 3,
    siteswap: "(4x,2x)(2,4x)*",
    difficulty: 4,
    prerequisites: ["infinity"],
    animation_gif_url: "https://example.com/als-slide.gif",
    animation_webm_url: null,
    animation_mp4_url: null,
    tutorial_urls: ["https://example.com/als-slide-tutorial"],
    description_preview: "Al's Slide is a three ball pattern.",
  },
  {
    id: "fountain",
    title: "Fountain",
    source_url: "https://example.com/fountain",
    category: "Four Ball Patterns",
    object_count: 4,
    siteswap: "4",
    difficulty: 3,
    prerequisites: [],
    animation_gif_url: null,
    animation_webm_url: null,
    animation_mp4_url: null,
    tutorial_urls: [],
    description_preview: null,
  },
  {
    id: "mystery",
    title: "Mystery",
    source_url: "https://example.com/mystery",
    category: null,
    object_count: null,
    siteswap: null,
    difficulty: null,
    prerequisites: [],
    animation_gif_url: null,
    animation_webm_url: null,
    animation_mp4_url: null,
    tutorial_urls: [],
    description_preview: null,
  },
];

describe("bucketTricks", () => {
  test("puts known tricks in known", () => {
    const buckets = bucketTricks(tricks, new Set(["cascade"]));
    expect(buckets.known.map((trick) => trick.id)).toEqual(["cascade"]);
  });

  test("puts tricks with all prerequisites in learnable", () => {
    const buckets = bucketTricks(tricks, new Set(["cascade"]));
    expect(buckets.learnable.map((trick) => trick.id)).toContain("reverse-cascade");
  });

  test("puts tricks with missing prerequisites in blocked", () => {
    const buckets = bucketTricks(tricks, new Set(["cascade"]));
    expect(buckets.blocked.map((trick) => trick.id)).toContain("als-slide");
  });

  test("treats tricks with no prerequisites as learnable when unknown", () => {
    const buckets = bucketTricks(tricks, new Set());
    expect(buckets.learnable.map((trick) => trick.id)).toContain("cascade");
  });
});

describe("filterTricks", () => {
  test("returns every trick with default filters", () => {
    expect(filterTricks(tricks, DEFAULT_TRICK_FILTERS)).toHaveLength(tricks.length);
  });

  test("filters by title query", () => {
    const filtered = filterTricks(tricks, {
      ...DEFAULT_TRICK_FILTERS,
      query: "slide",
    });
    expect(filtered.map((trick) => trick.id)).toEqual(["als-slide"]);
  });

  test("filters by category query", () => {
    const filtered = filterTricks(tricks, {
      ...DEFAULT_TRICK_FILTERS,
      query: "four ball",
    });
    expect(filtered.map((trick) => trick.id)).toEqual(["fountain"]);
  });

  test("filters by siteswap query", () => {
    const filtered = filterTricks(tricks, {
      ...DEFAULT_TRICK_FILTERS,
      query: "4x",
    });
    expect(filtered.map((trick) => trick.id)).toEqual(["als-slide"]);
  });

  test("filters by object count", () => {
    const filtered = filterTricks(tricks, {
      ...DEFAULT_TRICK_FILTERS,
      objectCount: 4,
    });
    expect(filtered.map((trick) => trick.id)).toEqual(["fountain"]);
  });

  test("filters easy tricks", () => {
    const filtered = filterTricks(tricks, {
      ...DEFAULT_TRICK_FILTERS,
      difficulty: "easy",
    });
    expect(filtered.map((trick) => trick.id)).toEqual(["cascade", "reverse-cascade", "fountain"]);
  });

  test("filters medium tricks", () => {
    const filtered = filterTricks(tricks, {
      ...DEFAULT_TRICK_FILTERS,
      difficulty: "medium",
    });
    expect(filtered.map((trick) => trick.id)).toEqual(["als-slide"]);
  });
});

describe("availableObjectCounts", () => {
  test("returns sorted unique non-null object counts", () => {
    expect(availableObjectCounts(tricks)).toEqual([3, 4]);
  });
});

describe("unlockCountsByTrickId", () => {
  test("counts direct tricks unlocked by each prerequisite", () => {
    const unlockCounts = unlockCountsByTrickId(tricks);

    expect(unlockCounts.get("cascade")).toBe(1);
    expect(unlockCounts.get("infinity")).toBe(1);
    expect(unlockCounts.get("reverse-cascade")).toBeUndefined();
  });
});

describe("missingPrerequisiteIds", () => {
  test("returns missing prerequisite IDs for a trick", () => {
    expect(
      missingPrerequisiteIds(
        {
          ...tricks[2],
          prerequisites: ["cascade", "infinity"],
        },
        new Set(["cascade"]),
      ),
    ).toEqual(["infinity"]);
  });

  test("returns an empty list when every prerequisite is known", () => {
    expect(missingPrerequisiteIds(tricks[1], new Set(["cascade"]))).toEqual([]);
  });
});
