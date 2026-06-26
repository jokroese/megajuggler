import { describe, expect, test } from "vitest";
import { bucketTricks, type Trick } from "./tricks";

const tricks: Trick[] = [
  {
    id: "cascade",
    title: "Cascade",
    source_url: "https://example.com/cascade",
    object_count: 3,
    siteswap: "3",
    difficulty: 1,
    prerequisites: [],
  },
  {
    id: "reverse-cascade",
    title: "Reverse Cascade",
    source_url: "https://example.com/reverse-cascade",
    object_count: 3,
    siteswap: "3",
    difficulty: 2,
    prerequisites: ["cascade"],
  },
  {
    id: "als-slide",
    title: "Al's Slide",
    source_url: "https://example.com/als-slide",
    object_count: 3,
    siteswap: "(4x,2x)(2,4x)*",
    difficulty: 4,
    prerequisites: ["infinity"],
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
