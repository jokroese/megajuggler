import { describe, expect, test } from "vitest";
import {
  animationUrl,
  availableObjectCounts,
  bucketTricks,
  DEFAULT_TRICK_FILTERS,
  descriptionPreview,
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
    object_count: 3,
    siteswap: "3",
    difficulty: 1,
    prerequisites: [],
    description: "The Cascade is the most basic three ball pattern.",
  },
  {
    id: "reverse-cascade",
    title: "Reverse Cascade",
    source_url: "https://example.com/reverse-cascade",
    object_count: 3,
    siteswap: "3",
    difficulty: 2,
    prerequisites: ["cascade"],
    description: null,
  },
  {
    id: "als-slide",
    title: "Al's Slide",
    source_url: "https://example.com/als-slide",
    object_count: 3,
    siteswap: "(4x,2x)(2,4x)*",
    difficulty: 4,
    prerequisites: ["infinity"],
    description: "Al's Slide is a three ball pattern.",
  },
  {
    id: "fountain",
    title: "Fountain",
    source_url: "https://example.com/fountain",
    object_count: 4,
    siteswap: "4",
    difficulty: 3,
    prerequisites: [],
    description: null,
  },
  {
    id: "mystery",
    title: "Mystery",
    source_url: "https://example.com/mystery",
    object_count: null,
    siteswap: null,
    difficulty: null,
    prerequisites: [],
    description: null,
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
      query: "fountain",
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

describe("animationUrl", () => {
  test("derives animation URLs from trick ID", () => {
    expect(animationUrl(tricks[0], "webm")).toBe("/data/media/loj/cascade.webm");
  });
});

describe("descriptionPreview", () => {
  test("normalises and truncates descriptions in the app", () => {
    expect(descriptionPreview("  Lots\n\nof    whitespace.  ")).toBe("Lots of whitespace.");
    const preview = descriptionPreview("word ".repeat(100), 30);
    expect(preview).not.toBeNull();
    expect(preview?.endsWith("…")).toBe(true);
    expect(preview?.length).toBeLessThanOrEqual(31);
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
